"""Unit & Integration Tests untuk Autonomous P2P PR Review Engine.

Memverifikasi kalkulasi git diff, penyimpanan PR & review, peninjauan otomatis
oleh QA (OWASP) & CTO (Arsitektur), perhitungan kuorum persetujuan, dan REST API.
"""

from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from app.core.config import settings
from app.db.init_db import init_database
from app.db.pr_repo import pr_repo
from app.engine.diff_engine import generate_file_unified_diff, compute_multi_file_diff
from app.engine.peer_reviewer import peer_reviewer


def test_diff_engine_calculations() -> None:
    """Memverifikasi pembentukan git unified diff dan kalkulasi penambahan/pengurangan baris."""
    old_c = "def hello():\n    return 'world'\n"
    new_c = "def hello():\n    # greeting\n    return 'INDONESIA'\n"

    diff_str, add_cnt, del_cnt = generate_file_unified_diff("main.py", old_c, new_c)
    assert "+    # greeting" in diff_str
    assert "-    return 'world'" in diff_str
    assert "+    return 'INDONESIA'" in diff_str
    assert add_cnt >= 2
    assert del_cnt >= 1

    # Multi-file aggregation
    files_delta = [
        {"path": "app.py", "old_content": "", "new_content": "import sys\n"},
        {"path": "old.py", "old_content": "dead code\n", "new_content": ""},
    ]
    res = compute_multi_file_diff(files_delta)
    assert len(res["files"]) == 2
    assert res["total_additions"] >= 1
    assert res["total_deletions"] >= 1


@pytest.mark.asyncio
async def test_pr_repo_and_quorum_lifecycle(tmp_path: Path) -> None:
    """Memverifikasi alur kuorum persetujuan PR: OPEN -> CHANGES_REQUESTED -> APPROVED -> MERGED."""
    db_file = str(tmp_path / "test_pr.db")
    await init_database(custom_path=db_file)

    pr = await pr_repo.create_pull_request(
        project_id="proj_alpha",
        ticket_id="tick_101",
        title="Add User Authentication",
        description="JWT based auth",
        source_branch="pr/proj_alpha/tick_101",
        author_role_id="role_backend",
        files_changed=[{"path": "auth.py", "status": "ADDED", "additions": 50, "deletions": 0}],
        diff_unified="+++ b/auth.py",
        additions_count=50,
        deletions_count=0,
        quorum_required=2,
        custom_path=db_file,
    )
    assert pr["status"] == "OPEN"
    assert pr["approvals_count"] == 0

    # Review 1: Approved oleh CTO
    await pr_repo.add_review(
        pr_id=pr["id"],
        reviewer_role_id="role_cto",
        reviewer_name="CTO AI",
        verdict="APPROVED",
        summary="Arsitektur modular bersih.",
        custom_path=db_file,
    )
    updated = await pr_repo.get_pull_request(pr["id"], custom_path=db_file)
    assert updated["status"] == "OPEN"
    assert updated["approvals_count"] == 1

    # Review 2: Approved oleh Frontend -> Kuorum tercapai (2/2)!
    await pr_repo.add_review(
        pr_id=pr["id"],
        reviewer_role_id="role_frontend",
        reviewer_name="Frontend Lead",
        verdict="APPROVED",
        summary="Kontrak API cocok.",
        custom_path=db_file,
    )
    approved_pr = await pr_repo.get_pull_request(pr["id"], custom_path=db_file)
    assert approved_pr["status"] == "APPROVED"
    assert approved_pr["approvals_count"] == 2

    # Merge PR
    merged_pr = await pr_repo.update_pr_status(pr["id"], "MERGED", custom_path=db_file)
    assert merged_pr["status"] == "MERGED"


@pytest.mark.asyncio
async def test_peer_reviewer_detection(tmp_path: Path) -> None:
    """Memverifikasi deteksi celah keamanan QA dan pelanggaran baris/print oleh CTO."""
    db_file = str(tmp_path / "test_reviewer.db")
    await init_database(custom_path=db_file)

    # Buat PR dengan kode bermasalah (ada hardcoded password dan print statement)
    bad_code = (
        'api_key = "sk-supersecret12345"\n'
        'print("Debugging token here")\n'
    )
    pr = await pr_repo.create_pull_request(
        project_id="proj_vuln",
        ticket_id="tick_999",
        title="Flawed Implementation",
        description="Testing reviewer catches",
        source_branch="pr/flaw",
        author_role_id="role_backend",
        files_changed=[{"path": "vuln.py", "new_content": bad_code}],
        custom_path=db_file,
    )

    # Jalankan full autonomous review
    res = await peer_reviewer.run_full_autonomous_review(pr["id"], custom_path=db_file)
    assert res["quorum_reached"] is False
    assert res["pr"]["status"] == "CHANGES_REQUESTED"

    # Verifikasi temuan inline
    reviews = res["reviews"]
    qa_review = next(r for r in reviews if r["reviewer_role_id"] == "role_qa_lead")
    assert qa_review["verdict"] == "CHANGES_REQUESTED"
    assert qa_review["security_score"] < 100

    cto_review = next(r for r in reviews if r["reviewer_role_id"] == "role_cto")
    assert cto_review["verdict"] == "CHANGES_REQUESTED"
    assert any("print()" in c["comment"] for c in cto_review["inline_comments"])


@pytest.mark.asyncio
async def test_pull_requests_rest_api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Memverifikasi endpoint REST API /api/v1/pull-requests/*."""
    db_file = tmp_path / "test_pr_api.db"
    test_db_url = f"sqlite+aiosqlite:///{db_file}"
    monkeypatch.setattr(settings, "DATABASE_URL", test_db_url)
    await init_database(str(db_file))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Buka PR via REST API
        create_payload = {
            "project_id": "proj_demo",
            "ticket_id": "tick_demo",
            "title": "Build Landing Hero",
            "description": "Hero with obsidian liquid aesthetics",
            "source_branch": "pr/proj_demo/hero",
            "author_role_id": "role_frontend",
            "files_delta": [
                {"path": "Hero.tsx", "old_content": "", "new_content": "export default function Hero() { return <div/>; }"}
            ],
            "quorum_required": 2,
        }
        resp = await client.post("/api/v1/pull-requests", json=create_payload)
        assert resp.status_code == 200
        pr_data = resp.json()
        pr_id = pr_data["id"]
        assert pr_data["status"] == "OPEN"
        assert pr_data["additions_count"] > 0

        # 2. Trigger auto-review
        auto_res = await client.post(f"/api/v1/pull-requests/{pr_id}/auto-review")
        assert auto_res.status_code == 200
        assert auto_res.json()["quorum_reached"] is True

        # 3. Merge PR
        merge_res = await client.post(f"/api/v1/pull-requests/{pr_id}/merge")
        assert merge_res.status_code == 200
        assert merge_res.json()["status"] == "MERGED"
