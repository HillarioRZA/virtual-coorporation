"""State-First Context Distillation & Handoff Rescue Engine.

Menyediakan utilitas ekstraksi state cerdas, pembersihan reasoning traces (<think>),
ekstraksi symbol table berbasis AST, dan penyambungan diferensial berkas
untuk mencegah pembengkakan token dan lost context saat failover model.
"""

import ast
import json
import re
from typing import Any, Dict, List, Optional
from app.core.logger import logger


def strip_reasoning_traces(content: Any) -> Any:
    """Membersihkan tag penalaran model (<think>...</think>) dari teks atau list pesan.

    Args:
        content: String respons LLM atau List dictionary pesan obrolan.

    Returns:
        String atau List pesan yang sudah bersih dari tag internal thinking.
    """
    if isinstance(content, list):
        cleaned_list = []
        for msg in content:
            if isinstance(msg, dict) and "content" in msg and isinstance(msg["content"], str):
                cleaned_msg = dict(msg)
                cleaned_msg["content"] = strip_reasoning_traces(msg["content"])
                cleaned_list.append(cleaned_msg)
            else:
                cleaned_list.append(msg)
        return cleaned_list

    if not isinstance(content, str) or not content:
        return content or ""

    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", content, flags=re.IGNORECASE)
    cleaned = re.sub(r"\[THINKING\][\s\S]*?\[/THINKING\]", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def export_ast_symbol_table(code: str) -> str:
    """Mengekstrak tanda tangan fungsi dan kelas dari kode Python menggunakan AST.

    Menghasilkan ringkasan ringkas (< 50-100 token) sehingga model cadangan mengetahui
    simbol, kelas, dan method yang dapat digunakan tanpa membaca seluruh berkas.
    """
    if not code or not code.strip():
        return ""
    signatures: List[str] = []
    try:
        tree = ast.parse(code)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                args = [a.arg for a in node.args.args]
                ret_ann = ast.unparse(node.returns) if node.returns else "Any"
                signatures.append(f"{prefix} {node.name}({', '.join(args)}) -> {ret_ann}: ...")
            elif isinstance(node, ast.ClassDef):
                signatures.append(f"class {node.name}: ...")
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        pfx = "async def" if isinstance(sub, ast.AsyncFunctionDef) else "def"
                        args = [a.arg for a in sub.args.args]
                        ret_ann = ast.unparse(sub.returns) if sub.returns else "Any"
                        signatures.append(f"    {pfx} {sub.name}({', '.join(args)}) -> {ret_ann}: ...")
        return "\n".join(signatures)
    except SyntaxError as err:
        logger.warning(f"Gagal mem-parse AST symbol table (sintaks parsial): {err}")
        return ""


def build_state_handoff_payload(
    task_description: str,
    completed_files: Dict[str, str],
    target_pending_file: str,
    contract_schema: Optional[str] = None,
    architectural_constraints: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Menyusun payload State-First Handoff ramping untuk model cadangan.

    Menggantikan pengoperan riwayat obrolan mentah 40k+ token menjadi ringkasan
    state terstruktur (~2.5k token) dengan retensi konteks maksimal.

    Args:
        task_description: Deskripsi tugas peran saat ini.
        completed_files: Dict berisi nama file dan kode sumbernya.
        target_pending_file: Nama berkas yang sedang harus disintesis.
        contract_schema: Skema kontrak OpenAPI atau Pydantic SSOT.
        architectural_constraints: Batasan arsitektur penting.

    Returns:
        Dictionary JSON handoff yang siap disuntikkan ke prompt model cadangan.
    """
    symbol_tables: Dict[str, str] = {}
    for filename, content in completed_files.items():
        if filename.endswith(".py"):
            symbols = export_ast_symbol_table(content)
            if symbols:
                symbol_tables[filename] = symbols

    handoff = {
        "handoff_mode": "STATE_FIRST_RESILIENT_FAILOVER",
        "current_task": task_description,
        "target_pending_file": target_pending_file,
        "completed_artifacts_summary": list(completed_files.keys()),
        "available_symbol_tables": symbol_tables,
        "contract_reference": contract_schema or "Standard Contract",
        "architectural_constraints": architectural_constraints or [
            "Strict Single Responsibility Principle",
            "Full type annotations on all functions",
            "Zero print statements, use configured logger",
        ],
    }
    return handoff


def prepare_differential_continuation(
    file_path: str,
    partial_code: str,
    target_endpoints: Optional[List[str]] = None,
) -> str:
    """Menyusun instruksi penyambungan berkas diferensial.

    Mencegah model cadangan menulis ulang seluruh berkas dari baris pertama
    ketika berkas sebelumnya terputus di tengah jalan.

    Args:
        file_path: Path berkas target.
        partial_code: Potongan kode yang sudah sempat ditulis.
        target_endpoints: Daftar endpoint yang belum selesai.

    Returns:
        Instruksi teks penyambungan diferensial.
    """
    lines = partial_code.splitlines()
    line_count = len(lines)
    tail_snippet = "\n".join(lines[-15:]) if line_count > 15 else partial_code

    endpoints_note = f" (target: {', '.join(target_endpoints)})" if target_endpoints else ""
    instruction = (
        f"Berkas '{file_path}' telah selesai secara parsial hingga baris {line_count}.\n"
        f"Berikut adalah cuplikan 15 baris terakhir sebagai jangkar konteks:\n"
        f"```python\n{tail_snippet}\n```\n"
        f"Lanjutkan penulisan implementasi berikutnya{endpoints_note} mulai dari baris {line_count + 1}.\n"
        f"DILARANG mengulang import atau fungsi yang sudah dideklarasikan sebelumnya."
    )
    return instruction
