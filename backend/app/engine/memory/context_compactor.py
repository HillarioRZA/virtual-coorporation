"""
Autonomous Context Compactor & Memory Resilience Subsystem (Hermes Pattern).
Mencegah ledakan context window melalui pemangkasan selektif (tool output pruning),
ringkasan progresif percakapan lampau, dan retensi utuh putaran dialog terakhir (tail retention).
"""

from typing import Any, Dict, List, Optional
from app.core.logger import logger

DEFAULT_MAX_TOOL_CHARS = 2000
DEFAULT_TAIL_RETENTION_COUNT = 4
DEFAULT_MAX_TOTAL_CHARS = 12000


class ContextCompactor:
    """Manajer pemadatan memori konteks percakapan dan perkakas agen multi-turn."""

    def __init__(
        self,
        max_tool_chars: int = DEFAULT_MAX_TOOL_CHARS,
        tail_count: int = DEFAULT_TAIL_RETENTION_COUNT,
        max_total_chars: int = DEFAULT_MAX_TOTAL_CHARS,
    ) -> None:
        self.max_tool_chars = max_tool_chars
        self.tail_count = tail_count
        self.max_total_chars = max_total_chars

    def prune_tool_output(self, content: str, max_chars: Optional[int] = None) -> str:
        """Memangkas luaran perkakas masif (misal diff/terminal) dengan preservasi head dan tail."""
        limit = max_chars or self.max_tool_chars
        if len(content) <= limit:
            return content

        head_len = limit // 2 - 100
        tail_len = limit // 2 - 100
        omitted = len(content) - (head_len + tail_len)

        pruned = (
            f"{content[:head_len]}\n\n"
            f"... [OUTPUT DIPANGKAS {omitted} KARAKTER UNTUK EFISIENSI TOKEN] ...\n\n"
            f"{content[-tail_len:]}"
        )
        logger.debug(f"Tool output dipangkas dari {len(content)} ke {len(pruned)} karakter.")
        return pruned

    def summarize_older_turns(self, older_events: List[Dict[str, Any]]) -> str:
        """Merangkum giliran percakapan lampau menjadi poin eksekutif progresif."""
        if not older_events:
            return ""

        summary_bullets: List[str] = []
        for ev in older_events:
            sender = ev.get("sender_role", "AGENT")
            event_type = ev.get("event_type", "MSG")
            raw_content = str(ev.get("content", "")).replace("\n", " ").strip()
            # Pangkas konten pesan per-item jika terlalu panjang
            if len(raw_content) > 120:
                raw_content = f"{raw_content[:117]}..."
            summary_bullets.append(f"- [{sender} | {event_type}]: {raw_content}")

        return (
            f"[EXECUTIVE STATE SUMMARY (Compacted {len(older_events)} Earlier Turns)]:\n"
            + "\n".join(summary_bullets)
        )

    def compact_context(
        self,
        events: List[Dict[str, Any]],
        tail_count: Optional[int] = None,
        max_total_chars: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Mengeksekusi pemadatan konteks terpadu dengan tail retention."""
        limit_tail = tail_count or self.tail_count
        budget_chars = max_total_chars or self.max_total_chars

        if not events:
            return []

        # 1. Prune masing-masing isi pesan perkakas jika ada
        cleaned_events: List[Dict[str, Any]] = []
        for ev in events:
            ev_copy = dict(ev)
            raw_txt = str(ev_copy.get("content", ""))
            if "🛠️ [Observasi Perkakas" in raw_txt or "```json" in raw_txt:
                ev_copy["content"] = self.prune_tool_output(raw_txt)
            cleaned_events.append(ev_copy)

        # 2. Tail Retention: Simpan N percakapan terakhir utuh
        if len(cleaned_events) <= limit_tail:
            return cleaned_events

        split_idx = len(cleaned_events) - limit_tail
        older = cleaned_events[:split_idx]
        recent = cleaned_events[split_idx:]

        summary_text = self.summarize_older_turns(older)
        compacted_entry = {
            "sender_role": "SYSTEM",
            "event_type": "CONTEXT_COMPACTED_SUMMARY",
            "content": summary_text,
        }

        result = [compacted_entry] + recent

        # 3. Guardrail hard character budget
        current_chars = sum(len(str(e.get("content", ""))) for e in result)
        while len(result) > 2 and current_chars > budget_chars:
            # Hapus pesan terlama di antara recent (indeks 1)
            dropped = result.pop(1)
            current_chars -= len(str(dropped.get("content", "")))

        return result


context_compactor = ContextCompactor()
