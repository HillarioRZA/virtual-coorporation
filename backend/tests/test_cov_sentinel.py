"""
Unit Tests untuk Internal CoV (Chain-of-Verification) Pre-Flight Gatekeeper & Sentinel API.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.init_db import init_database
from app.db.sentinel_repo import sentinel_repo
from app.engine.sentinel.manifest import get_stage_tool_manifest
from app.engine.sentinel.verifier import cov_gatekeeper


@pytest.mark.asyncio
async def test_lean_tool_manifest_generation(tmp_path):
    """Memverifikasi bahwa manifest perkakas dihasilkan secara adaptif sesuai tahap workflow."""
    # Tahap ideasi tidak membutuhkan perkakas teknis
    ideation_manifest = get_stage_tool_manifest("ideation")
    assert "TIDAK ADA PERKAKAS" in ideation_manifest

    # Tahap development menyertakan perkakas kode dan database
    dev_manifest = get_stage_tool_manifest("development")
    assert "inspect_db_schema" in dev_manifest
    assert "validate_api_contract" in dev_manifest
    assert "search_codebase" in dev_manifest


@pytest.mark.asyncio
async def test_cov_gatekeeper_pure_text_inspection(tmp_path):
    """Memverifikasi bahwa pesan percakapan biasa langsung disetujui tanpa pembengkakan token."""
    db_file = tmp_path / "test_sentinel.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"
    await init_database(custom_path=db_url)

    candidate = "Halo Founder, strategi go-to-market kita akan berfokus pada developer B2B."
    result = await cov_gatekeeper.inspect(
        project_id="proj_cov_test",
        agent_role="COS",
        candidate_content=candidate,
        stage="ideation",
        custom_path=db_url,
    )

    assert result.approved is True
    assert result.status == "APPROVED"
    assert result.tool_call is None
    assert result.inspected_content == candidate
    assert result.audit_id is not None


@pytest.mark.asyncio
async def test_cov_gatekeeper_valid_tool_call(tmp_path):
    """Memverifikasi bahwa pemanggilan perkakas dengan sintaks JSON valid disetujui."""
    db_file = tmp_path / "test_sentinel2.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"
    await init_database(custom_path=db_url)

    candidate = """Saya akan memeriksa skema tabel user.
```json
{
  "tool": "inspect_db_schema",
  "parameters": {
    "table_name": "users"
  }
}
```"""
    result = await cov_gatekeeper.inspect(
        project_id="proj_cov_test",
        agent_role="BACKEND",
        candidate_content=candidate,
        stage="development",
        custom_path=db_url,
    )

    assert result.approved is True
    assert result.status == "APPROVED"
    assert result.tool_call is not None
    assert result.tool_call["tool"] == "inspect_db_schema"
    assert result.tool_call["parameters"]["table_name"] == "users"


@pytest.mark.asyncio
async def test_sentinel_audit_repo_and_api(tmp_path):
    """Memverifikasi pencatatan audit log dan kueri endpoint Sentinel API."""
    db_file = tmp_path / "test_sentinel_api.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"
    await init_database(custom_path=db_url)

    # Catat audit log dummy
    await sentinel_repo.record_audit(
        project_id="proj_sentinel_api",
        agent_role="CTO",
        status="APPROVED",
        original_content="Refactor API endpoints",
        inspected_content="Refactor API endpoints",
        tool_name="git_diff_summary",
        tool_parameters={"base_ref": "HEAD~1"},
        latency_ms=45.2,
        custom_path=db_url,
    )

    # Catat audit log repair
    await sentinel_repo.record_audit(
        project_id="proj_sentinel_api",
        agent_role="FRONTEND",
        status="REPAIRED",
        original_content="Cari fungsi nav bar",
        inspected_content="Cari fungsi nav bar terkoreksi",
        tool_name="search_codebase",
        tool_parameters={"query": "Navbar", "is_symbol_only": False},
        repair_feedback="Parameter query diperbaiki",
        repairs_count=1,
        latency_ms=120.5,
        custom_path=db_url,
    )

    stats = await sentinel_repo.get_audit_stats("proj_sentinel_api", custom_path=db_url)
    assert stats["total_inspections"] == 2
    assert stats["approved_count"] == 1
    assert stats["repaired_count"] == 1
    assert stats["reliability_rate"] == 100.0

    logs = await sentinel_repo.get_audit_logs("proj_sentinel_api", custom_path=db_url)
    assert len(logs) == 2
    assert logs[0]["tool_name"] in ["git_diff_summary", "search_codebase"]
