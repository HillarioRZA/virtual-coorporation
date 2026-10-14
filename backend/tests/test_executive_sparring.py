"""
Unit Tests untuk Sprint 3: The Executive Sparring Room & Stage-Gate 1.
Menguji prompt registry, node CoS, node CTO, auto-correction loop, dan router Stage-Gate 1.
"""

from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock
import pytest
import pytest_asyncio

from app.core.prompts import clear_prompt_cache, load_prompt
from app.db.init_db import init_database
from app.engine.memory import MemoryManager
from app.engine.nodes.auto_correction import extract_json_payload, parse_and_repair_schema
from app.engine.nodes.cos import cos_sparring_node
from app.engine.nodes.cto import cto_architecture_node
from app.engine.nodes.sparring import sparring_room_node
from app.engine.routers import apply_gate_decision, router_gate_1, router_sparring
from app.engine.schemas import BusinessBriefSchema, SystemArchitectureSchema
from app.engine.state import VentureState
from app.engine.state_machine import NativeStateMachine
from app.gateway.client import UnifiedLLMClient


@pytest_asyncio.fixture
async def temp_db_path(tmp_path: Path) -> str:
    """Fixture database terisolasi untuk pengujian memori blackboard."""
    db_file = tmp_path / "test_sparring.db"
    db_str = str(db_file)
    await init_database(db_str)
    return db_str


def test_load_prompts_registry() -> None:
    """TASK-3.1.1 s/d 3.1.3: Menguji loader prompt CoS, CTO, caching, dan fallback."""
    clear_prompt_cache()

    cos_prompt = load_prompt("cos")
    assert "Chief of Staff" in cos_prompt
    assert "BusinessBriefSchema" in cos_prompt

    cto_prompt = load_prompt("cto")
    assert "Chief Technology Officer" in cto_prompt
    assert "SystemArchitectureSchema" in cto_prompt

    # Test caching (harus mengembalikan string yang sama)
    assert load_prompt("cos") is cos_prompt

    # Test fallback untuk role belum ada
    fallback = load_prompt("unknown_role")
    assert "UNKNOWN_ROLE" in fallback


def test_extract_json_payload() -> None:
    """Menguji utilitas ekstraksi JSON dari blok markdown dan teks polos."""
    raw_markdown = "```json\n{\"key\": \"value\"}\n```"
    assert extract_json_payload(raw_markdown) == '{"key": "value"}'

    raw_plain = '{"key": "value"}'
    assert extract_json_payload(raw_plain) == '{"key": "value"}'


@pytest.mark.asyncio
async def test_auto_correction_loop_success_on_repair() -> None:
    """TASK-3.2.3: Menguji auto-correction loop saat output awal error lalu diperbaiki."""
    mock_client = AsyncMock(spec=UnifiedLLMClient)

    # Output awal: JSON rusak (sintaks salah)
    # Output perbaikan: JSON valid mematuhi SystemArchitectureSchema
    valid_json = """{
        "archetype_id": 2,
        "frontend_framework": "Next.js 14",
        "backend_framework": "FastAPI",
        "database": "PostgreSQL",
        "estimated_inference_cost_per_user": 0.15,
        "circuit_breaker_limits": {"max_iterations": 5, "timeout_seconds": 90}
    }"""
    mock_client.complete.side_effect = [valid_json]

    result = await parse_and_repair_schema(
        llm_client=mock_client,
        raw_response="ini bukan json { invalid }",
        system_prompt="system",
        schema_cls=SystemArchitectureSchema,
        model="mock-model",
        provider="mock",
        max_repairs=2,
    )

    assert result.archetype_id == 2
    assert result.database == "PostgreSQL"
    assert mock_client.complete.call_count == 1  # Dipanggil 1x untuk perbaikan


