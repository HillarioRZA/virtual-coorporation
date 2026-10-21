"""
Secretary Task Bridge & Away-from-Desk Kanban Intermediary.
Menjembatani instruksi Founder via Telegram dengan sistem tiket otonom korporat multi-agen.
"""

import re
from typing import Any, Dict, List, Optional
from app.core.logger import logger
from app.db.role_repo import role_repo
from app.db.session import get_db_connection
from app.db.ticket_repo import ticket_repo


async def get_active_project_id(custom_path: Optional[str] = None) -> str:
    """Mengambil ID proyek aktif atau fallback ke default_proj."""
    try:
        async with get_db_connection(custom_path) as conn:
            async with conn.execute("SELECT id FROM projects LIMIT 1;") as cur:
                row = await cur.fetchone()
                if row:
                    return str(row["id"])
    except Exception as err:
        logger.debug(f"Gagal mendeteksi proyek aktif: {err}")
    return "default_proj"


async def handle_status_command(custom_path: Optional[str] = None) -> str:
    """Menyusun ringkasan real-time status seluruh papan Kanban korporat."""
    try:
        project_id = await get_active_project_id(custom_path)
        tickets = await ticket_repo.get_tickets(project_id=project_id, custom_path=custom_path)
        counts = {"TODO": 0, "IN_PROGRESS": 0, "DONE": 0, "FAILED": 0, "BACKLOG": 0}
        for t in tickets:
            st = t.get("status", "TODO")
            counts[st] = counts.get(st, 0) + 1

        total = len(tickets)
        done_pct = round((counts["DONE"] / total * 100), 1) if total > 0 else 0.0

        return (
            f"📊 *Laporan Eksekutif Status Kanban Korporat*:\n"
            f"• Proyek Aktif: `{project_id}`\n"
            f"• Progres Selesai: *{done_pct}%* ({counts['DONE']}/{total} tiket)\n"
            f"• Antrean Kerja: TODO: *{counts['TODO']}* | IN_PROGRESS: *{counts['IN_PROGRESS']}*\n"
            f"• Tiket Gagal/Kendala: *{counts['FAILED']}* | Cadangan: *{counts['BACKLOG']}*\n\n"
            f"_Ketik `/tasks` untuk melihat daftar tiket atau `/task <perintah>` untuk menugaskan agen._"
        )
    except Exception as err:
        logger.error(f"Gagal menyusun status Kanban: {err}")
        return f"Maaf Founder, gagal memuat status korporat: {err}"


async def handle_tasks_list(limit: int = 5, custom_path: Optional[str] = None) -> str:
    """Menampilkan daftar tiket terbaru beserta status dan agen penanggung jawab."""
    try:
        project_id = await get_active_project_id(custom_path)
        tickets = await ticket_repo.get_tickets(project_id=project_id, custom_path=custom_path)
        if not tickets:
            return f"Belum ada tiket tugas terdaftar pada proyek `{project_id}`."

        active = [t for t in tickets if t.get("status") in ("IN_PROGRESS", "TODO")][:limit]
        if not active:
            active = tickets[-limit:]

        lines = [f"📋 *Daftar Tiket Terkini ({project_id})*:"]
        for t in active:
            role = t.get("assigned_role_id", "unassigned")
            st = t.get("status", "TODO")
            emoji = "🟢" if st == "DONE" else "🟡" if st == "IN_PROGRESS" else "🔴" if st == "FAILED" else "⚪"
            lines.append(f"{emoji} `[{t['id']}]` *{t['title']}* ({role}) - `{st}`")

        return "\n".join(lines)
    except Exception as err:
        logger.error(f"Gagal memuat daftar tiket: {err}")
        return f"Gagal membaca daftar tugas: {err}"


async def handle_create_task_from_telegram(text: str, custom_path: Optional[str] = None) -> str:
    """Mengekstrak tugas baru dari instruksi Founder dan langsung mendaftarkannya ke antrean Kanban."""
    # Bersihkan prefix /task jika ada
    clean_prompt = re.sub(r"^/task\s+", "", text, flags=re.I).strip()
    if not clean_prompt:
        return "Mohon sertakan deskripsi tugas, contoh: `/task Buat endpoint otentikasi JWT untuk backend`"

    try:
        project_id = await get_active_project_id(custom_path)
        roles = await role_repo.get_roles(custom_path=custom_path)

        # Temukan peran dan divisi yang valid
        target_role_id = roles[0]["id"] if roles else "role_be"
        target_div_id = roles[0].get("division_id", "div_eng") if roles else "div_eng"
        target_branch_id = roles[0].get("branch_id", "branch_main") if roles else "branch_main"
        lower_prompt = clean_prompt.lower()

        for r in roles:
            r_name = str(r.get("name", "")).lower()
            r_id = str(r.get("id", "")).lower()
            if any(k in lower_prompt for k in [r_name, r_id.replace("role_", "")]):
                target_role_id = r["id"]
                target_div_id = r.get("division_id", target_div_id)
                target_branch_id = r.get("branch_id", target_branch_id)
                break

        title = clean_prompt.split(".")[0][:60]
        new_ticket = await ticket_repo.create_ticket(
            branch_id=target_branch_id,
            project_id=project_id,
            division_id=target_div_id,
            title=title,
            description=clean_prompt,
            status="TODO",
            assigned_role_id=target_role_id,
            priority="HIGH",
            custom_path=custom_path,
        )

        logger.info(f"Secretary Task Bridge: Tiket baru dibuat [{new_ticket['id']}] untuk [{target_role_id}]")
        return (
            f"📌 *[Tiket Berhasil Didaftarkan ke Kanban]*\n"
            f"• ID Tiket: `{new_ticket['id']}`\n"
            f"• Judul: *{new_ticket['title']}*\n"
            f"• Penanggung Jawab: `{target_role_id}`\n"
            f"• Status: `TODO` (Akan segera dieksekusi otonom oleh Kanban Runner)\n\n"
            f"_Laporan hasil kerja agen akan otomatis dikirimkan ke obrolan ini saat selesai._"
        )
    except Exception as err:
        logger.error(f"Gagal membuat tiket via Telegram: {err}")
        return f"Gagal mendaftarkan tugas ke Kanban: {err}"
