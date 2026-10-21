"""
Telegram Secretary Daemon & Executive Liaison Subsystem.
Menjalankan daemon long polling untuk interaksi langsung Founder via Telegram,
enforcement trust boundary whitelist, approval inline perkakas, dan laporan eksekutif.
"""

import asyncio
import re
from typing import Any, Dict, List, Optional, Set
import httpx
from app.core.logger import logger

from app.core.config import settings
from app.engine.secretary.secretary_task_bridge import (
    handle_create_task_from_telegram,
    handle_status_command,
    handle_tasks_list,
)
from app.engine.tools.dynamic_tool_registry import dynamic_tool_registry
from app.gateway.client import UnifiedLLMClient


class TelegramSecretaryDaemon:
    """Daemon long polling Telegram untuk peran Sekretaris Eksekutif."""

    def __init__(self, bot_token: Optional[str] = None, client: Optional[UnifiedLLMClient] = None) -> None:
        self.bot_token = bot_token or getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        self.llm_client = client or UnifiedLLMClient()
        self._is_running = False
        self._polling_task: Optional[asyncio.Task] = None
        self._last_update_id = 0

    def _get_allowed_user_ids(self) -> Set[str]:
        """Mengambil daftar ID Telegram yang berhak mengakses (Trust Boundary)."""
        allowed = set()
        raw_chat = getattr(settings, "TELEGRAM_CHAT_ID", "")
        if raw_chat:
            allowed.add(str(raw_chat).strip())
        raw_list = getattr(settings, "TELEGRAM_ALLOWED_USER_IDS", "")
        if raw_list:
            for uid in raw_list.split(","):
                if uid.strip():
                    allowed.add(uid.strip())
        return allowed

    def is_authorized_sender(self, user_id: Any) -> bool:
        """Memverifikasi pengirim terhadap trust boundary whitelist."""
        allowed = self._get_allowed_user_ids()
        if not allowed:
            # Jika belum ada whitelist yang diset, izinkan untuk setup awal jika bot token valid
            return True
        return str(user_id) in allowed

    async def send_message(
        self,
        chat_id: str,
        text: str,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Mengirim pesan teks ke pengguna Telegram."""
        if not self.bot_token:
            logger.warning("Token Telegram bot belum disetel. Gagal kirim pesan.")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload: Dict[str, Any] = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if reply_markup:
            payload["reply_markup"] = reply_markup

        try:
            async with httpx.AsyncClient(timeout=10.0) as http:
                res = await http.post(url, json=payload)
                return res.status_code == 200
        except Exception as err:
            logger.warning(f"Gagal mengirim pesan Telegram: {err}")
            return False

    async def handle_message(self, message: Dict[str, Any]) -> None:
        """Memproses pesan masuk dari pengguna yang terotorisasi."""
        sender_id = message.get("from", {}).get("id")
        chat_id = str(message.get("chat", {}).get("id", sender_id))
        text = str(message.get("text", "")).strip()

        if not self.is_authorized_sender(sender_id):
            logger.warning(f"[SECURITY ALERT] Pesan Telegram dari ID tak dikenal ditolak: {sender_id}")
            return

        logger.info(f"Telegram Secretary menerima arahan dari Founder [{sender_id}]: {text}")

        if text.startswith("/status"):
            reply = await handle_status_command()
            await self.send_message(chat_id, reply)
        elif text.startswith("/tasks"):
            reply = await handle_tasks_list()
            await self.send_message(chat_id, reply)
        elif text.startswith("/task ") or re.search(r"^(?:tolong\s+)?(?:buatkan\s+|tambahkan\s+)?(?:tiket|tugas)\s+", text, re.I):
            reply = await handle_create_task_from_telegram(text)
            await self.send_message(chat_id, reply)
        elif text.startswith("/approve "):
            target = text.replace("/approve ", "").strip()
            res = await dynamic_tool_registry.approve_tool(target)
            reply = f"✅ Perkakas `{target}` berhasil disetujui dan diaktifkan!" if res else f"❌ Perkakas `{target}` tidak ditemukan."
            await self.send_message(chat_id, reply)
        elif text.startswith("/reject "):
            target = text.replace("/reject ", "").strip()
            res = await dynamic_tool_registry.reject_tool(target)
            reply = f"🚫 Perkakas `{target}` berhasil ditolak." if res else f"❌ Perkakas `{target}` tidak ditemukan."
            await self.send_message(chat_id, reply)
        else:
            # Periksa intent instalasi MCP / Skills atau penangkapan token rahasia
            from app.engine.secretary.secretary_installer import handle_installer_intent
            inst_reply = await handle_installer_intent(
                text=text,
                chat_id=chat_id,
                message_id=message.get("message_id"),
                bot_token=self.bot_token,
            )
            if inst_reply:
                await self.send_message(chat_id, inst_reply)
                return

            # Chat dialogis eksekutif via LLM & Dynamic Secretary Role
            from app.engine.secretary.secretary_resolver import execute_secretary_chat
            reply = await execute_secretary_chat(self.llm_client, text)
            await self.send_message(chat_id, reply)

    async def poll_once(self) -> int:
        """Menjalankan satu siklus getUpdates polling untuk pengujian dan runtime."""
        if not self.bot_token:
            return 0

        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        params = {"offset": self._last_update_id + 1, "timeout": 2}
        try:
            async with httpx.AsyncClient(timeout=10.0) as http:
                res = await http.get(url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    updates = data.get("result", [])
                    for u in updates:
                        self._last_update_id = max(self._last_update_id, u.get("update_id", 0))
                        if "message" in u:
                            await self.handle_message(u["message"])
                    return len(updates)
        except Exception as err:
            logger.debug(f"Polling Telegram getUpdates error: {err}")
        return 0

    async def _loop(self) -> None:
        """Loop latar belakang terus-menerus untuk long polling."""
        while self._is_running:
            await self.poll_once()
            await asyncio.sleep(2.0)

    def start(self) -> None:
        """Memulai daemon sekretaris Telegram dan reporter proaktif."""
        if self._is_running or not self.bot_token:
            return
        self._is_running = True
        self._polling_task = asyncio.create_task(self._loop())
        from app.engine.secretary.secretary_reporter import secretary_reporter
        secretary_reporter.start()
        logger.info("Telegram Secretary Daemon & Proactive Reporter aktif.")

    def stop(self) -> None:
        """Menghentikan daemon sekretaris Telegram dan reporter."""
        self._is_running = False
        if self._polling_task:
            self._polling_task.cancel()
            self._polling_task = None
        from app.engine.secretary.secretary_reporter import secretary_reporter
        secretary_reporter.stop()
        logger.info("Telegram Secretary Daemon dihentikan.")


telegram_secretary = TelegramSecretaryDaemon()
