"""
Global test configuration & fixtures for pytest.
Memastikan kompatibilitas runtime asinkron antara pytest-asyncio dan anyio TaskStateStore.
"""

from typing import Any

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
