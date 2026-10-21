"""
Unit Tests untuk kanban_recovery.py (Ticket Execution and Checkpoint Recovery).
Menguji percobaan eksekusi tiket, recovery state, dan log runtime container.
"""

from unittest.mock import AsyncMock, patch
import pytest
from app.engine.runtime.kanban_recovery import execute_ticket_with_recovery
from app.engine.runtime.state import VentureState


@pytest.mark.asyncio
async def test_execute_ticket_with_recovery_success() -> None:
    """Menguji eksekusi sukses pada iterasi pertama."""
    ticket = {
        "id": "t_success",
        "title": "Build API",
        "project_id": "proj_123",
        "assigned_role_id": "role_be",
        "description": "Initial task description",
    }

    with patch("app.engine.runtime.kanban_recovery.execute_dynamic_role_node", new=AsyncMock()) as mock_exec, \
         patch("app.engine.runtime.kanban_recovery.MemoryManager") as mock_mem_cls:
        mock_mem = mock_mem_cls.return_value
        mock_mem.load_latest_checkpoint = AsyncMock(return_value=VentureState(project_id="proj_123", project_name="Build API", founder_idea="Build API"))
        mock_mem.save_checkpoint = AsyncMock()

        success, state, err = await execute_ticket_with_recovery(ticket, max_retries=2)
        assert success is True
        assert err is None
        assert mock_exec.call_count == 1
        assert mock_mem.save_checkpoint.call_count == 1


@pytest.mark.asyncio
async def test_execute_ticket_with_recovery_retry_then_success() -> None:
    """Menguji eksekusi gagal sekali lalu berhasil pada retry berikutnya."""
    ticket = {
        "id": "t_retry",
        "title": "Build Frontend",
        "project_id": "proj_456",
        "assigned_role_id": "role_fe",
        "description": "Setup UI layout",
    }

    call_count = 0

    async def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("Build error in container")
        return None

    with patch("app.engine.runtime.kanban_recovery.execute_dynamic_role_node", side_effect=side_effect) as mock_exec, \
         patch("app.engine.runtime.kanban_recovery.MemoryManager") as mock_mem_cls, \
         patch("app.engine.runtime.kanban_recovery.sandbox_log_collector.build_runtime_error_context", new=AsyncMock(return_value="[SANDBOX LOGS]: SyntaxError")) as mock_logs:
        mock_mem = mock_mem_cls.return_value
        mock_mem.load_latest_checkpoint = AsyncMock(return_value=VentureState(project_id="proj_456", project_name="Build Frontend", founder_idea="Build Frontend"))
        mock_mem.save_checkpoint = AsyncMock()

        success, state, err = await execute_ticket_with_recovery(ticket, max_retries=2)
        assert success is True
        assert err is None
        assert call_count == 2
        assert mock_logs.call_count == 1
