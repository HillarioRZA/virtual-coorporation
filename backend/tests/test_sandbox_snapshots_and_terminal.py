"""
Unit and Integration Tests untuk Sandbox Snapshots & Terminal Manager (Sprint 2.5).
"""

from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

from app.sandbox.snapshot_manager import SnapshotManager
from app.sandbox.terminal_manager import TerminalManager
from main import app


@pytest.fixture
def temp_sandbox_base(tmp_path: Path) -> Path:
    """Fixture menyediakan folder temporary untuk isolasi file snapshot."""
    return tmp_path / "test_projects_output"


@pytest.mark.asyncio
async def test_snapshot_create_and_list(temp_sandbox_base: Path):
    """Menguji pembuatan snapshot direktori dan pencatatan manifest."""
    sm = SnapshotManager(base_output_dir=temp_sandbox_base)
    project_id = "proj_snap_1"

    # Setup dummy project files
    p_dir = sm._get_project_dir(project_id)
    fe_dir = p_dir / "frontend"
    fe_dir.mkdir(parents=True, exist_ok=True)
    (fe_dir / "page.tsx").write_text("export default function Page() { return <div>Test</div>; }", encoding="utf-8")
    (p_dir / "README.md").write_text("# Project 1", encoding="utf-8")

    # Ambil snapshot
    snap = sm.create_snapshot(project_id, tag="PRE_HARDENING", description="Before AST scan")
    assert snap["tag"] == "PRE_HARDENING"
    assert snap["file_count"] == 2
    assert snap["total_bytes"] > 0

    # List snapshots
    history = sm.list_snapshots(project_id)
    assert len(history) == 1
    assert history[0]["id"] == snap["id"]


@pytest.mark.asyncio
async def test_snapshot_rollback_and_safety_backup(temp_sandbox_base: Path):
    """Menguji pemulihan 1-klik dan pembuatan safety backup otomatis."""
    sm = SnapshotManager(base_output_dir=temp_sandbox_base)
    project_id = "proj_rollback_1"

    p_dir = sm._get_project_dir(project_id)
    target_file = p_dir / "app.py"
    target_file.write_text("version = 1", encoding="utf-8")

    # Snapshot v1
    snap_v1 = sm.create_snapshot(project_id, tag="INITIAL_V1", description="Baseline v1")

    # Modifikasi file & tambah file baru
    target_file.write_text("version = 2_broken", encoding="utf-8")
    unwanted_file = p_dir / "dirty_hack.py"
    unwanted_file.write_text("broken_code()", encoding="utf-8")

    # Pemicuan Rollback ke v1
    res = await sm.rollback_snapshot(project_id, snap_v1["id"])
    assert res["status"] == "success"
    assert res["restored_snapshot_id"] == snap_v1["id"]

    # Verifikasi file kembali ke v1
    assert target_file.read_text(encoding="utf-8") == "version = 1"
    assert not unwanted_file.exists()

    # Verifikasi auto-safety backup tercatat di manifest
    history = sm.list_snapshots(project_id)
    assert len(history) == 2
    assert history[0]["tag"] == "AUTO_PRE_ROLLBACK"


@pytest.mark.asyncio
async def test_snapshot_delete(temp_sandbox_base: Path):
    """Menguji penghapusan snapshot dari manifest dan filesystem."""
    sm = SnapshotManager(base_output_dir=temp_sandbox_base)
    project_id = "proj_del_1"

    p_dir = sm._get_project_dir(project_id)
    (p_dir / "test.txt").write_text("hello", encoding="utf-8")

    snap = sm.create_snapshot(project_id, tag="TMP")
    assert len(sm.list_snapshots(project_id)) == 1

    deleted = sm.delete_snapshot(project_id, snap["id"])
    assert deleted is True
    assert len(sm.list_snapshots(project_id)) == 0

    # Menghapus snapshot yang tidak ada harus return False
    assert sm.delete_snapshot(project_id, "snap_invalid") is False


@pytest.mark.asyncio
async def test_terminal_manager_execution_and_guardrail(temp_sandbox_base: Path):
    """Menguji eksekusi terminal shell dan pencegahan perintah berbahaya."""
    tm = TerminalManager(base_output_dir=temp_sandbox_base)
    project_id = "proj_term_1"

    # Perintah aman sederhana
    events = []
    async for evt in tm.execute_command_stream(project_id, 'python -c "print(\'HELLO_TERMINAL\')"'):
        events.append(evt)

    types = [e["type"] for e in events]
    assert "start" in types
    assert "stdout" in types
    assert "exit" in types

    stdout_text = "".join([e.get("data", "") for e in events if e["type"] == "stdout"])
    assert "HELLO_TERMINAL" in stdout_text

    exit_event = next(e for e in events if e["type"] == "exit")
    assert exit_event["code"] == 0

    # Perintah berbahaya yang diblokir guardrail
    blocked_events = []
    async for evt in tm.execute_command_stream(project_id, "rmdir /s /q c:\\"):
        blocked_events.append(evt)

    stderr_text = "".join([e.get("data", "") for e in blocked_events if e["type"] == "stderr"])
    assert "GUARDRAIL" in stderr_text
    blocked_exit = next(e for e in blocked_events if e["type"] == "exit")
    assert blocked_exit["code"] == 126


@pytest.mark.asyncio
async def test_sandbox_snapshot_rest_api(temp_sandbox_base: Path, monkeypatch):
    """Menguji endpoint REST API /api/v1/sandbox/snapshots."""
    sm = SnapshotManager(base_output_dir=temp_sandbox_base)
    monkeypatch.setattr("app.api.v1.sandbox_snapshots.snapshot_manager", sm)

    project_id = "proj_api_snap"
    p_dir = sm._get_project_dir(project_id)
    (p_dir / "main.py").write_text("print('api_test')", encoding="utf-8")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Create Snapshot via REST
        res_post = await ac.post(
            f"/api/v1/sandbox/snapshots/{project_id}",
            json={"tag": "REST_TEST", "description": "Created via API"},
        )
        assert res_post.status_code == 201
        created = res_post.json()
        assert created["tag"] == "REST_TEST"
        snapshot_id = created["id"]

        # 2. List Snapshots via REST
        res_get = await ac.get(f"/api/v1/sandbox/snapshots/{project_id}")
        assert res_get.status_code == 200
        items = res_get.json()
        assert len(items) == 1
        assert items[0]["id"] == snapshot_id

        # 3. Rollback Snapshot via REST
        res_rb = await ac.post(f"/api/v1/sandbox/snapshots/{project_id}/rollback/{snapshot_id}")
        assert res_rb.status_code == 200
        assert res_rb.json()["status"] == "success"

        # 4. Delete Snapshot via REST
        res_del = await ac.delete(f"/api/v1/sandbox/snapshots/{project_id}/{snapshot_id}")
        assert res_del.status_code == 200
        assert res_del.json()["status"] == "deleted"

        # 5. Delete not found -> 404
        res_del_404 = await ac.delete(f"/api/v1/sandbox/snapshots/{project_id}/invalid_id")
        assert res_del_404.status_code == 404
