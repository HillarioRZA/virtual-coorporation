"""
Database Schema Initialization & Migration.
Membuat tabel SQLite fisik untuk projek, log event memori, checkpoints, ledger, PR, dan wisdom base.
"""

from typing import Optional
import aiosqlite

from app.core.logger import logger
from app.db.session import get_db_connection
from app.db.schema import DDL_SCHEMA
from app.db.ledger_schema import LEDGER_DDL_SCHEMA
from app.db.pr_schema import PR_DDL_SCHEMA
from app.db.wisdom_schema import WISDOM_DDL_SCHEMA
from app.db.sentinel_schema import SENTINEL_DDL_SCHEMA
from app.db.corporate_seeder import (
    seed_default_corporate_structure,
    seed_default_pipeline_stages,
    seed_default_corporate_wisdom,
    migrate_order_index,
    migrate_role_fallback_chain,
    migrate_branch_parent_column,
    migrate_role_thinking_level_column,
    migrate_rich_system_prompts,
)


async def init_database(custom_path: Optional[str] = None) -> None:
    """Menginisialisasi seluruh skema tabel, indeks, ledger, PR, dan wisdom base pada SQLite.

    Args:
        custom_path: Path basis data opsional (misal untuk testing).

    Raises:
        aiosqlite.Error: Jika terjadi kegagalan eksekusi skrip DDL.
    """
    logger.info("Memulai inisialisasi skema basis data SQLite...")
    try:
        async with get_db_connection(custom_path) as conn:
            await conn.executescript(DDL_SCHEMA)
            await conn.executescript(LEDGER_DDL_SCHEMA)
            await conn.executescript(PR_DDL_SCHEMA)
            await conn.executescript(WISDOM_DDL_SCHEMA)
            await conn.executescript(SENTINEL_DDL_SCHEMA)
            await migrate_order_index(conn)
            await migrate_role_fallback_chain(conn)
            await migrate_branch_parent_column(conn)
            await migrate_role_thinking_level_column(conn)
            await seed_default_corporate_structure(conn)
            await migrate_rich_system_prompts(conn)
            await seed_default_pipeline_stages(conn)
            await seed_default_corporate_wisdom(conn)
            await conn.commit()
            logger.info("Skema basis data SQLite, ledger, PR, & Corporate Wisdom berhasil divalidasi.")
    except aiosqlite.Error as err:
        logger.error(f"Gagal mengeksekusi DDL skema database: {err}")
        raise
