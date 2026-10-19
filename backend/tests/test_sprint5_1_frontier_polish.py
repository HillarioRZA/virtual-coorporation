"""
Unit & Integration Tests for Sprint 5.1 Frontier Polish & Hardening.
Tests CodebaseSearcher, AgentToolDispatcher, ToolSynthesizer AST scanning,
FinancialGuardrail WAL sync & topup, FlightRecorder persistence, and Frontier Radar API.
"""

from pathlib import Path
from typing import AsyncGenerator
import httpx
import pytest
import pytest_asyncio

from app.core.config import settings
from app.db.init_db import init_database
from app.engine.tools.agent_tool_dispatcher import agent_tool_dispatcher
from app.engine.governance.financial_guardrail import financial_guardrail
from app.engine.governance.flight_recorder import agent_flight_recorder
from app.engine.tools.tool_synthesizer import tool_synthesizer
from app.engine.tools.code_search import code_searcher
from main import app


@pytest_asyncio.fixture
async def test_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Asynchronous HTTP test client with isolated SQLite database."""
    db_file = tmp_path / "test_sprint5_1.db"
    test_db_url = f"sqlite+aiosqlite:///{db_file}"
    monkeypatch.setattr(settings, "DATABASE_URL", test_db_url)
    await init_database(str(db_file))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_codebase_searcher(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies symbol and regex searching across workspace files."""
    proj_dir = tmp_path / "proj-search"
    proj_dir.mkdir(parents=True)
    code_file = proj_dir / "calculator.py"
    code_file.write_text("def calculate_mrr(users: int) -> float:\n    return users * 10.0\n", encoding="utf-8")
    monkeypatch.setattr(code_searcher, "projects_dir", tmp_path)

    res_symbol = code_searcher.search_codebase("proj-search", query="calculate_mrr", is_symbol_only=True)
    assert res_symbol["total_matches"] == 1
    assert res_symbol["results"][0]["line"] == 1

    res_regex = code_searcher.search_codebase("proj-search", query="return users", is_symbol_only=False)
    assert res_regex["total_matches"] == 1


@pytest.mark.asyncio
async def test_agent_tool_dispatcher(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies ReAct tool parsing, execution, and step limits."""
    proj_dir = tmp_path / "proj-react"
    proj_dir.mkdir(parents=True)
    code_file = proj_dir / "models.py"
    code_file.write_text("class VentureApp:\n    pass\n", encoding="utf-8")
    monkeypatch.setattr(code_searcher, "projects_dir", tmp_path)

    tool_call_text = '{"tool": "search_codebase", "parameters": {"query": "VentureApp", "is_symbol_only": true}}'
    parsed = agent_tool_dispatcher.parse_tool_call(tool_call_text)
    assert parsed is not None
    assert parsed["tool"] == "search_codebase"

    obs = await agent_tool_dispatcher.execute_tool("proj-react", parsed["tool"], parsed["parameters"])
    assert obs.get("total_matches") == 1
    assert agent_tool_dispatcher.max_steps == 3


@pytest.mark.asyncio
async def test_tool_synthesizer_security(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies AST scanner and preflight auditor block unsafe ephemeral scripts."""
    monkeypatch.setattr(tool_synthesizer, "projects_dir", tmp_path)

    unsafe_eval = "def unsafe_exec(x: int) -> int:\n    return eval('x + 1')\n"
    res1 = tool_synthesizer.synthesize_tool_script("proj-sec", "evil.py", unsafe_eval)
    assert res1["success"] is False
    assert "Security Violation" in res1["error"]

    unsafe_import = "import non_existent_secret_cloud_pkg\ndef fetch_data():\n    pass\n"
    res2 = tool_synthesizer.synthesize_tool_script("proj-sec", "bad_import.py", unsafe_import)
    assert res2["success"] is False
    assert "Undeclared Dependency" in res2["error"]


@pytest.mark.asyncio
async def test_financial_guardrail_sync_and_topup() -> None:
    """Verifies token ledger synchronization and founder top-up functionality."""
    project_id = "proj-fin-1"
    status = await financial_guardrail.sync_with_ledger(project_id)
    assert status["total_tokens"] == 0
    assert status["total_cost_usd"] == 0.0

    # Freeze ticket by exceeding budget
    ticket_id = "ticket-test-1"
    financial_guardrail.record_usage(ticket_id, tokens=400000, cost_dollars=2.0, project_id=project_id)
    assert financial_guardrail.is_ticket_frozen(ticket_id) is True

    # Top-up budget to unfreeze
    topup = financial_guardrail.approve_founder_budget_topup(ticket_id, additional_tokens=150000, additional_dollars=0.75)
    assert topup["status"] == "UNFROZEN"
    assert financial_guardrail.is_ticket_frozen(ticket_id) is False


@pytest.mark.asyncio
async def test_flight_recorder_disk_reload(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies flight recorder events reload from persistent disk storage."""
    project_id = "proj-disk-log"
    out_dir = tmp_path / project_id
    out_dir.mkdir(parents=True)
    monkeypatch.setattr(agent_flight_recorder, "projects_dir", tmp_path)

    agent_flight_recorder.record_step(project_id, "TEST_DISPATCH", "role_test", {"code": 0})
    agent_flight_recorder._in_memory_logs.clear()

    reloaded = agent_flight_recorder.get_flight_log(project_id)
    assert len(reloaded) >= 1
    assert reloaded[0]["event_type"] == "TEST_DISPATCH"


@pytest.mark.asyncio
async def test_frontier_radar_api_endpoints(test_client: httpx.AsyncClient) -> None:
    """Verifies REST endpoints for Frontier Radar pane integration."""
    project_id = "proj-radar-api"

    res_logs = await test_client.get(f"/api/v1/projects/{project_id}/frontier-radar/flight-logs")
    assert res_logs.status_code == 200
    assert "events" in res_logs.json()

    res_fin = await test_client.get(f"/api/v1/projects/{project_id}/frontier-radar/financial-status")
    assert res_fin.status_code == 200
    assert "ledger" in res_fin.json()

    res_topup = await test_client.post(
        f"/api/v1/projects/{project_id}/frontier-radar/financial-topup",
        json={"ticket_id": "ticket-api-1", "additional_tokens": 150000, "additional_dollars": 0.75},
    )
    assert res_topup.status_code == 200
    assert res_topup.json()["topup_result"]["status"] == "UNFROZEN"

    res_visual = await test_client.get(f"/api/v1/projects/{project_id}/frontier-radar/visual-scorecard")
    assert res_visual.status_code == 200
    assert "scorecard" in res_visual.json()
