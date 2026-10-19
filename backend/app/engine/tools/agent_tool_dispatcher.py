"""
Autonomous Agent Tool Dispatcher & ReAct Execution Engine.
Mengeksekusi pemanggilan perkakas oleh agen secara aman dengan batas keras MAX_REACT_STEPS = 3.
"""

import json
import re
from typing import Any, Dict, Optional

from app.core.logger import logger
from app.engine.tools.db_inspector import db_inspector
from app.engine.tools.contract_validator import contract_validator
from app.engine.tools.diff_digest import diff_digest
from app.engine.tools.code_search import code_searcher
from app.engine.tools.tool_synthesizer import tool_synthesizer

MAX_REACT_STEPS = 3


class AgentToolDispatcher:
    """Orkestrator pemanggilan perkakas interaktif multi-turn bagi agen."""

    def __init__(self, max_steps: int = MAX_REACT_STEPS) -> None:
        """Inisialisasi dispatcher dengan batas langkah keras."""
        self.max_steps = max_steps

    def parse_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """Mengekstrak permintaan pemanggilan perkakas dari respons agen."""
        # Cari blok JSON {"tool": ..., "parameters": ...}
        match = re.search(r'\{\s*"tool"\s*:\s*"([^"]+)"\s*,\s*"parameters"\s*:\s*(\{[^}]*\})\s*\}', text)
        if match:
            tool_name = match.group(1).strip()
            try:
                params = json.loads(match.group(2))
                return {"tool": tool_name, "parameters": params}
            except json.JSONDecodeError:
                pass

        # Alternatif: blok ```json { "tool": ... } ```
        fence_match = re.search(r'```(?:json)?\s*(\{.*?"tool"\s*:.*?\})\s*```', text, re.DOTALL)
        if fence_match:
            try:
                data = json.loads(fence_match.group(1))
                if "tool" in data:
                    return {"tool": data["tool"], "parameters": data.get("parameters", {})}
            except json.JSONDecodeError:
                pass
        return None

    async def execute_tool(
        self,
        project_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Mengeksekusi perkakas sasaran secara aman dan mengembalikan observasi."""
        logger.info(f"AgentToolDispatcher: Mengeksekusi [{tool_name}] untuk proyek [{project_id}]...")
        try:
            if tool_name == "inspect_db_schema":
                tbl = parameters.get("table_name")
                if tbl:
                    return db_inspector.inspect_table_schema(project_id, tbl)
                return {"tables": db_inspector.list_tables(project_id)}

            elif tool_name == "validate_api_contract":
                code = parameters.get("code", "")
                return contract_validator.validate_code_against_spec(project_id, code)

            elif tool_name == "git_diff_summary":
                base_ref = parameters.get("base_ref", "HEAD~1")
                return await diff_digest.get_diff_summary(project_id, base_ref=base_ref)

            elif tool_name == "search_codebase":
                query = parameters.get("query", "")
                is_sym = parameters.get("is_symbol_only", False)
                return code_searcher.search_codebase(project_id, query, is_symbol_only=is_sym)

            elif tool_name == "runtime_tool_builder":
                action = parameters.get("action", "execute")
                script_name = parameters.get("script_name", "tool.py")
                if action == "synthesize":
                    code = parameters.get("code", "")
                    return tool_synthesizer.synthesize_tool_script(project_id, script_name, code)
                return await tool_synthesizer.execute_ephemeral_tool(project_id, script_name)

            elif tool_name == "lock_test_suite":
                from app.engine.tools.test_suite_locker import lock_test_suite
                fname = parameters.get("test_filename", "test_suite.py")
                content = parameters.get("test_content", "")
                return lock_test_suite(project_id, fname, content)

            elif tool_name == "write_code_bundle":
                from app.engine.tools.code_bundle_writer import write_backend_files, write_frontend_files
                from types import SimpleNamespace
                bundle_type = parameters.get("bundle_type", "backend")
                code_map = parameters.get("code_map", {})
                env = SimpleNamespace(**code_map)
                out_path = write_frontend_files(project_id, env) if bundle_type == "frontend" else write_backend_files(project_id, env)
                return {"status": "SUCCESS", "output_dir": str(out_path)}

            else:
                return {"error": f"Perkakas [{tool_name}] tidak dikenali atau belum terdaftar."}
        except Exception as err:
            logger.error(f"Kesalahan eksekusi tool [{tool_name}]: {err}")
            return {"error": str(err)}


agent_tool_dispatcher = AgentToolDispatcher()
