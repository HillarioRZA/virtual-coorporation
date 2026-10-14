"""
Dynamic Telegram Auth & Security Gate Manager.
Mengelola rotasi password acak (default: 6 jam), pengiriman via Telegram Bot API,
verifikasi sesi HMAC-SHA256, dan pencegahan penguncian (anti-lockout).
"""

from datetime import datetime, timedelta
import hashlib
import hmac
from pathlib import Path
import secrets
import string
from typing import Any, Dict, Optional, Tuple
import httpx

from app.core.config import settings
from app.core.logger import logger


class DynamicAuthManager:
    """Manajer gembok keamanan akses personal berbasis Telegram Bot dan password dinamis."""

    def __init__(self) -> None:
        self.active_password: Optional[str] = None
        self.expires_at: Optional[datetime] = None
        self.last_sent_at: Optional[datetime] = None
        self.rotation_hours: int = 6
        self.secret_salt: str = secrets.token_hex(32)

    def is_enabled(self) -> bool:
        """Mengecek apakah gembok autentikasi sedang aktif."""
        # Jika AUTH_GATE_ENABLED ada di settings, gunakan nilainya; jika tidak default False
        return bool(getattr(settings, "AUTH_GATE_ENABLED", False))

    def get_rotation_hours(self) -> int:
        """Mengambil interval jam rotasi password."""
        return int(getattr(settings, "AUTH_ROTATION_HOURS", self.rotation_hours))

    def generate_new_password(self, length: int = 6) -> str:
        """Menghasilkan password acak kriptografis (format: 6-digit alphanum/pin)."""
        chars = string.digits + string.ascii_uppercase.replace("O", "").replace("I", "")
        # Format e.g. '849-217'
        part1 = "".join(secrets.choice(chars) for _ in range(3))
        part2 = "".join(secrets.choice(chars) for _ in range(3))
        new_pw = f"{part1}-{part2}"

        self.active_password = new_pw
        hours = self.get_rotation_hours()
        self.expires_at = datetime.now() + timedelta(hours=hours)
        logger.info(f"Password dinamis baru diterbitkan. Berlaku hingga: {self.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        return new_pw

    def verify_password(self, input_pw: str) -> bool:
        """Memverifikasi kecocokan password dan memeriksa batas masa berlaku."""
        if not self.is_enabled():
            return True
        if not self.active_password:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            logger.warning("Password input ditolak: masa berlaku telah kedaluwarsa.")
            return False

        # Format sanitasi (hilangkan spasi dan case-insensitive)
        clean_input = input_pw.strip().upper()
        clean_target = self.active_password.strip().upper()
        return hmac.compare_digest(clean_input, clean_target)

    def create_session_token(self) -> str:
        """Membuat token sesi terverifikasi HMAC-SHA256 untuk disimpan client."""
        exp_ts = int(self.expires_at.timestamp()) if self.expires_at else int((datetime.now() + timedelta(hours=6)).timestamp())
        payload = f"authenticated:{exp_ts}:{self.secret_salt}"
        sig = hmac.new(settings.APP_SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return f"{exp_ts}.{sig}"

    def verify_session_token(self, token: Optional[str]) -> bool:
        """Memeriksa keabsahan session token dari browser."""
        if not self.is_enabled():
            return True
        if not token or "." not in token:
            return False
        try:
            exp_str, sig = token.split(".", 1)
            exp_ts = int(exp_str)
            if datetime.now().timestamp() > exp_ts:
                return False
            payload = f"authenticated:{exp_ts}:{self.secret_salt}"
            expected = hmac.new(settings.APP_SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
            return hmac.compare_digest(sig, expected)
        except Exception:
            return False

    async def dispatch_to_telegram(self, custom_password: Optional[str] = None, reason: str = "ROTATION") -> Tuple[bool, str]:
        """Mengirim pesan notifikasi password ke Telegram Bot chat pengguna."""
        bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        chat_id = getattr(settings, "TELEGRAM_CHAT_ID", None)
        pw = custom_password or self.active_password or self.generate_new_password()

        if not bot_token or not chat_id:
            # Fallback anti-lockout: catat di log server agar pengguna tetap tahu passwordnya
            logger.warning(f"[SECURITY ANTI-LOCKOUT] Token/Chat ID Telegram belum diisi! Password Aktif: [{pw}]")
            return False, "Token atau Chat ID Telegram belum dikonfigurasi di Settings."

        exp_str = self.expires_at.strftime("%d %b %Y, %H:%M WIB") if self.expires_at else "6 Jam"
        msg = (
            "🔐 <b>[Venture Studio Security Gate]</b>\n"
            f"<b>Alasan:</b> {reason}\n\n"
            f"🔑 <b>Password Akses:</b> <code>{pw}</code>\n"
            f"⏳ <b>Masa Berlaku:</b> {self.get_rotation_hours()} Jam\n"
            f"🕒 <b>Kedaluwarsa:</b> {exp_str}\n\n"
            "<i>Masukkan password di atas pada popup layar untuk membuka Cockpit Dashboard Anda.</i>"
        )

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": msg,
            "parse_mode": "HTML",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    self.last_sent_at = datetime.now()
                    logger.info("Notifikasi password berhasil terkirim ke Telegram.")
                    return True, "Password berhasil dikirim ke Telegram."
                else:
                    err_msg = f"Telegram API error ({res.status_code}): {res.text}"
                    logger.warning(f"{err_msg}. Emergency Password: [{pw}]")
                    return False, err_msg
        except Exception as err:
            logger.warning(f"Koneksi Telegram gagal: {err}. Emergency Password: [{pw}]")
            return False, f"Gagal menghubungi server Telegram: {str(err)}"

    async def check_and_rotate_if_needed(self) -> None:
        """Memeriksa apakah waktu rotasi telah tiba dan mengirim password baru jika perlu."""
        if not self.is_enabled():
            return
        if not self.active_password or not self.expires_at or datetime.now() >= self.expires_at:
            logger.info("Masa berlaku password habis. Menjalankan rotasi otomatis...")
            new_pw = self.generate_new_password()
            await self.dispatch_to_telegram(new_pw, reason="ROTASI OTOMATIS (SCHEDULED)")


auth_manager = DynamicAuthManager()
