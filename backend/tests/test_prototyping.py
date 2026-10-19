"""
Unit Tests untuk Sprint 4: Prototyping Code Generator & Stage-Gate 2.
Menguji node PM, node UI/UX, node Frontend, penulisan berkas Next.js, dan router Stage-Gate 2.
"""

from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock
import pytest
import pytest_asyncio

from app.db.init_db import init_database
from app.engine.memory.memory import MemoryManager
from app.engine.nodes.frontend import FrontendCodeBundle, frontend_prototyping_node, write_frontend_files
from app.engine.nodes.pm import pm_spec_freeze_node
from app.engine.nodes.prototyping import mock_prototyping_phase_node, prd_and_specs_phase_node
from app.engine.nodes.ui_ux import ui_ux_spec_node
from app.engine.runtime.routers import (
    apply_gate_decision,
    router_gate_2,
    router_mock_prototyping,
    router_prd_and_specs,
)
from app.engine.runtime.state import VentureState
from app.engine.runtime.state_machine import NativeStateMachine
from app.gateway.client import UnifiedLLMClient


@pytest_asyncio.fixture
async def temp_db_path(tmp_path: Path) -> str:
    """Fixture database terisolasi untuk pengujian memori."""
    db_file = tmp_path / "test_proto.db"
    db_str = str(db_file)
    await init_database(db_str)
    return db_str


@pytest.mark.asyncio
async def test_pm_spec_freeze_node(temp_db_path: str) -> None:
    """TASK-4.2.1: Menguji node PM menghasilkan PRDContractSchema dan mengunci OpenAPI spec."""
    mem = MemoryManager(db_path=temp_db_path)
    mock_client = AsyncMock(spec=UnifiedLLMClient)

    pm_json = """{
        "prd": {
            "product_name": "DataPulse MVP",
            "tagline": "Realtime AI SaaS Churn Predictor",
            "core_happy_path_steps": [
                "Langkah 1: Upload CSV file",
                "Langkah 2: Train auto-classifier",
                "Langkah 3: Tampilkan visualisasi churn radar"
            ],
            "in_scope_mvp_features": [
                {
                    "role": "Founder",
                    "action": "Upload churn CSV",
                    "benefit": "Melihat probabilitas churn",
                    "acceptance_criteria": ["CSV tervalidasi", "Hasil muncul < 5s"]
                }
            ],
            "out_of_scope_features": ["Integrasi payment Stripe"]
        },
        "openapi_spec": {
            "openapi": "3.1.0",
            "info": {"title": "DataPulse API", "version": "1.0.0"},
            "paths": {
                "/auth/login": {"post": {}},
                "/api/v1/core-data": {"get": {}},
                "/api/v1/checkout": {"post": {}}
            }
        }
    }"""
    mock_client.complete.return_value = pm_json

    state = VentureState(
        project_id="proj_pm_test",
        project_name="DataPulse",
        stage="PRD_AND_SPECS",
        founder_idea="Churn predictor",
    )

    updates = await pm_spec_freeze_node(state, llm_client=mock_client, memory_mgr=mem)
    assert "prd_spec" in updates
    assert "openapi_spec" in updates
    assert updates["project_name"] == "DataPulse MVP"

    # Verifikasi event blackboard
    logs = await mem.get_event_logs("proj_pm_test")
    assert len(logs) == 1
    assert logs[0]["sender_role"] == "PM"
    assert logs[0]["artifact_ref"] == "openapi_spec"


@pytest.mark.asyncio
async def test_ui_ux_spec_node(temp_db_path: str) -> None:
    """TASK-4.2.2: Menguji node UI/UX menghasilkan UIComponentSpecSchema dan Tailwind tokens."""
    mem = MemoryManager(db_path=temp_db_path)
    mock_client = AsyncMock(spec=UnifiedLLMClient)

    ui_json = """{
        "theme_colors": {"primary": "#3B82F6", "background": "#0F172A"},
        "layout_type": "split_screen",
        "screens": ["Dashboard", "Simulation"],
        "components": [
            {
                "name": "PredictButton",
                "type": "button",
                "props": {"label": "Run Predict"},
                "tailwind_classes": "px-4 py-2 bg-blue-600 rounded text-white font-bold"
            }
        ]
    }"""
    mock_client.complete.return_value = ui_json

    state = VentureState(
        project_id="proj_ui_test",
        project_name="DataPulse",
        stage="PRD_AND_SPECS",
        founder_idea="Churn predictor",
    )

    updates = await ui_ux_spec_node(state, llm_client=mock_client, memory_mgr=mem)
    assert "ui_spec" in updates
    ui = updates["ui_spec"]
    assert ui.layout_type == "split_screen"
    assert len(ui.components) == 1

    # Verifikasi event blackboard
    logs = await mem.get_event_logs("proj_ui_test")
    assert len(logs) == 1
    assert logs[0]["sender_role"] == "UI_UX"


def test_write_frontend_files() -> None:
    """Menguji penyimpanan file kode Next.js ke folder projects_output."""
    bundle = FrontendCodeBundle(
        api_client_code="// api client",
        core_feature_component_code="// core feature",
        page_code="// home page",
    )
    fe_dir = write_frontend_files("proj_files_test", bundle)
    assert fe_dir.exists()
    assert (fe_dir / "src" / "services" / "apiClient.ts").is_file()
    assert (fe_dir / "src" / "components" / "CoreFeature.tsx").is_file()
    assert (fe_dir / "src" / "app" / "page.tsx").is_file()


