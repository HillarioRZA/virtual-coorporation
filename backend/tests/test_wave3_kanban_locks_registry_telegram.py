"""
Unit & Integration Tests untuk Gelombang 3 (Fase 5 & 7):
Autonomous Kanban Runner, File Lock Manager, DynamicToolRegistry, dan Telegram Secretary Daemon.
"""

import asyncio
from unittest.mock import AsyncMock, patch
import pytest

from app.db.init_db import init_database
from app.db.ticket_repo import ticket_repo
from app.engine.runtime.kanban_runner import kanban_runner
from app.engine.tools.file_lock_manager import file_lock_manager
from app.engine.tools.dynamic_tool_registry import dynamic_tool_registry
from app.engine.secretary.telegram_daemon import TelegramSecretaryDaemon


@pytest.mark.asyncio
async def test_file_lock_manager_concurrency():
    """Menguji bahwa FileLockManager mencegah race condition pada file yang sama."""
    order = []

    async def worker(worker_id: int, delay: float):
        async with file_lock_manager.acquire("proj_test", "backend/app/main.py"):
            order.append(f"start_{worker_id}")
            await asyncio.sleep(delay)
            order.append(f"end_{worker_id}")

    # Jalankan worker 1 dan 2 secara paralel
    await asyncio.gather(worker(1, 0.05), worker(2, 0.01))

    # Karena terkunci mutual exclusive, worker 1 harus selesai sebelum worker 2 mulai
    assert order == ["start_1", "end_1", "start_2", "end_2"] or order == ["start_2", "end_2", "start_1", "end_1"]


@pytest.mark.asyncio
async def test_dynamic_tool_registry_lifecycle(tmp_path):
    """Menguji proposal, approval, persistensi DB, dan eksekusi DynamicToolRegistry."""
    db_file = tmp_path / "test_dyn_tools.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"
    await init_database(custom_path=db_url)

    tool_code = """
def calculate_runway(cash_balance: float, burn_rate: float) -> float:
    if burn_rate <= 0:
        return 999.0
    return round(cash_balance / burn_rate, 2)
"""
    # 1. Propose
    prop = await dynamic_tool_registry.propose_tool(
        name="calculate_runway",
        description="Menghitung estimasi runway keuangan dalam bulan.",
        parameters_schema={"cash_balance": "float", "burn_rate": "float"},
        python_code=tool_code,
        created_by="role_cfo",
        custom_path=db_url,
    )
    assert prop["status"] == "PENDING_APPROVAL"
    assert dynamic_tool_registry.is_tool_registered("calculate_runway") is False

    # 2. Approve
    approved = await dynamic_tool_registry.approve_tool("calculate_runway", custom_path=db_url)
    assert approved is not None
    assert approved["status"] == "APPROVED"
    assert dynamic_tool_registry.is_tool_registered("calculate_runway") is True

    # 3. Execute
    runway = await dynamic_tool_registry.execute_tool("calculate_runway", cash_balance=100000.0, burn_rate=20000.0)
    assert runway == 5.0

    # 4. Reload from DB simulation
    registry_reloaded = dynamic_tool_registry.__class__()
    count = await registry_reloaded.load_approved_tools_from_db(custom_path=db_url)
    assert count >= 1
    assert registry_reloaded.is_tool_registered("calculate_runway") is True


