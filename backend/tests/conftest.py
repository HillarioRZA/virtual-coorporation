"""
Global test configuration & fixtures for pytest.
Memastikan kompatibilitas runtime asinkron antara pytest-asyncio dan anyio TaskStateStore,
serta menyediakan isolasi basis data total agar pengujian tidak mencemari database produksi.
"""

import asyncio
from pathlib import Path
from typing import Any
import pytest

from app.core.config import settings
from app.core.logger import logger
from app.db.init_db import init_database

try:
    import anyio._backends._asyncio

    def _safe_task_state_getitem(self: Any, key: Any) -> Any:
        try:
            return self._task_states[key]
        except KeyError:
            if hasattr(key, "get_coro") and (coro := key.get_coro()):
                if state := self._preliminary_task_states.get(coro):
                    return state
        raise KeyError(key)

    def _safe_task_state_setitem(self: Any, key: Any, value: Any) -> None:
        if hasattr(key, "get_coro"):
            self._task_states[key] = value
        else:
            self._preliminary_task_states[key] = value

    def _safe_task_state_delitem(self: Any, key: Any) -> None:
        if hasattr(key, "get_coro"):
            if key in self._task_states:
                del self._task_states[key]
        else:
            if key in self._preliminary_task_states:
                del self._preliminary_task_states[key]

    anyio._backends._asyncio.TaskStateStore.__getitem__ = _safe_task_state_getitem
    anyio._backends._asyncio.TaskStateStore.__setitem__ = _safe_task_state_setitem
    anyio._backends._asyncio.TaskStateStore.__delitem__ = _safe_task_state_delitem
except Exception:
    pass


def pytest_configure(config: pytest.Config) -> None:
    """Konfigurasi global pytest: mengalihkan basis data default ke file uji terisolasi.

    Args:
        config: Konfigurasi sesi pytest.
    """
    test_db_dir = Path(__file__).resolve().parent / ".test_cache"
    try:
        test_db_dir.mkdir(parents=True, exist_ok=True)
    except OSError as err:
        logger.error(f"Gagal membuat direktori cache test: {err}")
        return

    test_db_file = test_db_dir / "test_isolated_suite.db"
    if test_db_file.exists():
        try:
            test_db_file.unlink()
        except OSError as err:
            logger.warning(f"Gagal menghapus file DB test lama: {err}")

    settings.DATABASE_URL = f"sqlite+aiosqlite:///{test_db_file}"
    try:
        asyncio.run(init_database(str(test_db_file)))
    except Exception as err:
        logger.error(f"Gagal menginisialisasi DB uji terisolasi: {err}")


def pytest_unconfigure(config: pytest.Config) -> None:
    """Membersihkan file basis data uji terisolasi setelah seluruh pengujian selesai.

    Args:
        config: Konfigurasi sesi pytest.
    """
    test_db_dir = Path(__file__).resolve().parent / ".test_cache"
    test_db_file = test_db_dir / "test_isolated_suite.db"
    if test_db_file.exists():
        try:
            test_db_file.unlink()
        except OSError:
            pass
