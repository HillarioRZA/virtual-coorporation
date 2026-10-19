"""Git-Style Diff Generation & Calculation Engine.

Menghitung unified diff, penambahan (+), pengurangan (-), dan statistik perubahan berkas
untuk Pull Request internal antar-karyawan AI.
"""

import difflib
from typing import Any, Dict, List, Tuple
from app.core.logger import logger


def generate_file_unified_diff(file_path: str, old_code: str, new_code: str) -> Tuple[str, int, int]:
    """Menghasilkan representasi git-style unified diff untuk satu berkas.

    Args:
        file_path: Lokasi relatif berkas yang diubah.
        old_code: Isi kode sebelum perubahan (kosong jika berkas baru).
        new_code: Isi kode setelah disintesis atau direvisi.

    Returns:
        Tuple berisi (diff_text, additions_count, deletions_count).
    """
    old_lines = old_code.splitlines(keepends=True)
    new_lines = new_code.splitlines(keepends=True)

    diff_lines = list(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="",
        )
    )

    additions = 0
    deletions = 0
    for line in diff_lines:
        if line.startswith("+") and not line.startswith("+++"):
            additions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1

    return "\n".join(diff_lines), additions, deletions


def compute_multi_file_diff(files_delta: List[Dict[str, str]]) -> Dict[str, Any]:
    """Menghitung agregasi diff untuk kumpulan berkas dalam suatu Pull Request.

    Args:
        files_delta: List dictionary berisi {'path': ..., 'old_content': ..., 'new_content': ...}.

    Returns:
        Dictionary ringkasan diff terpadu: files_summary, combined_diff, total_add, total_del.
    """
    combined_diff_parts: List[str] = []
    files_summary: List[Dict[str, Any]] = []
    total_additions = 0
    total_deletions = 0

    for item in files_delta:
        path = item.get("path", "unknown")
        old_c = item.get("old_content", "")
        new_c = item.get("new_content", "")

        diff_str, add_cnt, del_cnt = generate_file_unified_diff(path, old_c, new_c)
        total_additions += add_cnt
        total_deletions += del_cnt

        if diff_str:
            combined_diff_parts.append(diff_str)

        files_summary.append({
            "path": path,
            "status": "ADDED" if not old_c else ("DELETED" if not new_c else "MODIFIED"),
            "additions": add_cnt,
            "deletions": del_cnt,
        })

    logger.debug(f"Kalkulasi diff selesai: {len(files_summary)} berkas (+{total_additions}, -{total_deletions}).")
    return {
        "files": files_summary,
        "unified_diff": "\n\n".join(combined_diff_parts),
        "total_additions": total_additions,
        "total_deletions": total_deletions,
    }


def validate_and_preview_patch(file_path: str, old_code: str, patch_payload: str) -> Dict[str, Any]:
    """Menerapkan patch, memvalidasi sintaks AST, dan menghitung unified diff tanpa mengubah disk.

    Args:
        file_path: Path berkas target (misal: 'main.py').
        old_code: Isi kode sebelum patch.
        patch_payload: String blok TARGET/REPLACEMENT.

    Returns:
        Dict berisi 'new_code', 'unified_diff', 'additions', 'deletions'.
    """
    from app.engine.tools.ast_patcher import apply_search_replace_blocks, validate_python_syntax

    new_code = apply_search_replace_blocks(old_code, patch_payload)
    if file_path.endswith(".py"):
        validate_python_syntax(new_code, file_path)

    diff_str, additions, deletions = generate_file_unified_diff(file_path, old_code, new_code)
    return {
        "file_path": file_path,
        "new_code": new_code,
        "unified_diff": diff_str,
        "additions": additions,
        "deletions": deletions,
    }

