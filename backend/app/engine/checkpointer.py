"""
State Checkpointer Persistence Engine.
Menyimpan dan memuat snapshot VentureState ter-versi ke tabel state_checkpoints.
"""

import json
from typing import Optional
import aiosqlite

from app.core.logger import logger
from app.db.session import get_db_connection
from app.engine.state import VentureState


class StateCheckpointer:
    """Pengelola snapshot serialisasi state proyek ke SQLite."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        """Inisialisasi checkpointer.

        Args:
            db_path: Path basis data khusus (opsional).
        """
        self.db_path = db_path

    async def save_checkpoint(self, state: VentureState) -> int:
        """Menyimpan snapshot VentureState ke tabel state_checkpoints.

        Args:
            state: Instance VentureState yang akan disimpan.

        Returns:
            ID entri checkpoint yang baru dibuat.
        """
        state_blob = json.dumps(state.to_dict())
        try:
            async with get_db_connection(self.db_path) as conn:
                cursor = await conn.execute(
                    "SELECT COALESCE(MAX(step_number), 0) + 1 FROM state_checkpoints WHERE project_id = ?",
                    (state.project_id,),
                )
                step_row = await cursor.fetchone()
                step_number = step_row[0] if step_row else 1

                ins_cursor = await conn.execute(
                    """
                    INSERT INTO state_checkpoints (project_id, stage, state_blob, step_number)
                    VALUES (?, ?, ?, ?)
                    """,
                    (state.project_id, state.stage, state_blob, step_number),
                )
                await conn.execute(
                    "UPDATE projects SET stage = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (state.stage, state.project_id),
                )
                await conn.commit()
                checkpoint_id = ins_cursor.lastrowid or 0
                logger.info(f"Checkpoint Saved [ID:{checkpoint_id} | Step:{step_number}] for {state.project_id}")
                return checkpoint_id
        except aiosqlite.Error as err:
            logger.error(f"Gagal menyimpan checkpoint state [{state.project_id}]: {err}")
            raise

    async def load_latest_checkpoint(self, project_id: str) -> Optional[VentureState]:
        """Memuat snapshot state terakhir untuk memulihkan VentureState.

        Args:
            project_id: ID proyek sasaran.

        Returns:
            VentureState tervalidasi atau None jika belum ada checkpoint.
        """
        try:
            async with get_db_connection(self.db_path) as conn:
                cursor = await conn.execute(
                    """
                    SELECT state_blob FROM state_checkpoints
                    WHERE project_id = ?
                    ORDER BY step_number DESC, id DESC LIMIT 1
                    """,
                    (project_id,),
                )
                row = await cursor.fetchone()
                if not row:
                    return None
                data = json.loads(row["state_blob"])
                return VentureState.from_dict(data)
        except (aiosqlite.Error, json.JSONDecodeError, ValueError) as err:
            logger.error(f"Gagal memuat checkpoint untuk [{project_id}]: {err}")
            raise