@pytest.mark.asyncio
async def test_auto_correction_loop_exceeded_raises_error() -> None:
    """TASK-3.2.3: Menguji bahwa jika perbaikan habis maka melempar ValueError."""
    mock_client = AsyncMock(spec=UnifiedLLMClient)
    mock_client.complete.return_value = "tetap bukan json"

    with pytest.raises(ValueError) as exc_info:
        await parse_and_repair_schema(
            llm_client=mock_client,
            raw_response="bukan json",
            system_prompt="system",
            schema_cls=SystemArchitectureSchema,
            model="mock",
            provider="mock",
            max_repairs=1,
        )
    assert "Failed to produce valid SystemArchitectureSchema" in str(exc_info.value)


@pytest.mark.asyncio
async def test_cos_sparring_node_execution(temp_db_path: str) -> None:
    """TASK-3.2.1: Menguji eksekusi node CoS dan pencatatan event ke Blackboard."""
    mem = MemoryManager(db_path=temp_db_path)
    mock_client = AsyncMock(spec=UnifiedLLMClient)

    cos_json = """{
        "problem_statement": "Churn tinggi pada SaaS B2B",
        "proposed_solution": "Mesin analitik prediksi churn berbasis machine learning",
        "target_audience": "Perusahaan SaaS skala menengah",
        "monetization_model": "usage_credits",
        "pricing_tiers": [{"tier_name": "Pro", "price_monthly": 49.0, "features_included": ["Predict"]}],
        "projected_margin_percentage": 85.0,
        "market_feasibility_score": 92,
        "risks_and_mitigations": ["Risiko data -> Validasi schema"]
    }"""
    mock_client.complete.return_value = cos_json

    state = VentureState(
        project_id="proj_cos_test",
        project_name="ChurnShield",
        stage="SPARRING_ROOM",
        founder_idea="SaaS Churn Predictor",
    )

    updates = await cos_sparring_node(state, llm_client=mock_client, memory_mgr=mem)
    assert "business_brief" in updates
    brief: BusinessBriefSchema = updates["business_brief"]
    assert brief.monetization_model == "usage_credits"
    assert brief.market_feasibility_score == 92

    # Verifikasi event Blackboard
    logs = await mem.get_event_logs("proj_cos_test")
    assert len(logs) == 1
    assert logs[0]["sender_role"] == "COS"
    assert logs[0]["artifact_ref"] == "business_brief"


@pytest.mark.asyncio
async def test_cto_architecture_node_execution(temp_db_path: str) -> None:
    """TASK-3.2.2: Menguji eksekusi node CTO dan penguncian Golden Path archetype."""
    mem = MemoryManager(db_path=temp_db_path)
    mock_client = AsyncMock(spec=UnifiedLLMClient)

    cto_json = """{
        "archetype_id": 4,
        "frontend_framework": "Next.js 14 App Router",
        "backend_framework": "FastAPI Python",
        "database": "DuckDB + Parquet",
        "estimated_inference_cost_per_user": 0.05,
        "circuit_breaker_limits": {"max_iterations": 5, "timeout_seconds": 90}
    }"""
    mock_client.complete.return_value = cto_json

    state = VentureState(
        project_id="proj_cto_test",
        project_name="DataPulse",
        stage="SPARRING_ROOM",
        founder_idea="Predictive analytics",
    )

    updates = await cto_architecture_node(state, llm_client=mock_client, memory_mgr=mem)
    assert "system_architecture" in updates
    assert updates["selected_archetype"] == 4
    arch: SystemArchitectureSchema = updates["system_architecture"]
    assert arch.database == "DuckDB + Parquet"

    # Verifikasi event Blackboard
    logs = await mem.get_event_logs("proj_cto_test")
    assert len(logs) == 1
    assert logs[0]["sender_role"] == "CTO"
    assert logs[0]["artifact_ref"] == "system_architecture"


