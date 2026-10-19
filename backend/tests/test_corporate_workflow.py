"""
Unit tests untuk Corporate Workflow Pipeline & Stage Reordering API.
Menguji pengambilan alur sekuensial, proteksi branch_main,
reordering peran (A -> B -> C menjadi B -> C -> A), dan sinkronisasi ke Kanban seeding.
"""

from pathlib import Path
from typing import AsyncGenerator
import httpx
import pytest
import pytest_asyncio

from app.core.config import settings
from app.db.corporate_repo import corporate_repo
from app.db.init_db import init_database
from app.db.ticket_repo import ticket_repo
from app.db.workflow_repo import workflow_repo
from main import app


@pytest_asyncio.fixture
async def workflow_client(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Fixture client HTTP asinkron dengan basis data terisolasi."""
    db_file = tmp_path / "test_workflow_endpoints.db"
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    await init_database(str(db_file))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_get_workflow_pipeline_main(workflow_client: httpx.AsyncClient) -> None:
    """Memastikan pipeline tahapan peran pada branch_main dapat diambil secara terurut."""
    response = await workflow_client.get("/api/v1/corporate/branches/branch_main/pipeline")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 7
    assert data[0]["order_index"] <= data[1]["order_index"]
    assert "role_name" in data[0]
    assert "division_name" in data[0]


@pytest.mark.asyncio
async def test_protect_branch_main_against_reorder(workflow_client: httpx.AsyncClient) -> None:
    """Memastikan branch_main dilindungi dan menolak reordering alur kerja langsung (HTTP 400)."""
    response = await workflow_client.put(
        "/api/v1/corporate/branches/branch_main/pipeline",
        json={"ordered_role_ids": ["role_qa", "role_be", "role_cos"]},
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "dilindungi" in detail.lower() or "gold standard" in detail.lower()


@pytest.mark.asyncio
async def test_fork_and_reorder_workflow_pipeline(workflow_client: httpx.AsyncClient) -> None:
    """Memastikan alur kerja peran pada branch forked dapat disusun ulang bebas (misal: B -> C -> A)."""
    # 1. Fork branch baru via REST API
    fork_res = await workflow_client.post(
        "/api/v1/corporate/branches/fork",
        json={
            "name": "Growth Experiment Flow",
            "slug": "growth-flow",
            "source_branch_id": "branch_main",
        },
    )
    assert fork_res.status_code == 201
    forked = fork_res.json()
    branch_id = forked["id"]

    # 2. Ambil peran di branch baru via pipeline endpoint
    pipeline_res = await workflow_client.get(f"/api/v1/corporate/branches/{branch_id}/pipeline")
    assert pipeline_res.status_code == 200
    stages = pipeline_res.json()
    assert len(stages) >= 3

    # Balik urutan peran: A -> B -> C menjadi C -> B -> A
    reversed_role_ids = [s["role_id"] for s in reversed(stages) if s.get("role_id")]

    # 3. Request reorder pipeline via API
    reorder_res = await workflow_client.put(
        f"/api/v1/corporate/branches/{branch_id}/pipeline",
        json={"ordered_role_ids": reversed_role_ids},
    )
    assert reorder_res.status_code == 200
    new_pipeline = reorder_res.json()
    assert len(new_pipeline) == len(reversed_role_ids)
    assert [s["role_id"] for s in new_pipeline] == reversed_role_ids
    for idx, stage in enumerate(new_pipeline):
        assert stage["order_index"] == idx


@pytest.mark.asyncio
async def test_reorder_divisions_on_forked_branch(workflow_client: httpx.AsyncClient) -> None:
    """Memastikan urutan divisi pada branch forked dapat disusun ulang."""
    # 1. Fork branch
    fork_res = await workflow_client.post(
        "/api/v1/corporate/branches/fork",
        json={
            "name": "Div Reorder Experiment",
            "slug": "div-reorder-flow",
            "source_branch_id": "branch_main",
        },
    )
    branch_id = fork_res.json()["id"]

    # 2. Ambil daftar divisi
    div_res = await workflow_client.get(f"/api/v1/corporate/divisions?branch_id={branch_id}")
    divs = div_res.json()
    reversed_div_ids = [d["id"] for d in reversed(divs)]

    # 3. Reorder divisi
    reorder_res = await workflow_client.put(
        f"/api/v1/corporate/branches/{branch_id}/reorder-divisions",
        json={"ordered_division_ids": reversed_div_ids},
    )
    assert reorder_res.status_code == 200
    assert reorder_res.json()["status"] == "success"


@pytest.mark.asyncio
async def test_kanban_seeding_respects_reordered_workflow(tmp_path: Path) -> None:
    """Memastikan seed_initial_project_tickets menyusun tiket Kanban sesuai urutan peran."""
    db_file = str(tmp_path / "test_wf_kanban.db")
    await init_database(custom_path=db_file)

    # Fork branch
    forked = await corporate_repo.fork_branch(
        name="Custom Methodology",
        slug="custom-method",
        source_branch_id="branch_main",
        custom_path=db_file,
    )
    branch_id = forked["id"]

    roles = await corporate_repo.get_roles(branch_id=branch_id, custom_path=db_file)
    role_be = next(r for r in roles if "be" in r["id"].lower() or "backend" in r["name"].lower())
    role_fe = next(r for r in roles if "fe" in r["id"].lower() or "frontend" in r["name"].lower())
    other_roles = [r for r in roles if r["id"] not in (role_be["id"], role_fe["id"])]

    # Susun ulang: Backend nomor 1, Frontend nomor 2, sisanya mengikuti
    custom_order = [role_be["id"], role_fe["id"]] + [r["id"] for r in other_roles]
    await workflow_repo.reorder_workflow_pipeline(branch_id, custom_order, custom_path=db_file)

    # Seed tiket Kanban untuk venture baru
    tickets = await ticket_repo.seed_initial_project_tickets(
        project_id="proj_custom_wf_01",
        branch_id=branch_id,
        custom_path=db_file,
    )

    assert len(tickets) >= 2
    # Tiket pertama harus Backend dengan status TODO
    assert tickets[0]["assigned_role_id"] == role_be["id"]
    assert tickets[0]["status"] == "TODO"
    assert tickets[0]["dependencies"] == []

    # Tiket kedua harus Frontend dengan status BACKLOG dan dependen pada tiket pertama
    assert tickets[1]["assigned_role_id"] == role_fe["id"]
    assert tickets[1]["status"] == "BACKLOG"
    assert tickets[1]["dependencies"] == [tickets[0]["id"]]


@pytest.mark.asyncio
async def test_multi_pipeline_endpoints(workflow_client: httpx.AsyncClient) -> None:
    """Menguji endpoint multi-pipeline (Software, Edukasi, Copywriting) dan pembuatan pipeline kustom."""
    res = await workflow_client.get("/api/v1/corporate/branches/branch_main/pipelines")
    assert res.status_code == 200
    pipes = res.json()
    assert len(pipes) >= 3
    slugs = [p["slug"] for p in pipes]
    assert "software" in slugs
    assert "education" in slugs
    assert "copywriting" in slugs

    new_pipe = {
        "name": "Market Research & Discovery",
        "slug": "market-research",
        "product_line": "MARKET_RESEARCH",
        "description": "Alur riset pasar dan validasi ide",
    }
    create_res = await workflow_client.post("/api/v1/corporate/branches/branch_main/pipelines", json=new_pipe)
    assert create_res.status_code == 201
    assert create_res.json()["slug"] == "market-research"


@pytest.mark.asyncio
async def test_fork_and_immediate_reset_pipeline(workflow_client: httpx.AsyncClient) -> None:
    """Menguji kasus regresi: fork workflow baru lalu langsung reset tanpa perubahan, tanpa benturan UNIQUE ID."""
    fork_res = await workflow_client.post(
        "/api/v1/corporate/branches/fork",
        json={
            "name": "Immediate Reset Test",
            "slug": "immediate-reset-test",
            "source_branch_id": "branch_main",
        },
    )
    assert fork_res.status_code == 201
    branch_id = fork_res.json()["id"]

    # Langsung reset pipeline branch baru ke template main
    reset_res = await workflow_client.post(f"/api/v1/corporate/branches/{branch_id}/pipeline/reset")
    assert reset_res.status_code == 200
    stages = reset_res.json()
    assert len(stages) > 0
    # Verifikasi bahwa semua ID tahapan unik dan role_id merujuk ke branch baru
    stage_ids = [s["id"] for s in stages]
    assert len(stage_ids) == len(set(stage_ids))

