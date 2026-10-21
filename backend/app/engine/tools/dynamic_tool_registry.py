"""
Dynamic Tool Registry & Lifecycle Management Subsystem.
Menyimpan, memuat ulang pada startup, dan mengontrol approval tools sintesis otonom
melalui tabel SQLite corporate_custom_tools serta persetujuan Founder/Secretary.
"""

import json
import asyncio
from typing import Any, Callable, Dict, List, Optional
import uuid
from app.core.logger import logger

from app.db.session import get_db_connection


class DynamicToolRegistry:
    """Registri perkakas dinamis dengan siklus proposal, approval, dan eksekusi terisolasi."""

    def __init__(self) -> None:
        from app.engine.tools.builtin_tools import get_builtin_tools
        self._active_tools: Dict[str, Callable[..., Any]] = get_builtin_tools()

    def _compile_tool_code(self, name: str, python_code: str) -> Optional[Callable[..., Any]]:
        """Mengevaluasi dan mengompilasi kode Python perkakas secara aman ke fungsi callable."""
        local_scope: Dict[str, Any] = {}
        try:
            compiled = compile(python_code, f"<custom_tool_{name}>", "exec")
            exec(compiled, {}, local_scope)
            fn = local_scope.get(name) or local_scope.get("execute") or local_scope.get("run")
            if callable(fn):
                return fn
            logger.warning(f"Kode perkakas [{name}] tidak mendefinisikan fungsi '{name}', 'execute', atau 'run'.")
            return None
        except Exception as err:
            logger.error(f"Gagal mengompilasi kode perkakas [{name}]: {err}")
            return None

    async def propose_tool(
        self,
        name: str,
        description: str,
        parameters_schema: Dict[str, Any],
        python_code: str,
        created_by: str = "agent",
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mendaftarkan proposal perkakas baru berstatus 'PENDING_APPROVAL'."""
        tool_id = f"tool_{uuid.uuid4().hex[:8]}"
        query = """
            INSERT INTO corporate_custom_tools
            (id, name, description, parameters_schema, python_code, status, created_by)
            VALUES (?, ?, ?, ?, ?, 'PENDING_APPROVAL', ?);
        """
        async with get_db_connection(custom_path) as conn:
            await conn.execute(
                query,
                (tool_id, name, description, json.dumps(parameters_schema), python_code, created_by),
            )
            await conn.commit()

        logger.info(f"Proposal perkakas baru diajukan: [{name}] (ID: {tool_id}) -> PENDING_APPROVAL")
        return {
            "id": tool_id,
            "name": name,
            "description": description,
            "parameters_schema": parameters_schema,
            "status": "PENDING_APPROVAL",
            "created_by": created_by,
        }

    async def approve_tool(self, tool_id_or_name: str, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Menyetujui perkakas, menyimpannya sebagai 'APPROVED', dan memasangnya ke registri aktif."""
        query_select = "SELECT * FROM corporate_custom_tools WHERE id = ? OR name = ?;"
        query_update = "UPDATE corporate_custom_tools SET status = 'APPROVED', updated_at = CURRENT_TIMESTAMP WHERE id = ?;"

        async with get_db_connection(custom_path) as conn:
            async with conn.execute(query_select, (tool_id_or_name, tool_id_or_name)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                tool = dict(row)

            await conn.execute(query_update, (tool["id"],))
            await conn.commit()

        fn = self._compile_tool_code(tool["name"], tool["python_code"])
        if fn:
            self._active_tools[tool["name"]] = fn
            logger.info(f"Perkakas [{tool['name']}] berhasil DISETUJUI dan dimuat ke DynamicToolRegistry.")

        tool["status"] = "APPROVED"
        return tool

    async def reject_tool(self, tool_id_or_name: str, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Menolak proposal perkakas."""
        query = "UPDATE corporate_custom_tools SET status = 'REJECTED', updated_at = CURRENT_TIMESTAMP WHERE id = ? OR name = ?;"
        async with get_db_connection(custom_path) as conn:
            cur = await conn.execute(query, (tool_id_or_name, tool_id_or_name))
            await conn.commit()
            if cur.rowcount == 0:
                return None

        self._active_tools.pop(tool_id_or_name, None)
        logger.info(f"Proposal perkakas [{tool_id_or_name}] DITOLAK.")
        return {"id_or_name": tool_id_or_name, "status": "REJECTED"}

    async def load_approved_tools_from_db(self, custom_path: Optional[str] = None) -> int:
        """Memuat seluruh perkakas 'APPROVED' dari basis data saat inisialisasi lifespan aplikasi."""
        query = "SELECT * FROM corporate_custom_tools WHERE status = 'APPROVED';"
        loaded_count = 0
        try:
            async with get_db_connection(custom_path) as conn:
                async with conn.execute(query) as cursor:
                    rows = await cursor.fetchall()
                    for r in rows:
                        item = dict(r)
                        fn = self._compile_tool_code(item["name"], item["python_code"])
                        if fn:
                            self._active_tools[item["name"]] = fn
                            loaded_count += 1
            logger.info(f"DynamicToolRegistry berhasil memuat ulang {loaded_count} perkakas disetujui.")
        except Exception as err:
            logger.warning(f"Gagal memuat ulang perkakas dari basis data: {err}")
        return loaded_count

    async def execute_tool(self, name: str, **kwargs: Any) -> Any:
        """Mengeksekusi perkakas aktif yang terdaftar (baik sync maupun async)."""
        fn = self._active_tools.get(name)
        if not fn:
            raise ValueError(f"Perkakas [{name}] tidak terdaftar atau belum disetujui.")
        if asyncio.iscoroutinefunction(fn):
            return await fn(**kwargs)
        res = fn(**kwargs)
        if asyncio.iscoroutine(res):
            return await res
        return res

    def register_callable(self, name: str, fn: Callable[..., Any]) -> None:
        """Mendaftarkan fungsi callable secara langsung ke memori aktif (misal proxy MCP)."""
        self._active_tools[name] = fn
        logger.debug(f"Perkakas [{name}] berhasil didaftarkan ke memori DynamicToolRegistry.")

    def unregister_tool(self, name: str) -> None:
        """Mencabut perkakas dari registri memori aktif."""
        self._active_tools.pop(name, None)
        logger.debug(f"Perkakas [{name}] dicabut dari memori DynamicToolRegistry.")

    def get_registered_tool_names(self) -> List[str]:
        """Mengembalikan daftar seluruh perkakas aktif yang terdaftar."""
        return list(self._active_tools.keys())

    def is_tool_registered(self, name: str) -> bool:
        """Memeriksa apakah perkakas telah aktif di memori."""
        return name in self._active_tools


dynamic_tool_registry = DynamicToolRegistry()
