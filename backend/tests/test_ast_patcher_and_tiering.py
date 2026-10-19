"""Unit tests for Pillar 1 (AST Patcher & Diff Engine) and Pillar 4 (Model Router Tiering)."""

from pathlib import Path
import tempfile
from typing import Any, Dict, List
import pytest

from app.engine.tools.ast_patcher import (
    apply_ast_patch_to_file,
    apply_search_replace_blocks,
    validate_python_syntax,
)
from app.engine.quality.diff_engine import validate_and_preview_patch
from app.engine.runtime.model_router import SovereignModelRouter


def test_apply_search_replace_single_block() -> None:
    """Menguji penggantian blok kode tunggal dengan format TARGET / REPLACEMENT."""
    original = "def hello():\n    return 'old'\n"
    patch = "<<<< TARGET\n    return 'old'\n====\n    return 'new'\n>>>> REPLACEMENT\n"
    res = apply_search_replace_blocks(original, patch)
    assert res == "def hello():\n    return 'new'\n"


def test_apply_search_replace_multi_block() -> None:
    """Menguji penggantian beberapa blok non-kontigu dalam satu payload patch."""
    original = "x = 1\ny = 2\nz = 3\n"
    patch = (
        "<<<< TARGET\nx = 1\n====\nx = 10\n>>>> REPLACEMENT\n\n"
        "<<<< TARGET\nz = 3\n====\nz = 30\n>>>> REPLACEMENT\n"
    )
    res = apply_search_replace_blocks(original, patch)
    assert res == "x = 10\ny = 2\nz = 30\n"


def test_apply_search_replace_missing_target_raises_value_error() -> None:
    """Memastikan ValueError dilempar jika target block tidak ditemukan dalam kode."""
    original = "def foo(): pass\n"
    patch = "<<<< TARGET\ndef bar(): pass\n====\ndef baz(): pass\n>>>> REPLACEMENT\n"
    with pytest.raises(ValueError, match="TARGET tidak ditemukan"):
        apply_search_replace_blocks(original, patch)


def test_validate_python_syntax_valid() -> None:
    """Memastikan kode Python valid mengembalikan True."""
    code = "def valid_func(a: int) -> int:\n    return a * 2\n"
    assert validate_python_syntax(code, "test.py") is True


def test_validate_python_syntax_invalid_raises_syntax_error() -> None:
    """Memastikan kode Python dengan sintaks rusak melempar SyntaxError."""
    broken_code = "def broken(a: int\n    return a\n"
    with pytest.raises(SyntaxError):
        validate_python_syntax(broken_code, "test.py")


def test_apply_ast_patch_to_file_atomic(tmp_path: Path) -> None:
    """Menguji penulisan patch secara atomik ke disk."""
    py_file = tmp_path / "sample.py"
    py_file.write_text("def run():\n    val = 1\n    return val\n", encoding="utf-8")

    patch = "<<<< TARGET\n    val = 1\n====\n    val = 99\n>>>> REPLACEMENT\n"
    new_content = apply_ast_patch_to_file(str(py_file), patch)
    assert "val = 99" in new_content
    assert "val = 99" in py_file.read_text(encoding="utf-8")


def test_apply_ast_patch_to_file_prevents_corrupt_python(tmp_path: Path) -> None:
    """Memastikan file di disk tidak rusak jika patch menghasilkan syntax error."""
    py_file = tmp_path / "safe.py"
    original_code = "def safe():\n    return 42\n"
    py_file.write_text(original_code, encoding="utf-8")

    bad_patch = "<<<< TARGET\n    return 42\n====\n    return (broken syntax\n>>>> REPLACEMENT\n"
    with pytest.raises(SyntaxError):
        apply_ast_patch_to_file(str(py_file), bad_patch)

    # File asli harus tetap utuh
    assert py_file.read_text(encoding="utf-8") == original_code


def test_validate_and_preview_patch() -> None:
    """Menguji kalkulasi preview diff terpadu tanpa menulis ke disk."""
    old_code = "name = 'Alpha'\nage = 20\n"
    patch = "<<<< TARGET\nage = 20\n====\nage = 25\n>>>> REPLACEMENT\n"
    preview = validate_and_preview_patch("config.py", old_code, patch)
    assert preview["file_path"] == "config.py"
    assert "age = 25" in preview["new_code"]
    assert preview["additions"] == 1
    assert preview["deletions"] == 1
    assert "-age = 20" in preview["unified_diff"]
    assert "+age = 25" in preview["unified_diff"]


@pytest.mark.asyncio
async def test_model_router_tier_escalation_turn_logic() -> None:
    """Menguji logika eskalasi dinamis kandidat model berdasarkan turn_count."""
    router = SovereignModelRouter()
    fallback_chain = [
        {"provider": "test_provider", "model": "workhorse-v1", "is_enabled": True, "tier": 2},
        {"provider": "test_provider", "model": "escalated-v2", "is_enabled": True, "tier": 1},
    ]

    # Mock client complete agar tidak melakukan request jaringan
    class MockClient:
        async def complete(self, **kwargs: Any) -> str:
            return f"Answer from {kwargs.get('model')}"

    router.client = MockClient()  # type: ignore

    # Pada Turn 1: model utama diprioritaskan
    out1, ledger1 = await router.execute_routed_completion(
        prompt="Halo",
        primary_provider="test_provider",
        primary_model="primary-daily",
        fallback_chain=fallback_chain,
        turn_count=1,
    )
    assert "primary-daily" in out1
    assert ledger1["status"] == "SUCCESS"

    # Pada Turn 2 (Rework / Eskalasi): kandidat Tier 1 diprioritaskan terlebih dahulu
    out2, ledger2 = await router.execute_routed_completion(
        prompt="Perbaiki kode",
        primary_provider="test_provider",
        primary_model="primary-daily",
        fallback_chain=fallback_chain,
        turn_count=2,
    )
    assert "escalated-v2" in out2
    assert ledger2["status"] == "SUCCESS"

