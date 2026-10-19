"""
Unit and Integration Tests for Executive Governance & Circuit Breaker.
Menguji deteksi perulangan konsultasi antar-agen (Anti-Infinite Loop),
hak veto / intervensi CEO (override), pelaporan eskalasi C-Level, dan REST API.
"""

from pathlib import Path
from typing import AsyncGenerator
import httpx
import pytest
import pytest_asyncio

from app.core.config import settings
from app.db.init_db import init_database
from app.db.ticket_repo import ticket_repo
from app.engine.governance.circuit_breaker import AgentCircuitBreaker
from main import app


@pytest_asyncio.fixture
async def test_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Fixture client HTTP asinkron dengan basis data terisolasi."""
    db_file = tmp_path / "test_gov.db"
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    await init_database(str(db_file))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_circuit_breaker_detection_and_blocking(tmp_path: Path) -> None:
    """Menguji bahwa circuit breaker memblokir tiket setelah 3 kali konsultasi tanpa kemajuan."""
    db_file = str(tmp_path / "test_cb.db")
    await init_database(custom_path=db_file)

    ticket = await ticket_repo.create_ticket(
        branch_id="branch_main",
        project_id="proj_cb_1",
        division_id="div_eng",
        title="Implementasi OAuth2 Refresh",
        description="Fitur refresh token",
        status="IN_PROGRESS",
        custom_path=db_file,
    )
    t_id = ticket["id"]
    cb = AgentCircuitBreaker(max_turns=3)

    # Turn 1
    blocked_1 = await cb.record_consultation_turn(
        ticket_id=t_id, project_id="proj_cb_1", branch_id="branch_main",
        sender_role="backend", recipient_role="pm", topic_summary="Tanya skema refresh",
    )
    assert blocked_1 is False
    assert cb.get_status(t_id).turn_count == 1
    assert cb.get_status(t_id).is_blocked is False

    # Turn 2
    blocked_2 = await cb.record_consultation_turn(
        ticket_id=t_id, project_id="proj_cb_1", branch_id="branch_main",
        sender_role="pm", recipient_role="backend", topic_summary="Jawaban ambigu",
    )
    assert blocked_2 is False

    # Turn 3 -> Harus terblokir (Circuit Breaker Triggered)
    blocked_3 = await cb.record_consultation_turn(
        ticket_id=t_id, project_id="proj_cb_1", branch_id="branch_main",
        sender_role="backend", recipient_role="pm", topic_summary="Klarifikasi berulang",
    )
    assert blocked_3 is True
    assert cb.get_status(t_id).is_blocked is True
    assert cb.get_status(t_id).turn_count == 3

    cb.reset_counter(t_id)
    assert cb.get_status(t_id).is_blocked is False
    assert cb.get_status(t_id).turn_count == 0


@pytest.mark.asyncio
async def test_ceo_override_actions(tmp_path: Path) -> None:
    """Menguji eksekusi manual override CEO (FORCE_PROCEED, REASSIGN, INTERVENE)."""
    db_file = str(tmp_path / "test_override.db")
    await init_database(custom_path=db_file)

    t = await ticket_repo.create_ticket(
        branch_id="branch_main",
        project_id="proj_override_1",
        division_id="div_eng",
        title="Database Indexing",
        description="Tugas terblokir",
        status="BLOCKED_LOOP_DETECTED",
        custom_path=db_file,
    )
    cb = AgentCircuitBreaker()

    # 1. FORCE_PROCEED
    res_proceed = await cb.execute_ceo_override(
        ticket_id=t["id"], project_id="proj_override_1", branch_id="branch_main", action="FORCE_PROCEED",
        custom_path=db_file,
    )
    assert res_proceed["status"] == "success"
    updated = await ticket_repo.get_ticket_by_id(t["id"], custom_path=db_file)
    assert updated["status"] == "DONE"

    # 2. INTERVENE
    res_intervene = await cb.execute_ceo_override(
        ticket_id=t["id"], project_id="proj_override_1", branch_id="branch_main", action="INTERVENE",
        directive="Gunakan HttpOnly Cookie", custom_path=db_file,
    )
    assert res_intervene["status"] == "success"
    updated2 = await ticket_repo.get_ticket_by_id(t["id"], custom_path=db_file)
    assert updated2["status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_governance_api_endpoints(test_client: httpx.AsyncClient) -> None:
    """Menguji seluruh endpoint REST API pada /api/v1/governance."""
    project_id = "proj_gov_api_1"

    # 1. Buat tiket
    ticket_res = await test_client.post(
        "/api/v1/corporate/tickets",
        json={
            "branch_id": "branch_main", "project_id": project_id, "division_id": "div_eng",
            "title": "API Gateway Rate Limit", "description": "Tugas API Gateway",
        },
    )
    assert ticket_res.status_code == 201
    ticket_id = ticket_res.json()["id"]

    # 2. Status Circuit Breaker
    status_res = await test_client.get(f"/api/v1/governance/status/{ticket_id}?project_id={project_id}")
    assert status_res.status_code == 200
    assert status_res.json()["ticket_id"] == ticket_id

    # 3. CEO Override via API
    override_payload = {
        "ticket_id": ticket_id,
        "project_id": project_id,
        "branch_id": "branch_main",
        "override": {
            "action": "FORCE_PROCEED",
            "directive": "Lanjutkan langsung ke QA",
        },
    }
    override_res = await test_client.post("/api/v1/governance/override", json=override_payload)
    assert override_res.status_code == 200
    assert override_res.json()["status"] == "success"

    # 4. Submit C-Level Escalation Report
    escalation_payload = {
        "project_id": project_id,
        "reporter_role": "cto",
        "title": "Dilema Stack Database: SQLite WAL vs PostgreSQL",
        "summary": "SQLite sangat cepat di sandbox, tapi beban read-heavy butuh Postgres.",
        "options": [
            {"option_id": "A", "label": "Gunakan SQLite WAL", "impact": "Simpel, nol dependensi."},
            {"option_id": "B", "label": "Gunakan PostgreSQL asyncpg", "impact": "Enterprise-ready."},
        ],
        "urgency": "HIGH",
    }
    esc_res = await test_client.post("/api/v1/governance/escalate", json=escalation_payload)
    assert esc_res.status_code == 200
    esc_data = esc_res.json()
    assert esc_data["reporter_role"] == "cto"
    report_id = esc_data["id"]

    # 5. Submit CEO 1-Click Decision
    decision_payload = {
        "report_id": report_id,
        "project_id": project_id,
        "branch_id": "branch_main",
        "decision": {
            "selected_option_id": "A",
            "feedback": "Pilih SQLite WAL untuk MVP fase 1.",
        },
    }
    dec_res = await test_client.post("/api/v1/governance/decision", json=decision_payload)
    assert dec_res.status_code == 200
    assert dec_res.json()["selected_option"] == "A"
