"""
Unit & Integration Tests untuk Sprint 2.2: Asynchronous Actor Event Bus & Task Concurrency Dispatcher.
Menguji pub/sub event bus, persistensi event SQLite, manajemen worker pool, eksekusi paralel (Frontend + Backend),
dan endpoint REST event bus.
"""

import asyncio
from pathlib import Path
from typing import Any, AsyncGenerator, Dict
import httpx
import pytest
import pytest_asyncio

from app.core.config import settings
from app.db.init_db import init_database
from app.engine.corporate_schemas import CorporateMessageCreate
from app.engine.dispatcher import task_dispatcher
from app.engine.event_bus import corporate_event_bus
from app.engine.memory import MemoryManager
from app.engine.state import VentureState
from app.engine.worker_pool import AgentWorkerPool
from app.gateway.client import UnifiedLLMClient
from main import app


@pytest_asyncio.fixture
async def test_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Fixture client HTTP asinkron dengan basis data SQLite terisolasi."""
    db_file = tmp_path / "test_async_event.db"
    test_db_url = f"sqlite+aiosqlite:///{db_file}"
    monkeypatch.setattr(settings, "DATABASE_URL", test_db_url)

    await init_database(str(db_file))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_event_bus_publish_and_subscribe(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Menguji pub/sub in-memory non-blocking pada CorporateEventBus."""
    db_file = tmp_path / "test_bus.db"
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    await init_database(str(db_file))

    project_id = "proj_test_bus_1"
    sub_queue = await corporate_event_bus.subscribe(project_id)

    event_payload = CorporateMessageCreate(
        branch_id="branch_main",
        project_id=project_id,
        channel_type="LOUNGE",
        sender_role_id="role_fe",
        recipient_role_id="role_be",
        event_type="SCHEMA_CHANGE",
        content="Frontend membutuhkan field session_token pada endpoint auth.",
        token_cost=0.005,
    )

    saved_msg = await corporate_event_bus.publish(event_payload, custom_path=str(db_file))
    assert saved_msg["id"] > 0
    assert saved_msg["event_type"] == "SCHEMA_CHANGE"

    # Terima event dari antrian subscriber
    received = await asyncio.wait_for(sub_queue.get(), timeout=2.0)
    assert received["sender_role_id"] == "role_fe"
    assert received["content"] == event_payload.content

    await corporate_event_bus.unsubscribe(project_id, sub_queue)


