"""
Anthropic Claude Native Provider Adapter.
Mengimplementasikan antarmuka REST API native untuk model Claude 3.5 Sonnet / Haiku.
"""

import json
from typing import Any, AsyncGenerator, Dict, Optional
import httpx

from app.core.logger import logger


class AnthropicAdapter:
    """Adapter resmi untuk API Anthropic Messages."""

    def __init__(
        self,
        timeout_seconds: float = 90.0,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        """Inisialisasi adapter dengan konfigurasi timeout dan transport opsional."""
        self.timeout = httpx.Timeout(timeout_seconds, connect=10.0)
        self.transport = transport

    def _build_headers(self, api_key: str) -> Dict[str, str]:
        """Membangun header resmi Anthropic API dengan dukungan Prompt Caching."""
        return {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "prompt-caching-2024-07-31",
            "content-type": "application/json",
        }

    def _build_cached_system(self, system_prompt: str) -> Any:
        """Membentuk blok system prompt deterministik dengan flag cache_control ephemeral."""
        if not system_prompt:
            return ""
        return [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    async def complete(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        api_key: str,
        base_url: str = "https://api.anthropic.com",
        temperature: float = 0.7,
        response_format: Optional[Dict[str, Any]] = None,
        thinking_level: str = "medium",
    ) -> str:
        """Panggilan completion non-streaming Anthropic API."""
        url = f"{base_url.rstrip('/')}/v1/messages"
        headers = self._build_headers(api_key)
        payload: Dict[str, Any] = {
            "model": model,
            "max_tokens": 4096,
            "system": self._build_cached_system(system_prompt),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        budgets = {"low": 1024, "medium": 4096, "high": 8192}
        if thinking_level in budgets:
            payload["thinking"] = {"type": "enabled", "budget_tokens": budgets[thinking_level]}
            payload["max_tokens"] = budgets[thinking_level] + 4096

        try:
            async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client:
                res = await client.post(url, headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                return data["content"][0]["text"]
        except httpx.HTTPStatusError as err:
            logger.error(f"Anthropic HTTP {err.response.status_code} Error: {err.response.text}")
            raise
        except (httpx.TimeoutException, httpx.RequestError) as err:
            logger.error(f"Anthropic Network/Timeout Error: {err}")
            raise

    async def stream_tokens(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        api_key: str,
        base_url: str = "https://api.anthropic.com",
        temperature: float = 0.7,
        thinking_level: str = "medium",
    ) -> AsyncGenerator[str, None]:
        """Panggilan streaming token Anthropic via SSE."""
        url = f"{base_url.rstrip('/')}/v1/messages"
        headers = self._build_headers(api_key)
        payload: Dict[str, Any] = {
            "model": model,
            "max_tokens": 4096,
            "system": self._build_cached_system(system_prompt),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "stream": True,
        }
        budgets = {"low": 1024, "medium": 4096, "high": 8192}
        if thinking_level in budgets:
            payload["thinking"] = {"type": "enabled", "budget_tokens": budgets[thinking_level]}
            payload["max_tokens"] = budgets[thinking_level] + 4096

        try:
            async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as res:
                    res.raise_for_status()
                    async for line in res.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        try:
                            event_data = json.loads(data_str)
                            if event_data.get("type") == "content_block_delta":
                                delta = event_data.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    yield delta.get("text", "")
                        except (json.JSONDecodeError, KeyError):
                            continue
        except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.RequestError) as err:
            logger.error(f"Anthropic Streaming Error: {err}")
            raise
