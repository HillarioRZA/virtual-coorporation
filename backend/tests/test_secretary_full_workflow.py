"""
Unit Tests untuk Alur Penuh Telegram Secretary Agent (Diskusi, Tugas, Konfirmasi, Laporan).
"""

from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest

from app.db.init_db import init_database
from app.engine.secretary.secretary_installer import handle_installer_intent
from app.engine.secretary.secretary_reporter import secretary_reporter
from app.engine.secretary.secretary_task_bridge import (
    handle_create_task_from_telegram,
    handle_status_command,
    handle_tasks_list,
)
from app.engine.secretary.telegram_daemon import TelegramSecretaryDaemon


@pytest.mark.asyncio
async def test_secretary_task_bridge_workflow(tmp_path: Path):
    """Menguji pembuatan tiket via instruksi Telegram dan kueri status Kanban."""
    db_file = tmp_path / "test_sec.db"
    await init_database(str(db_file))

    # Buat tiket via Telegram
    reply = await handle_create_task_from_telegram(
        text="/task Buat endpoint otentikasi login JWT",
        custom_path=str(db_file),
    )
    assert "Tiket Berhasil Didaftarkan" in reply
    assert "Penanggung Jawab:" in reply

    # Periksa status Kanban
    status_reply = await handle_status_command(custom_path=str(db_file))
    assert "Status Kanban Korporat" in status_reply
    assert "TODO: *1*" in status_reply

    # Periksa daftar tugas
    tasks_reply = await handle_tasks_list(custom_path=str(db_file))
    assert "Daftar Tiket Terkini" in tasks_reply
    assert "Buat endpoint otentikasi login JWT" in tasks_reply


def test_secretary_reporter_event_formatting():
    """Menguji pemformatan event bus menjadi laporan eksekutif Telegram."""
    completed_event = {
        "event_type": "TASK_COMPLETED",
        "ticket_id": "ticket_123",
        "sender_role_id": "role_coder",
        "payload": {"message": "Berhasil membuat modul otentikasi"},
    }
    comp_text = secretary_reporter.format_event_report(completed_event)
    assert comp_text is not None
    assert "Tugas Selesai" in comp_text
    assert "ticket_123" in comp_text

    failed_event = {
        "event_type": "TASK_FAILED",
        "ticket_id": "ticket_456",
        "sender_role_id": "role_qa",
        "payload": {"message": "Assertion error pada test suite"},
    }
    fail_text = secretary_reporter.format_event_report(failed_event)
    assert fail_text is not None
    assert "Kendala Agen" in fail_text
    assert "ticket_456" in fail_text


@pytest.mark.asyncio
async def test_secretary_installer_confirm_skill():
    """Menguji penanganan eksekusi /confirm_skill via git_importer."""
    mock_result = {
        "name": "ui-ux-pro-max",
        "category": "Design System",
        "files_count": 15,
        "folder_path": "/skills/design-system/ui-ux-pro-max",
    }
    with patch("app.engine.skills.git_importer.import_skill_from_git", new=AsyncMock(return_value=mock_result)):
        reply = await handle_installer_intent(
            text="/confirm_skill https://github.com/nextlevelbuilder/ui-ux-pro-max-skill",
            chat_id="12345",
            message_id=1,
            bot_token="fake_token",
        )
        assert reply is not None
        assert "Skill Berhasil Dipasang" in reply
        assert "ui-ux-pro-max" in reply
        assert "15" in reply


@pytest.mark.asyncio
async def test_telegram_daemon_dispatches_task_bridge(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Menguji routing /status dan /task di dalam TelegramSecretaryDaemon."""
    db_file = tmp_path / "test_daemon.db"
    await init_database(str(db_file))
    monkeypatch.setattr("app.core.config.settings.DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")

    daemon = TelegramSecretaryDaemon(bot_token="test_bot_token")
    sent_messages = []

    async def mock_send(chat_id: str, text: str, **kwargs):
        sent_messages.append(text)
        return True

    daemon.send_message = mock_send  # type: ignore

    # Uji kirim /status
    msg_status = {"from": {"id": 111}, "chat": {"id": 111}, "text": "/status"}
    await daemon.handle_message(msg_status)
    assert len(sent_messages) == 1
    assert "Status Kanban Korporat" in sent_messages[0]

    # Uji kirim /task
    msg_task = {"from": {"id": 111}, "chat": {"id": 111}, "text": "/task Selesaikan unit test"}
    await daemon.handle_message(msg_task)
    assert len(sent_messages) == 2
    assert "Tiket Berhasil Didaftarkan" in sent_messages[1]

    # Uji kirim /help
    msg_help = {"from": {"id": 111}, "chat": {"id": 111}, "text": "/help"}
    await daemon.handle_message(msg_help)
    assert len(sent_messages) == 3
    assert "Halo Founder! Saya adalah Sekretaris Eksekutif" in sent_messages[2]


@pytest.mark.asyncio
async def test_secretary_installer_tokenless_mcp(tmp_path: Path):
    """Menguji dry-run dan instalasi server MCP tanpa token via /confirm_mcp."""
    from app.engine.secretary.secretary_installer import _PENDING_MCP_INSTALL
    # 1. Trigger dry-run
    dry_reply = await handle_installer_intent(
        text="pasang mcp @modelcontextprotocol/server-memory",
        chat_id="chat_mem",
        message_id=1,
        bot_token="test_token",
    )
    assert dry_reply is not None
    assert "Dry-Run MCP Inspection" in dry_reply
    assert "server-memory" in dry_reply

    # 2. Konfirmasi tanpa token rahasia
    with patch("app.engine.mcp.mcp_manager.mcp_manager.register_mcp_server", new=AsyncMock(return_value={"name": "server-memory", "tools_count": 5})):
        confirm_reply = await handle_installer_intent(
            text="/confirm_mcp",
            chat_id="chat_mem",
            message_id=2,
            bot_token="test_token",
        )
        assert confirm_reply is not None
        assert "server-memory" in confirm_reply
        assert "5 perkakas aktif" in confirm_reply


@pytest.mark.asyncio
async def test_resolve_secretary_role_prefers_seeded_secretary(tmp_path: Path):
    """Menguji bahwa resolve_secretary_role menemukan role_secretary yang terdaftar di database."""
    from app.engine.secretary.secretary_resolver import resolve_secretary_role
    db_file = tmp_path / "test_sec_res.db"
    await init_database(str(db_file))
    sec_role = await resolve_secretary_role(custom_path=str(db_file))
    assert sec_role["id"] == "role_secretary"
    assert "chat_telegram" in sec_role.get("tool_permissions", [])
