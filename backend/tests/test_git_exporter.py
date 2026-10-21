"""
Unit Tests untuk GitExporter.
Menguji penegakan auto-.gitignore dan siklus checkpoint Git lokal.
"""

from pathlib import Path
import pytest
from app.engine.tools.git_exporter import GitExporter


def test_ensure_gitignore_creation(tmp_path: Path) -> None:
    """Menguji pembuatan file .gitignore baru dengan entri default."""
    exporter = GitExporter()
    exporter.ensure_gitignore(tmp_path)

    gi_file = tmp_path / ".gitignore"
    assert gi_file.exists()
    content = gi_file.read_text(encoding="utf-8")
    assert "node_modules/" in content
    assert ".next/" in content
    assert "__pycache__/" in content
    assert ".env" in content


def test_ensure_gitignore_appends_missing(tmp_path: Path) -> None:
    """Menguji penambahan entri penting jika .gitignore sudah ada tapi belum lengkap."""
    exporter = GitExporter()
    gi_file = tmp_path / ".gitignore"
    gi_file.write_text("node_modules/\n", encoding="utf-8")

    exporter.ensure_gitignore(tmp_path)
    updated = gi_file.read_text(encoding="utf-8")
    assert ".next/" in updated
    assert "__pycache__/" in updated
    assert ".env" in updated


@pytest.mark.asyncio
async def test_export_project_checkpoint_skipped_if_nonexistent() -> None:
    """Menguji bahwa project ID yang tidak memiliki folder disk dilewati dengan aman."""
    exporter = GitExporter()
    res = await exporter.export_project_checkpoint("non_existent_project_99999")
    assert res["status"] == "SKIPPED"
