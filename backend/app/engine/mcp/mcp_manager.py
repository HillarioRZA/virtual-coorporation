"""Manajer Server Model Context Protocol (MCP) & Penegak Guardrail Ketergantungan Izin."""

import json
import re
import uuid
from typing import Any, Dict, List, Optional

from app.core.logger import logger
from app.core.security import SecretVaultManager
from app.db.session import get_db_connection
from app.engine.mcp.mcp_client_bridge import mcp_client_bridge
from app.engine.tools.dynamic_tool_registry import dynamic_tool_registry


class MCPManager:
    """Orkestrator Server MCP dengan penyimpanan SQLite dan perlindungan guardrail referensial."""

    def __init__(self, vault: Optional[SecretVaultManager] = None) -> None:
        self.vault = vault or SecretVaultManager()

    async def discover_mcp_tools(
        self, command_or_url: str, transport: str = "stdio", env_vars: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """Melakukan dry-run discovery tools tanpa menyimpan konfigurasi ke basis data."""
        return await mcp_client_bridge.run_discovery(command_or_url, transport, env_vars)

    async def register_mcp_server(
        self,
        name: str,
        command_or_url: str,
        transport: str = "stdio",
        env_vars: Optional[Dict[str, str]] = None,
        custom_db_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mendaftarkan server MCP baru, menyimpan manifest tools, dan mendaftarkan proxy ke registry."""
        cleaned = re.sub(r"[^a-zA-Z0-9_-]", "", name.strip().lower())
        if not cleaned:
            raise ValueError("Nama server MCP tidak valid.")

        tools = await self.discover_mcp_tools(command_or_url, transport, env_vars)
        encrypted_env = self.vault.encrypt(json.dumps(env_vars or {}))
        server_id = f"mcp_{uuid.uuid4().hex[:8]}"

        query = "INSERT INTO corporate_mcp_servers (id, name, transport, command_or_url, env_vars_encrypted, status, tools_manifest) VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?);"
        async with get_db_connection(custom_db_path) as conn:
            await conn.execute(query, (server_id, cleaned, transport, command_or_url, encrypted_env, json.dumps(tools)))
            await conn.commit()

        self._register_server_tools_in_memory(server_id, cleaned, tools, custom_db_path)
        logger.info(f"Server MCP [{cleaned}] berhasil didaftarkan dengan {len(tools)} perkakas.")
        return {"id": server_id, "name": cleaned, "tools_count": len(tools), "tools": tools}

    def _register_server_tools_in_memory(
        self, server_id: str, server_name: str, tools: List[Dict[str, Any]], custom_db_path: Optional[str] = None
    ) -> None:
        """Membuat fungsi proxy eksekusi on-demand untuk setiap tool MCP di memori aktif."""
        for t in tools:
            raw_name = t.get("name", "tool")
            namespaced = f"mcp:{server_name}:{raw_name}"

            async def _make_proxy(t_name=raw_name, s_id=server_id, **kwargs):
                return await self.execute_mcp_tool(s_id, t_name, kwargs, custom_db_path=custom_db_path)

            dynamic_tool_registry.register_callable(namespaced, _make_proxy)

    async def rehydrate_active_servers(self, custom_db_path: Optional[str] = None) -> int:
        """Merehidrasi seluruh proxy tool server aktif ke DynamicToolRegistry saat startup server."""
        rehydrated = 0
        try:
            async with get_db_connection(custom_db_path) as conn:
                async with conn.execute("SELECT * FROM corporate_mcp_servers WHERE status = 'ACTIVE';") as cur:
                    for r in await cur.fetchall():
                        item = dict(r)
                        tools = json.loads(item["tools_manifest"] or "[]")
                        self._register_server_tools_in_memory(item["id"], item["name"], tools, custom_db_path)
                        rehydrated += len(tools)
            logger.info(f"MCPManager: {rehydrated} perkakas MCP berhasil direhidrasi ke memori.")
        except Exception as err:
            logger.warning(f"Gagal merehidrasi server MCP dari basis data: {err}")
        return rehydrated

    async def delete_mcp_server(
        self, server_id: str, force: bool = False, custom_db_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Menghapus server MCP dengan pemeriksaan guardrail terhadap role agen yang masih menggunakannya."""
        async with get_db_connection(custom_db_path) as conn:
            async with conn.execute("SELECT * FROM corporate_mcp_servers WHERE id = ?;", (server_id,)) as cur:
                row = await cur.fetchone()
                if not row:
                    raise ValueError(f"Server MCP dengan ID [{server_id}] tidak ditemukan.")
                server = dict(row)

            tools = json.loads(server["tools_manifest"] or "[]")
            mcp_tool_names = {f"mcp:{server['name']}:{t.get('name')}" for t in tools}

            if not force:
                async with conn.execute("SELECT name, tool_permissions FROM corporate_roles;") as cur:
                    conflicts = [
                        r["name"] for r in await cur.fetchall()
                        if any(p in mcp_tool_names for p in json.loads(r["tool_permissions"] or "[]"))
                    ]
                    if conflicts:
                        raise ValueError(
                            f"Gagal menghapus! Server MCP ini masih aktif digunakan oleh agen: "
                            f"{', '.join(conflicts)}. Silakan nonaktifkan izin pada agen tersebut dahulu."
                        )

            await conn.execute("DELETE FROM corporate_mcp_servers WHERE id = ?;", (server_id,))
            await conn.commit()

        for t_name in mcp_tool_names:
            dynamic_tool_registry.unregister_tool(t_name)
        logger.info(f"Server MCP [{server['name']}] berhasil dihapus.")
        return {"id": server_id, "name": server["name"], "status": "DELETED"}

    async def execute_mcp_tool(
        self, server_id: str, tool_name: str, parameters: Dict[str, Any], custom_db_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mengeksekusi tool MCP secara on-demand dengan mendekripsi environment variables."""
        async with get_db_connection(custom_db_path) as conn:
            async with conn.execute("SELECT * FROM corporate_mcp_servers WHERE id = ?;", (server_id,)) as cur:
                row = await cur.fetchone()
                if not row:
                    return {"error": f"Server MCP [{server_id}] tidak ditemukan."}
                server = dict(row)

        env_vars: Dict[str, str] = {}
        if server.get("env_vars_encrypted"):
            try:
                env_vars = json.loads(self.vault.decrypt(server["env_vars_encrypted"]))
            except Exception as e:
                logger.warning(f"Gagal mendekripsi env vars server MCP [{server['name']}]: {e}")

        return await mcp_client_bridge.call_tool(
            command_or_url=server["command_or_url"],
            tool_name=tool_name,
            parameters=parameters,
            transport=server.get("transport", "stdio"),
            env_vars=env_vars,
        )

    async def list_mcp_servers(self, custom_db_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mendapatkan daftar seluruh server MCP beserta status penggunaan oleh peran agen."""
        async with get_db_connection(custom_db_path) as conn:
            async with conn.execute("SELECT * FROM corporate_mcp_servers ORDER BY created_at DESC;") as cur:
                servers = [dict(r) for r in await cur.fetchall()]
            async with conn.execute("SELECT name, tool_permissions FROM corporate_roles;") as cur:
                roles = [dict(r) for r in await cur.fetchall()]

        results = []
        for s in servers:
            tools = json.loads(s.get("tools_manifest") or "[]")
            server_tools = {f"mcp:{s['name']}:{t.get('name')}" for t in tools}
            active_agents = [
                r["name"] for r in roles
                if any(p in server_tools for p in json.loads(r.get("tool_permissions") or "[]"))
            ]
            results.append({
                "id": s["id"],
                "name": s["name"],
                "transport": s["transport"],
                "command_or_url": s["command_or_url"],
                "status": s["status"],
                "tools": tools,
                "active_agents": active_agents,
                "created_at": s["created_at"],
            })
        return results


mcp_manager = MCPManager()
