"""
Unit Tests untuk Dynamic Telegram Auth & Security Gate.
Menguji penerbitan password dinamis, rotasi otomatis, session token HMAC-SHA256,
pencegahan lockout, dan integrasi endpoint REST API /auth.
"""

from datetime import datetime, timedelta
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from app.core.auth_manager import DynamicAuthManager, auth_manager
from app.core.config import settings
from main import app


@pytest.fixture(autouse=True)
def reset_auth_manager():
    """Reset status auth_manager sebelum setiap pengujian."""
    original_enabled = settings.AUTH_GATE_ENABLED
    original_pw = auth_manager.active_password
    original_exp = auth_manager.expires_at

    auth_manager.active_password = None
    auth_manager.expires_at = None
    settings.AUTH_GATE_ENABLED = True

    yield

    settings.AUTH_GATE_ENABLED = original_enabled
    auth_manager.active_password = original_pw
    auth_manager.expires_at = original_exp


def test_password_generation_and_verification():
    """Menguji pembuatan password acak dan validasi kecocokan."""
    mgr = DynamicAuthManager()
    settings.AUTH_GATE_ENABLED = True

    pw = mgr.generate_new_password()
    assert len(pw) == 7  # Format 'XXX-XXX'
    assert "-" in pw
    assert mgr.expires_at is not None
    assert mgr.expires_at > datetime.now()

    # Verifikasi benar (termasuk case-insensitive dan spasi)
    assert mgr.verify_password(pw) is True
    assert mgr.verify_password(f" {pw.lower()} ") is True
    assert mgr.verify_password("WRONG-PIN") is False


def test_password_expiration():
    """Menguji bahwa password kedaluwarsa ditolak."""
    mgr = DynamicAuthManager()
    settings.AUTH_GATE_ENABLED = True

    pw = mgr.generate_new_password()
    # Simulasikan waktu sudah melewati expires_at
    mgr.expires_at = datetime.now() - timedelta(minutes=5)

    assert mgr.verify_password(pw) is False


def test_session_token_hmac():
    """Menguji pembuatan dan verifikasi token sesi HMAC-SHA256."""
    mgr = DynamicAuthManager()
    settings.AUTH_GATE_ENABLED = True
    mgr.generate_new_password()

    token = mgr.create_session_token()
    assert "." in token
    assert mgr.verify_session_token(token) is True

    # Token rusak / palsu
    assert mgr.verify_session_token("invalid.token") is False
    assert mgr.verify_session_token(token + "tamper") is False


@pytest.mark.asyncio
async def test_telegram_dispatch_mock():
    """Menguji dispatch ke Telegram Bot API."""
    mgr = DynamicAuthManager()
    settings.AUTH_GATE_ENABLED = True
    settings.TELEGRAM_BOT_TOKEN = "mock_bot_token"
    settings.TELEGRAM_CHAT_ID = "mock_chat_id"

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"ok": true}'
        mock_post.return_value = mock_resp

        success, msg = await mgr.dispatch_to_telegram(reason="TEST")
        assert success is True
        assert "berhasil dikirim" in msg
        assert mgr.last_sent_at is not None


@pytest.mark.asyncio
async def test_auth_api_flow():
    """Menguji alur API v1 /auth: status, verify, resend, rotate."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Cek status (belum terautentikasi)
        res_status = await client.get("/api/v1/auth/status")
        assert res_status.status_code == 200
        status_data = res_status.json()["data"]
        assert status_data["is_enabled"] is True
        assert status_data["is_authenticated"] is False

        # 2. Coba rotate tanpa token (harus ditolak 401 oleh security middleware)
        res_rot_unauth = await client.post("/api/v1/auth/rotate")
        assert res_rot_unauth.status_code == 401


        # 3. Terbitkan password aktif oleh sistem
        active_pw = auth_manager.generate_new_password()
        assert active_pw is not None

        # 4. Verifikasi dengan password salah
        res_bad = await client.post("/api/v1/auth/verify", json={"password": "INCORRECT"})
        assert res_bad.status_code == 401
        assert "Kode akses tidak valid" in res_bad.json()["detail"]

        # 5. Verifikasi dengan password benar
        res_ok = await client.post("/api/v1/auth/verify", json={"password": active_pw})
        assert res_ok.status_code == 200
        token = res_ok.json()["data"]["session_token"]
        assert token is not None

        # 6. Cek status dengan Bearer token
        res_auth = await client.get("/api/v1/auth/status", headers={"Authorization": f"Bearer {token}"})
        assert res_auth.status_code == 200
        assert res_auth.json()["data"]["is_authenticated"] is True

        # 7. Rotate dengan Bearer token yang valid (harus sukses 200)
        res_rot_auth = await client.post("/api/v1/auth/rotate", headers={"Authorization": f"Bearer {token}"})
        assert res_rot_auth.status_code == 200

        # 8. Coba panggil /api/v1/projects tanpa token saat gate aktif (harus ditolak 401 oleh middleware)
        res_proj_unauth = await client.get("/api/v1/projects")
        assert res_proj_unauth.status_code == 401
        assert "Akses ditolak" in res_proj_unauth.json()["message"]

        # 9. Panggil /api/v1/projects dengan Bearer token (harus diizinkan 200)
        res_proj_auth = await client.get("/api/v1/projects", headers={"Authorization": f"Bearer {token}"})
        assert res_proj_auth.status_code == 200


