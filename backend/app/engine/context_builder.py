"""
Context Builder for Multi-Agent Working Memory.
Mengimplementasikan Context Projection 3-Tier + Tier 0 Corporate Wisdom Base.
"""

import json
from typing import Any, Dict, List, Optional
from app.core.logger import logger
from app.engine.state import VentureState

COMPACTION_THRESHOLD = 20
MAX_CONTEXT_CHARS = 16000


class ContextBuilder:
    """Perakit memori kerja agen berbasis Context Projection terpadu."""

    @staticmethod
    def get_pinned_contracts(target_role: str, state: VentureState) -> List[Dict[str, str]]:
        """Tier 1: Mengambil kontrak resmi terkunci yang relevan untuk role spesifik."""
        role = target_role.upper()
        pinned: List[Dict[str, str]] = []

        def _dump(obj: Any) -> Optional[Any]:
            if obj is None:
                return None
            if hasattr(obj, "model_dump"):
                return obj.model_dump(mode="json")
            return obj if isinstance(obj, dict) else None

        specs = [
            (["FRONTEND", "BACKEND", "QA"], state.openapi_spec, "PINNED API CONTRACT (OpenAPI 3.1) - STRICT IMMUTABLE TRUTH"),
            (["FRONTEND", "QA"], state.ui_spec, "PINNED UI SPECIFICATION - STRICT"),
            (["BACKEND", "DEVSECOPS", "PM"], state.system_architecture, "PINNED ARCHITECTURE BLUEPRINT"),
            (["QA", "UI_UX", "LEGAL", "BACKEND"], state.prd_spec, "PINNED LEAN PRD CONTRACT"),
            (["PM", "UI_UX", "LEGAL", "CTO"], state.business_brief, "PINNED BUSINESS BRIEF & MONETIZATION"),
        ]

        for allowed_roles, raw_spec, header in specs:
            if role in allowed_roles and raw_spec:
                data = _dump(raw_spec)
                if data:
                    pinned.append({
                        "role": "system",
                        "content": f"[{header}]:\n{json.dumps(data, indent=2)}",
                    })

        return pinned

    @staticmethod
    def format_wisdom_prompt(wisdom_items: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """Tier 0: Memformat memori institusional korporat menjadi prompt guidance ringkas."""
        if not wisdom_items:
            return None
        lines = ["[CORPORATE WISDOM & CROSS-VENTURE HISTORICAL PRECEDENTS]:"]
        for it in wisdom_items[:2]:
            ns = it.get("namespace", "wisdom")
            title = it.get("title", "Guideline")
            prob = it.get("problem_pattern", "")
            sol = it.get("solution_guideline", "")
            lines.append(f"- [{ns} | \"{title}\"]\n  Problem: {prob}\n  Prescriptive Rule: {sol}")
        return {"role": "system", "content": "\n".join(lines)}

    @staticmethod
    def compact_older_messages(older_events: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """Tier 3 Compaction: Merangkum riwayat pesan lama yang melampaui sliding window."""
        if not older_events:
            return None
        summary_lines: List[str] = []
        for ev in older_events:
            sender = ev.get("sender_role", "UNKNOWN")
            event_type = ev.get("event_type", "CHAT")
            snippet = str(ev.get("content", "")).replace("\n", " ").strip()
            if len(snippet) > 100:
                snippet = f"{snippet[:97]}..."
            summary_lines.append(f"- [{sender} | {event_type}]: {snippet}")

        return {
            "role": "system",
            "content": f"[EXECUTIVE STATE SUMMARY (Compacted {len(older_events)} Earlier Turns)]:\n" + "\n".join(summary_lines),
        }

    @classmethod
    def assemble_context(
        cls,
        target_role: str,
        state: VentureState,
        scoped_events: List[Dict[str, Any]],
        limit_recent_messages: int = 6,
        wisdom_items: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, str]]:
        """Merakit working memory lengkap dari Tier 0 (Wisdom), Tier 1, Tier 2, dan Tier 3."""
        role = target_role.upper()
        messages: List[Dict[str, str]] = []

        # TIER 0: Corporate Wisdom Base
        if wisdom_items:
            wisdom_msg = cls.format_wisdom_prompt(wisdom_items)
            if wisdom_msg:
                messages.append(wisdom_msg)

        # Strategic Bridge: Injeksi manifest lintas divisi untuk peran Kreatif & Marketing (Divisi B & C)
        cross_div_roles = {"UX", "DESIGNER", "COPYWRITER", "CONTENT", "EDUCATOR", "MARKETER", "SEO", "GROWTH"}
        if role in cross_div_roles:
            from app.engine.state_handoff import build_cross_division_manifest
            manifest = build_cross_division_manifest(state.project_id, state)
            messages.append({
                "role": "system",
                "content": f"[CROSS-DIVISION STRATEGIC MANIFEST]:\n{json.dumps(manifest, indent=2)}",
            })

        # TIER 1: Pinned Contracts
        messages.extend(cls.get_pinned_contracts(role, state))


        # TIER 3: Compaction pesan lama
        total_events = len(scoped_events)
        if total_events > limit_recent_messages:
            split_idx = total_events - limit_recent_messages
            compacted_msg = cls.compact_older_messages(scoped_events[:split_idx])
            if compacted_msg:
                messages.append(compacted_msg)
            recent_events = scoped_events[split_idx:]
        else:
            recent_events = scoped_events

        # TIER 2: Sliding Window pesan terbaru
        for ev in recent_events:
            sender = str(ev.get("sender_role", "")).upper()
            content = str(ev.get("content", ""))
            if sender in ["CEO", "FOUNDER"]:
                messages.append({"role": "user", "content": f"[CEO]: {content}"})
            elif sender in ["SYSTEM", "COMPILER", "LINTER"]:
                messages.append({"role": "system", "content": f"[{sender}]: {content}"})
            elif sender == role:
                messages.append({"role": "assistant", "content": content})
            else:
                messages.append({"role": "user", "content": f"[{sender}]: {content}"})

        # Guardrail hard token budget (< 16.000 karakter)
        total_chars = sum(len(m["content"]) for m in messages)
        while messages and total_chars > MAX_CONTEXT_CHARS and len(messages) > 2:
            removed = messages.pop(1)
            total_chars -= len(removed["content"])

        return messages
