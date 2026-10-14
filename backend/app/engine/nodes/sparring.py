"""
The Executive Sparring Room Node.
Mengorkestrasikan sinergi CoS dan CTO pada Fase 1 hingga menghasilkan brief dan arsitektur lengkap.
"""

from typing import Any, Dict, Optional

from app.core.logger import logger
from app.engine.memory import MemoryManager
from app.engine.nodes.cos import cos_sparring_node
from app.engine.nodes.cto import cto_architecture_node
from app.engine.state import VentureState
from app.gateway.client import UnifiedLLMClient


async def sparring_room_node(
    state: VentureState,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_mgr: Optional[MemoryManager] = None,
) -> Dict[str, Any]:
    """Eksekusi gabungan Troika Eksekutif (CoS lalu CTO) pada tahap SPARRING_ROOM.

    Args:
        state: State aktif proyek venture.
        llm_client: Client gateway BYOK LLM opsional.
        memory_mgr: Manajer memori SQLite opsional.

    Returns:
        Dict update state berisi 'business_brief', 'system_architecture', dan 'selected_archetype'.
    """
    logger.info(f"Memulai sesi Sparring Room untuk proyek: [{state.project_id}]")

    # 1. Eksekusi CoS untuk analisis komersial & monetisasi
    cos_updates = await cos_sparring_node(state, llm_client=llm_client, memory_mgr=memory_mgr)
    if "business_brief" in cos_updates:
        state.business_brief = cos_updates["business_brief"]

    # 2. Eksekusi CTO untuk penentuan arsitektur teknis berdasarkan analisis CoS
    cto_updates = await cto_architecture_node(state, llm_client=llm_client, memory_mgr=memory_mgr)

    return {
        "business_brief": state.business_brief,
        "system_architecture": cto_updates.get("system_architecture"),
        "selected_archetype": cto_updates.get("selected_archetype", state.selected_archetype),
    }
