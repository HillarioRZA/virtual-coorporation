"""
Built-in Standard Tools Registry Module.
Mendefinisikan implementasi perkakas bawaan sistem yang didaftarkan
ke dalam DynamicToolRegistry tanpa percabangan if-elif statis.
"""

from types import SimpleNamespace
from typing import Any, Callable, Dict
from app.core.logger import logger

from app.engine.tools.db_inspector import db_inspector
from app.engine.tools.contract_validator import contract_validator
from app.engine.tools.diff_digest import diff_digest
from app.engine.tools.code_search import code_searcher
from app.engine.tools.tool_synthesizer import tool_synthesizer
from app.engine.tools.test_suite_locker import lock_test_suite
from app.engine.tools.code_bundle_writer import write_backend_files, write_frontend_files
from app.engine.tools.file_lock_manager import file_lock_manager


def tool_inspect_db_schema(project_id: str, **parameters: Any) -> Dict[str, Any]:
    """Menginspeksi skema tabel basis data proyek."""
    tbl = parameters.get("table_name")
    if tbl:
        return db_inspector.inspect_table_schema(project_id, tbl)
    return {"tables": db_inspector.list_tables(project_id)}


def tool_validate_api_contract(project_id: str, **parameters: Any) -> Dict[str, Any]:
    """Memvalidasi kode terhadap spesifikasi OpenAPI ventura."""
    code = parameters.get("code", "")
    return contract_validator.validate_code_against_spec(project_id, code)


async def tool_git_diff_summary(project_id: str, **parameters: Any) -> Dict[str, Any]:
    """Mengambil rangkuman diff git proyek."""
    base_ref = parameters.get("base_ref", "HEAD~1")
    return await diff_digest.get_diff_summary(project_id, base_ref=base_ref)


def tool_search_codebase(project_id: str, **parameters: Any) -> Dict[str, Any]:
    """Mencari simbol atau teks pada basis kode proyek."""
    query = parameters.get("query", "")
    is_sym = parameters.get("is_symbol_only", False)
    return code_searcher.search_codebase(project_id, query, is_symbol_only=is_sym)


async def tool_runtime_tool_builder(project_id: str, **parameters: Any) -> Dict[str, Any]:
    """Menyintesis atau mengeksekusi perkakas ephemeral runtime."""
    action = parameters.get("action", "execute")
    script_name = parameters.get("script_name", "tool.py")
    if action == "synthesize":
        code = parameters.get("code", "")
        return tool_synthesizer.synthesize_tool_script(project_id, script_name, code)
    return await tool_synthesizer.execute_ephemeral_tool(project_id, script_name)


def tool_lock_test_suite(project_id: str, **parameters: Any) -> Dict[str, Any]:
    """Mengunci test suite menjadi berkas read-only."""
    fname = parameters.get("test_filename", "test_suite.py")
    content = parameters.get("test_content", "")
    return lock_test_suite(project_id, fname, content)


async def tool_write_code_bundle(project_id: str, **parameters: Any) -> Dict[str, Any]:
    """Menulis bundel kode frontend atau backend dengan proteksi file lock mutex."""
    bundle_type = parameters.get("bundle_type", "backend")
    code_map = parameters.get("code_map", {})
    env = SimpleNamespace(**code_map)

    async with file_lock_manager.acquire(project_id, f"bundle_{bundle_type}"):
        if bundle_type == "frontend":
            out_path = write_frontend_files(project_id, env)
        else:
            out_path = write_backend_files(project_id, env)
    return {"status": "SUCCESS", "output_dir": str(out_path)}


async def tool_run_lsp_diagnostics(project_id: str, **parameters: Any) -> Dict[str, Any]:
    """Mengecek error tipe fatal (Pyright / TypeScript) pada berkas tertentu."""
    from app.engine.lsp.lsp_service import lsp_service
    file_path = parameters.get("file_path", "")
    if not file_path:
        return {"error": "Parameter 'file_path' wajib diisi."}
    diags = await lsp_service.get_diagnostics(project_id, file_path)
    return {
        "status": "SUCCESS",
        "file_path": file_path,
        "errors_count": len(diags),
        "diagnostics": diags,
    }


def get_builtin_tools() -> Dict[str, Callable[..., Any]]:
    """Mengembalikan peta perkakas standar bawaan sistem."""
    from app.engine.skills.skill_agent_tools import tool_consult_skill_library, tool_read_skill_detail
    return {
        "inspect_db_schema": tool_inspect_db_schema,
        "validate_api_contract": tool_validate_api_contract,
        "git_diff_summary": tool_git_diff_summary,
        "search_codebase": tool_search_codebase,
        "runtime_tool_builder": tool_runtime_tool_builder,
        "lock_test_suite": tool_lock_test_suite,
        "write_code_bundle": tool_write_code_bundle,
        "consult_skill_library": tool_consult_skill_library,
        "read_skill_detail": tool_read_skill_detail,
        "run_lsp_diagnostics": tool_run_lsp_diagnostics,
    }
