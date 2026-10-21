"""
Unit Tests untuk TurnGuard (Inspired by Hermes Agent).
Menguji empty response detection, repetition loop detection, dan validation pipeline.
"""

import pytest
from app.engine.runtime.turn_guard import TurnGuard


def test_empty_response_detection() -> None:
    """Menguji deteksi string kosong atau whitespace."""
    guard = TurnGuard(max_empty_retries=2)
    assert guard.is_empty_response(None) is True
    assert guard.is_empty_response("") is True
    assert guard.is_empty_response("   \n\t  ") is True
    assert guard.is_empty_response("Hello World") is False


def test_empty_retry_streak_and_fallback() -> None:
    """Menguji penghitungan streak kosong dan pemicuan sinyal fallback."""
    guard = TurnGuard(max_empty_retries=2)
    model_key = "openrouter:deepseek-r1"

    should_fb, streak = guard.record_empty_attempt(model_key)
    assert streak == 1
    assert should_fb is False

    should_fb_2, streak_2 = guard.record_empty_attempt(model_key)
    assert streak_2 == 2
    assert should_fb_2 is True

    guard.reset_empty_attempt(model_key)
    _, streak_reset = guard.record_empty_attempt(model_key)
    assert streak_reset == 1


def test_repetition_dominated_detection() -> None:
    """Menguji deteksi degenerate repetition loops."""
    guard = TurnGuard()
    # Normal text
    normal_text = (
        "This is a normal paragraph with standard diversity of words and concepts. "
        "It discusses various architectural paradigms such as microservices, modular monoliths, "
        "event-driven architecture, and asynchronous message brokers."
    )
    assert guard.is_repetition_dominated(normal_text) is False

    # Degenerate repetition loop (panjang >= 200 dengan frasa >= 40 chars berulang >= 4x)
    repeated_chunk = "Sistem ini akan mengeksekusi analisis pasar mendalam untuk menemukan celah ceruk bisnis. "
    looping_text = repeated_chunk * 6
    assert guard.is_repetition_dominated(looping_text) is True


def test_validate_turn_output_pipeline() -> None:
    """Menguji pipeline validasi lengkap untuk output model."""
    guard = TurnGuard()
    # Case 1: valid
    valid, cleaned, err = guard.validate_turn_output("  Hasil analisis arsitektur valid.  ", "test-model")
    assert valid is True
    assert cleaned == "Hasil analisis arsitektur valid."
    assert err is None

    # Case 2: empty
    valid_e, _, err_e = guard.validate_turn_output("   ", "test-model")
    assert valid_e is False
    assert "Empty response" in str(err_e)
