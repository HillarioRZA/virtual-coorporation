"""
Unit Tests untuk Unified BYOK LLM Gateway & Provider Adapters.
Menguji koneksi terpadu, adapter OpenAI/Anthropic/Gemini/OpenRouter, dan fallback cascade.
"""

import json
from typing import List
import httpx
import pytest

from app.gateway.adapters.anthropic_adapter import AnthropicAdapter
from app.gateway.adapters.gemini_adapter import GeminiAdapter
from app.gateway.adapters.openai_compatible import OpenAICompatibleAdapter
from app.gateway.client import UnifiedLLMClient


@pytest.mark.asyncio
async def test_openai_compatible_adapter_complete() -> None:
    """Menguji panggilan complete pada OpenAICompatibleAdapter dengan transport mock."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert "/chat/completions" in str(request.url)
        assert request.headers.get("Authorization") == "Bearer sk-dummy"
        content = json.dumps({"choices": [{"message": {"content": "Halo dari OpenAI/OpenRouter"}}]})
        return httpx.Response(200, content=content.encode("utf-8"))

    adapter = OpenAICompatibleAdapter(transport=httpx.MockTransport(mock_handler))
    result = await adapter.complete(
        prompt="Hai",
        system_prompt="System",
        model="deepseek-chat",
        api_key="sk-dummy",
        base_url="https://openrouter.ai/api/v1",
    )
    assert result == "Halo dari OpenAI/OpenRouter"


@pytest.mark.asyncio
async def test_anthropic_adapter_complete() -> None:
    """Menguji panggilan complete pada AnthropicAdapter dengan transport mock."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert "/v1/messages" in str(request.url)
        assert request.headers.get("x-api-key") == "sk-ant-dummy"
        content = json.dumps({"content": [{"text": "Halo dari Claude"}]})
        return httpx.Response(200, content=content.encode("utf-8"))

    adapter = AnthropicAdapter(transport=httpx.MockTransport(mock_handler))
    result = await adapter.complete(
        prompt="Hai",
        system_prompt="System",
        model="claude-3-5-sonnet",
        api_key="sk-ant-dummy",
    )
    assert result == "Halo dari Claude"


@pytest.mark.asyncio
async def test_gemini_adapter_complete() -> None:
    """Menguji panggilan complete pada GeminiAdapter dengan transport mock."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert "generateContent" in str(request.url)
        assert "key=gemini-dummy-key" in str(request.url)
        content = json.dumps({"candidates": [{"content": {"parts": [{"text": "Halo dari Gemini"}]}}]})
        return httpx.Response(200, content=content.encode("utf-8"))

    adapter = GeminiAdapter(transport=httpx.MockTransport(mock_handler))
    result = await adapter.complete(
        prompt="Hai",
        system_prompt="System",
        model="gemini-2.5-flash",
        api_key="gemini-dummy-key",
    )
    assert result == "Halo dari Gemini"


@pytest.mark.asyncio
async def test_streaming_tokens_openai_compatible() -> None:
    """Menguji streaming token generator SSE pada OpenAICompatibleAdapter."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert "/chat/completions" in str(request.url)
        lines = [
            'data: {"choices": [{"delta": {"content": "Halo "}}]}\n\n',
            'data: {"choices": [{"delta": {"content": "Dunia"}}]}\n\n',
            "data: [DONE]\n\n",
        ]
        return httpx.Response(200, content="".join(lines).encode("utf-8"))

    adapter = OpenAICompatibleAdapter(transport=httpx.MockTransport(mock_handler))
    tokens: List[str] = []
    async for token in adapter.stream_tokens(
        prompt="Streaming test",
        system_prompt="",
        model="deepseek-chat",
        api_key="sk-dummy",
        base_url="https://api.deepseek.com/v1",
    ):
        tokens.append(token)

    assert "".join(tokens) == "Halo Dunia"


@pytest.mark.asyncio
async def test_unified_client_fallback_cascade() -> None:
    """Menguji mekanisme failover fallback cascade ketika provider pertama gagal 500."""
    call_attempts = 0

    def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_attempts
        call_attempts += 1
        if call_attempts == 1:
            # Kegagalan simulasi provider pertama
            return httpx.Response(500, content=b"Server Busy / Rate Limit")
        # Sukses pada fallback provider kedua
        content = json.dumps({"choices": [{"message": {"content": "Sukses dari Fallback OpenRouter"}}]})
        return httpx.Response(200, content=content.encode("utf-8"))

    client = UnifiedLLMClient(transport=httpx.MockTransport(mock_handler))
    response = await client.complete(
        prompt="Uji Fallback",
        model="primary-model",
        provider="deepseek",
        fallback_providers=[("openrouter", "deepseek/deepseek-r1")],
    )

    assert response == "Sukses dari Fallback OpenRouter"
    assert call_attempts == 2
