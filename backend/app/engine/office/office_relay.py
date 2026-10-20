"""
Office Mention Relay Module.
Menangani estafet konsultasi antar-agen di Oasis Live Command HQ dengan pengawalan Circuit Breaker
untuk mencegah perdebatan tanpa henti (infinite consultation loop).
"""

import asyncio
from typing import Any, Callable, Coroutine, Optional
from app.core.logger import logger
from app.db.role_repo import role_repo
from app.engine.governance.circuit_breaker import agent_circuit_breaker
from app.engine.roles.mention_relay import can_relay, extract_relay_mentions


async def relay_office_mentions(
    project_id: str,
    sender_role_name: str,
    reply_content: str,
    relay_hop: int,
    dispatch_fn: Callable[..., Coroutine[Any, Any, None]],
    ticket_id: Optional[str] = None,
) -> None:
    """Mengekstrak @mention agen dan meneruskan estafet jika diizinkan circuit breaker."""
    if not can_relay(relay_hop):
        return

    active_roles = await role_repo.get_roles()
    for tgt_id in extract_relay_mentions(reply_content, sender_role_name, active_roles):
        tgt_role = await role_repo.get_role_by_id(tgt_id)
        tgt_name = tgt_role["name"] if tgt_role else tgt_id

        effective_ticket = ticket_id or f"office_{project_id}"
        is_blocked = await agent_circuit_breaker.record_consultation_turn(
            ticket_id=effective_ticket,
            project_id=project_id,
            branch_id="branch_main",
            sender_role=sender_role_name,
            recipient_role=tgt_name,
            topic_summary=reply_content[:120],
        )
        if is_blocked:
            logger.warning(f"Circuit Breaker memblokir estafet relay dari [{sender_role_name}] ke [{tgt_name}].")
            break

        logger.info(f"Relaying baton from [{sender_role_name}] to [{tgt_name}] (Hop: {relay_hop + 1})...")
        asyncio.create_task(
            dispatch_fn(
                project_id=project_id,
                role_id=tgt_id,
                instruction=f"@{tgt_name}, berikut tanggapan dari @{sender_role_name}: \"{reply_content[:300]}\". Berikan tanggapan dari keahlian Anda.",
                relay_hop=relay_hop + 1,
                ticket_id=ticket_id,
            )
        )
