"""
Base Contract Handler Interface.
Mendefinisikan antarmuka abstrak untuk seluruh polymorphic contract handlers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.engine.runtime.state import VentureState


class BaseContractHandler(ABC):
    """Kelas abstrak dasar untuk penangan kontrak spesifik artefak."""

    @abstractmethod
    def can_handle(self, payload: Dict[str, Any]) -> bool:
        """Memeriksa apakah kontrak payload cocok ditangani oleh handler ini."""
        pass

    @abstractmethod
    async def handle(
        self,
        payload: Dict[str, Any],
        state: VentureState,
        sbx: Optional[Any] = None,
        proxy: Optional[Any] = None,
        vault: Optional[Any] = None,
    ) -> None:
        """Mengeksekusi penyelarasan state dan side-effect berdasarkan payload."""
        pass
