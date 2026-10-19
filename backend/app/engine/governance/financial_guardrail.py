"""
Autonomous Financial Circuit Breaker & Token-Spend Guardrail.
Mencegah lonjakan pengeluaran token API LLM dan membekukan tugas jika melampaui kuota,
tersinkronisasi dengan SQLite corporate_token_ledger dan relay SSE real-time.
"""

from typing import Any, Dict, Optional, Set
from app.core.logger import logger
from app.core.stream import stream_manager
from app.db.token_ledger_repo import token_ledger_repo

DEFAULT_MAX_TOKENS_PER_TICKET = 350000
DEFAULT_MAX_COST_DOLLARS = 1.50


class FinancialCircuitBreaker:
    """Pengawas anggaran finansial per tiket untuk mencegah cost runaway."""

    def __init__(
        self,
        max_tokens: int = DEFAULT_MAX_TOKENS_PER_TICKET,
        max_cost: float = DEFAULT_MAX_COST_DOLLARS,
    ) -> None:
        """Inisialisasi batas kuota token dan biaya finansial per tiket."""
        self.max_tokens = max_tokens
        self.max_cost = max_cost
        self._ticket_spend: Dict[str, Dict[str, float]] = {}
        self._frozen_tickets: Set[str] = set()

    async def sync_with_ledger(self, project_id: str) -> Dict[str, Any]:
        """Menyinkronkan akumulasi pengeluaran token dan biaya riil dari basis data SQLite."""
        try:
            summary = await token_ledger_repo.get_token_summary(project_id=project_id)
            return {
                "project_id": project_id,
                "total_tokens": summary.get("total_tokens", 0),
                "total_cost_usd": summary.get("total_cost_usd", 0.0),
                "total_requests": summary.get("total_requests", 0),
            }
        except Exception as err:
            logger.warning(f"Gagal sinkronisasi ledger finansial [{project_id}]: {err}")
            return {"project_id": project_id, "total_tokens": 0, "total_cost_usd": 0.0}

    def record_usage(
        self,
        ticket_id: str,
        tokens: int,
        cost_dollars: float,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mencatat konsumsi token dan biaya satu pemanggilan model."""
        if ticket_id not in self._ticket_spend:
            self._ticket_spend[ticket_id] = {"tokens": 0, "cost": 0.0}

        self._ticket_spend[ticket_id]["tokens"] += tokens
        self._ticket_spend[ticket_id]["cost"] += cost_dollars

        total_tok = self._ticket_spend[ticket_id]["tokens"]
        total_cost = self._ticket_spend[ticket_id]["cost"]

        is_exceeded = total_tok >= self.max_tokens or total_cost >= self.max_cost
        if is_exceeded:
            self._frozen_tickets.add(ticket_id)
            logger.critical(
                f"Financial Circuit Breaker TERPICU pada tiket [{ticket_id}]: "
                f"{total_tok:,} tokens (${total_cost:.3f}). Batas: {self.max_tokens:,} tokens (${self.max_cost:.2f})."
            )

        return {
            "ticket_id": ticket_id,
            "accumulated_tokens": total_tok,
            "accumulated_cost": round(total_cost, 4),
            "is_frozen": is_exceeded,
            "quota_status": "FROZEN_PENDING_APPROVAL" if is_exceeded else "HEALTHY",
        }

    async def emit_freeze_event(self, project_id: str, ticket_id: str) -> None:
        """Menyiarkan peristiwa pembekuan anggaran ke SSE bus real-time."""
        spend = self._ticket_spend.get(ticket_id, {"tokens": 0, "cost": 0.0})
        await stream_manager.publish(
            project_id=project_id,
            event_type="financial_quota_freeze",
            data={
                "ticket_id": ticket_id,
                "tokens_used": spend["tokens"],
                "cost_usd": spend["cost"],
                "max_tokens": self.max_tokens,
                "max_cost": self.max_cost,
                "status": "FROZEN_PENDING_APPROVAL",
            },
        )

    def is_ticket_frozen(self, ticket_id: str) -> bool:
        """Memeriksa apakah tiket sedang dibekukan akibat kuota finansial habis."""
        return ticket_id in self._frozen_tickets

    def approve_founder_budget_topup(
        self,
        ticket_id: str,
        additional_tokens: int = 150000,
        additional_dollars: float = 0.75,
    ) -> Dict[str, Any]:
        """Membuka kembali tiket yang dibekukan setelah Founder menyetujui penambahan anggaran."""
        self._frozen_tickets.discard(ticket_id)
        if ticket_id in self._ticket_spend:
            self._ticket_spend[ticket_id]["tokens"] = max(0, self._ticket_spend[ticket_id]["tokens"] - additional_tokens)
            self._ticket_spend[ticket_id]["cost"] = max(0.0, self._ticket_spend[ticket_id]["cost"] - additional_dollars)

        logger.info(f"Financial Circuit Breaker: Tiket [{ticket_id}] dicairkan dengan topup kuota.")
        return {
            "ticket_id": ticket_id,
            "status": "UNFROZEN",
            "message": "Tiket aktif kembali dengan alokasi anggaran tambahan.",
        }


financial_guardrail = FinancialCircuitBreaker()
