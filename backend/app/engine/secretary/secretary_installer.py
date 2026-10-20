"""
Telegram Secretary MCP & Skills Dry-Run Confirmation & Secret Token Interceptor.
Menangani inspeksi awal, penghapusan pesan token rahasia (anti-leak), dan eksekusi instalasi mandiri.
"""

import json
import re
from typing import Any, Dict, Optional
import httpx
from app.core.logger import logger
from app.engine.mcp.mcp_manager import mcp_manager
from app.engine.skills.skills_hub import skills_hub

# Sesi pending instalasi dalam memori (chat_id -> metadata)
_PENDING_MCP_INSTALL: Dict[str, Dict[str, Any]] = {}


async def delete_telegram_message(bot_token: str, chat_id: str, message_id: int) -> bool:
    """Menghapus pesan sensitif dari obrolan Telegram menggunakan API deleteMessage."""
    if not bot_token or not message_id:
        return False
    url = f"https://api.telegram.org/bot{bot_token}/deleteMessage"
    try:
        async with httpx.AsyncClient(timeout=8.0) as http:
            res = await http.post(url, json={"chat_id": chat_id, "message_id": message_id})
            return res.status_code == 200
    except Exception as err:
        logger.warning(f"Gagal menghapus pesan Telegram [{message_id}]: {err}")
        return False


async def handle_installer_intent(
    text: str, chat_id: str, message_id: Optional[int], bot_token: str
) -> Optional[str]:
    """Mendeteksi intent dry-run dan mengintersepsi token rahasia sebelum masuk ke log/LLM."""
    clean_text = text.strip()

    # 1. Intersepsi balasan token / konfirmasi
    token_match = re.search(r"token\s*=\s*([^\s]+)", clean_text, re.I)
    if token_match and chat_id in _PENDING_MCP_INSTALL:
        secret_token = token_match.group(1).strip()
        logger.info(f"Secretary Interceptor: Menerima token rahasia Founder (redacted: token=***)")

        # Hapus pesan pengguna yang memuat token rahasia
        if message_id:
            await delete_telegram_message(bot_token, chat_id, message_id)

        pending = _PENDING_MCP_INSTALL.pop(chat_id)
        cmd = pending["command"]
        name = pending["name"]
        env_vars = {"GITHUB_TOKEN": secret_token} if "github" in name.lower() else {"API_TOKEN": secret_token}

        try:
            res = await mcp_manager.register_mcp_server(
                name=name, command_or_url=cmd, env_vars=env_vars
            )
            return (
                f"🔒 *[Token Diamankan & Pesan Dihapus]*\n"
                f"✅ Server MCP `{res['name']}` berhasil diinstal dengan {res['tools_count']} perkakas aktif!\n"
                f"Perkakas telah didaftarkan ke permission pool korporat."
            )
        except Exception as err:
            return f"❌ Gagal memasang server MCP: {err}"

    # 2. Permintaan instalasi MCP ("install mcp ...")
    mcp_req = re.search(r"(?:install|pasang)\s+mcp\s+([a-zA-Z0-9_\-/@]+)", clean_text, re.I)
    if mcp_req:
        target = mcp_req.group(1).strip()
        server_name = re.sub(r"[^a-zA-Z0-9_-]", "", target.split("/")[-1].lower())
        cmd = f"npx -y {target}" if not target.startswith("npx") else target
        if target.lower() in ("github", "server-github"):
            cmd = "npx -y @modelcontextprotocol/server-github"
            server_name = "github"

        _PENDING_MCP_INSTALL[chat_id] = {"name": server_name, "command": cmd}
        return (
            f"🔍 *[Dry-Run MCP Inspection]*:\n"
            f"Target: `{cmd}`\n"
            f"Server Name: `{server_name}`\n"
            f"Kebutuhan Token: `GITHUB_TOKEN` (jika menggunakan API privat).\n\n"
            f"Apakah Anda setuju memasang MCP ini? Balas dengan:\n"
            f"`Ya, token=ghp_xxx` (pesan akan langsung dihapus otomatis demi keamanan)."
        )

    # 3. Permintaan instalasi Skill ("install skill ...")
    skill_req = re.search(r"(?:install|pasang)\s+skill[s]?\s+(?:dari\s+)?([^\s]+)", clean_text, re.I)
    if skill_req:
        target_url = skill_req.group(1).strip()
        return (
            f"📚 *[Dry-Run Skills Inspection]*:\n"
            f"Sumber: `{target_url}`\n"
            f"Status: Siap diunduh ke perpustakaan publik.\n"
            f"Kategori otomatis akan disesuaikan dari metadata `SKILL.md`.\n\n"
            f"Ketik `/confirm_skill {target_url}` untuk menyelesaikan instalasi."
        )

    return None
