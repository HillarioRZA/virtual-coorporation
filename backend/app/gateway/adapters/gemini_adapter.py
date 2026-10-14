"""
Google Gemini Native Provider Adapter.
Mengimplementasikan antarmuka REST API native untuk model Gemini 2.5 Flash / Pro.
"""

import json
from typing import Any, AsyncGenerator, Dict, Optional
import httpx

from app.core.logger import logger


class GeminiAdapter:
    """Adapter resmi untuk Google Generative Language (Gemini) API."""

    def __init__(
        self,
        timeout_seconds: float = 90.0,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        """Inisialisasi adapter dengan konfigurasi timeout dan transport opsional."""
        self.timeout = httpx.Timeout(timeout_seconds, connect=10.0)
        self.transport = transport

    def _build_payload(self, prompt: str, system_prompt: str, temperature: float) -> Dict[str, Any]:
        """Membangun payload JSON untuk Gemini generateContent."""
        payload: Dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        return payload

    async def complete(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        api_key: str,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        temperature: float = 0.7,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Panggilan completion non-streaming Gemini API."""
        url = f"{base_url.rstrip('/')}/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = self._build_payload(prompt, system_prompt, temperature)

        try:
            async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client:
                res = await client.post(url, headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except httpx.HTTPStatusError as err:
            logger.error(f"Gemini HTTP {err.response.status_code} Error: {err.response.text}")
            raise
        except (httpx.TimeoutException, httpx.RequestError) as err:
            logger.error(f"Gemini Network/Timeout Error: {err}")
            raise

    async def stream_tokens(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        api_key: str,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """Panggilan streaming token Gemini via Server-Sent Events (SSE)."""
        url = f"{base_url.rstrip('/')}/models/{model}:streamGenerateContent?alt=sse&key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = self._build_payload(prompt, system_prompt, temperature)

        try:
            async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as res:
                    res.raise_for_status()
                    async for line in res.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        try:
                            chunk = json.loads(data_str)
                            parts = chunk["candidates"][0]["content"]["parts"]
                            for part in parts:
                                token = part.get("text", "")
                                if token:
                                    yield token
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
        except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.RequestError) as err:
            logger.error(f"Gemini Streaming Error: {err}")
            raise
