"""
Unit & Integration Tests untuk Sprint 2.4: Autonomous Virtual Kanban Board & Live WebSocket Lounge.
Menguji repositori tiket, transisi status, auto-seeding awal, endpoint REST tiket,
dan streaming obrolan inter-agent melalui WebSocket.
"""

from pathlib import Path
from typing import Any, AsyncGenerator, Dict
import httpx
import pytest
import pytest_asyncio

from app.core.config import settings
from app.db.init_db import init_database
from app.db.ticket_repo import ticket_repo
from app.engine.dispatcher import task_dispatcher
from app.engine.state import VentureState
from app.gateway.client import UnifiedLLMClient
from main import app


@pytest_asyncio.fixture
async def test_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Fixture client HTTP asinkron dengan basis data terisolasi."""
    db_file = tmp_path / "test_tickets.db"
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    await init_database(str(db_file))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_ticket_crud_and_status_transition(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Menguji pembuatan tiket, pembacaan dengan filter, dan transisi status antarkolom."""
    db_file = tmp_path / "test_ticket_crud.db"
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    await init_database(str(db_file))

    project_id = "proj_kanban_crud_1"

    # 1. Buat tiket baru
    ticket = await ticket_repo.create_ticket(
        branch_id="branch_main",
        project_id=project_id,
        division_id="div_eng",
        assigned_role_id="role_fe",
        title="Buat Komponen Landing Page",
        description="Rancang komponen hero section dan CTA",
        product_line="SOFTWARE",
        priority="HIGH",
        status="BACKLOG",
        custom_path=str(db_file),
    )
    assert ticket["id"].startswith("tick_")
    assert ticket["status"] == "BACKLOG"
    assert ticket["priority"] == "HIGH"

    # 2. Ambil tiket dengan filter
    backlog_tickets = await ticket_repo.get_tickets(
        project_id=project_id,
        status="BACKLOG",
        custom_path=str(db_file),
    )
    assert len(backlog_tickets) == 1
    assert backlog_tickets[0]["id"] == ticket["id"]

    # 3. Transisi status ke IN_PROGRESS
    updated = await ticket_repo.transition_ticket_status(
        ticket_id=ticket["id"],
        new_status="IN_PROGRESS",
        custom_path=str(db_file),
    )
    assert updated is not None
    assert updated["status"] == "IN_PROGRESS"

    # 4. Transisi status ke DONE beserta artefak
    done_ticket = await ticket_repo.transition_ticket_status(
        ticket_id=ticket["id"],
        new_status="DONE",
        artifact_refs=["projects_output/proj_kanban_crud_1/frontend/page.tsx"],
        custom_path=str(db_file),
    )
    assert done_ticket is not None
    assert done_ticket["status"] == "DONE"
    assert len(done_ticket["artifact_refs"]) == 1

    # 5. Hapus tiket
    deleted = await ticket_repo.delete_ticket(ticket["id"], custom_path=str(db_file))
    assert deleted is True


