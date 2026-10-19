"""Unit Tests untuk State-First Context Handoff & Sovereign Model Router.

Memverifikasi pembersihan jejak reasoning CoT, kompresi AST symbol table (<50 tokens),
pre-flight sliding window rate limiter, dan eksekusi failover cascade.
"""

import pytest
import time
from typing import Dict, Any, List

from app.engine.memory.state_handoff import (
    strip_reasoning_traces,
    export_ast_symbol_table,
    build_state_handoff_payload,
    prepare_differential_continuation,
)
from app.engine.runtime.model_router import UpstreamChannel, SovereignModelRouter
from app.db.init_db import init_database


def test_strip_reasoning_traces() -> None:
    """Memverifikasi pembersihan tag <think> dan blok reasoning dari teks dan pesan."""
    raw_text = "<think>Let me analyze the problem first...</think>Here is the clean answer."
    cleaned = strip_reasoning_traces(raw_text)
    assert cleaned == "Here is the clean answer."
    assert "<think>" not in cleaned

    messages = [
        {"role": "system", "content": "You are a lead architect."},
        {"role": "assistant", "content": "<think>Planning AST parse...</think>def execute(): pass"},
    ]
    cleaned_msgs = strip_reasoning_traces(messages)
    assert len(cleaned_msgs) == 2
    assert cleaned_msgs[1]["content"] == "def execute(): pass"


def test_export_ast_symbol_table() -> None:
    """Memverifikasi ekstraksi simbol class & fungsi dari kode Python via AST."""
    code = (
        "class PaymentGateway:\n"
        "    def authorize(self, amount: float) -> bool:\n"
        "        return True\n\n"
        "async def process_refund(tx_id: str) -> None:\n"
        "    pass\n"
    )
    symbols = export_ast_symbol_table(code)
    assert "class PaymentGateway" in symbols
    assert "def authorize" in symbols
    assert "async def process_refund" in symbols

    # Test syntax error fallback
    bad_code = "def syntax error here:::"
    fallback_symbols = export_ast_symbol_table(bad_code)
    assert fallback_symbols == ""


def test_build_state_handoff_payload() -> None:
    """Memverifikasi pembentukan payload handoff tanpa polusi jejak CoT."""
    code = "def calculate_discount(price: float) -> float:\n    return price * 0.9\n"
    payload = build_state_handoff_payload(
        task_description="Implement business discounts",
        completed_files={"pricing.py": code},
        target_pending_file="checkout.py",
        contract_schema="POST /checkout -> 200 OK",
        architectural_constraints=["SRP File limit 150-200 lines"],
    )
    assert payload["handoff_mode"] == "STATE_FIRST_RESILIENT_FAILOVER"
    assert payload["current_task"] == "Implement business discounts"
    assert payload["target_pending_file"] == "checkout.py"
    assert "pricing.py" in payload["available_symbol_tables"]
    assert "def calculate_discount" in payload["available_symbol_tables"]["pricing.py"]


def test_prepare_differential_continuation() -> None:
    """Memverifikasi konstruksi prompt kelanjutan diferensial untuk model cadangan."""
    partial_code = "class AuthManager:\n    def __init__(self):\n        pass\n"
    instruction = prepare_differential_continuation(
        file_path="app/core/auth.py",
        partial_code=partial_code,
        target_endpoints=["/api/v1/auth/login", "/api/v1/auth/refresh"],
    )
    assert "app/core/auth.py" in instruction
    assert "class AuthManager" in instruction
    assert "/api/v1/auth/login" in instruction
    assert "DILARANG mengulang import" in instruction


@pytest.mark.asyncio
async def test_upstream_channel_rate_limiter() -> None:
    """Memverifikasi sliding-window rate limiter dan aktivasi cooldown."""
    channel = UpstreamChannel(
        provider="openrouter",
        model="google/gemini-2.0-flash-001",
        rpm_limit=3,
        tpm_limit=5000,
    )
    assert channel.is_healthy() is True

    # Test throttle tracking
    await channel.throttle_if_needed(estimated_tokens=100)
    assert len(channel.request_timestamps) == 1

    # Test cooldown manual
    channel.set_cooldown(seconds=10)
    assert channel.is_healthy() is False
    assert channel.cooldown_until is not None


@pytest.mark.asyncio
async def test_sovereign_model_router_failover(tmp_path) -> None:
    """Memverifikasi auto-failover ke saluran cadangan jika saluran utama gagal."""
    db_file = str(tmp_path / "test_router.db")
    await init_database(custom_path=db_file)

    class MockClient:
        async def complete(self, prompt: str, system_prompt: str, model: str, provider: str, temperature: float) -> str:
            if "unstable" in model:
                raise RuntimeError("429 Too Many Requests: Rate limit exceeded")
            return "SUCCESS_FROM_BACKUP"

    mock_client = MockClient()
    router = SovereignModelRouter(client=mock_client)

    fallback_chain = [
        {"provider": "openrouter", "model": "google/gemini-2.0-flash-001", "is_enabled": True}
    ]

    # Eksekusi dengan primary model yang sengaja dibuat gagal
    output, ledger_entry = await router.execute_routed_completion(
        prompt="Design venture landing page",
        system_prompt="You are an architect",
        primary_provider="openrouter",
        primary_model="unstable/model:free",
        fallback_chain=fallback_chain,
        temperature=0.2,
        role_id="role_architect",
        project_id="proj_test_failover",
        custom_path=db_file,
    )

    assert output == "SUCCESS_FROM_BACKUP"
    assert ledger_entry["is_fallback"] is True
