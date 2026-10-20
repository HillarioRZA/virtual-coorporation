"""
Bridge Klien Protokol Model Context Protocol (MCP).
Menangani transport stdio (subprocess / docker) dan komunikasi JSON-RPC 2.0.
"""

import asyncio
import json
import os
import shlex
from typing import Any, Dict, List, Optional
from app.core.logger import logger


class MCPClientBridge:
    """Klien JSON-RPC 2.0 untuk berkomunikasi dengan Server MCP eksternal."""

    def __init__(self, timeout_seconds: float = 30.0) -> None:
        """Inisialisasi bridge dengan timeout komunikasi."""
        self.timeout_seconds = timeout_seconds

    async def _send_jsonrpc(
        self,
        process: asyncio.subprocess.Process,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        msg_id: int = 1,
    ) -> Dict[str, Any]:
        """Mengirim pesan JSON-RPC 2.0 ke stdin proses dan membaca balasan dari stdout."""
        payload = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": method,
            "params": params or {},
        }
        raw_msg = json.dumps(payload) + "\n"
        if not process.stdin:
            raise RuntimeError("Proses MCP tidak memiliki saluran stdin terbuka.")

        process.stdin.write(raw_msg.encode("utf-8"))
        await process.stdin.drain()

        # Baca satu baris respon dari stdout
        if not process.stdout:
            raise RuntimeError("Proses MCP tidak memiliki saluran stdout terbuka.")

        line = await asyncio.wait_for(process.stdout.readline(), timeout=self.timeout_seconds)
        if not line:
            stderr_out = await process.stderr.read() if process.stderr else b""
            raise RuntimeError(f"Server MCP terputus tanpa respon: {stderr_out.decode('utf-8', errors='ignore')}")

        try:
            return json.loads(line.decode("utf-8").strip())
        except json.JSONDecodeError as err:
            raise ValueError(f"Respon server MCP bukan format JSON valid: {err} | Raw: {line[:200]}")

    async def run_discovery(
        self,
        command_or_url: str,
        transport: str = "stdio",
        env_vars: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """Melakukan handshake dan mengambil daftar tool (tools/list) dari server MCP."""
        logger.info(f"MCPClientBridge: Memulai discovery tools untuk [{command_or_url}] ({transport})...")
        effective_env = os.environ.copy()
        if env_vars:
            effective_env.update(env_vars)

        cmd_parts = shlex.split(command_or_url)
        process = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=effective_env,
        )
        try:
            # 1. Initialize
            init_res = await self._send_jsonrpc(
                process,
                method="initialize",
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "virtual-corporation-hub", "version": "1.0"},
                },
                msg_id=1,
            )
            if "error" in init_res:
                raise RuntimeError(f"Inisialisasi MCP gagal: {init_res['error']}")

            # 2. Notifikasi initialized
            notif = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
            if process.stdin:
                process.stdin.write(notif.encode("utf-8"))
                await process.stdin.drain()

            # 3. tools/list
            tools_res = await self._send_jsonrpc(process, method="tools/list", params={}, msg_id=2)
            if "error" in tools_res:
                raise RuntimeError(f"Gagal memuat tools/list: {tools_res['error']}")

            result = tools_res.get("result", {})
            return result.get("tools", [])
        finally:
            try:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=2.0)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass

    async def call_tool(
        self,
        command_or_url: str,
        tool_name: str,
        parameters: Dict[str, Any],
        transport: str = "stdio",
        env_vars: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Mengeksekusi tool tunggal (tools/call) pada proses server MCP secara on-demand."""
        effective_env = os.environ.copy()
        if env_vars:
            effective_env.update(env_vars)

        cmd_parts = shlex.split(command_or_url)
        process = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=effective_env,
        )
        try:
            # Handshake cepat
            await self._send_jsonrpc(
                process,
                method="initialize",
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "virtual-corporation-hub", "version": "1.0"},
                },
                msg_id=1,
            )
            notif = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
            if process.stdin:
                process.stdin.write(notif.encode("utf-8"))
                await process.stdin.drain()

            # Execute tool call
            call_res = await self._send_jsonrpc(
                process,
                method="tools/call",
                params={"name": tool_name, "arguments": parameters},
                msg_id=2,
            )
            if "error" in call_res:
                return {"error": call_res["error"]}
            return call_res.get("result", {})
        finally:
            try:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=2.0)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass


mcp_client_bridge = MCPClientBridge()
