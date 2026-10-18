"""
Base Protocol for LLM Provider Adapters.
Mendefinisikan kontrak interface terpadu untuk seluruh adapter penyedia LLM.
"""

from typing import Any, AsyncGenerator, Dict, Optional, Protocol


class BaseLLMAdapter(Protocol):
    """Protokol dasar antarmuka adapter penyedia LLM."""

    async def complete(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        api_key: str,
        base_url: str,
        temperature: float = 0.7,
        response_format: Optional[Dict[str, Any]] = None,
        thinking_level: str = "medium",
    ) -> str:
        """Mengirimkan permintaan teks completion non-streaming."""
        ...

    async def stream_tokens(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        api_key: str,
        base_url: str,
        temperature: float = 0.7,
        thinking_level: str = "medium",
    ) -> AsyncGenerator[str, None]:
        """Mengalirkan token secara real-time via generator asinkron."""
        ...
