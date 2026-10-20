"""
REST API Endpoints untuk Manajemen Server Model Context Protocol (MCP).
Menangani instalasi, dry-run discovery, listing status, dan penghapusan ber-guardrail.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.engine.mcp.mcp_manager import mcp_manager

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol (MCP)"])


class MCPDryRunRequest(BaseModel):
    command_or_url: str = Field(description="Command npx/python atau URL SSE server MCP")
    transport: str = Field(default="stdio", description="stdio | docker | sse")
    env_vars: Optional[Dict[str, str]] = Field(default=None, description="Environment variables opsional")


class MCPInstallRequest(BaseModel):
    name: str = Field(description="Nama unik server MCP (misal: github, postgres)")
    command_or_url: str = Field(description="Command npx/python atau URL SSE server MCP")
    transport: str = Field(default="stdio", description="stdio | docker | sse")
    env_vars: Optional[Dict[str, str]] = Field(default=None, description="Kredensial atau API keys")


@router.get("/servers")
async def list_servers() -> List[Dict[str, Any]]:
    """Mendapatkan daftar seluruh server MCP terdaftar beserta status penggunaan agen."""
    try:
        return await mcp_manager.list_mcp_servers()
    except Exception as err:
        logger.error(f"Gagal memuat daftar server MCP: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/dry-run")
async def dry_run_discovery(req: MCPDryRunRequest) -> Dict[str, Any]:
    """Menguji koneksi server MCP dan mengambil daftar perkakas yang disediakan tanpa menyimpannya."""
    try:
        tools = await mcp_manager.discover_mcp_tools(
            command_or_url=req.command_or_url,
            transport=req.transport,
            env_vars=req.env_vars,
        )
        return {"status": "SUCCESS", "tools_count": len(tools), "tools": tools}
    except Exception as err:
        logger.warning(f"Dry-run discovery MCP gagal: {err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Koneksi handshake MCP gagal: {err}",
        )


@router.post("/install", status_code=status.HTTP_201_CREATED)
async def install_server(req: MCPInstallRequest) -> Dict[str, Any]:
    """Menginstal dan mendaftarkan server MCP ke basis data dan permission pool sistem."""
    try:
        res = await mcp_manager.register_mcp_server(
            name=req.name,
            command_or_url=req.command_or_url,
            transport=req.transport,
            env_vars=req.env_vars,
        )
        return {"status": "SUCCESS", "server": res}
    except Exception as err:
        logger.error(f"Gagal menginstal server MCP: {err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gagal menginstal server MCP: {err}",
        )


@router.delete("/servers/{server_id}")
async def delete_server(server_id: str, force: bool = False) -> Dict[str, Any]:
    """Menghapus server MCP dengan penolakan keras (409 Conflict) jika masih digunakan oleh agen."""
    try:
        return await mcp_manager.delete_mcp_server(server_id, force=force)
    except ValueError as val_err:
        # Penolakan guardrail referensial
        logger.warning(f"Guardrail MCP menolak penghapusan server [{server_id}]: {val_err}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(val_err))
    except Exception as err:
        logger.error(f"Kesalahan penghapusan server MCP [{server_id}]: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/all-tools")
async def get_all_tools() -> Dict[str, Any]:
    """Mengembalikan seluruh perkakas aktif di sistem (Built-in + MCP Tools) untuk seleksi izin role."""
    from app.engine.tools.builtin_tools import get_builtin_tools
    builtin_keys = list(get_builtin_tools().keys())
    servers = await mcp_manager.list_mcp_servers()
    mcp_tools = []
    for s in servers:
        s_name = s["name"]
        for t in s.get("tools", []):
            mcp_tools.append({
                "id": f"mcp:{s_name}:{t.get('name')}",
                "label": f"[{s_name.upper()}] {t.get('name')}",
                "description": t.get("description", ""),
                "server_name": s_name,
            })
    return {"builtin": builtin_keys, "mcp_tools": mcp_tools}

