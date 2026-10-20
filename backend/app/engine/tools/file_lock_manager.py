"""
Workspace File Lock Manager Subsystem.
Menyediakan mekanisme penguncian berkas asinkron per-file path (asyncio.Lock)
untuk mencegah race condition saat multi-agen menulis/memodifikasi berkas secara paralel.
"""

import asyncio
from contextlib import asynccontextmanager
import os
from typing import AsyncGenerator, Dict
from loguru import logger


class FileLockManager:
    """Manajer penguncian berkas konkurensi tingkat proyek dan berkas."""

    def __init__(self) -> None:
        self._locks: Dict[str, asyncio.Lock] = {}
        self._meta_lock = asyncio.Lock()

    @asynccontextmanager
    async def acquire(self, project_id: str, file_path: str) -> AsyncGenerator[None, None]:
        """Mengakuisisi kunci berkas spesifik secara asinkron sebelum operasi I/O."""
        normalized_path = os.path.normpath(file_path).replace("\\", "/").lower()
        key = f"{project_id}:{normalized_path}"

        async with self._meta_lock:
            if key not in self._locks:
                self._locks[key] = asyncio.Lock()
            lock = self._locks[key]

        logger.debug(f"Menunggu file lock untuk [{key}]...")
        async with lock:
            logger.debug(f"File lock didapatkan untuk [{key}].")
            try:
                yield
            finally:
                logger.debug(f"File lock dilepaskan untuk [{key}].")


file_lock_manager = FileLockManager()
