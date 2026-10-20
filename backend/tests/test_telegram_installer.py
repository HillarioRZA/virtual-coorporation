"""
Unit Tests untuk Telegram Secretary Installer, Dry-Run Intent, dan Interceptor Redaction & Message Deletion.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.engine.secretary.secretary_installer import handle_installer_intent, delete_telegram_message


@pytest.mark.asyncio
async def test_telegram_dry_run_mcp_intent():
    """Memverifikasi deteksi permintaan pemasangan MCP dan balasan preview dry-run."""
    reply = await handle_installer_intent(
        text="tolong pasang mcp github",
        chat_id="chat_123",
        message_id=101,
        bot_token="mock_token",
    )
    assert reply is not None
    assert "Dry-Run MCP Inspection" in reply
    assert "server-github" in reply
    assert "token=ghp_xxx" in reply


@pytest.mark.asyncio
async def test_telegram_token_interceptor_and_auto_delete():
    """Memverifikasi penangkapan token, pemanggilan deleteMessage, dan registrasi server."""
    # 1. Pemicu dry-run awal agar pending session tercipta
    await handle_installer_intent(
        text="pasang mcp github",
        chat_id="chat_456",
        message_id=201,
        bot_token="mock_token",
    )

    # 2. Balasan persetujuan Founder yang memuat token rahasia
    with patch("app.engine.secretary.secretary_installer.delete_telegram_message", new=AsyncMock(return_value=True)) as mock_del:
        with patch("app.engine.mcp.mcp_manager.mcp_manager.register_mcp_server", new=AsyncMock(return_value={"name": "github", "tools_count": 3})):
            reply = await handle_installer_intent(
                text="Ya, token=ghp_secret_secret_12345",
                chat_id="chat_456",
                message_id=202,
                bot_token="mock_token",
            )

            # Verifikasi deleteMessage dipanggil untuk menghapus pesan sensitif dari chat
            mock_del.assert_called_once_with("mock_token", "chat_456", 202)
            assert reply is not None
            assert "Token Diamankan & Pesan Dihapus" in reply
            assert "Server MCP `github` berhasil diinstal" in reply


@pytest.mark.asyncio
async def test_telegram_dry_run_skill_intent():
    """Memverifikasi deteksi permintaan pemasangan skill."""
    reply = await handle_installer_intent(
        text="tolong install skill dari https://github.com/anthropics/skills",
        chat_id="chat_789",
        message_id=301,
        bot_token="mock_token",
    )
    assert reply is not None
    assert "Dry-Run Skills Inspection" in reply
    assert "https://github.com/anthropics/skills" in reply
