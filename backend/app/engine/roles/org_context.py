"""
Corporate Organization Context Builder.
Menyusun konteks struktur organisasi aktif (Divisi, Tujuan, Peran, Jobdesk) untuk disuntikkan ke prompt LLM.
"""

from typing import Optional
from app.core.logger import logger
from app.db.division_repo import division_repo
from app.db.role_repo import role_repo


async def build_organization_context_prompt(
    branch_id: Optional[str] = None,
    custom_path: Optional[str] = None,
) -> str:
    """Membangun teks representasi hierarki organisasi korporat aktif.

    Args:
        branch_id: ID branch tertentu opsional.
        custom_path: Path SQLite kustom opsional.

    Returns:
        String struktur organisasi terformat.
    """
    try:
        divisions = await division_repo.get_divisions(branch_id=branch_id, custom_path=custom_path)
        roles = await role_repo.get_roles(branch_id=branch_id, custom_path=custom_path)
        if not divisions and not roles:
            return ""

        lines = ["STRUKTUR ORGANISASI KORPORAT AKTIF:"]
        for div in divisions:
            div_desc = div.get("description") or "Operasional Divisi"
            lines.append(f"Divisi: {div['name']} (Tujuan: {div_desc})")
            div_roles = [r for r in roles if r.get("division_id") == div["id"]]
            for r in div_roles:
                job = r.get("job_description") or "Menjalankan tugas spesialisasi peran"
                lines.append(f"  - Peran: @{r['name']} | Jobdesk: {job}")
        return "\n".join(lines)
    except Exception as err:
        logger.warning(f"Gagal memuat konteks organisasi: {err}")
        return ""
