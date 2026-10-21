"""
Secretary Proactive Event Reporter Subsystem.
Mendengarkan event bus korporat dan mengirimkan laporan eksekutif instan ke ponsel Founder via Telegram.
"""

import asyncio
from typing import Any, Dict, Optional
from app.core.config import settings
from app.core.logger import logger
from app.engine.runtime.event_bus import corporate_event_bus


class SecretaryReporter:
    """Reporter latar belakang yang mem-forward status penting agen ke obrolan Telegram Founder."""

    def __init__(self) -> None:
        self._is_running = False
        self._listener_task: Optional[asyncio.Task] = None

    def _get_target_chat_id(self) -> Optional[str]:
        """Mengambil chat ID tujuan Founder dari konfigurasi rahasia."""
        chat_id = getattr(settings, "TELEGRAM_CHAT_ID", "")
        if chat_id:
            return str(chat_id).strip()
        allowed = getattr(settings, "TELEGRAM_ALLOWED_USER_IDS", "")
        if allowed:
            first_id = allowed.split(",")[0].strip()
            if first_id:
                return first_id
        return None

    def format_event_report(self, event: Dict[str, Any]) -> Optional[str]:
        """Menyusun teks markdown laporan eksekutif berdasarkan tipe event."""
        etype = str(event.get("event_type", ""))
        payload = event.get("payload", {})
        if isinstance(payload, str):
            payload = {"message": payload}

        ticket_id = event.get("ticket_id") or payload.get("ticket_id", "N/A")
        role_id = event.get("sender_role_id") or payload.get("role_id", "Sistem")
        desc = payload.get("message") or payload.get("description") or "Pembaruan status operasional."

        if etype == "TASK_COMPLETED":
            return (
                f"🚀 *[Laporan Eksekutif: Tugas Selesai]*\n"
                f"• Agen: `{role_id}`\n"
                f"• Tiket: `{ticket_id}`\n"
                f"• Keterangan: {desc}\n\n"
                f"_Periksa web UI untuk artefak dan detail kode lengkap._"
            )
        elif etype == "TASK_FAILED":
            return (
                f"⚠️ *[Laporan Eksekutif: Kendala Agen]*\n"
                f"• Agen: `{role_id}`\n"
                f"• Tiket: `{ticket_id}`\n"
                f"• Kesalahan: `{desc}`\n\n"
                f"_Ketik `/status` untuk ringkasan atau tugaskan kembali agen via Telegram._"
            )
        elif etype == "CIRCUIT_BREAKER_TRIGGERED":
            return (
                f"🛑 *[Peringatan Keamanan: Circuit Breaker Terpicu]*\n"
                f"• Peran Terdampak: `{role_id}`\n"
                f"• Alasan: `{desc}`\n"
                f"Pemberhentian darurat telah diaktifkan untuk melindungi anggaran token."
            )
        return None

    async def _listen_loop(self) -> None:
        """Loop asinkron berlangganan event bus korporat."""
        from app.engine.secretary.telegram_daemon import telegram_secretary
        queue = await corporate_event_bus.subscribe("default_proj")
        try:
            while self._is_running:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=2.0)
                    chat_id = self._get_target_chat_id()
                    if not chat_id:
                        continue
                    report = self.format_event_report(event)
                    if report:
                        await telegram_secretary.send_message(chat_id, report)
                        logger.debug(f"Secretary Reporter mengirim laporan [{event.get('event_type')}] ke Telegram.")
                except asyncio.TimeoutError:
                    continue
                except Exception as err:
                    logger.debug(f"Error dalam loop listening event bus: {err}")
        finally:
            await corporate_event_bus.unsubscribe("default_proj", queue)

    def start(self) -> None:
        """Memulai listener reporter laporan proaktif."""
        if self._is_running:
            return
        self._is_running = True
        self._listener_task = asyncio.create_task(self._listen_loop())
        logger.info("Secretary Proactive Event Reporter aktif.")

    def stop(self) -> None:
        """Menghentikan listener reporter."""
        self._is_running = False
        if self._listener_task:
            self._listener_task.cancel()
            self._listener_task = None
        logger.info("Secretary Proactive Event Reporter dihentikan.")


secretary_reporter = SecretaryReporter()
