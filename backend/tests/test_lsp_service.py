"""
Unit Tests untuk In-Sandbox LSP Service, Project-Wide Filtering, dan Pre-PR Gatekeeper.
"""

from pathlib import Path
import pytest
from unittest.mock import AsyncMock, patch
from app.db.init_db import init_database
from app.db.pr_repo import pr_repo
from app.engine.lsp.lsp_service import lsp_service
from app.engine.quality.lsp_gatekeeper import lsp_gatekeeper


@pytest.fixture
def lsp_test_db(tmp_path):
    """Menyiapkan path basis data sementara untuk pengujian PR & LSP Gatekeeper."""
    return str(tmp_path / "test_lsp.db")


@pytest.mark.asyncio
async def test_lsp_python_ast_fallback_detects_syntax_errors(tmp_path):
    """Memverifikasi deteksi sintaksis Python rusak melalui fallback AST parser."""
    broken_file = tmp_path / "broken.py"
    broken_file.write_text("def broken_syntax(\n    return 42", encoding="utf-8")

    diags = await lsp_service.get_python_diagnostics(tmp_path, target_file="broken.py")
    assert len(diags) >= 1
    assert diags[0]["severity"] == "error"
    assert diags[0]["code"] == "SyntaxError"


@pytest.mark.asyncio
async def test_lsp_typescript_project_diagnostics_filtering(tmp_path):
    """Memverifikasi parsing output tsc project mode dan penyaringan berdasarkan file target."""
    (tmp_path / "tsconfig.json").write_text("{}", encoding="utf-8")
    mock_tsc_output = (
        "src/app/page.tsx(14,5): error TS2322: Type 'string' is not assignable to type 'number'.\n"
        "src/components/Header.tsx(20,1): error TS1005: ';' expected.\n"
    )

    with patch.object(lsp_service, "_run_command", new=AsyncMock(return_value=(2, mock_tsc_output, ""))):
        # 1. Ambil diagnostik untuk page.tsx saja
        diags_page = await lsp_service.get_typescript_diagnostics(tmp_path, target_file="src/app/page.tsx")
        assert len(diags_page) == 1
        assert diags_page[0]["line"] == 14
        assert diags_page[0]["code"] == "TS2322"

        # 2. Ambil diagnostik tanpa filter (semua file)
        diags_all = await lsp_service.get_typescript_diagnostics(tmp_path, target_file=None)
        assert len(diags_all) == 2


@pytest.mark.asyncio
async def test_lsp_gatekeeper_blocks_pr_with_type_errors(lsp_test_db, tmp_path):
    """Memverifikasi bahwa LSP Gatekeeper menandai CHANGES_REQUESTED saat terdapat fatal type errors."""
    await init_database(custom_path=lsp_test_db)
    pr = await pr_repo.create_pull_request(
        project_id="proj_lsp",
        ticket_id="ticket_001",
        title="Add Broken Feature",
        description="Feature with invalid syntax",
        source_branch="feature_branch",
        author_role_id="role_backend",
        files_changed=[{"path": "backend/app/bad_file.py", "new_content": "invalid syntax ("}],
        custom_path=lsp_test_db,
    )

    mock_errors = [{
        "file": "backend/app/bad_file.py",
        "line": 1,
        "code": "SyntaxError",
        "message": "unexpected EOF while parsing",
        "severity": "error",
    }]

    with patch.object(lsp_service, "get_diagnostics", new=AsyncMock(return_value=mock_errors)):
        rev = await lsp_gatekeeper.review_pr_type_diagnostics(
            pr_id=pr["id"], files=pr["files"], custom_path=lsp_test_db
        )

        assert rev["verdict"] == "CHANGES_REQUESTED"
        assert len(rev["inline_comments"]) == 1
        assert "SyntaxError" in rev["inline_comments"][0]["comment"]
