"""
Production Hardening Composite Orchestrator Node.
Mengorkestrasikan sintesis backend, audit keamanan QA, dan dokumen legal pada fase industrialisasi.
"""

from typing import Any, Dict, Optional

from app.core.logger import logger
from app.engine.memory import MemoryManager
from app.engine.nodes.backend import backend_engineering_node
from app.engine.nodes.legal import legal_compliance_node
from app.engine.nodes.qa import qa_eval_node
from app.engine.state import VentureState
from app.gateway.client import UnifiedLLMClient


async def production_hardening_node(
    state: VentureState,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_manager: Optional[MemoryManager] = None,
) -> Dict[str, Any]:
    """Composite node yang mengeksekusi pipeline industrialisasi secara berurutan."""
    logger.info(f"Memulai composite Production Hardening pipeline untuk [{state.project_id}]")
    client = llm_client or UnifiedLLMClient()
    mem = memory_manager or MemoryManager()

    # 1. Eksekusi Backend Engineer Node
    await backend_engineering_node(state, llm_client=client, memory_manager=mem)

    # 2. Eksekusi QA & Security Auditor Node
    await qa_eval_node(state, llm_client=client, memory_manager=mem)

    # 3. Eksekusi Legal & Compliance Counsel Node
    await legal_compliance_node(state, llm_client=client, memory_manager=mem)

    logger.info(f"Composite Production Hardening selesai untuk [{state.project_id}], siap menuju GATE_3_WAITING")
    return {
        "quality_scorecard": state.quality_scorecard,
        "token_usage": state.token_usage,
        "event_logs": state.event_logs,
    }
