"""
Unit Test Suite untuk Fase 3 (Tool Synthesizer, Episodic Memory, Financial Guardrail, dan Flight Recorder).
"""

from pathlib import Path
import pytest

from app.engine.tool_synthesizer import DynamicToolRegistry
from app.engine.episodic_memory import CrossVentureEpisodicMemory
from app.engine.financial_guardrail import FinancialCircuitBreaker
from app.engine.flight_recorder import AgentFlightRecorder


@pytest.mark.asyncio
async def test_tool_synthesizer_lifecycle(tmp_path: Path) -> None:
    """Menguji siklus hidup sintesis skrip, eksekusi ephemeral, dan registrasi dinamis."""
    registry = DynamicToolRegistry(projects_dir=tmp_path)
    project_id = "test_synth_proj"

    # 1. Tolak kode dengan kesalahan sintaks
    bad_res = registry.synthesize_tool_script(project_id, "broken_tool.py", "def foo( invalid syntax")
    assert bad_res["success"] is False

    # 2. Sintesis skrip valid
    valid_code = "import sys\nprint('HELLO_TOOL_SYNTHESIZER')\nsys.exit(0)\n"
    ok_res = registry.synthesize_tool_script(project_id, "hello_tool.py", valid_code)
    assert ok_res["success"] is True

    # 3. Eksekusi perkakas terisolasi
    exec_res = await registry.execute_ephemeral_tool(project_id, "hello_tool.py")
    assert exec_res["success"] is True
    assert "HELLO_TOOL_SYNTHESIZER" in exec_res["stdout"]

    # 4. Verifikasi pendaftaran otomatis ke tool registry aktif
    active = registry.list_active_tools(project_id)
    assert "hello_tool.py" in active


def test_cross_venture_episodic_memory() -> None:
    """Menguji pencatatan pengalaman dan pencarian semantik preseden lintas venture."""
    memory = CrossVentureEpisodicMemory()

    memory.record_experience(
        title="Next.js Hydration Mismatch with LocalStorage",
        problem_pattern="Hydration error when reading window.localStorage in SSR initial render",
        root_cause="Server render HTML differs from client-side rendered DOM",
        proven_solution="Use useEffect hook or dynamic import with ssr: false",
        tags=["nextjs", "react", "ssr", "hydration"],
        source_venture="venture_alpha",
    )

    # Retrieval semantik relevan
    results = memory.retrieve_relevant_experiences("How to fix hydration mismatch in next.js?")
    assert len(results) > 0
    top_card = results[0]["card"]
    assert top_card["title"] == "Next.js Hydration Mismatch with LocalStorage"

    # Format injeksi prompt
    prompt_snippet = memory.format_prompt_injection("hydration error Next.js")
    assert prompt_snippet is not None
    assert "CROSS-VENTURE HISTORICAL LESSONS" in prompt_snippet
    assert "venture_alpha" in prompt_snippet


def test_financial_circuit_breaker() -> None:
    """Menguji proteksi hard token & dollar quota per tiket tugas."""
    breaker = FinancialCircuitBreaker(max_tokens=100000, max_cost=1.0)
    ticket_id = "ticket_feat_payment"

    # Konsumsi awal sehat
    res1 = breaker.record_usage(ticket_id, tokens=50000, cost_dollars=0.45)
    assert res1["quota_status"] == "HEALTHY"
    assert breaker.is_ticket_frozen(ticket_id) is False

    # Konsumsi kedua melampaui kuota
    res2 = breaker.record_usage(ticket_id, tokens=60000, cost_dollars=0.60)
    assert res2["quota_status"] == "FROZEN_PENDING_APPROVAL"
    assert breaker.is_ticket_frozen(ticket_id) is True

    # Founder topup / override persetujuan anggaran
    unfreeze_res = breaker.approve_founder_budget_topup(ticket_id, additional_tokens=100000, additional_dollars=1.0)
    assert unfreeze_res["status"] == "UNFROZEN"
    assert breaker.is_ticket_frozen(ticket_id) is False


def test_agent_flight_recorder(tmp_path: Path) -> None:
    """Menguji pencatatan append-only flight stream dan time-travel step inspection."""
    recorder = AgentFlightRecorder(projects_dir=tmp_path)
    project_id = "test_flight_proj"

    evt1 = recorder.record_step(
        project_id=project_id,
        event_type="STATE_TRANSITION",
        agent_role="ARCHITECT",
        payload={"selected_archetype": "fintech_gateway", "db": "sqlite"},
    )
    assert evt1["step_index"] == 1

    evt2 = recorder.record_step(
        project_id=project_id,
        event_type="CODE_DIFF_APPLIED",
        agent_role="BACKEND",
        payload={"file": "main.py", "lines_added": 45},
    )
    assert evt2["step_index"] == 2

    # Verifikasi time-travel replay
    replayed = recorder.replay_step(project_id, step_index=2)
    assert replayed is not None
    assert replayed["agent_role"] == "BACKEND"
    assert replayed["payload"]["file"] == "main.py"
