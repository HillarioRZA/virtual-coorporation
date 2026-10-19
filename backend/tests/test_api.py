"""
Unit & Integration Tests untuk FastAPI API v1 Endpoints & SSE Streaming.
Menguji endpoint /health, CRUD /projects, /sparring/chat, /gates/{id}/decision, dan StreamManager.
"""

from pathlib import Path
from typing import AsyncGenerator
import httpx
import pytest
import pytest_asyncio

from app.core.config import settings
from app.core.stream import stream_manager
from app.db.init_db import init_database
from app.engine.memory.memory import MemoryManager
from app.engine.runtime.state import VentureState
from main import app


@pytest_asyncio.fixture
async def test_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Fixture client HTTP asinkron dengan database SQLite terisolasi."""
    db_file = tmp_path / "test_api.db"
    test_db_url = f"sqlite+aiosqlite:///{db_file}"
    monkeypatch.setattr(settings, "DATABASE_URL", test_db_url)

    await init_database(str(db_file))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_health_endpoint(test_client: httpx.AsyncClient) -> None:
    """Menguji endpoint health check backend."""
    response = await test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "venture-incubator-hub"


@pytest.mark.asyncio
async def test_create_project_and_get_detail(test_client: httpx.AsyncClient) -> None:
    """Menguji pendaftaran proyek baru dan inspeksi detail snapshot state."""
    payload = {
        "name": "DataPulse Analytics",
        "founder_idea": "SaaS analytics platform for predicting customer churn via CSV files.",
        "archetype_id": 4,
    }
    create_res = await test_client.post("/api/v1/projects", json=payload)
    assert create_res.status_code == 201
    create_data = create_res.json()
    assert create_data["status"] == "success"
    project_id = create_data["data"]["project_id"]
    assert project_id.startswith("proj_")
    assert create_data["data"]["stage"] == "SPARRING_ROOM"

    # Ambil detail proyek yang baru dibuat
    get_res = await test_client.get(f"/api/v1/projects/{project_id}")
    assert get_res.status_code == 200
    detail = get_res.json()["data"]
    assert detail["project_id"] == project_id
    assert detail["project_name"] == "DataPulse Analytics"
    assert "preview_url" in detail


@pytest.mark.asyncio
async def test_create_project_validation_error(test_client: httpx.AsyncClient) -> None:
    """Menguji validasi payload tidak valid (nama kosong & ide terlalu pendek)."""
    invalid_payload = {"name": "", "founder_idea": "short", "archetype_id": 9}
    res = await test_client.post("/api/v1/projects", json=invalid_payload)
    assert res.status_code == 422
    assert res.json()["status"] == "error"


@pytest.mark.asyncio
async def test_list_projects(test_client: httpx.AsyncClient) -> None:
    """Menguji retrieval daftar portofolio proyek beserta metrik token cost."""
    # Buat proyek sampel
    payload = {
        "name": "E-Commerce AI Copilot",
        "founder_idea": "Automated product descriptions and dynamic pricing engine.",
        "archetype_id": 1,
    }
    await test_client.post("/api/v1/projects", json=payload)

    list_res = await test_client.get("/api/v1/projects")
    assert list_res.status_code == 200
    items = list_res.json()["data"]
    assert len(items) >= 1
    sample = items[0]
    assert "tokens_cost" in sample
    assert "net_profit" in sample
    assert sample["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_get_nonexistent_project_returns_404(test_client: httpx.AsyncClient) -> None:
    """Menguji penanganan ID proyek yang tidak terdaftar."""
    res = await test_client.get("/api/v1/projects/proj_nonexistent_99")
    assert res.status_code == 404
    assert "tidak ditemukan" in res.json()["detail"]


@pytest.mark.asyncio
async def test_sparring_chat(test_client: httpx.AsyncClient) -> None:
    """Menguji pengiriman chat Founder ke Executive Sparring Room."""
    # Setup proyek
    c_res = await test_client.post(
        "/api/v1/projects",
        json={"name": "Logistics AI", "founder_idea": "Smart fleet routing for trucks.", "archetype_id": 2},
    )
    p_id = c_res.json()["data"]["project_id"]

    chat_payload = {
        "message": "Saya ingin optimasi rute fokus pada penghematan bahan bakar solar.",
        "target_agent": "CTO",
    }
    chat_res = await test_client.post(f"/api/v1/projects/{p_id}/sparring/chat", json=chat_payload)
    assert chat_res.status_code == 200
    assert chat_res.json()["status"] == "queued"

    # Verifikasi event tercatat di blackboard memory
    mem = MemoryManager()
    events = await mem.get_event_logs(p_id)
    chat_events = [e for e in events if e["event_type"] == "CHAT"]
    assert len(chat_events) == 1
    assert chat_events[0]["recipient_role"] == "CTO"


@pytest.mark.asyncio
async def test_gate_1_decision_approve_and_kill(test_client: httpx.AsyncClient) -> None:
    """Menguji eksekusi keputusan Stage-Gate 1 untuk APPROVE dan KILL."""
    mem = MemoryManager()

    # Skenario 1: APPROVE -> transisi ke PRD_AND_SPECS
    p1_res = await test_client.post(
        "/api/v1/projects",
        json={"name": "Health App", "founder_idea": "Personalized nutrition tracker via photos.", "archetype_id": 3},
    )
    p1_id = p1_res.json()["data"]["project_id"]

    # Simulasikan state di GATE_1_WAITING
    s1 = await mem.load_latest_checkpoint(p1_id)
    assert s1 is not None
    s1.stage = "GATE_1_WAITING"
    await mem.save_checkpoint(s1)

    dec_res1 = await test_client.post(
        f"/api/v1/projects/{p1_id}/gates/gate_1/decision",
        json={"action": "APPROVE", "feedback": "Brief dan arsitektur sangat solid."},
    )
    assert dec_res1.status_code == 200
    assert dec_res1.json()["data"]["current_stage"] == "PRD_AND_SPECS"

    # Skenario 2: KILL -> transisi ke PROJECT_KILLED
    p2_res = await test_client.post(
        "/api/v1/projects",
        json={"name": "Unviable Idea", "founder_idea": "Generic social network clone.", "archetype_id": 1},
    )
    p2_id = p2_res.json()["data"]["project_id"]
    s2 = await mem.load_latest_checkpoint(p2_id)
    assert s2 is not None
    s2.stage = "GATE_1_WAITING"
    await mem.save_checkpoint(s2)

    dec_res2 = await test_client.post(
        f"/api/v1/projects/{p2_id}/gates/gate_1/decision",
        json={"action": "KILL", "feedback": "Pasar sudah terlalu jenuh."},
    )
    assert dec_res2.status_code == 200
    assert dec_res2.json()["data"]["current_stage"] == "PROJECT_KILLED"


@pytest.mark.asyncio
async def test_preview_status(test_client: httpx.AsyncClient) -> None:
    """Menguji endpoint pemeriksaan kesiapan preview sandbox."""
    res = await test_client.post(
        "/api/v1/projects",
        json={"name": "Fintech App", "founder_idea": "Micro-invoicing for freelancers.", "archetype_id": 1},
    )
    p_id = res.json()["data"]["project_id"]

    status_res = await test_client.get(f"/api/v1/projects/{p_id}/preview/status")
    assert status_res.status_code == 200
    data = status_res.json()["data"]
    assert "preview_url" in data
    assert "port" in data


@pytest.mark.asyncio
async def test_stream_manager_publish_subscribe() -> None:
    """Menguji modul in-memory pub/sub StreamManager."""
    project_id = "proj_stream_test"
    queue = await stream_manager.subscribe(project_id)

    # Publish event
    await stream_manager.publish(project_id, "state_change", {"stage": "GATE_2_WAITING"})
    received = await queue.get()
    assert received["event"] == "state_change"
    assert received["data"]["stage"] == "GATE_2_WAITING"

    # Unsubscribe
    await stream_manager.unsubscribe(project_id, queue)
