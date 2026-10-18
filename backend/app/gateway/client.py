"""
Unified BYOK Multi-Provider LLM Gateway.
Menyediakan gerbang komunikasi terpadu dengan orkestrasi adapter dan fallback cascade otomatis.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
import httpx

from app.core.config import settings
from app.core.logger import logger
from app.gateway.adapters.anthropic_adapter import AnthropicAdapter
from app.gateway.adapters.gemini_adapter import GeminiAdapter
from app.gateway.adapters.openai_compatible import OpenAICompatibleAdapter
from app.gateway.base import BaseLLMAdapter


class UnifiedLLMClient:
    """Gateway HTTP Asinkron Universal untuk memanggil model apa pun via BYOK."""

    def __init__(self, transport: Optional[httpx.AsyncBaseTransport] = None) -> None:
        """Inisialisasi adapter untuk setiap keluarga penyedia model."""
        self.openai_compat = OpenAICompatibleAdapter(transport=transport)
        self.anthropic = AnthropicAdapter(transport=transport)
        self.gemini = GeminiAdapter(transport=transport)

    def _resolve_adapter(self, provider: str) -> BaseLLMAdapter:
        """Menentukan instance adapter yang sesuai berdasarkan nama provider."""
        prov = provider.lower()
        if prov in ["openai", "openai_compatible", "deepseek", "groq", "mistral", "ollama", "openrouter", "custom"]:
            return self.openai_compat
        elif prov == "anthropic":
            return self.anthropic
        elif prov == "gemini":
            return self.gemini
        else:
            raise ValueError(f"Provider LLM '{provider}' tidak dikenali.")

    def _resolve_credentials(self, provider: str) -> Tuple[str, str]:
        """Mengambil pasangan (api_key, base_url) secara dinamis dari konfigurasi sistem."""
        prov = provider.lower()
        if prov == "openrouter":
            return settings.OPENROUTER_API_KEY or "", settings.OPENROUTER_BASE_URL
        elif prov == "deepseek":
            return settings.DEEPSEEK_API_KEY or "", settings.DEEPSEEK_BASE_URL
        elif prov == "anthropic":
            return settings.ANTHROPIC_API_KEY or "", settings.ANTHROPIC_BASE_URL
        elif prov == "gemini":
            return settings.GEMINI_API_KEY or "", settings.GEMINI_BASE_URL
        elif prov == "ollama":
            return "", settings.OLLAMA_BASE_URL
        elif prov in ["openai_compatible", "custom"]:
            key = getattr(settings, "OPENAI_COMPATIBLE_API_KEY", "") or settings.OPENAI_API_KEY or ""
            base = getattr(settings, "OPENAI_COMPATIBLE_BASE_URL", "") or "https://api.openai.com/v1"
            return key, base
        else:
            return settings.OPENAI_API_KEY or "", settings.OPENAI_BASE_URL

    async def complete(
        self,
        prompt: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        response_format: Optional[Dict[str, Any]] = None,
        fallback_providers: Optional[List[Tuple[str, str]]] = None,
        thinking_level: str = "medium",
    ) -> str:
        """Panggilan completion teks dengan dukungan failover cascade otomatis."""
        active_provider = provider or "deepseek"
        active_model = model or "deepseek-reasoner"
        candidates = [(active_provider, active_model)]
        if fallback_providers:
            candidates.extend(fallback_providers)

        last_error: Optional[Exception] = None
        for prov, mdl in candidates:
            try:
                adapter = self._resolve_adapter(prov)
                api_key, base_url = self._resolve_credentials(prov)
                logger.info(f"Mengirim LLM Completion via Provider: [{prov}] | Model: [{mdl}]")
                return await adapter.complete(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=mdl,
                    api_key=api_key,
                    base_url=base_url,
                    temperature=temperature,
                    response_format=response_format,
                    thinking_level=thinking_level,
                )
            except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.RequestError) as err:
                last_error = err
                logger.warning(f"Provider [{prov}] mengalami kegagalan: {err}. Mencoba provider berikutnya...")
                continue

        logger.error(f"Seluruh kandidat provider gagal dieksekusi: {last_error}")
        raise RuntimeError(f"All LLM providers failed: {last_error}") from last_error

    async def stream_tokens(
        self,
        prompt: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        thinking_level: str = "medium",
    ) -> AsyncGenerator[str, None]:
        """Panggilan completion streaming token secara real-time."""
        active_provider = provider or "deepseek"
        active_model = model or "deepseek-reasoner"
        adapter = self._resolve_adapter(active_provider)
        api_key, base_url = self._resolve_credentials(active_provider)

        logger.info(f"Memulai streaming token LLM via Provider: [{active_provider}] | Model: [{active_model}]")
        async for token in adapter.stream_tokens(
            prompt=prompt,
            system_prompt=system_prompt,
            model=active_model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            thinking_level=thinking_level,
        ):
            yield token
