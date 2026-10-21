"""
SQLite Blackboard Memory & Context Projection Manager.
Mengelola persistensi event multi-agen, checkpointing state, dan perakitan working memory 3-tier.
"""

from typing import Any, Dict, List, Optional
import aiosqlite

from app.core.logger import logger
from app.db.session import get_db_connection
from app.engine.runtime.checkpointer import StateCheckpointer
from app.engine.memory.context_builder import ContextBuilder
from app.engine.runtime.state import VentureState


class MemoryManager:
    """Manajer memori terpusat berbasis SQLite Blackboard Event Store."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path
        self.checkpointer = StateCheckpointer(db_path=db_path)

    async def ensure_project(
        self, project_id: str, name: str = "Untitled Venture",
        founder_idea: str = "", archetype_id: int = 1, stage: str = "SPARRING_ROOM",
    ) -> None:
        """Memastikan record proyek induk tersedia di tabel projects."""
        try:
            async with get_db_connection(self.db_path) as conn:
                await conn.execute(
                    "INSERT OR IGNORE INTO projects (id, name, stage, archetype_id, founder_idea) VALUES (?, ?, ?, ?, ?)",
                    (project_id, name, stage, archetype_id, founder_idea),
                )
                await conn.commit()
        except aiosqlite.Error as err:
            logger.error(f"Gagal memastikan record proyek [{project_id}]: {err}")
            raise

    async def log_event(
        self, project_id: str, stage: str, sender_role: str, recipient_role: str,
        event_type: str, content: str, artifact_ref: Optional[str] = None, token_cost: float = 0.0,
    ) -> int:
        """Menyimpan entri percakapan/aksi baru ke blackboard agent_event_logs."""
        await self.ensure_project(project_id, stage=stage)
        try:
            async with get_db_connection(self.db_path) as conn:
                sql = (
                    "INSERT INTO agent_event_logs "
                    "(project_id, stage, sender_role, recipient_role, event_type, content, artifact_ref, token_cost) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                )
                cursor = await conn.execute(
                    sql,
                    (project_id, stage, sender_role, recipient_role, event_type, content, artifact_ref, token_cost),
                )
                await conn.commit()
                log_id = cursor.lastrowid or 0
                logger.debug(f"Event Logged [ID:{log_id}] {sender_role}->{recipient_role} ({stage})")
                return log_id
        except aiosqlite.Error as err:
            logger.error(f"Gagal mencatat event ke blackboard: {err}")
            raise

    async def get_event_logs(
        self, project_id: str, stage: Optional[str] = None, limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Mengambil riwayat event log dari blackboard."""
        query = "SELECT * FROM agent_event_logs WHERE project_id = ?"
        params: List[Any] = [project_id]
        if stage:
            query += " AND stage = ?"
            params.append(stage)
        query += " ORDER BY id ASC LIMIT ?"
        params.append(limit)

        try:
            async with get_db_connection(self.db_path) as conn:
                cursor = await conn.execute(query, tuple(params))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except aiosqlite.Error as err:
            logger.error(f"Gagal mengambil riwayat event log: {err}")
            raise

    async def save_checkpoint(self, state: VentureState) -> int:
        """Menyimpan snapshot VentureState ke tabel state_checkpoints."""
        await self.ensure_project(
            project_id=state.project_id, name=state.project_name,
            founder_idea=state.founder_idea, archetype_id=state.selected_archetype, stage=state.stage,
        )
        return await self.checkpointer.save_checkpoint(state)

    async def load_latest_checkpoint(self, project_id: str) -> Optional[VentureState]:
        """Memuat checkpoint terakhir untuk memulihkan VentureState."""
        return await self.checkpointer.load_latest_checkpoint(project_id)

    async def build_context_for_agent(
        self,
        project_id: str,
        target_role: str,
        state: VentureState,
        limit_recent_messages: int = 6,
        role_permissions: Optional[List[str]] = None,
    ) -> List[Dict[str, str]]:
        """Merakit working memory 3-tier untuk pemanggilan model LLM agen tertentu."""
        role = target_role.upper()
        try:
            async with get_db_connection(self.db_path) as conn:
                sql = (
                    "SELECT sender_role, recipient_role, event_type, content, artifact_ref, created_at "
                    "FROM agent_event_logs WHERE project_id = ? "
                    "AND (recipient_role = ? OR recipient_role = 'BROADCAST' OR sender_role = ?) ORDER BY id ASC"
                )
                cursor = await conn.execute(sql, (project_id, role, role))
                rows = await cursor.fetchall()
                scoped_events = [dict(r) for r in rows]

            return ContextBuilder.assemble_context(
                target_role=role,
                state=state,
                scoped_events=scoped_events,
                limit_recent_messages=limit_recent_messages,
                role_permissions=role_permissions,
            )
        except aiosqlite.Error as err:
            logger.error(f"Gagal merakit konteks memori untuk role [{role}]: {err}")
            raise
