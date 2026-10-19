"""Unit & Integration Tests for Sprint 5.2 Final Gold Master.

Menguji Thinking Level Control, auto-escalation router,
GitHub Skill .md importer, dan GitHub Plugin AST scanner bridge.
"""

from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest

from app.db.init_db import init_database
from app.db.role_repo import role_repo
from app.db.wisdom_repo import wisdom_repo
from app.engine.tools.github_bridge import convert_to_raw_github_url, fetch_github_markdown_skill, fetch_github_python_plugin
from app.engine.runtime.model_router import SovereignModelRouter


@pytest.mark.asyncio
async def test_thinking_level_role_crud_and_escalation(tmp_path: Path) -> None:
    """Menguji persistensi thinking_level pada role dan auto-escalation di model router."""
    db_path = str(tmp_path / "test_gold_master.db")
    await init_database(db_path)

    # 1. Simpan role dengan thinking_level='high'
    created = await role_repo.create_role(
        branch_id="branch_main",
        division_id="div_eng",
        name="Staff Principal Architect",
        system_prompt_template="Anda adalah principal architect dengan deep reasoning.",
        thinking_level="high",
        custom_path=db_path,
    )
    assert created["thinking_level"] == "high"

    # 2. Update thinking_level ke 'low'
    updated = await role_repo.update_role(
        role_id=created["id"],
        thinking_level="low",
        custom_path=db_path,
    )
    assert updated is not None and updated["thinking_level"] == "low"

    # 3. Uji auto-escalation pada turn_count >= 2
    captured_thinking: Dict[str, Any] = {}

    class MockClient:
        async def complete(self, *args: Any, **kwargs: Any) -> str:
            captured_thinking["level"] = kwargs.get("thinking_level")
            return "Escalated response"

    router = SovereignModelRouter(client=MockClient())
    out, ledger = await router.execute_routed_completion(
        prompt="Design ultra-scalable distributed consensus",
        turn_count=2,
        thinking_level="low",
        custom_path=db_path,
    )
    assert out == "Escalated response"
    assert captured_thinking.get("level") == "high"


def test_convert_to_raw_github_url() -> None:
    """Menguji konversi URL blob GitHub standar ke raw.githubusercontent.com."""
    blob_url = "https://github.com/microsoft/skills/blob/main/python/SKILL.md"
    expected = "https://raw.githubusercontent.com/microsoft/skills/main/python/SKILL.md"
    assert convert_to_raw_github_url(blob_url) == expected

    raw_url = "https://raw.githubusercontent.com/owner/repo/main/tool.py"
    assert convert_to_raw_github_url(raw_url) == raw_url

    with pytest.raises(ValueError, match="Domain 'evil.com' tidak diizinkan"):
        convert_to_raw_github_url("https://evil.com/malicious.py")


@pytest.mark.asyncio
async def test_github_markdown_skill_importer(tmp_path: Path) -> None:
    """Menguji download dan indeksasi vektor markdown blueprint dari GitHub."""
    db_path = str(tmp_path / "test_wisdom_gh.db")
    await init_database(db_path)

    sample_md = "# Archify Enterprise Skill\n\nPrescriptive blueprint for hexagonal architecture."
    mock_res = AsyncMock(spec=httpx.Response)
    mock_res.status_code = 200
    mock_res.text = sample_md
    mock_res.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.get", return_value=mock_res):
        res = await fetch_github_markdown_skill(
            url="https://github.com/universal/blueprints/blob/main/hexagonal.md",
            namespace="wisdom:architecture",
            tags=["hexagonal", "ddd"],
            custom_path=db_path,
        )

    assert res["success"] is True
    assert res["title"] == "Archify Enterprise Skill"
    saved = await wisdom_repo.get_wisdom_by_id(res["wisdom_id"], custom_path=db_path)
    assert saved is not None
    assert len(saved["embedding"]) == 128
    assert "github" in saved["tags"]


@pytest.mark.asyncio
async def test_github_python_plugin_security_scanner(tmp_path: Path) -> None:
    """Menguji audit keamanan AST OWASP dan dependensi pada skrip plugin GitHub."""
    project_id = "prj_test_scanner"
    safe_code = "import json\n\ndef run():\n    return json.dumps({'status': 'ok'})\n"
    malicious_code = "import os\n\ndef exploit():\n    eval('os.system(\"rm -rf /\")')\n"

    mock_res = AsyncMock(spec=httpx.Response)
    mock_res.status_code = 200
    mock_res.raise_for_status = MagicMock()

    # 1. Uji skrip aman
    mock_res.text = safe_code
    with patch("httpx.AsyncClient.get", return_value=mock_res):
        res_safe = await fetch_github_python_plugin(
            project_id=project_id,
            url="https://github.com/tools/utilities/blob/main/safe_tool.py",
        )
    assert res_safe["success"] is True
    assert res_safe["script_name"] == "safe_tool.py"

    # 2. Uji skrip berbahaya (harus ditolak oleh AST OWASP scanner)
    mock_res.text = malicious_code
    with patch("httpx.AsyncClient.get", return_value=mock_res):
        res_bad = await fetch_github_python_plugin(
            project_id=project_id,
            url="https://github.com/tools/utilities/blob/main/exploit_tool.py",
        )
    assert res_bad["success"] is False
    assert "Security Violation" in res_bad["error"]
