"""
Agent Worker Pool Manager.
Mengelola siklus hidup background task asyncio untuk eksekusi agen secara non-blocking,
termasuk pemantauan status, penanganan exception terisolasi, dan graceful cancellation.
"""

import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set

from app.core.logger import logger


class AgentWorkerPool:
    """Manajer worker pool asinkron untuk tugas agen otonom berbasis asyncio.Task."""

    def __init__(self) -> None:
        """Inisialisasi registry task aktif dan lock sinkronisasi."""
        self._active_tasks: Set[asyncio.Task] = set()
        self._task_metadata: Dict[asyncio.Task, str] = {}
        self._lock = asyncio.Lock()

    def spawn_worker(self, role_slug: str, coro: Awaitable[Any]) -> asyncio.Task:
        """Mendaftarkan dan meluncurkan task worker asinkron baru.

        Args:
            role_slug: Identifier peran agen pelaksana (misal: 'frontend', 'backend').
            coro: Coroutine fungsi yang akan dijalankan.

        Returns:
            asyncio.Task yang sedang berjalan di background event loop.
        """
        task = asyncio.create_task(coro)
        self._active_tasks.add(task)
        self._task_metadata[task] = role_slug

        def _on_done(t: asyncio.Task) -> None:
            self._active_tasks.discard(t)
            role = self._task_metadata.pop(t, "unknown")
            if t.cancelled():
                logger.info(f"Worker [{role}] dibatalkan secara graceful.")
            elif t.exception():
                logger.error(f"Worker [{role}] mengalami kegagalan: {t.exception()}")
            else:
                logger.info(f"Worker [{role}] berhasil menyelesaikan tugasnya.")

        task.add_done_callback(_on_done)
        logger.debug(f"Worker [{role_slug}] spawned. Total aktif: {len(self._active_tasks)}")
        return task

    async def wait_all(self, timeout: float = 60.0) -> List[Any]:
        """Menunggu seluruh worker yang aktif menyelesaikan eksekusinya.

        Args:
            timeout: Batas waktu tunggu maksimal dalam detik.

        Returns:
            List hasil kembalian dari task yang selesai dengan sukses.

        Raises:
            asyncio.TimeoutError: Jika eksekusi melampaui batas timeout yang ditentukan.
        """
        if not self._active_tasks:
            return []

        tasks_to_wait = list(self._active_tasks)
        done, pending = await asyncio.wait(tasks_to_wait, timeout=timeout)

        if pending:
            logger.warning(f"{len(pending)} worker tasks melampaui batas timeout ({timeout}s).")

        results = []
        for t in done:
            if not t.cancelled() and not t.exception():
                results.append(t.result())
        return results

    async def cancel_all(self) -> None:
        """Membatalkan seluruh worker yang sedang aktif secara graceful."""
        if not self._active_tasks:
            return

        logger.info(f"Membatalkan {len(self._active_tasks)} worker tasks aktif...")
        for task in list(self._active_tasks):
            if not task.done():
                task.cancel()

        # Tunggu sampai seluruh task menerima sinyal cancel
        await asyncio.gather(*list(self._active_tasks), return_exceptions=True)
        self._active_tasks.clear()
        self._task_metadata.clear()
        logger.info("Seluruh worker tasks berhasil dibatalkan dan dibersihkan.")

    def active_workers_count(self) -> int:
        """Mengembalikan jumlah worker yang sedang aktif saat ini.

        Returns:
            Integer total worker aktif.
        """
        return len(self._active_tasks)


agent_worker_pool = AgentWorkerPool()
