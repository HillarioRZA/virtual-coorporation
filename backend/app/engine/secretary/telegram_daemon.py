"""
Telegram Secretary Daemon & Executive Liaison Subsystem.
Menjalankan daemon long polling untuk interaksi langsung Founder via Telegram,
enforcement trust boundary whitelist, approval inline perkakas, dan laporan eksekutif.
"""

import asyncio
from typing import Any, Dict, List, Optional, Set
import httpx
from loguru import logger

from app.core.config import settings
from app.db.ticket_repo import ticket_repo
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
            tickets = await ticket_repo.get_tickets(project_id="default_proj")
            counts = {"TODO": 0, "IN_PROGRESS": 0, "DONE": 0, "FAILED": 0}
            for t in tickets:
                st = t.get("status", "TODO")
                counts[st] = counts.get(st, 0) + 1
            reply = (
                f"📊 *Status Kanban Korporat*:\n"
                f"- TODO: {counts['TODO']}\n"
                f"- IN PROGRESS: {counts['IN_PROGRESS']}\n"
                f"- DONE: {counts['DONE']}\n"
                f"- FAILED: {counts['FAILED']}"
            )
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
            # Chat dialogis eksekutif via LLM & Dynamic Secretary Role
            from app.engine.secretary.secretary_resolver import (
                resolve_secretary_role,
                build_secretary_prompt,
                extract_and_register_tool_proposal,
            )
            sec_role = await resolve_secretary_role()
            sys_prompt = build_secretary_prompt(sec_role)
            model = sec_role.get("model_name") or "deepseek/deepseek-r1:free"
            provider = sec_role.get("model_provider") or "openrouter"
            temperature = float(sec_role.get("temperature", 0.4))

            try:
                reply = await self.llm_client.complete(
                    prompt=text,
                    system_prompt=sys_prompt,
                    model=model,
                    provider=provider,
                    temperature=temperature,
                )
                # Periksa apakah LLM mengusulkan/merancang perkakas baru
                proposal = await extract_and_register_tool_proposal(
                    llm_reply=reply,
                    creator_role_id=sec_role.get("id", "role_secretary"),
                )
                if proposal:
                    p_name = proposal["name"]
                    reply += (
                        f"\n\n🛠️ *[Perkakas Baru Berhasil Diajukan]*:\n"
                        f"Perkakas `{p_name}` telah didaftarkan ke sistem dengan status `PENDING_APPROVAL`.\n"
                        f"Ketik `/approve {p_name}` untuk mengaktifkannya secara instan!"
                    )
            except Exception as err:
                reply = f"Maaf Founder, terdapat kendala saat memproses arahan: {err}"
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
        """Memulai daemon sekretaris Telegram."""
        if self._is_running or not self.bot_token:
            return
        self._is_running = True
        self._polling_task = asyncio.create_task(self._loop())
        logger.info("Telegram Secretary Daemon aktif dalam mode Long Polling.")

    def stop(self) -> None:
        """Menghentikan daemon sekretaris Telegram."""
        self._is_running = False
        if self._polling_task:
            self._polling_task.cancel()
            self._polling_task = None
        logger.info("Telegram Secretary Daemon dihentikan.")


telegram_secretary = TelegramSecretaryDaemon()
