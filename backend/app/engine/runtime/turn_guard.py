"""
Turn-Loop Resilience Guard Subsystem (Inspired by Hermes Agent).
Menyediakan Empty Response Guard dan Repetition Loop Guard untuk mencegah
kebocoran token dan halusinasi berantai saat LLM mengalami degradasi keluaran.
"""

from typing import Dict, Optional, Tuple
from app.core.logger import logger

MIN_FRAGMENT_LENGTH_FOR_REPETITION: int = 200
REPEAT_WINDOW_CHARS: int = 40
MIN_REPEAT_COUNT: int = 4


class TurnGuard:
    """Pengawal ketahanan putaran kognitif agen terhadap anomali output LLM."""

    def __init__(self, max_empty_retries: int = 2) -> None:
        self.max_empty_retries = max_empty_retries
        self._empty_streaks: Dict[str, int] = {}

    def is_empty_response(self, text: Optional[str]) -> bool:
        """Memeriksa apakah respons model kosong atau hanya terdiri dari whitespace."""
        if text is None:
            return True
        return len(text.strip()) == 0

    def record_empty_attempt(self, model_key: str) -> Tuple[bool, int]:
        """
        Mencatat streak respons kosong.
        Mengembalikan (should_fallback: bool, current_streak: int).
        """
        current = self._empty_streaks.get(model_key, 0) + 1
        self._empty_streaks[model_key] = current
        logger.warning(f"Empty response terdeteksi pada model [{model_key}] (Streak: {current}/{self.max_empty_retries})")
        should_fallback = current >= self.max_empty_retries
        return should_fallback, current

    def reset_empty_attempt(self, model_key: str) -> None:
        """Mereset streak saat model berhasil menghasilkan keluaran valid."""
        if model_key in self._empty_streaks:
            del self._empty_streaks[model_key]

    def is_repetition_dominated(self, text: str) -> bool:
        """
        Mendeteksi apakah teks didominasi oleh perulangan frasa (degenerate repetition loop).
        Mengecek apakah potongan string >= 40 karakter diulang >= 4 kali berturut-turut.
        """
        if not isinstance(text, str) or len(text) < MIN_FRAGMENT_LENGTH_FOR_REPETITION:
            return False

        try:
            n = len(text)
            step = max(10, REPEAT_WINDOW_CHARS // 2)
            for i in range(0, min(n - REPEAT_WINDOW_CHARS, 1500), step):
                chunk = text[i : i + REPEAT_WINDOW_CHARS]
                if not chunk.strip():
                    continue
                count = text.count(chunk)
                if count >= MIN_REPEAT_COUNT:
                    logger.warning(
                        f"Repetition loop terdeteksi! Frasa '{chunk[:20]}...' muncul {count}x dalam output {n} karakter."
                    )
                    return True
        except Exception as err:
            logger.debug(f"Pemeriksaan repetition guard diabaikan karena error: {err}")
            return False

        return False

    def validate_turn_output(self, raw_output: str, model_key: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validasi menyeluruh keluaran turn.
        Mengembalikan (is_valid: bool, cleaned_output: str, reason: Optional[str]).
        """
        if self.is_empty_response(raw_output):
            should_fallback, streak = self.record_empty_attempt(model_key)
            reason = "FALLBACK_TRIGGERED" if should_fallback else "EMPTY_RETRY"
            return False, "", f"Empty response from model {model_key} (streak {streak})"

        if self.is_repetition_dominated(raw_output):
            logger.error(f"Turn ditolak: Output dari {model_key} terperangkap dalam repetition loop.")
            return False, "", "Repetition loop detected in model output"

        self.reset_empty_attempt(model_key)
        return True, raw_output.strip(), None


turn_guard = TurnGuard()
