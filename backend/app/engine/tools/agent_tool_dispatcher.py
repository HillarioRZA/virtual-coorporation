"""
Autonomous Agent Tool Dispatcher & ReAct Execution Engine.
Mengeksekusi pemanggilan perkakas oleh agen secara aman dengan batas keras MAX_REACT_STEPS = 3.
"""

import json
import re
from typing import Any, Dict, Optional

from app.core.logger import logger
from app.engine.tools.dynamic_tool_registry import dynamic_tool_registry

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
            if dynamic_tool_registry.is_tool_registered(tool_name):
                res = await dynamic_tool_registry.execute_tool(tool_name, project_id=project_id, **parameters)
                return res if isinstance(res, dict) else {"result": res}
            return {"error": f"Perkakas [{tool_name}] tidak dikenali atau belum terdaftar."}
        except Exception as err:
            logger.error(f"Kesalahan eksekusi tool [{tool_name}]: {err}")
            return {"error": str(err)}


agent_tool_dispatcher = AgentToolDispatcher()
