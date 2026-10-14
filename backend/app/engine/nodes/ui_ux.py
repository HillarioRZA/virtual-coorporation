"""
Lead UI/UX Designer Agent Node.
Menghasilkan UIComponentSpecSchema dan design tokens Tailwind CSS untuk prototipe interaktif.
"""

import json
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.engine.memory import MemoryManager
from app.engine.nodes.auto_correction import parse_and_repair_schema
from app.engine.schemas import UIComponentSpecSchema
from app.engine.state import VentureState
from app.gateway.client import UnifiedLLMClient


async def ui_ux_spec_node(
    state: VentureState,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_mgr: Optional[MemoryManager] = None,
) -> Dict[str, Any]:
    """Eksekusi node UI/UX Designer pada tahap PRD_AND_SPECS.

    Args:
        state: State aktif proyek venture.
        llm_client: Client gateway BYOK LLM opsional.
        memory_mgr: Manajer memori SQLite opsional.

    Returns:
        Dict update state berisi 'ui_spec'.
    """
    client = llm_client or UnifiedLLMClient()
    model, provider = settings.get_agent_model_and_provider("UI_UX")
    system_prompt = load_prompt("ui_ux")

    logger.info(f"UI/UX Node Executing for Project: [{state.project_id}] via {provider}/{model}")

    prd_info = state.prd_spec.model_dump(mode="json") if state.prd_spec else {}
    brief_info = state.business_brief.model_dump(mode="json") if state.business_brief else {}

    user_prompt = (
        f"Produk: {state.project_name}\n"
        f"Lean PRD:\n{json.dumps(prd_info, indent=2)}\n\n"
        f"Business Brief:\n{json.dumps(brief_info, indent=2)}\n\n"
        f"Rancang spesifikasi komponen antarmuka pengguna: palet warna tema, "
        f"tipe tata letak, daftar halaman, dan rincian spesifikasi komponen dengan utility class Tailwind CSS."
    )

    if memory_mgr:
        try:
            context_msgs = await memory_mgr.build_context_for_agent(
                project_id=state.project_id,
                target_role="UI_UX",
                state=state,
            )
            chat_history = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in context_msgs])
            if chat_history.strip():
                user_prompt = f"Riwayat Konteks:\n{chat_history}\n\n{user_prompt}"
        except Exception as mem_err:
            logger.warning(f"Gagal mengambil konteks memori UI/UX: {mem_err}")

    raw_response = await client.complete(
        prompt=user_prompt,
        system_prompt=system_prompt,
        model=model,
        provider=provider,
        temperature=0.5,
    )

    validated_ui = await parse_and_repair_schema(
        llm_client=client,
        raw_response=raw_response,
        system_prompt=system_prompt,
        schema_cls=UIComponentSpecSchema,
        model=model,
        provider=provider,
        max_repairs=2,
    )

    if memory_mgr:
        try:
            summary = (
                f"UI Spec Disusun. Layout: {validated_ui.layout_type} | "
                f"Screens: {validated_ui.screens} | "
                f"Total Komponen: {len(validated_ui.components)}"
            )
            await memory_mgr.log_event(
                project_id=state.project_id,
                stage=state.stage,
                sender_role="UI_UX",
                recipient_role="BROADCAST",
                event_type="ARTIFACT_PUBLISHED",
                content=summary,
                artifact_ref="ui_spec",
                token_cost=0.015,
            )
        except Exception as log_err:
            logger.warning(f"Gagal mencatat event UI/UX ke memory blackboard: {log_err}")

    return {"ui_spec": validated_ui}
