"""
Unit & Integration Tests untuk Sprint 2.1: Dynamic Corporate Schema, Git-Style Workflow Branching, & CRUD Registry.
Menguji auto-seeding branch main, forking alur kerja organisasi, isolasi role di branch kustom,
aktivasi branch, dan proteksi penghapusan entitas bawaan sistem.
"""

from pathlib import Path
from typing import AsyncGenerator
import httpx
import pytest
import pytest_asyncio

from app.core.config import settings
from app.db.corporate_repo import corporate_repo
from app.db.init_db import init_database
from main import app


@pytest_asyncio.fixture
async def test_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Fixture client HTTP asinkron dengan basis data SQLite terisolasi."""
    db_file = tmp_path / "test_corporate.db"
    test_db_url = f"sqlite+aiosqlite:///{db_file}"
    monkeypatch.setattr(settings, "DATABASE_URL", test_db_url)

    await init_database(str(db_file))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_default_corporate_seeding(test_client: httpx.AsyncClient) -> None:
    """Menguji auto-seeding branch main, 3 divisi Tech Core, dan 7 peran bawaan sistem."""
    # 1. Cek Branch Main
    branch_res = await test_client.get("/api/v1/corporate/branches")
    assert branch_res.status_code == 200
    branches = branch_res.json()
    assert len(branches) >= 1
    main_branch = next(b for b in branches if b["id"] == "branch_main")
    assert main_branch["is_active_main"] is True
    assert main_branch["slug"] == "main"

    # 2. Cek Divisi Default
    div_res = await test_client.get("/api/v1/corporate/divisions?branch_id=branch_main")
    assert div_res.status_code == 200
    divisions = div_res.json()
    div_ids = [d["id"] for d in divisions]
    assert "div_exec" in div_ids
    assert "div_eng" in div_ids
    assert "div_product" in div_ids

    # 3. Cek Role Default
    role_res = await test_client.get("/api/v1/corporate/roles?branch_id=branch_main")
    assert role_res.status_code == 200
    roles = role_res.json()
    role_slugs = [r["slug"] for r in roles]
    assert "cos" in role_slugs
    assert "cto" in role_slugs
    assert "pm" in role_slugs
    assert "ux" in role_slugs
    assert "frontend" in role_slugs
    assert "backend" in role_slugs
    assert "qa" in role_slugs


@pytest.mark.asyncio
async def test_fork_branch_clones_entire_hierarchy(test_client: httpx.AsyncClient) -> None:
    """Menguji fitur Git-Style forking branch: menduplikasi seluruh divisi dan role secara atomik."""
    fork_payload = {
        "name": "Agile Fast-Track Experiment",
        "slug": "agile-fast-track",
        "description": "Eksperimen metodologi Agile tanpa peran QA terpisah.",
        "source_branch_id": "branch_main",
    }
    fork_res = await test_client.post("/api/v1/corporate/branches/fork", json=fork_payload)
    assert fork_res.status_code == 201
    forked_branch = fork_res.json()
    new_branch_id = forked_branch["id"]
    assert new_branch_id.startswith("branch_")
    assert forked_branch["is_active_main"] is False

    # Verifikasi divisi terduplikasi di branch baru
    div_res = await test_client.get(f"/api/v1/corporate/divisions?branch_id={new_branch_id}")
    assert div_res.status_code == 200
    forked_divs = div_res.json()
    assert len(forked_divs) == 3

    # Verifikasi role terduplikasi di branch baru
    role_res = await test_client.get(f"/api/v1/corporate/roles?branch_id={new_branch_id}")
    assert role_res.status_code == 200
    forked_roles = role_res.json()
    assert len(forked_roles) == 7


@pytest.mark.asyncio
async def test_deactivate_and_modify_role_in_forked_branch(test_client: httpx.AsyncClient) -> None:
    """Menguji isolasi sandbox: memodifikasi/menonaktifkan role di branch kustom tanpa memengaruhi branch main."""
    # 1. Fork branch baru
    fork_res = await test_client.post(
        "/api/v1/corporate/branches/fork",
        json={"name": "Lean Experiment", "slug": "lean-exp", "source_branch_id": "branch_main"},
    )
    assert fork_res.status_code == 201
    forked_branch_id = fork_res.json()["id"]

    # 2. Ambil role QA di branch kustom
    roles_res = await test_client.get(f"/api/v1/corporate/roles?branch_id={forked_branch_id}")
    qa_forked = next(r for r in roles_res.json() if r["slug"] == "qa")
    qa_forked_id = qa_forked["id"]

    # 3. Nonaktifkan QA role di branch kustom
    update_res = await test_client.put(
        f"/api/v1/corporate/roles/{qa_forked_id}",
        json={"is_active": False, "token_budget_per_task": 15000},
    )
    assert update_res.status_code == 200
    updated_qa = update_res.json()
    assert updated_qa["is_active"] is False
    assert updated_qa["token_budget_per_task"] == 15000

    # 4. Verifikasi bahwa pada branch_main, role QA asli TETAP AKTIF (is_active = True)
    main_roles_res = await test_client.get("/api/v1/corporate/roles?branch_id=branch_main")
    main_qa = next(r for r in main_roles_res.json() if r["slug"] == "qa")
    assert main_qa["is_active"] is True
    assert main_qa["token_budget_per_task"] == 8000


@pytest.mark.asyncio
async def test_activate_branch_promotes_to_main(test_client: httpx.AsyncClient) -> None:
    """Menguji promosi branch eksperimen menjadi active production main."""
    fork_res = await test_client.post(
        "/api/v1/corporate/branches/fork",
        json={"name": "Sprint 3 Workflow", "slug": "sprint-3", "source_branch_id": "branch_main"},
    )
    branch_id = fork_res.json()["id"]

    # Promosikan branch ini
    activate_res = await test_client.post(f"/api/v1/corporate/branches/{branch_id}/activate")
    assert activate_res.status_code == 200
    assert activate_res.json()["is_active_main"] is True

    # Cek bahwa branch_main lama tidak lagi aktif
    active_res = await test_client.get("/api/v1/corporate/branches/active")
    assert active_res.status_code == 200
    assert active_res.json()["id"] == branch_id


@pytest.mark.asyncio
async def test_protect_branch_main_from_deletion(test_client: httpx.AsyncClient) -> None:
    """Menguji proteksi: branch 'branch_main' tidak dapat dihapus."""
    del_res = await test_client.delete("/api/v1/corporate/branches/branch_main")
    assert del_res.status_code == 400
    assert "tidak dapat dihapus" in del_res.json()["detail"]


@pytest.mark.asyncio
async def test_custom_division_crud_and_protection(test_client: httpx.AsyncClient) -> None:
    """Menguji pembuatan divisi kustom, update, proteksi sistem bawaan, dan penghapusan."""
    # 1. Buat divisi kustom baru
    create_payload = {
        "branch_id": "branch_main",
        "name": "Digital Education Division",
        "slug": "digital-education",
        "description": "Pembuatan kursus online, silabus, dan materi edukasi",
        "accent_color": "#a855f7",
        "icon_name": "GraduationCap",
    }
    create_res = await test_client.post("/api/v1/corporate/divisions", json=create_payload)
    assert create_res.status_code == 201
    new_div = create_res.json()
    div_id = new_div["id"]
    assert div_id.startswith("div_")

    # 2. Update divisi
    update_res = await test_client.put(
        f"/api/v1/corporate/divisions/{div_id}",
        json={"description": "Pembuatan kursus bootcamp dan latihan interaktif"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["description"] == "Pembuatan kursus bootcamp dan latihan interaktif"

    # 3. Coba hapus divisi bawaan 'div_eng' (harus ditolak 400)
    del_default_res = await test_client.delete("/api/v1/corporate/divisions/div_eng")
    assert del_default_res.status_code == 400
    assert "bawaan sistem" in del_default_res.json()["detail"]

    # 4. Hapus divisi kustom (harus berhasil 200)
    del_custom_res = await test_client.delete(f"/api/v1/corporate/divisions/{div_id}")
    assert del_custom_res.status_code == 200
    assert del_custom_res.json()["status"] == "success"


@pytest.mark.asyncio
async def test_custom_role_crud_and_protection(test_client: httpx.AsyncClient) -> None:
    """Menguji pembuatan role kustom baru, update model, proteksi sistem, dan penghapusan."""
    # 1. Daftarkan role baru di bawah div_exec
    role_payload = {
        "branch_id": "branch_main",
        "division_id": "div_exec",
        "name": "Chief Financial Officer",
        "slug": "cfo",
        "system_prompt_template": "Kamu adalah CFO AI yang bertugas mengaudit token burn rate dan efisiensi biaya proyek.",
        "model_provider": "openrouter",
        "model_name": "deepseek/deepseek-r1:free",
        "temperature": 0.1,
        "tool_permissions": ["read_file"],
        "token_budget_per_task": 5000,
        "is_active": True,
    }
    create_res = await test_client.post("/api/v1/corporate/roles", json=role_payload)
    assert create_res.status_code == 201
    new_role = create_res.json()
    role_id = new_role["id"]
    assert role_id.startswith("role_")

    # 2. Update model
    update_res = await test_client.put(
        f"/api/v1/corporate/roles/{role_id}",
        json={"temperature": 0.3, "token_budget_per_task": 6000},
    )
    assert update_res.status_code == 200
    assert update_res.json()["temperature"] == 0.3
    assert update_res.json()["token_budget_per_task"] == 6000

    # 3. Coba hapus role bawaan 'role_cto' (harus ditolak 400)
    del_default_res = await test_client.delete("/api/v1/corporate/roles/role_cto")
    assert del_default_res.status_code == 400
    assert "bawaan sistem" in del_default_res.json()["detail"]

    # 4. Hapus role kustom (harus berhasil 200)
    del_custom_res = await test_client.delete(f"/api/v1/corporate/roles/{role_id}")
    assert del_custom_res.status_code == 200
    assert del_custom_res.json()["status"] == "success"
