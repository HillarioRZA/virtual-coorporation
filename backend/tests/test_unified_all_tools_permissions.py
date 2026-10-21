"""
Unit Tests untuk Unified Tool Permissions Endpoint (Built-in + MCP + Secretary Custom Tools).
"""

from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

from app.db.init_db import init_database
from app.db.session import get_db_connection
from main import app


@pytest.mark.asyncio
async def test_get_all_tools_includes_custom_approved_tools(tmp_path: Path):
    """Menguji bahwa GET /api/v1/mcp/all-tools menyertakan perkakas custom disetujui."""
    db_file = tmp_path / "test_tools.db"
    await init_database(str(db_file))

    # Masukkan custom tool buatan sekretaris dengan status APPROVED
    async with get_db_connection(str(db_file)) as conn:
        await conn.execute(
            """
            INSERT INTO corporate_custom_tools (id, name, description, parameters_schema, python_code, status, created_by)
            VALUES (?, ?, ?, ?, ?, 'APPROVED', ?);
            """,
            (
                "tool_test_calc",
                "custom_calculator",
                "Perkakas kalkulator dinamis buatan sekretaris",
                "{}",
                "def custom_calculator(): pass",
                "role_secretary",
            ),
        )
        await conn.commit()

    # Panggil endpoint API all-tools
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Patch session connection ke custom db
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("app.core.config.settings.DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
            res = await client.get("/api/v1/mcp/all-tools")
            assert res.status_code == 200
            data = res.json()
            assert "builtin" in data
            assert "mcp_tools" in data
            assert "custom_tools" in data

            c_tools = data["custom_tools"]
            names = [ct["name"] for ct in c_tools]
            assert "custom_calculator" in names
            calc_tool = next(ct for ct in c_tools if ct["name"] == "custom_calculator")
            assert calc_tool["created_by"] == "role_secretary"
            assert "[CUSTOM]" in calc_tool["label"]