@pytest.mark.asyncio
async def test_kanban_runner_atomic_claim_and_dependencies(tmp_path):
    """Menguji claim atomik SQLite dan resolusi DAG dependency pada Kanban Runner."""
    db_file = tmp_path / "test_kanban_atomic.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"
    await init_database(custom_path=db_url)

    # Buat tiket induk (Prerequisite)
    t_arch = await ticket_repo.create_ticket(
        branch_id="branch_main",
        project_id="p_kbn",
        division_id="div_eng",
        title="Architecture Contract",
        description="Create arch",
        status="TODO",
        custom_path=db_url,
    )

    # Buat tiket anak (Tergantung t_arch)
    t_backend = await ticket_repo.create_ticket(
        branch_id="branch_main",
        project_id="p_kbn",
        division_id="div_eng",
        title="Backend Coding",
        description="Implement API",
        status="TODO",
        dependencies=[t_arch["id"]],
        custom_path=db_url,
    )

    # Cek dependencies sebelum t_arch selesai
    can_run = await kanban_runner.are_dependencies_met(t_backend, "p_kbn", custom_path=db_url)
    assert can_run is False

    # Klaim atomik t_arch
    claim1 = await ticket_repo.claim_ticket_atomic(t_arch["id"], custom_path=db_url)
    assert claim1 is not None
    assert claim1["status"] == "IN_PROGRESS"

    # Klaim ulang pada tiket yang sama harus None (mencegah double worker)
    claim2 = await ticket_repo.claim_ticket_atomic(t_arch["id"], custom_path=db_url)
    assert claim2 is None

    # Selesaikan t_arch
    await ticket_repo.transition_ticket_status(t_arch["id"], "DONE", custom_path=db_url)

    # Sekarang dependensi t_backend terpenuhi
    can_run_now = await kanban_runner.are_dependencies_met(t_backend, "p_kbn", custom_path=db_url)
    assert can_run_now is True


@pytest.mark.asyncio
async def test_telegram_secretary_daemon_trust_boundary():
    """Menguji Trust Boundary Enforcer pada Telegram Secretary Daemon."""
    daemon = TelegramSecretaryDaemon(bot_token="fake_bot_token")

    with patch.object(daemon, "_get_allowed_user_ids", return_value={"999888777"}):
        # 1. Pengirim liar / unauthorized
        unauthorized_msg = {
            "from": {"id": 111222333},
            "chat": {"id": 111222333},
            "text": "System wipe",
        }
        with patch.object(daemon, "send_message", new_callable=AsyncMock) as mock_send:
            await daemon.handle_message(unauthorized_msg)
            # Pesan liar wajib di-drop tanpa respons
            mock_send.assert_not_called()

        # 2. Pengirim authorized (Founder)
        authorized_msg = {
            "from": {"id": 999888777},
            "chat": {"id": 999888777},
            "text": "/status",
        }
        with patch.object(daemon, "send_message", new_callable=AsyncMock) as mock_send:
            await daemon.handle_message(authorized_msg)
            mock_send.assert_called_once()
            args, _ = mock_send.call_args
            assert "Status Kanban Korporat" in args[1]


@pytest.mark.asyncio
async def test_telegram_secretary_dynamic_tool_proposal(tmp_path):
    """Menguji dialog sekretaris via Telegram yang menghasilkan proposal perkakas baru."""
    db_url = f"sqlite+aiosqlite:///{tmp_path / 'test_sec_tools.db'}"
    await init_database(custom_path=db_url)

    mock_llm = AsyncMock()
    mock_llm.complete.return_value = (
        'Tentu Founder:\n```tool_proposal\n'
        '{"name": "calculate_roi_v2", "description": "Hitung ROI.", '
        '"parameters_schema": {"gain": "float", "cost": "float"}, '
        '"python_code": "def calculate_roi_v2(gain: float, cost: float) -> float:\\n    return round((gain - cost) / cost * 100, 2)"}\n'
        '```'
    )
    daemon = TelegramSecretaryDaemon(bot_token="test_token", client=mock_llm)

    with patch.object(daemon, "_get_allowed_user_ids", return_value={"12345"}), \
         patch.object(daemon, "send_message", new_callable=AsyncMock) as mock_send:
        await daemon.handle_message({"from": {"id": 12345}, "chat": {"id": 12345}, "text": "Buatkan tool ROI"})
        mock_send.assert_called_once()
        sent_text = mock_send.call_args[0][1]
        assert "calculate_roi_v2" in sent_text and "/approve calculate_roi_v2" in sent_text

        # Sekarang Founder menyetujui tool via Telegram
        await daemon.handle_message({"from": {"id": 12345}, "chat": {"id": 12345}, "text": "/approve calculate_roi_v2"})
        assert mock_send.call_count == 2
        assert "berhasil disetujui" in mock_send.call_args[0][1]

