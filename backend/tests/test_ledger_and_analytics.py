"""Unit Tests untuk Corporate Token Ledger & CFO Analytics Endpoints.

Memverifikasi pembukuan token, pelacakan burn-rate finansial, agregasi biaya peran agen,
dan endpoint REST API /api/v1/analytics/*.
"""

from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from app.core.config import settings
from app.db.token_ledger_repo import token_ledger_repo
from app.db.init_db import init_database


@pytest.mark.asyncio
async def test_token_ledger_repository_crud(tmp_path: Path) -> None:
    """Memverifikasi pencatatan dan penghitungan agregasi pada buku kas token."""
    db_file = str(tmp_path / "test_ledger.db")
    await init_database(custom_path=db_file)

    # 1. Catat transaksi token
    await token_ledger_repo.record_token_usage(
        project_id="proj_sprint31",
        branch_id="branch_main",
        pipeline_id="pipe_dev",
        role_id="role_backend",
        model_name="google/gemini-2.0-flash-001",
        provider="openrouter",
        upstream_channel="openrouter:google/gemini-2.0-flash-001",
        input_tokens=1000,
        output_tokens=500,
        cost_usd=0.00035,
        latency_ms=420,
        is_fallback=False,
        custom_path=db_file,
    )

    await token_ledger_repo.record_token_usage(
        project_id="proj_sprint31",
        branch_id="branch_main",
        pipeline_id="pipe_dev",
        role_id="role_backend",
        model_name="deepseek/deepseek-r1:free",
        provider="openrouter",
        upstream_channel="openrouter:deepseek/deepseek-r1:free",
        input_tokens=2000,
        output_tokens=1000,
        cost_usd=0.0,
        latency_ms=850,
        is_fallback=True,
        custom_path=db_file,
    )

    # 2. Ringkasan total
    summary = await token_ledger_repo.get_token_summary(project_id="proj_sprint31", custom_path=db_file)
    assert summary["total_input_tokens"] == 3000
    assert summary["total_output_tokens"] == 1500
    assert summary["total_requests"] == 2
    assert summary["total_fallbacks"] == 1
    assert abs(summary["total_cost_usd"] - 0.00035) < 0.0002

    # 3. Burn rate timeline
    burn_rate = await token_ledger_repo.get_burn_rate_timeline(
        days=7, custom_path=db_file
    )
    assert len(burn_rate) >= 1
    assert burn_rate[0]["tokens"] == 4500

    # 4. Agregasi biaya peran
    role_costs = await token_ledger_repo.get_role_burn_rates(custom_path=db_file)
    assert len(role_costs) >= 1
    assert role_costs[0]["role_id"] == "role_backend"


@pytest.mark.asyncio
async def test_analytics_api_endpoints(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Memverifikasi respon HTTP dari seluruh endpoint /api/v1/analytics/*."""
    db_file = tmp_path / "test_analytics.db"
    test_db_url = f"sqlite+aiosqlite:///{db_file}"
    monkeypatch.setattr(settings, "DATABASE_URL", test_db_url)
    await init_database(str(db_file))

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Token Summary
        resp = await client.get("/api/v1/analytics/token-summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_input_tokens" in data
        assert "total_cost_usd" in data

        # 2. Burn Rate
        resp_burn = await client.get("/api/v1/analytics/burn-rate?days=7")
        assert resp_burn.status_code == 200
        assert isinstance(resp_burn.json(), list)

        # 3. Role Costs
        resp_role = await client.get("/api/v1/analytics/role-costs")
        assert resp_role.status_code == 200
        assert isinstance(resp_role.json(), list)

        # 4. Channel Health Radar
        resp_chan = await client.get("/api/v1/analytics/channel-health")
        assert resp_chan.status_code == 200
        assert isinstance(resp_chan.json(), list)

        # 5. Set Budget Cap
        resp_cap = await client.post("/api/v1/analytics/budget-cap", json={"budget_cap_usd": 125.0})
        assert resp_cap.status_code == 200
        assert resp_cap.json()["budget_cap_usd"] == 125.0
