"""
System Prompts Registry & Loader.
Memuat dan men-cache system prompt untuk 11 peran agen dari file markdown.
"""

from pathlib import Path
from typing import Dict, Optional

from app.core.logger import logger

# Direktori penyimpanan file prompt (backend/prompts/)
PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"

# Cache in-memory untuk menghindari pembacaan disk berulang
_PROMPT_CACHE: Dict[str, str] = {}


def load_prompt(role: str, custom_dir: Optional[Path] = None) -> str:
    """Memuat system prompt untuk peran agen tertentu.

    Args:
        role: Nama peran agen (e.g. 'COS', 'CTO', 'PM').
        custom_dir: Direktori kustom opsional (untuk testing).

    Returns:
        String isi system prompt.

    Raises:
        FileNotFoundError: Jika file prompt tidak ditemukan dan tidak ada fallback.
    """
    normalized_role = role.lower().strip()
    cache_key = f"{normalized_role}_{custom_dir or 'default'}"

    if cache_key in _PROMPT_CACHE:
        return _PROMPT_CACHE[cache_key]

    target_dir = custom_dir or PROMPTS_DIR
    prompt_file = target_dir / f"{normalized_role}_prompt.md"

    if not prompt_file.exists():
        from app.db.corporate_prompts import DEFAULT_ROLE_PROMPTS
        fallback = DEFAULT_ROLE_PROMPTS.get(
            normalized_role, f"Anda adalah agen {role.upper()} yang bertugas sesuai keahlian teknis Anda."
        )
        _PROMPT_CACHE[cache_key] = fallback
        return fallback

    try:
        content = prompt_file.read_text(encoding="utf-8")
        _PROMPT_CACHE[cache_key] = content
        logger.debug(f"Prompt loaded and cached for role: [{role.upper()}] from {prompt_file.name}")
        return content
    except OSError as err:
        logger.error(f"Gagal membaca file prompt [{prompt_file}]: {err}")
        raise


def clear_prompt_cache() -> None:
    """Membersihkan cache prompt (berguna saat reload atau pengujian)."""
    _PROMPT_CACHE.clear()
    logger.debug("Prompt cache cleared.")
