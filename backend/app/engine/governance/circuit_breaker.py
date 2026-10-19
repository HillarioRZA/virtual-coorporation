"""
Agent Interaction Circuit Breaker & Anti-Infinite Loop Guardrail.
Mendeteksi dan menghentikan perulangan perdebatan tak berujung (discussion loops)
antar-agen secara otomatis, serta menyediakan mekanisme manual override bagi CEO.
"""

from typing import Any, Dict, Optional, Set
from app.core.logger import logger
from app.db.ticket_repo import ticket_repo
from app.engine.schemas.corporate_schemas import CorporateMessageCreate
from app.engine.runtime.event_bus import corporate_event_bus
from app.engine.schemas.workflow_schemas import CircuitBreakerStatus

MAX_CONSECUTIVE_TURNS = 3


class AgentCircuitBreaker:
    """Pengawas anti-infinite loop antar-agen pada level tiket tugas."""

    def __init__(self, max_turns: int = MAX_CONSECUTIVE_TURNS) -> None:
        """Inisialisasi registry counter giliran diskusi dan set tiket terblokir."""
        self.max_turns = max_turns
        self._turn_counters: Dict[str, int] = {}
        self._blocked_tickets: Set[str] = set()

    async def record_consultation_turn(
        self,
        ticket_id: str,
        project_id: str,
        branch_id: str,
        sender_role: str,
        recipient_role: str,
        topic_summary: str,
    ) -> bool:
        """Mencatat satu giliran diskusi/tanya-jawab antar-agen pada tiket.

        Args:
            ticket_id: ID tiket Kanban sasaran.
            project_id: ID proyek venture aktif.
            branch_id: ID branch alur kerja.
            sender_role: Peran penanya.
            recipient_role: Peran yang ditanyai.
            topic_summary: Ringkasan masalah/pertanyaan.

        Returns:
            True jika circuit breaker terpicu dan membekukan tugas, False jika masih di bawah limit.
        """
        current_count = self._turn_counters.get(ticket_id, 0) + 1
        self._turn_counters[ticket_id] = current_count
        logger.info(f"CircuitBreaker Tick: Tiket [{ticket_id}] turn {current_count}/{self.max_turns}")

        if current_count >= self.max_turns:
            self._blocked_tickets.add(ticket_id)
            warning_msg = (
                f"⚠️ Circuit Breaker Terpicu: Diskusi antara [{sender_role}] dan [{recipient_role}] "
                f"telah mencapai {current_count} putaran tanpa kemajuan kode baru ({topic_summary}). "
                f"Tugas otomatis DIBEKUKAN menunggu intervensi / hak veto CEO."
            )
            logger.warning(warning_msg)

            try:
                await ticket_repo.transition_ticket_status(ticket_id, "BLOCKED_LOOP_DETECTED")
                await corporate_event_bus.publish(
                    CorporateMessageCreate(
                        branch_id=branch_id,
                        project_id=project_id,
                        channel_type="LOUNGE",
                        sender_role_id="system",
                        ticket_id=ticket_id,
                        event_type="CIRCUIT_BREAKER_TRIGGERED",
                        content=warning_msg,
                    )
                )
            except Exception as err:
                logger.error(f"Gagal memancarkan event circuit breaker: {err}")
            return True

        return False

    def reset_counter(self, ticket_id: str) -> None:
        """Mereset counter giliran ketika ada kemajuan kode atau artefak baru."""
        self._turn_counters.pop(ticket_id, None)
        self._blocked_tickets.discard(ticket_id)
        logger.debug(f"CircuitBreaker Reset untuk tiket [{ticket_id}]")

    def get_status(self, ticket_id: str, project_id: str = "") -> CircuitBreakerStatus:
        """Memeriksa status pengawas pada tiket tertentu."""
        count = self._turn_counters.get(ticket_id, 0)
        is_blocked = ticket_id in self._blocked_tickets or count >= self.max_turns
        return CircuitBreakerStatus(
            ticket_id=ticket_id,
            project_id=project_id,
            turn_count=count,
            is_blocked=is_blocked,
            reason="Diskusi melampaui batas 3 putaran" if is_blocked else None,
        )

    async def execute_ceo_override(
        self,
        ticket_id: str,
        project_id: str,
        branch_id: str,
        action: str,
        directive: Optional[str] = None,
        target_role_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mengeksekusi intervensi manual hak veto CEO terhadap tiket yang terblokir.

        Args:
            ticket_id: ID tiket sasaran.
            project_id: ID proyek venture.
            branch_id: ID branch alur kerja.
            action: 'FORCE_PROCEED', 'INTERVENE', atau 'REASSIGN'.
            directive: Arahan instruksi CEO.
            target_role_id: Peran baru jika dialihkan.
            custom_path: Path basis data opsional untuk testing.

        Returns:
            Dict hasil pembaruan status tiket.
        """
        self.reset_counter(ticket_id)
        logger.info(f"CEO Override Executed on [{ticket_id}]: {action}")

        if action == "FORCE_PROCEED":
            updated = await ticket_repo.transition_ticket_status(ticket_id, "DONE", custom_path=custom_path)
            msg = f"👑 CEO Manual Override: Tiket [{ticket_id}] dipaksa lanjut (FORCE PROCEED -> DONE) oleh Founder."
        elif action == "REASSIGN":
            updated = await ticket_repo.transition_ticket_status(ticket_id, "TODO", custom_path=custom_path)
            msg = f"👑 CEO Manual Override: Tiket dialihkan ke peran [{target_role_id}]. Arahan: {directive or 'None'}"
        else:  # INTERVENE
            updated = await ticket_repo.transition_ticket_status(ticket_id, "IN_PROGRESS", custom_path=custom_path)
            msg = f"👑 CEO Intervensi Langsung: Founder memberikan arahan: '{directive}'"

        try:
            await corporate_event_bus.publish(
                CorporateMessageCreate(
                    branch_id=branch_id,
                    project_id=project_id,
                    channel_type="LOUNGE",
                    sender_role_id="chairman",
                    ticket_id=ticket_id,
                    event_type="CEO_INTERVENTION",
                    content=msg,
                )
            )
        except Exception as err:
            logger.error(f"Gagal menyiarkan CEO override ke event bus: {err}")

        return {"status": "success", "action": action, "ticket": updated}


agent_circuit_breaker = AgentCircuitBreaker()
