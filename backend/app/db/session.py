"""
SQLite Database Session & Connection Management.
Mengelola koneksi aiosqlite asinkron dengan optimasi WAL (Write-Ahead Logging).
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import os
from pathlib import Path
from typing import Optional
import aiosqlite

from app.core.config import BASE_DIR, settings
from app.core.logger import logger


def resolve_db_path(custom_path: Optional[str] = None) -> str:
    """Menentukan path file database SQLite dan memastikan direktori induk tersedia.

    Args:
        custom_path: Path basis data khusus (misal untuk testing).

    Returns:
        String path absolut atau relatif ke file database.
    """
    raw_path = custom_path or settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    db_file = Path(raw_path)
    if not db_file.is_absolute():
        db_file = (BASE_DIR / db_file).resolve()
    if not db_file.parent.exists():
        try:
            db_file.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Direktori database dibuat: {db_file.parent}")
        except OSError as err:
            logger.error(f"Gagal membuat direktori database {db_file.parent}: {err}")
            raise
    return str(db_file)


@asynccontextmanager
async def get_db_connection(custom_path: Optional[str] = None) -> AsyncGenerator[aiosqlite.Connection, None]:
    """Context manager asinkron untuk koneksi SQLite dengan konfigurasi PRAGMA optimal.

    Args:
        custom_path: Path basis data opsional.

    Yields:
        aiosqlite.Connection terkonfigurasi.
    """
    db_path = resolve_db_path(custom_path)
    try:
        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row
            # Konfigurasi WAL mode untuk konkurensi pembacaan & penulisan paralel
            await conn.execute("PRAGMA journal_mode = WAL;")
            await conn.execute("PRAGMA synchronous = NORMAL;")
            await conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
    except aiosqlite.Error as err:
        logger.error(f"Kesalahan koneksi SQLite ({db_path}): {err}")
        raise
