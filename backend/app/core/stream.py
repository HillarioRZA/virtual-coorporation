"""
Server-Sent Events (SSE) Stream Manager.
Mengelola publikasi dan langganan event real-time asinkron berbasis asyncio.Queue.
"""

import asyncio
import json
from typing import Any, AsyncGenerator, Dict, Optional, Set

from app.core.logger import logger


class StreamManager:
    """Manajer in-memory pub/sub untuk Server-Sent Events per proyek."""

    def __init__(self) -> None:
        """Inisialisasi registry antrian per project_id."""
        self._subscribers: Dict[str, Set[asyncio.Queue[Dict[str, Any]]]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, project_id: str) -> asyncio.Queue[Dict[str, Any]]:
        """Mendaftarkan subscriber baru untuk menerima event proyek tertentu.

        Args:
            project_id: ID proyek sasaran.

        Returns:
            asyncio.Queue yang akan menerima pesan event.
        """
        queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        async with self._lock:
            if project_id not in self._subscribers:
                self._subscribers[project_id] = set()
            self._subscribers[project_id].add(queue)
            logger.debug(f"SSE Subscribed: Project [{project_id}] (Total: {len(self._subscribers[project_id])})")
        return queue

    async def unsubscribe(self, project_id: str, queue: asyncio.Queue[Dict[str, Any]]) -> None:
        """Menghapus subscriber dari registry proyek.

        Args:
            project_id: ID proyek sasaran.
            queue: Antrian subscriber yang akan dihentikan.
        """
        async with self._lock:
            if project_id in self._subscribers:
                self._subscribers[project_id].discard(queue)
                if not self._subscribers[project_id]:
                    del self._subscribers[project_id]
                logger.debug(f"SSE Unsubscribed: Project [{project_id}]")

    async def publish(self, project_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """Mempublikasikan event ke seluruh subscriber proyek yang aktif.

        Args:
            project_id: ID proyek sasaran.
            event_type: Tipe event (e.g. 'sparring_token', 'state_change').
            data: Payload dictionary event.
        """
        payload = {"event": event_type, "data": data}
        async with self._lock:
            subscribers = list(self._subscribers.get(project_id, set()))

        if not subscribers:
            logger.debug(f"SSE Publish skipped: Tidak ada subscriber aktif untuk [{project_id}]")
            return

        for q in subscribers:
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                logger.warning(f"SSE Queue penuh untuk subscriber project [{project_id}], drop event.")

    async def event_generator(
        self,
        project_id: str,
        heartbeat_interval: float = 15.0,
    ) -> AsyncGenerator[str, None]:
        """Menghasilkan format stream SSE standar dengan heartbeat berkala.

        Args:
            project_id: ID proyek sasaran.
            heartbeat_interval: Interval detik untuk mengirim keepalive ping.

        Yields:
            String terformat event-stream SSE.
        """
        queue = await self.subscribe(project_id)
        try:
            # Kirim event awal tanda koneksi berhasil
            init_data = json.dumps({"project_id": project_id, "status": "connected"})
            yield f"event: connected\ndata: {init_data}\n\n"

            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=heartbeat_interval)
                    event_name = msg.get("event", "message")
                    data_str = json.dumps(msg.get("data", {}))
                    yield f"event: {event_name}\ndata: {data_str}\n\n"
                except asyncio.TimeoutError:
                    # Heartbeat keepalive untuk menjaga koneksi tetap hidup
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            logger.debug(f"SSE Client disconnected untuk project [{project_id}]")
            raise
        finally:
            await self.unsubscribe(project_id, queue)


# Singleton instance global
stream_manager = StreamManager()
