"""Semantic AST Patch Engine.

Mem-parsing blok TARGET/REPLACEMENT, memvalidasi sintaks AST Python sebelum komit,
dan menerapkan modifikasi berkas secara atomik untuk menghemat token output.
"""

import ast
from pathlib import Path
import re
import tempfile
from typing import List, Tuple
from app.core.logger import logger

_BLOCK_PATTERN = re.compile(
    r"^<{4,7}\s*(?:TARGET|SEARCH)\s*\r?\n([\s\S]*?)\r?\n={4,7}\s*\r?\n([\s\S]*?)\r?\n>{4,7}(?:\s*REPLACEMENT)?\s*$",
    re.MULTILINE,
)


def parse_patch_blocks(patch_payload: str) -> List[Tuple[str, str]]:
    """Mengekstrak pasangan (target, replacement) dari payload patch."""
    matches = _BLOCK_PATTERN.findall(patch_payload)
    if not matches:
        # Fallback jika marker tidak memiliki newline pembuka/penutup yang ketat
        alt_pattern = re.compile(
            r"<{4,7}\s*(?:TARGET|SEARCH)[^\n]*\n([\s\S]*?)\n={4,7}[^\n]*\n([\s\S]*?)\n>{4,7}[^\n]*",
            re.MULTILINE,
        )
        matches = alt_pattern.findall(patch_payload)
    return matches


def apply_search_replace_blocks(original_content: str, patch_payload: str) -> str:
    """Menerapkan seluruh blok TARGET -> REPLACEMENT pada isi berkas asli.

    Args:
        original_content: String isi berkas saat ini.
        patch_payload: String payload patch berisi satu atau lebih blok TARGET/REPLACEMENT.

    Returns:
        String isi berkas baru setelah seluruh blok diaplikasikan.

    Raises:
        ValueError: Jika blok patch kosong atau target blok tidak ditemukan dalam berkas.
    """
    blocks = parse_patch_blocks(patch_payload)
    if not blocks:
        raise ValueError("Format patch tidak valid: Tidak ditemukan blok <<<< TARGET ... ==== ... >>>> REPLACEMENT.")

    updated_content = original_content
    for idx, (target_block, replacement_block) in enumerate(blocks, start=1):
        if target_block not in updated_content:
            preview = target_block[:60].replace("\n", "\\n")
            raise ValueError(f"Blok #{idx} gagal diaplikasikan: TARGET tidak ditemukan dalam kode ({preview}...)")
        updated_content = updated_content.replace(target_block, replacement_block, 1)

    return updated_content


def validate_python_syntax(code: str, file_path: str = "") -> bool:
    """Memvalidasi sintaks kode Python menggunakan ast.parse.

    Args:
        code: String kode sumber.
        file_path: Path berkas opsional untuk pengecekan ekstensi.

    Returns:
        True jika kode valid.

    Raises:
        SyntaxError: Jika kode memiliki kesalahan sintaksis Python.
    """
    if file_path and not file_path.endswith(".py"):
        return True

    try:
        ast.parse(code)
        return True
    except SyntaxError as err:
        logger.error(f"Validasi AST gagal pada baris {err.lineno}: {err.msg}")
        raise SyntaxError(f"AST Validation Error di baris {err.lineno}: {err.msg}") from err


def apply_ast_patch_to_file(file_path: str, patch_payload: str) -> str:
    """Menerapkan patch secara atomik ke disk setelah validasi sintaks.

    Args:
        file_path: Lokasi berkas target di disk.
        patch_payload: String payload blok patch.

    Returns:
        String isi berkas baru yang telah tersimpan.

    Raises:
        FileNotFoundError: Jika berkas target tidak ada.
        ValueError: Jika target blok tidak cocok.
        SyntaxError: Jika kode Python baru tidak valid.
        IOError: Jika operasi baca/tulis disk gagal.
    """
    path_obj = Path(file_path).resolve()
    if not path_obj.exists() or not path_obj.is_file():
        raise FileNotFoundError(f"Berkas target tidak ditemukan: {file_path}")

    try:
        original_content = path_obj.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as err:
        logger.error(f"Gagal membaca berkas {file_path}: {err}")
        raise IOError(f"Gagal membaca berkas: {err}") from err

    new_content = apply_search_replace_blocks(original_content, patch_payload)
    if file_path.endswith(".py"):
        validate_python_syntax(new_content, file_path)

    # Simpan secara atomik menggunakan berkas temporer di direktori yang sama
    parent_dir = path_obj.parent
    try:
        with tempfile.NamedTemporaryFile("w", dir=parent_dir, delete=False, encoding="utf-8") as tmp:
            tmp.write(new_content)
            tmp_path = Path(tmp.name)
        tmp_path.replace(path_obj)
        logger.info(f"Patch AST berhasil diaplikasikan secara atomik ke {path_obj.name}")
        return new_content
    except OSError as err:
        logger.error(f"Gagal menuliskan patch ke disk ({file_path}): {err}")
        raise IOError(f"Gagal menulis berkas: {err}") from err
