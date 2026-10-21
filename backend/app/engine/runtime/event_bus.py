"""
Corporate Asynchronous Event Bus.
Mengelola publikasi dan langganan event inter-agent secara real-time berbasis asyncio.Queue
serta persistensi log pesan ke tabel SQLite WAL.
"""

import asyncio
from typing import Any, Dict, List, Optional, Set
import aiosqlite

from app.core.logger import logger
from app.db.session import get_db_connection
from app.engine.schemas.corporate_schemas import CorporateMessageCreate


class CorporateEventBus:
    """Event bus asinkron terdistribusi untuk komunikasi dan koordinasi antar-agen korporat."""

    def __init__(self) -> None:
        """Inisialisasi registry antrian subscriber dan lock sinkronisasi."""
        self._subscribers: Dict[str, Set[asyncio.Queue[Dict[str, Any]]]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, project_id: str) -> asyncio.Queue[Dict[str, Any]]:
        """Mendaftarkan antrean subscriber baru untuk mendengarkan event proyek tertentu.

        Args:
            project_id: ID proyek sasaran.

        Returns:
            asyncio.Queue yang akan menerima payload event secara real-time.
        """
        queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        async with self._lock:
            if project_id not in self._subscribers:
                self._subscribers[project_id] = set()
            self._subscribers[project_id].add(queue)
            logger.debug(f"EventBus Subscribed: Project [{project_id}] (Total: {len(self._subscribers[project_id])})")
        return queue

    async def unsubscribe(self, project_id: str, queue: asyncio.Queue[Dict[str, Any]]) -> None:
        """Menghapus antrean subscriber dari registry proyek.

        Args:
            project_id: ID proyek sasaran.
            queue: Antrian subscriber yang akan dilepas.
        """
        async with self._lock:
            if project_id in self._subscribers:
                self._subscribers[project_id].discard(queue)
                if not self._subscribers[project_id]:
                    del self._subscribers[project_id]
                logger.debug(f"EventBus Unsubscribed: Project [{project_id}]")

    async def publish(self, event: CorporateMessageCreate, custom_path: Optional[str] = None) -> Dict[str, Any]:
        """Menyimpan pesan ke basis data dan menyiarkannya ke seluruh subscriber aktif.

        Args:
            event: Data DTO pesan yang akan dipublikasikan.
            custom_path: Path basis data khusus opsional.

        Returns:
            Dict representasi pesan yang tersimpan lengkap dengan ID dan timestamp.

        Raises:
            aiosqlite.Error: Jika terjadi kegagalan penulisan basis data SQLite.
        """
        msg_id: int = 0
        created_at: str = ""
        query = """
            INSERT INTO corporate_messages 
            (branch_id, project_id, channel_type, sender_role_id, recipient_role_id, ticket_id, event_type, content, token_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id, created_at;
        """
        try:
            async with get_db_connection(custom_path) as conn:
                await conn.execute(
                    "INSERT OR IGNORE INTO projects (id, name, founder_idea) VALUES (?, ?, ?);",
                    (event.project_id, event.project_id, "Corporate Project Workspace"),
                )
                async with conn.execute(
                    query,
                    (
                        event.branch_id,
                        event.project_id,
                        event.channel_type,
                        event.sender_role_id,
                        event.recipient_role_id,
                        event.ticket_id,
                        event.event_type,
                        event.content,
                        event.token_cost,
                    ),
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        msg_id = int(row["id"])
                        created_at = str(row["created_at"])
                await conn.commit()
        except aiosqlite.Error as err:
            logger.error(f"Gagal mencatat event ke basis data: {err}")
            raise

        payload: Dict[str, Any] = {
            "id": msg_id,
            "branch_id": event.branch_id,
            "project_id": event.project_id,
            "channel_type": event.channel_type,
            "sender_role_id": event.sender_role_id,
            "recipient_role_id": event.recipient_role_id,
            "ticket_id": event.ticket_id,
            "event_type": event.event_type,
            "content": event.content,
            "token_cost": event.token_cost,
            "created_at": created_at,
        }

        # Broadcast in-memory non-blocking ke subscriber aktif
        async with self._lock:
            subscribers = self._subscribers.get(event.project_id, set()).copy()
            if "*" in self._subscribers:
                subscribers.update(self._subscribers["*"])

        for sub_queue in subscribers:
            try:
                sub_queue.put_nowait(payload)
            except asyncio.QueueFull:
                logger.warning(f"Antrian subscriber penuh untuk project {event.project_id}, pesan dilewati.")

        logger.info(f"EventBus Broadcast [{event.event_type}] from {event.sender_role_id} in {event.project_id}")
        return payload

    async def get_history(
        self, project_id: str, limit: int = 50, custom_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Mengambil riwayat pesan dan event log untuk proyek tertentu.

        Args:
            project_id: ID proyek sasaran.
            limit: Jumlah maksimum pesan terambil.
            custom_path: Path basis data opsional.

        Returns:
            List dictionary pesan terurut waktu menaik.
        """
        query = """
            SELECT id, branch_id, project_id, channel_type, sender_role_id, recipient_role_id,
                   ticket_id, event_type, content, token_cost, created_at
            FROM corporate_messages
            WHERE project_id = ?
            ORDER BY id DESC
            LIMIT ?;
        """
        async with get_db_connection(custom_path) as conn:
            async with conn.execute(query, (project_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]


corporate_event_bus = CorporateEventBus()