@pytest.mark.asyncio
async def test_seed_initial_project_tickets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Menguji auto-seeding 5 tiket pipeline awal (PRD, Arsitektur, FE, BE, QA)."""
    db_file = tmp_path / "test_seed.db"
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    await init_database(str(db_file))

    project_id = "proj_seed_test"
    seeded = await ticket_repo.seed_initial_project_tickets(project_id, custom_path=str(db_file))
    assert len(seeded) == 5

    # Pemanggilan kedua harus mengembalikan daftar yang sama tanpa duplikasi
    second_call = await ticket_repo.seed_initial_project_tickets(project_id, custom_path=str(db_file))
    assert len(second_call) == 5


@pytest.mark.asyncio
async def test_ticket_rest_api_endpoints(test_client: httpx.AsyncClient) -> None:
    """Menguji endpoint REST API tiket /api/v1/corporate/tickets."""
    project_id = "proj_api_tickets_1"

    # 1. Seed Initial
    seed_res = await test_client.post(f"/api/v1/corporate/tickets/{project_id}/seed-initial")
    assert seed_res.status_code == 200
    tickets = seed_res.json()
    assert len(tickets) == 5

    # 2. List Tickets
    list_res = await test_client.get(f"/api/v1/corporate/tickets/{project_id}")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 5

    # 3. Create Custom Ticket
    new_ticket_payload = {
        "branch_id": "branch_main",
        "project_id": project_id,
        "division_id": "div_eng",
        "assigned_role_id": "role_qa",
        "title": "Cek Celah SQL Injection",
        "description": "Lakukan audit injeksi pada parameter get_tickets",
        "priority": "CRITICAL",
        "product_line": "SOFTWARE",
    }
    create_res = await test_client.post("/api/v1/corporate/tickets", json=new_ticket_payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["priority"] == "CRITICAL"

    # 4. Transition Status
    trans_res = await test_client.post(
        f"/api/v1/corporate/tickets/{created['id']}/transition?target_status=IN_PROGRESS"
    )
    assert trans_res.status_code == 200
    assert trans_res.json()["status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_dispatcher_auto_transitions_tickets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Menguji bahwa dispatch_parallel_engineering otomatis mentransisikan tiket FE dan BE ke DONE."""
    db_file = tmp_path / "test_dispatch_tickets.db"
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    await init_database(str(db_file))

    project_id = "proj_dispatch_tick_1"

    # Inisialisasi tiket awal
    await ticket_repo.seed_initial_project_tickets(project_id, custom_path=str(db_file))

    state = VentureState(
        project_id=project_id,
        project_name="Kanban Auto App",
        founder_idea="SaaS kanban otomatis",
        selected_archetype=1,
    )
    state.openapi_spec = {"openapi": "3.0.0", "paths": {}}

    mock_client = UnifiedLLMClient()

    async def _mock_complete(*args: Any, **kwargs: Any) -> str:
        content = f"{kwargs.get('prompt', '')} {kwargs.get('system_prompt', '')}"
        if "Frontend" in content:
            return (
                '```json\n{\n'
                '  "api_client_code": "export const api = { fetch: () => ({}) };",\n'
                '  "core_feature_component_code": "export default function Core() { return <div>Kanban</div>; }",\n'
                '  "page_code": "export default function Home() { return <main>Kanban App</main>; }"\n'
                '}\n```'
            )
        return (
            '```json\n{\n'
            '  "main_code": "from fastapi import FastAPI\\napp = FastAPI()\\n@app.get(\'/health\')\\ndef h(): return {\'ok\': True}",\n'
            '  "models_code": "from pydantic import BaseModel\\nclass Item(BaseModel):\\n    id: str",\n'
            '  "routers_code": "from fastapi import APIRouter\\nrouter = APIRouter()\\n@router.get(\'/items\')\\ndef it(): return []",\n'
            '  "migration_code": "def upgrade():\\n    pass\\ndef downgrade():\\n    pass",\n'
            '  "requirements_content": "fastapi>=0.115.0\\nuvicorn>=0.31.0\\npydantic>=2.0.0"\n'
            '}\n```'
        )

    monkeypatch.setattr(mock_client, "complete", _mock_complete)

    # Jalankan paralel dispatch
    await task_dispatcher.dispatch_parallel_engineering(
        state=state,
        branch_id="branch_main",
        llm_client=mock_client,
        custom_path=str(db_file),
    )

    # Periksa bahwa tiket Frontend dan Backend telah berstatus DONE
    tickets = await ticket_repo.get_tickets(project_id, custom_path=str(db_file))
    fe_ticket = next(t for t in tickets if t["assigned_role_id"] == "role_fe")
    be_ticket = next(t for t in tickets if t["assigned_role_id"] == "role_be")

    assert fe_ticket["status"] == "DONE"
    assert be_ticket["status"] == "DONE"
    assert len(fe_ticket["artifact_refs"]) > 0
    assert len(be_ticket["artifact_refs"]) > 0
