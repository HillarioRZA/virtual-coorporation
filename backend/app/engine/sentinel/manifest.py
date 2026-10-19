"""
Lean Tool Manifest Generator untuk CoV Gatekeeper.
Menghasilkan ringkasan token-efisien (~150-200 token) berdasarkan tahap alur kerja aktif.
"""

from typing import Dict, List, Union

LEAN_TOOL_DEFINITIONS: Dict[str, Dict[str, Union[str, Dict[str, str]]]] = {
    "inspect_db_schema": {
        "desc": "Inspeksi daftar tabel atau skema detail tabel SQLite proyek.",
        "params": {"table_name": "string (opsional, kosongkan untuk daftar semua tabel)"},
    },
    "validate_api_contract": {
        "desc": "Validasi sintaksis kode implementasi terhadap kontrak spesifikasi OpenAPI.",
        "params": {"code": "string (kode sumber endpoint yang akan diuji)"},
    },
    "git_diff_summary": {
        "desc": "Ringkasan perbedaan baris kode pada repositori git lokal.",
        "params": {"base_ref": "string (opsional, default 'HEAD~1')"},
    },
    "search_codebase": {
        "desc": "Pencarian teks atau simbol fungsi/class pada seluruh berkas kode proyek.",
        "params": {
            "query": "string (kata kunci atau nama simbol)",
            "is_symbol_only": "boolean (opsional, True untuk filter simbol AST)",
        },
    },
    "runtime_tool_builder": {
        "desc": "Sintesis dan eksekusi skrip python utilitas pada sandbox terisolasi.",
        "params": {
            "action": "'synthesize' | 'execute'",
            "script_name": "string (nama berkas skrip .py)",
            "code": "string (diperlukan jika action='synthesize')",
        },
    },
    "lock_test_suite": {
        "desc": "Menyimpan skenario uji TDD, mengunci file (chmod 444), dan mendaftarkan read-only guardrail.",
        "params": {
            "test_filename": "string (misal: 'test_api.py')",
            "test_content": "string (blok kode pengujian Pytest/Jest)",
        },
    },
    "write_code_bundle": {
        "desc": "Menulis kode implementasi frontend/backend dengan proteksi read-only.",
        "params": {
            "bundle_type": "'frontend' | 'backend'",
            "code_map": "object (kamus berkas dan isi kodenya)",
        },
    },
}

# Pemetaan perkakas berdasarkan nomor atau nama tahapan workflow
STAGE_TOOLS_MAPPING: Dict[str, List[str]] = {
    "ideation": [],
    "brief": [],
    "strategy": [],
    "prd": ["validate_api_contract", "search_codebase"],
    "architecture": ["inspect_db_schema", "validate_api_contract", "search_codebase"],
    "development": [
        "inspect_db_schema",
        "validate_api_contract",
        "git_diff_summary",
        "search_codebase",
        "runtime_tool_builder",
        "write_code_bundle",
    ],
    "qa": ["validate_api_contract", "git_diff_summary", "search_codebase", "lock_test_suite"],
    "deployment": ["git_diff_summary", "runtime_tool_builder"],
}


def get_stage_tool_manifest(stage: Union[str, int]) -> str:
    """Menghasilkan representasi teks ringkas dari perkakas yang diizinkan untuk tahap tertentu.

    Args:
        stage: Nomor tahap (1-7) atau nama slug tahap (misal 'development').

    Returns:
        String ringkas deskripsi perkakas untuk diinjeksi ke prompt CoV.
    """
    stage_key = str(stage).lower()
    # Konversi nomor tahap ke nama kategori
    num_to_stage = {
        "1": "ideation",
        "2": "prd",
        "3": "architecture",
        "4": "development",
        "5": "development",
        "6": "qa",
        "7": "deployment",
    }
    canonical_stage = num_to_stage.get(stage_key, stage_key)
    allowed_tools = STAGE_TOOLS_MAPPING.get(canonical_stage, list(LEAN_TOOL_DEFINITIONS.keys()))

    if not allowed_tools:
        return "TIDAK ADA PERKAKAS YANG DIPERLUKAN (Hanya teks respons murni diperbolehkan)."

    lines: List[str] = []
    for tool_name in allowed_tools:
        info = LEAN_TOOL_DEFINITIONS.get(tool_name)
        if not info:
            continue
        params_desc = ", ".join([f"{k}: {v}" for k, v in info["params"].items()])  # type: ignore
        lines.append(f"- {tool_name}: {info['desc']} | Params: {{{params_desc}}}")

    return "\n".join(lines)
