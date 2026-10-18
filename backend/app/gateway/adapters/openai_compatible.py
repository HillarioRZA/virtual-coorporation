"""
OpenAI-Compatible LLM Provider Adapter.
Mendukung OpenAI, DeepSeek, Groq, Mistral, Ollama lokal, dan OpenRouter.
"""

import json
from typing import Any, AsyncGenerator, Dict, List, Optional
import httpx

from app.core.logger import logger


class OpenAICompatibleAdapter:
    """Adapter untuk seluruh penyedia model yang mengimplementasikan spesifikasi REST OpenAI."""

    def __init__(
        self,
        timeout_seconds: float = 90.0,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        """Inisialisasi adapter dengan konfigurasi timeout dan transport opsional.

        Args:
            timeout_seconds: Durasi batas waktu permintaan HTTP (default: 90s).
            transport: Custom async transport (berguna untuk testing/mocking).
        """
        self.timeout = httpx.Timeout(timeout_seconds, connect=10.0)
        self.transport = transport

    def _build_headers(self, api_key: str, base_url: str) -> Dict[str, str]:
        """Membangun header HTTP termasuk metadata khusus OpenRouter jika relevan."""
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        if "openrouter.ai" in base_url:
            headers["HTTP-Referer"] = "http://localhost:3000"
            headers["X-Title"] = "Virtual Tech Startup Studio"
        return headers

    def _build_deterministic_messages(self, prompt: str, system_prompt: str) -> List[Dict[str, str]]:
        """Menyusun struktur pesan statis deterministik (system prompt di blok awal) untuk prefix caching."""
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt.strip()})
        messages.append({"role": "user", "content": prompt.strip()})
        return messages

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
        """Panggilan completion non-streaming OpenAI-compatible dengan prefix caching."""
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = self._build_headers(api_key, base_url)
        payload: Dict[str, Any] = {
            "model": model,
            "messages": self._build_deterministic_messages(prompt, system_prompt),
            "temperature": temperature,
        }
        if thinking_level in ("low", "medium", "high"):
            payload["reasoning_effort"] = thinking_level
        if response_format:
            payload["response_format"] = response_format

        try:
            async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client:
                res = await client.post(url, headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as err:
            logger.error(f"OpenAI-compatible HTTP {err.response.status_code} Error: {err.response.text}")
            raise
        except (httpx.TimeoutException, httpx.RequestError) as err:
            logger.error(f"OpenAI-compatible Network/Timeout Error: {err}")
            raise

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
        """Panggilan completion streaming via Server-Sent Events (SSE)."""
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = self._build_headers(api_key, base_url)
        payload: Dict[str, Any] = {
            "model": model,
            "messages": self._build_deterministic_messages(prompt, system_prompt),
            "temperature": temperature,
            "stream": True,
        }
        if thinking_level in ("low", "medium", "high"):
            payload["reasoning_effort"] = thinking_level

        try:
            async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as res:
                    res.raise_for_status()
                    async for line in res.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            token = chunk["choices"][0]["delta"].get("content", "")
                            if token:
                                yield token
                        except (json.JSONDecodeError, KeyError):
                            continue
        except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.RequestError) as err:
            logger.error(f"OpenAI-compatible Streaming Error: {err}")
            raise