@pytest.mark.asyncio
async def test_frontend_prototyping_node(temp_db_path: str) -> None:
    """TASK-4.2.3: Menguji node Frontend menghasilkan kode dan URL preview sandbox."""
    mem = MemoryManager(db_path=temp_db_path)
    mock_client = AsyncMock(spec=UnifiedLLMClient)

    fe_json = """{
        "api_client_code": "export const api = { fetchCoreData: () => ({ status: 'ok' }) };",
        "core_feature_component_code": "export default function Core() { return <div>Demo</div>; }",
        "page_code": "export default function Home() { return <main>App</main>; }"
    }"""
    mock_client.complete.return_value = fe_json

    state = VentureState(
        project_id="proj_fe_test",
        project_name="DataPulse",
        stage="MOCK_PROTOTYPING",
        founder_idea="Churn predictor",
        openapi_spec={"openapi": "3.1.0"},
    )

    updates = await frontend_prototyping_node(state, llm_client=mock_client, memory_mgr=mem)
    assert "preview_url" in updates
    assert updates["preview_url"].startswith("http")

    # Verifikasi event blackboard
    logs = await mem.get_event_logs("proj_fe_test")
    assert len(logs) == 1
    assert logs[0]["sender_role"] == "FRONTEND"
    assert logs[0]["event_type"] == "PREVIEW_READY"


def test_router_gate_2_transitions() -> None:
    """Menguji router Stage-Gate 2 (APPROVE, REVISE, KILL)."""
    state = VentureState(
        project_id="proj_gate2",
        project_name="Gate 2 Test",
        stage="GATE_2_WAITING",
        founder_idea="Idea",
    )

    # 1. Tanpa keputusan: tetap di GATE_2_WAITING
    assert router_gate_2(state) == "GATE_2_WAITING"

    # 2. APPROVE / GO_PRODUCTION -> PRODUCTION_HARDENING
    apply_gate_decision(state, "GO_PRODUCTION", feedback="Demo luar biasa, lanjut produksi.")
    assert router_gate_2(state) == "PRODUCTION_HARDENING"

    # 3. REVISE / ITERATE -> MOCK_PROTOTYPING
    apply_gate_decision(state, "ITERATE", feedback="Ganti warna dan tata letak.")
    assert router_gate_2(state) == "MOCK_PROTOTYPING"

    # 4. KILL -> PROJECT_KILLED
    apply_gate_decision(state, "KILL", feedback="Hentikan proyek.")
    assert router_gate_2(state) == "PROJECT_KILLED"


@pytest.mark.asyncio
async def test_end_to_end_prototyping_pipeline(temp_db_path: str) -> None:
    """TASK-4.2.4: Menguji alur lengkap PRD_AND_SPECS -> MOCK_PROTOTYPING -> GATE_2_WAITING."""
    mem = MemoryManager(db_path=temp_db_path)
    mock_client = AsyncMock(spec=UnifiedLLMClient)

    pm_json = """{
        "prd": {
            "product_name": "E2E Prototyper",
            "tagline": "End to end test",
            "core_happy_path_steps": ["Step 1", "Step 2", "Step 3"],
            "in_scope_mvp_features": [{"role": "User", "action": "Act", "benefit": "Ben", "acceptance_criteria": ["OK"]}],
            "out_of_scope_features": []
        },
        "openapi_spec": {"openapi": "3.1.0", "paths": {}}
    }"""

    ui_json = """{
        "theme_colors": {"primary": "#3B82F6"},
        "layout_type": "split_screen",
        "screens": ["Home"],
        "components": [{"name": "Btn", "type": "button", "props": {}, "tailwind_classes": "btn"}]
    }"""

    fe_json = """{
        "api_client_code": "export const api = {};",
        "core_feature_component_code": "export default function F() { return <div/>; }",
        "page_code": "export default function P() { return <div/>; }"
    }"""

    mock_client.complete.side_effect = [pm_json, ui_json, fe_json]

    fsm = NativeStateMachine(checkpointer=mem.save_checkpoint)

    async def prd_specs_handler(st: VentureState) -> Dict[str, Any]:
        return await prd_and_specs_phase_node(st, llm_client=mock_client, memory_mgr=mem)

    async def mock_proto_handler(st: VentureState) -> Dict[str, Any]:
        return await mock_prototyping_phase_node(st, llm_client=mock_client, memory_mgr=mem)

    fsm.register_node("PRD_AND_SPECS", prd_specs_handler)
    fsm.register_router("PRD_AND_SPECS", router_prd_and_specs)

    fsm.register_node("MOCK_PROTOTYPING", mock_proto_handler)
    fsm.register_router("MOCK_PROTOTYPING", router_mock_prototyping)

    state = VentureState(
        project_id="proj_e2e_proto",
        project_name="E2E Prototype",
        stage="PRD_AND_SPECS",
        founder_idea="Autonomous MVP builder",
    )

    # 1. Step PRD_AND_SPECS -> MOCK_PROTOTYPING
    state = await fsm.step(state)
    assert state.stage == "MOCK_PROTOTYPING"
    assert state.prd_spec is not None
    assert state.ui_spec is not None

    # 2. Step MOCK_PROTOTYPING -> GATE_2_WAITING
    state = await fsm.step(state)
    assert state.stage == "GATE_2_WAITING"
    assert state.preview_url is not None
    assert state.preview_url.startswith("http")

    # 3. Founder Approve Demo Day (Stage-Gate 2)
    apply_gate_decision(state, "GO_PRODUCTION")
    assert router_gate_2(state) == "PRODUCTION_HARDENING"
