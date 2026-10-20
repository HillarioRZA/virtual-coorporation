"""
Unit and Integration Tests for Virtual World Corporate Office Simulator.
Menguji tata letak kampus 4-tier, auto-slotting, event bus translation, dan REST endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import api_v1_router
from app.engine.office.office_layout import get_canonical_campus_layout, auto_slot_role, SpatialTier
from app.engine.office.office_simulator import office_sim_engine

_app = FastAPI()
_app.include_router(api_v1_router, prefix="/api/v1")


@pytest.fixture
def client() -> TestClient:
    """Fixture FastAPI TestClient."""
    return TestClient(_app)


def test_canonical_campus_layout_structure() -> None:
    """Menguji struktur 4-tier kampus Silicon Valley dan keberadaan seluruh sayap gedung."""
    layout = get_canonical_campus_layout()
    assert layout["campus_name"] == "Sovereign Silicon Campus"
    wings = layout["wings"]
    assert len(wings) == 4

    wing_tiers = [w["tier"] for w in wings]
    assert SpatialTier.EXECUTIVE.value in wing_tiers
    assert SpatialTier.LEAD_MANAGEMENT.value in wing_tiers
    assert SpatialTier.WORKER_SPECIALIST.value in wing_tiers
    assert SpatialTier.COMMONS.value in wing_tiers

    # Verifikasi sayap Penthouse memiliki meja Founder
    penthouse = next(w for w in wings if w["id"] == "wing_penthouse")
    roles = [f.get("assigned_role") for f in penthouse["furniture"]]
    assert "role_founder" in roles
    assert "role_cos" in roles


def test_auto_slotting_new_role() -> None:
    """Menguji penambahan peran baru secara dinamis tanpa hardcode."""
    layout = get_canonical_campus_layout()
    updated = auto_slot_role(
        layout=layout,
        role_id="role_ai_security",
        label="AI Security Auditor",
        tier=SpatialTier.WORKER_SPECIALIST,
    )
    eng_wing = next(w for w in updated["wings"] if w["id"] == "wing_engineering")
    assigned = [f.get("assigned_role") for f in eng_wing["furniture"]]
    assert "role_ai_security" in assigned


def test_office_simulator_event_handling() -> None:
    """Menguji mutasi state spasial agen saat menerima event bus."""
    # 1. Test TASK_STARTED
    office_sim_engine.handle_bus_event(
        "TASK_STARTED",
        {"role_id": "role_fe", "ticket_id": "T-FE-01", "target_file": "page.tsx"},
    )
    fe_agent = office_sim_engine.agents["role_fe"]
    assert fe_agent.activity_state == "CODING"
    assert fe_agent.active_file == "page.tsx"

    # 2. Test STAGE_GATE_TRIGGERED
    office_sim_engine.handle_bus_event("STAGE_GATE_TRIGGERED", {})
    assert fe_agent.activity_state == "MEETING"

    # 3. Test CONSULT_ROLE
    office_sim_engine.handle_bus_event("CONSULT_ROLE", {"role_id": "role_fe"})
    assert fe_agent.activity_state == "CONSULTING"
    assert "Diskusi di Oasis" in (fe_agent.speech_bubble or "")

    # 4. Test CIRCUIT_BREAKER_TRIGGERED
    office_sim_engine.handle_bus_event(
        "CIRCUIT_BREAKER_TRIGGERED",
        {"role_id": "role_be", "reason": "Syntax SyntaxError"},
    )
    be_agent = office_sim_engine.agents["role_be"]
    assert be_agent.activity_state == "BLOCKED"

    # Reset fe_agent to IDLE
    office_sim_engine.handle_bus_event("TASK_COMPLETED", {"role_id": "role_fe"})
    assert fe_agent.activity_state == "IDLE"


def test_office_simulator_step_and_intervene() -> None:
    """Menguji detak siklus simulasi aktivitas agen dan intervensi langsung CEO."""
    agent = office_sim_engine.agents["role_fe"]
    agent.activity_state = "CONSULTING"

    office_sim_engine.step_simulation()
    assert agent.activity_state == "IDLE"

    res = office_sim_engine.intervene_agent("role_fe", "Prioritaskan responsive navbar!")
    assert res["status"] == "SUCCESS"
    assert "Prioritaskan responsive navbar!" in agent.scratchpad
    assert agent.activity_state == "CODING"


def test_office_rest_endpoints(client: TestClient) -> None:
    """Menguji seluruh endpoint REST API corporate office."""
    project_id = "proj_office_test"

    # 1. GET layout
    resp = client.get(f"/api/v1/corporate/office/layout/{project_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "wings" in data

    # 2. GET state
    resp = client.get(f"/api/v1/corporate/office/state/{project_id}")
    assert resp.status_code == 200
    state = resp.json()
    assert "agents" in state
    assert len(state["agents"]) > 0

    # 3. POST intervene
    intervene_payload = {
        "role_id": "role_fe",
        "instruction": "Deploy dark mode UI segera.",
    }
    resp = client.post("/api/v1/corporate/office/intervene", json=intervene_payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCESS"

    # 4. POST demo-step
    resp = client.post("/api/v1/corporate/office/demo-step")
    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCESS"


def test_office_websocket_lifecycle_and_events(client: TestClient) -> None:
    """Menguji siklus hidup WebSocket Office, pengiriman snapshot awal, dan penanganan event."""
    project_id = "proj_ws_test_office"
    with client.websocket_connect(f"/api/v1/corporate/ws/office/{project_id}") as ws:
        # 1. Verifikasi inisialisasi state
        init_data = ws.receive_json()
        assert init_data["type"] == "INIT_STATE"
        assert "agents" in init_data["data"]

        # 2. Kirim aksi DEMO_STEP
        ws.send_json({"type": "DEMO_STEP"})
        update_data = ws.receive_json()
        assert update_data["type"] == "OFFICE_UPDATE"
        assert update_data["event"] == "DEMO_STEP"

        # 3. Kirim instruksi INTERVENE
        ws.send_json({"type": "INTERVENE", "role_id": "role_fe", "instruction": "Percepat sintesis UI"})
        intervene_data = ws.receive_json()
        assert intervene_data["type"] == "OFFICE_UPDATE"
        assert intervene_data["event"] == "INTERVENE"


def test_office_directive_endpoints(client: TestClient) -> None:
    """Menguji endpoint directive scoped interruption dan @all moderation gate."""
    # 1. Scoped single-agent directive
    resp = client.post(
        "/api/v1/corporate/office/directive",
        json={
            "project_id": "proj_dir_test",
            "mentions": ["role_fe"],
            "instruction": "Perbaiki responsive layout",
            "ticket_id": "T-102",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["mode"] == "SCOPED_INTERRUPTION"

    # 2. Executive moderator gate for @all
    resp_all = client.post(
        "/api/v1/corporate/office/directive",
        json={
            "project_id": "proj_dir_test",
            "mentions": ["all"],
            "instruction": "Sprint review Q4",
        },
    )
    assert resp_all.status_code == 200
    assert resp_all.json()["mode"] == "EXECUTIVE_MODERATED"

    # 3. Directive dengan format camelCase dari frontend (projectId)
    resp_camel = client.post(
        "/api/v1/corporate/office/directive",
        json={"projectId": "proj_dir_test", "mentions": ["role_cos"], "instruction": "Halo CoS"},
    )
    assert resp_camel.status_code == 200
    assert resp_camel.json()["status"] == "SUCCESS"