@pytest.mark.asyncio
async def test_event_bus_sqlite_persistence_and_history(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Menguji persistensi log pesan ke tabel corporate_messages dan pembacaan riwayatnya."""
    db_file = tmp_path / "test_history.db"
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    await init_database(str(db_file))

    project_id = "proj_test_history_1"

    for i in range(3):
        await corporate_event_bus.publish(
            CorporateMessageCreate(
                branch_id="branch_main",
                project_id=project_id,
                channel_type="LOUNGE",
                sender_role_id="role_cto",
                event_type="TASK_COMPLETED",
                content=f"Log progres iterasi ke-{i + 1}",
                token_cost=0.001 * (i + 1),
            ),
            custom_path=str(db_file),
        )

    history = await corporate_event_bus.get_history(project_id, limit=10, custom_path=str(db_file))
    assert len(history) == 3
    assert history[0]["content"] == "Log progres iterasi ke-3"
    assert history[2]["content"] == "Log progres iterasi ke-1"


@pytest.mark.asyncio
async def test_worker_pool_lifecycle_and_cancellation() -> None:
    """Menguji manajemen worker pool asyncio: spawn, wait, dan graceful cancellation."""
    pool = AgentWorkerPool()

    async def _dummy_task(duration: float, result_val: str) -> str:
        await asyncio.sleep(duration)
        return result_val

    # 1. Spawn dan tunggu selesai
    task1 = pool.spawn_worker("worker_a", _dummy_task(0.05, "sukses_a"))
    task2 = pool.spawn_worker("worker_b", _dummy_task(0.08, "sukses_b"))

    assert pool.active_workers_count() == 2
    results = await pool.wait_all(timeout=2.0)
    assert "sukses_a" in results
    assert "sukses_b" in results
    assert pool.active_workers_count() == 0

    # 2. Test Cancellation
    async def _long_task() -> None:
        await asyncio.sleep(10.0)

    pool.spawn_worker("worker_long", _long_task())
    assert pool.active_workers_count() == 1
    await pool.cancel_all()
    assert pool.active_workers_count() == 0


@pytest.mark.asyncio
async def test_parallel_engineering_dispatcher(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Menguji eksekusi paralel (Frontend + Backend) menggunakan TaskConcurrencyDispatcher."""
    db_file = tmp_path / "test_dispatch.db"
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    await init_database(str(db_file))

    project_id = "proj_dispatch_parallel_1"

    # Siapkan VentureState yang memiliki OpenAPI Spec valid
    state = VentureState(
        project_id=project_id,
        project_name="DataFlow Cloud",
        founder_idea="SaaS automasi pipeline data.",
        selected_archetype=1,
    )
    state.openapi_spec = {
        "openapi": "3.0.0",
        "info": {"title": "DataFlow API", "version": "1.0.0"},
        "paths": {"/api/v1/data": {"get": {"summary": "Get pipeline data"}}},
    }

    # Jalankan eksekusi paralel dengan mock LLM response
    mock_client = UnifiedLLMClient()

    async def _mock_complete(*args: Any, **kwargs: Any) -> str:
        prompt = kwargs.get("prompt", "")
        system_prompt = kwargs.get("system_prompt", "")
        content = f"{prompt} {system_prompt} {' '.join(str(a) for a in args)}"
        if "Frontend" in content or "page_code" in content or "component" in content:
            return (
                '```json\n{\n'
                '  "api_client_code": "export const api = { fetch: () => ({}) };",\n'
                '  "core_feature_component_code": "export default function Core() { return <div>DataFlow</div>; }",\n'
                '  "page_code": "export default function Home() { return <main>Pipeline</main>; }"\n'
                '}\n```'
            )
        return (
            '```json\n{\n'
            '  "main_code": "from fastapi import FastAPI\\napp = FastAPI()",\n'
            '  "models_code": "from pydantic import BaseModel\\nclass Item(BaseModel): pass",\n'
            '  "routers_code": "from fastapi import APIRouter\\nrouter = APIRouter()",\n'
            '  "migration_code": "def upgrade(): pass\\ndef downgrade(): pass",\n'
            '  "requirements_content": "fastapi>=0.115.0\\nuvicorn>=0.31.0"\n'
            '}\n```'
        )

    monkeypatch.setattr(mock_client, "complete", _mock_complete)

    result = await task_dispatcher.dispatch_parallel_engineering(
        state=state,
        branch_id="branch_main",
        llm_client=mock_client,
        custom_path=str(db_file),
    )

    assert result["status"] == "success"
    assert result["elapsed_seconds"] >= 0.0
    assert result["project_id"] == project_id

    # Verifikasi direktori output frontend dan backend keduanya terbuat
    out_dir = (
        Path(__file__).resolve().parent.parent.parent / "projects_output"
        if (Path(__file__).resolve().parent.parent.parent / "projects_output").exists()
        else Path("projects_output")
    )
    fe_dir = out_dir / project_id / "frontend"
    be_dir = out_dir / project_id / "backend"
    assert fe_dir.exists()
    assert be_dir.exists()


@pytest.mark.asyncio
async def test_corporate_events_api_endpoints(test_client: httpx.AsyncClient) -> None:
    """Menguji REST API endpoint /corporate/events dan /corporate/dispatch/concurrent."""
    project_id = "proj_api_event_1"

    # 1. Publish Event
    event_payload = {
        "branch_id": "branch_main",
        "project_id": project_id,
        "channel_type": "LOUNGE",
        "sender_role_id": "role_cos",
        "event_type": "MESSAGE",
        "content": "Diskusi koordinasi pembagian tugas sprint dimulai.",
        "token_cost": 0.002,
    }
    pub_res = await test_client.post("/api/v1/corporate/events", json=event_payload)
    assert pub_res.status_code == 201
    pub_data = pub_res.json()
    assert pub_data["id"] > 0
    assert pub_data["content"] == event_payload["content"]

    # 2. Get Events History
    hist_res = await test_client.get(f"/api/v1/corporate/events/{project_id}")
    assert hist_res.status_code == 200
    events = hist_res.json()
    assert len(events) >= 1
    assert events[0]["sender_role_id"] == "role_cos"

    # 3. Test Dispatch Concurrent dengan Project Tidak Ditemukan
    dispatch_res = await test_client.post("/api/v1/corporate/dispatch/concurrent/non_existent_proj")
    assert dispatch_res.status_code == 404
