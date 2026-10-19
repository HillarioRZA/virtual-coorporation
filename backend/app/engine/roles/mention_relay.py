"""
Agent-to-Agent Mention & Baton Relay Engine.
Mendeteksi @mention pada respons agen, mengabaikan self-mention, dan menerapkan guardrail MAX_RELAY_HOPS = 3.
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple
from app.core.logger import logger

MAX_RELAY_HOPS = 3
BROADCAST_TOKENS: Set[str] = {"all", "everyone", "executives", "broadcast", "channel", "here"}
ROLE_ALIASES: Dict[str, str] = {
    "cos": "Chief of Staff",
    "cto": "Chief Technology Officer",
    "pm": "Product Manager",
    "ux": "UI/UX Architect",
    "ui/ux": "UI/UX Architect",
    "fe": "Frontend Engineer",
    "frontend": "Frontend Engineer",
    "be": "Backend Engineer",
    "backend": "Backend Engineer",
    "qa": "QA & SecOps Engineer",
}


def parse_chat_mentions(
    message: str, active_roles: List[Dict[str, Any]]
) -> Tuple[bool, List[Dict[str, Any]]]:
    """Mendeteksi apakah pesan ditujukan untuk broadcast atau peran spesifik.

    Args:
        message: Isi teks pesan Founder atau agen.
        active_roles: Daftar kamus peran aktif dari basis data.

    Returns:
        Tuple (is_broadcast, list_peran_tertuju).
    """
    clean_msg = message.lower()
    for token in BROADCAST_TOKENS:
        if re.search(rf"@{re.escape(token)}\b", clean_msg):
            return True, []

    matched_roles: List[Dict[str, Any]] = []
    matched_ids: Set[str] = set()

    # Urutkan peran dari nama terpanjang ke terpendek untuk prioritas multi-kata
    sorted_roles = sorted(active_roles, key=lambda r: len(r.get("name", "")), reverse=True)

    for role in sorted_roles:
        r_name = role.get("name", "").strip()
        if not r_name:
            continue
        # Cek @Nama Peran (misal @Chief of Staff)
        pattern = rf"@{re.escape(r_name.lower())}\b"
        if re.search(pattern, clean_msg):
            if role["id"] not in matched_ids:
                matched_ids.add(role["id"])
                matched_roles.append(role)

    # Cek alias singkat (misal @CTO, @CoS)
    for alias, full_name in ROLE_ALIASES.items():
        if re.search(rf"@{re.escape(alias)}\b", clean_msg):
            for role in active_roles:
                if role.get("name", "").lower() == full_name.lower():
                    if role["id"] not in matched_ids:
                        matched_ids.add(role["id"])
                        matched_roles.append(role)

    is_broadcast = len(matched_roles) == 0 and ("@" not in clean_msg or any(f"@{b}" in clean_msg for b in BROADCAST_TOKENS))
    return is_broadcast, matched_roles


def extract_relay_mentions(
    content: str, sender_role: str, active_roles: Optional[List[Dict[str, Any]]] = None
) -> List[str]:
    """Mengekstraksi daftar nama/ID peran sasaran yang di-mention tanpa self-mention.

    Args:
        content: Teks respons agen.
        sender_role: Nama atau ID peran pengirim saat ini.
        active_roles: Daftar peran aktif opsional.

    Returns:
        List identifier peran target yang valid.
    """
    sender_norm = sender_role.lower().strip()
    targets: List[str] = []

    if active_roles:
        _, mentioned = parse_chat_mentions(content, active_roles)
        for r in mentioned:
            r_name = r.get("name", "").lower()
            r_id = r.get("id", "").lower()
            if r_name == sender_norm or r_id == sender_norm:
                continue
            targets.append(r["id"])
        return targets

    # Fallback regex jika data roles belum termuat
    raw = re.findall(r"@([\w\s]{2,30})\b", content)
    for m in raw:
        norm = m.strip().lower()
        if norm in BROADCAST_TOKENS or norm == sender_norm:
            continue
        if norm not in targets:
            targets.append(norm)
    return targets


def can_relay(relay_hop: int) -> bool:
    """Mengecek apakah relay hop masih dalam batas guardrail aman."""
    if relay_hop >= MAX_RELAY_HOPS:
        logger.warning(f"Baton Relay Guardrail: Max hops ({MAX_RELAY_HOPS}) tercapai.")
        return False
    return True
