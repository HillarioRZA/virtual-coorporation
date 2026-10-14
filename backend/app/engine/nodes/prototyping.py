"""
Prototyping Phase Composite Orchestration Node.
Mengorkestrasikan rangkaian eksekusi PM, UI/UX, dan Frontend hingga mencapai Stage-Gate 2.
"""

from typing import Any, Dict, Optional

from app.core.logger import logger
from app.engine.memory import MemoryManager
from app.engine.nodes.frontend import frontend_prototyping_node
from app.engine.nodes.pm import pm_spec_freeze_node
from app.engine.nodes.ui_ux import ui_ux_spec_node
from app.engine.state import VentureState
from app.gateway.client import UnifiedLLMClient
from app.sandbox.proxy import ProxyManager
from app.sandbox.runner import SandboxManager


async def prd_and_specs_phase_node(
    state: VentureState,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_mgr: Optional[MemoryManager] = None,
) -> Dict[str, Any]:
    """Eksekusi gabungan Product Guild (PM lalu UI/UX) pada tahap PRD_AND_SPECS.

    Args:
        state: State aktif proyek venture.
        llm_client: Client gateway BYOK LLM opsional.
        memory_mgr: Manajer memori SQLite opsional.

    Returns:
        Dict update state berisi 'prd_spec', 'openapi_spec', dan 'ui_spec'.
    """
    logger.info(f"Memulai eksekusi tahap PRD_AND_SPECS untuk proyek: [{state.project_id}]")

    # 1. PM Node: Kunci PRD & OpenAPI Spec
    pm_updates = await pm_spec_freeze_node(state, llm_client=llm_client, memory_mgr=memory_mgr)
    state.prd_spec = pm_updates["prd_spec"]
    state.openapi_spec = pm_updates["openapi_spec"]
    state.project_name = pm_updates.get("project_name", state.project_name)

    # 2. UI/UX Node: Buat UI Component Spec
    ui_updates = await ui_ux_spec_node(state, llm_client=llm_client, memory_mgr=memory_mgr)
    state.ui_spec = ui_updates["ui_spec"]

    return {
        "prd_spec": state.prd_spec,
        "openapi_spec": state.openapi_spec,
        "ui_spec": state.ui_spec,
        "project_name": state.project_name,
    }


async def mock_prototyping_phase_node(
    state: VentureState,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_mgr: Optional[MemoryManager] = None,
    sandbox_mgr: Optional[SandboxManager] = None,
    proxy_mgr: Optional[ProxyManager] = None,
) -> Dict[str, Any]:
    """Eksekusi Frontend Engineer & Sandbox Mount pada tahap MOCK_PROTOTYPING.

    Args:
        state: State aktif proyek venture.
        llm_client: Client gateway BYOK LLM opsional.
        memory_mgr: Manajer memori SQLite opsional.
        sandbox_mgr: Manajer sandbox opsional.
        proxy_mgr: Manajer proxy opsional.

    Returns:
        Dict update state berisi 'preview_url'.
    """
    logger.info(f"Memulai eksekusi tahap MOCK_PROTOTYPING untuk proyek: [{state.project_id}]")

    fe_updates = await frontend_prototyping_node(
        state=state,
        llm_client=llm_client,
        memory_mgr=memory_mgr,
        sandbox_mgr=sandbox_mgr,
        proxy_mgr=proxy_mgr,
    )
    state.preview_url = fe_updates["preview_url"]
    return fe_updates
