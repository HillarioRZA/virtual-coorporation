"""
Unit Tests untuk MCPManager, Rehidrasi Startup, Dependency Guardrail, dan CoV Tier Routing.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch
from app.db.init_db import init_database
from app.engine.mcp.mcp_manager import MCPManager
from app.engine.mcp.mcp_client_bridge import mcp_client_bridge
from app.engine.sentinel.verifier import is_read_only_tool
from app.engine.tools.dynamic_tool_registry import dynamic_tool_registry
from app.db.session import get_db_connection


@pytest.fixture
def mcp_test_db(tmp_path):
    """Menyiapkan path basis data sementara untuk pengujian MCP."""
    return str(tmp_path / "test_mcp.db")


@pytest.mark.asyncio
async def test_mcp_registration_and_discovery(mcp_test_db):
    """Memverifikasi registrasi server MCP dan pemetaan tool ke DynamicToolRegistry."""
    await init_database(custom_path=mcp_test_db)
    mock_tools = [
        {"name": "create_issue", "description": "Buat issue GitHub baru"},
        {"name": "list_prs", "description": "Daftar Pull Request aktif"},
    ]
    with patch.object(mcp_client_bridge, "run_discovery", new=AsyncMock(return_value=mock_tools)):
        mgr = MCPManager()
        res = await mgr.register_mcp_server(
            name="github",
            command_or_url="npx -y @modelcontextprotocol/server-github",
            env_vars={"GITHUB_TOKEN": "ghp_mock_123"},
            custom_db_path=mcp_test_db,
        )

        assert res["name"] == "github"
        assert res["tools_count"] == 2
        assert dynamic_tool_registry.is_tool_registered("mcp:github:create_issue")
        assert dynamic_tool_registry.is_tool_registered("mcp:github:list_prs")


@pytest.mark.asyncio
async def test_mcp_dependency_guardrail_prevents_deletion(mcp_test_db):
    """Memverifikasi penolakan penghapusan server MCP jika tool aktif digunakan oleh role agen."""
    await init_database(custom_path=mcp_test_db)
    mock_tools = [{"name": "query_db", "description": "Jalankan SQL query"}]
    with patch.object(mcp_client_bridge, "run_discovery", new=AsyncMock(return_value=mock_tools)):
        mgr = MCPManager()
        server_res = await mgr.register_mcp_server(
            name="postgres",
            command_or_url="npx -y @modelcontextprotocol/server-postgres",
            custom_db_path=mcp_test_db,
        )

        # Buat role buatan yang menggunakan tool mcp:postgres:query_db
        async with get_db_connection(mcp_test_db) as conn:
            await conn.execute(
                """
                INSERT INTO corporate_roles (id, branch_id, division_id, name, system_prompt_template, tool_permissions)
                VALUES ('role_db_lead', 'branch_main', 'div_eng', 'Database Specialist', 'DB Prompt', ?);
                """,
                (json.dumps(["read_file", "mcp:postgres:query_db"]),),
            )
            await conn.commit()

        # Percobaan hapus tanpa force wajib menghasilkan ValueError (Guardrail)
        with pytest.raises(ValueError) as exc_info:
            await mgr.delete_mcp_server(server_res["id"], force=False, custom_db_path=mcp_test_db)

        assert "Database Specialist" in str(exc_info.value)
        assert "masih aktif digunakan oleh agen" in str(exc_info.value)

        # Jika dihapus dengan force=True, operasi diizinkan
        del_res = await mgr.delete_mcp_server(server_res["id"], force=True, custom_db_path=mcp_test_db)
        assert del_res["status"] == "DELETED"
        assert not dynamic_tool_registry.is_tool_registered("mcp:postgres:query_db")


@pytest.mark.asyncio
async def test_mcp_rehydrate_active_servers(mcp_test_db):
    """Memverifikasi rehidrasi seluruh perkakas aktif saat startup tanpa menjalankan container."""
    await init_database(custom_path=mcp_test_db)
    mock_tools = [{"name": "push_file", "description": "Push berkas ke repo"}]
    with patch.object(mcp_client_bridge, "run_discovery", new=AsyncMock(return_value=mock_tools)):
        mgr = MCPManager()
        await mgr.register_mcp_server(
            name="gitlab",
            command_or_url="npx -y @modelcontextprotocol/server-gitlab",
            custom_db_path=mcp_test_db,
        )

    # Simulasikan restart: kosongkan registry memori
    dynamic_tool_registry.unregister_tool("mcp:gitlab:push_file")
    assert not dynamic_tool_registry.is_tool_registered("mcp:gitlab:push_file")

    # Jalankan rehidrasi
    count = await mgr.rehydrate_active_servers(custom_db_path=mcp_test_db)
    assert count >= 1
    assert dynamic_tool_registry.is_tool_registered("mcp:gitlab:push_file")


def test_mcp_cov_tier_classification():
    """Memverifikasi klasifikasi Two-Tier CoV: read tools masuk Tier 1, mutating masuk Tier 2."""
    assert is_read_only_tool("mcp:github:list_issues") is True
    assert is_read_only_tool("mcp:github:read_file") is True
    assert is_read_only_tool("mcp:postgres:get_schema") is True
    assert is_read_only_tool("mcp:github:create_pull_request") is False
    assert is_read_only_tool("mcp:github:push_file") is False
    assert is_read_only_tool("mcp:postgres:delete_record") is False
