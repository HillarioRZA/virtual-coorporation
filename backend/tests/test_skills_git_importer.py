"""
Unit Tests untuk Git & Remote Repository Importer Subsystem pada Skills Hub.
"""

from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest

from app.engine.skills.git_importer import (
    collect_repo_files,
    import_skill_from_git,
    parse_skill_metadata,
)
from app.engine.skills.skills_hub import skills_hub


def test_parse_skill_metadata_extraction():
    """Menguji parsing nama, kategori, dan deskripsi dari konten SKILL.md."""
    sample_md = """# UI UX Pro Max Skill
Kategori: Design System
Deskripsi: Playbook komprehensif untuk styling modern glassmorphism.

## Petunjuk
Gunakan palette warna harmonis.
"""
    meta = parse_skill_metadata(sample_md, default_name="ui-ux-pro-max-skill")
    assert meta["name"] == "ui-ux-pro-max-skill"
    assert meta["category"] == "Design System"
    assert "Playbook komprehensif" in meta["description"]


def test_collect_repo_files(tmp_path: Path):
    """Menguji pengumpulan berkas dari struktur repositori yang di-clone."""
    (tmp_path / "SKILL.md").write_text("# Test Skill\nDeskripsi singkat.", encoding="utf-8")
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "audit.py").write_text("print('audit')", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("git config", encoding="utf-8")

    files = collect_repo_files(tmp_path)
    assert "SKILL.md" in files
    assert "scripts/audit.py" in files
    assert ".git/config" not in files


@pytest.mark.asyncio
async def test_import_skill_from_git_success(tmp_path: Path):
    """Menguji alur lengkap import_skill_from_git dengan mock clone."""
    db_file = tmp_path / "test_skills.db"
    skills_root = tmp_path / "skills_store"
    skills_hub.root_dir = skills_root

    from app.db.init_db import init_database
    await init_database(str(db_file))

    with patch("app.engine.skills.git_importer.clone_or_download_repo", new=AsyncMock(return_value=True)):
        with patch("app.engine.skills.git_importer.collect_repo_files") as mock_collect:
            mock_collect.return_value = {
                "SKILL.md": "# UI UX PRO MAX\nCategory: Design System\nDeskripsi: Standar UI/UX premium.",
                "scripts/check_contrast.py": "# Contrast Checker",
            }
            res = await import_skill_from_git(
                repo_url="https://github.com/nextlevelbuilder/ui-ux-pro-max-skill",
                custom_db_path=str(db_file),
            )
            assert res["name"] == "ui-ux-pro-max"
            assert res["category"] == "Design System"
            assert res["files_count"] == 2

            # Verifikasi pencarian FTS5
            found = await skills_hub.search_skills("contrast", custom_db_path=str(db_file))
            assert len(found) > 0
            assert found[0]["name"] == "ui-ux-pro-max"