def test_router_gate_1_transitions() -> None:
    """TASK-3.2.4: Menguji evaluasi keputusan CEO (APPROVE, REVISE, KILL)."""
    state = VentureState(
        project_id="proj_gate1",
        project_name="Gate 1 Test",
        stage="GATE_1_WAITING",
        founder_idea="Idea",
    )

    # 1. Tanpa keputusan: tetap di GATE_1_WAITING
    assert router_gate_1(state) == "GATE_1_WAITING"

    # 2. APPROVE -> PRD_AND_SPECS
    apply_gate_decision(state, "APPROVE", feedback="Konsep bisnis bagus, lanjutkan.")
    assert state.gate_decision == "APPROVE"
    assert router_gate_1(state) == "PRD_AND_SPECS"

    # 3. REVISE -> SPARRING_ROOM
    apply_gate_decision(state, "REVISE", feedback="Ubah pricing tier.")
    assert router_gate_1(state) == "SPARRING_ROOM"

    # 4. KILL -> PROJECT_KILLED
    apply_gate_decision(state, "KILL", feedback="Pasar terlalu jenuh.")
    assert router_gate_1(state) == "PROJECT_KILLED"

    # 5. Invalid action melempar ValueError
    with pytest.raises(ValueError):
        apply_gate_decision(state, "INVALID_ACTION")


@pytest.mark.asyncio
async def test_end_to_end_sparring_to_gate_1_flow(temp_db_path: str) -> None:
    """Menguji siklus lengkap SPARRING_ROOM -> GATE_1_WAITING -> PRD_AND_SPECS."""
    mem = MemoryManager(db_path=temp_db_path)
    mock_client = AsyncMock(spec=UnifiedLLMClient)

    cos_json = """{
        "problem_statement": "Problem",
        "proposed_solution": "Solution",
        "target_audience": "Audience",
        "monetization_model": "flat_monthly",
        "pricing_tiers": [{"tier_name": "Starter", "price_monthly": 19.0, "features_included": ["Basic"]}],
        "projected_margin_percentage": 75.0,
        "market_feasibility_score": 85,
        "risks_and_mitigations": ["Risk -> Mitigation"]
    }"""

    cto_json = """{
        "archetype_id": 1,
        "frontend_framework": "Next.js 14",
        "backend_framework": "FastAPI",
        "database": "PostgreSQL",
        "estimated_inference_cost_per_user": 0.02,
        "circuit_breaker_limits": {"max_iterations": 5, "timeout_seconds": 90}
    }"""

    mock_client.complete.side_effect = [cos_json, cto_json]

    fsm = NativeStateMachine(checkpointer=mem.save_checkpoint)

    async def sparring_handler(st: VentureState) -> Dict[str, Any]:
        return await sparring_room_node(st, llm_client=mock_client, memory_mgr=mem)

    fsm.register_node("SPARRING_ROOM", sparring_handler)
    fsm.register_router("SPARRING_ROOM", router_sparring)

    state = VentureState(
        project_id="proj_e2e_sparring",
        project_name="Auto SaaS",
        stage="SPARRING_ROOM",
        founder_idea="Automated Billing Assistant",
    )

    # Eksekusi step SPARRING_ROOM
    state = await fsm.step(state)
    assert state.stage == "GATE_1_WAITING"
    assert state.business_brief is not None
    assert state.system_architecture is not None
    assert state.selected_archetype == 1

    # Verifikasi 2 event tercatat di Blackboard Memory (1 dari CoS, 1 dari CTO)
    logs = await mem.get_event_logs("proj_e2e_sparring")
    assert len(logs) == 2
    assert logs[0]["sender_role"] == "COS"
    assert logs[1]["sender_role"] == "CTO"

    # Founder memberikan persetujuan Stage-Gate 1
    apply_gate_decision(state, "APPROVE", feedback="Siap masuk perancangan PRD.")
    next_stage = router_gate_1(state)
    state.stage = next_stage
    assert state.stage == "PRD_AND_SPECS"
