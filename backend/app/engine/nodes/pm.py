"""
Product Manager (PM) Agent Node.
Menghasilkan Lean PRD terstruktur dan mengunci spesifikasi OpenAPI 3.1 sebagai SSOT.
"""

import json
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict

from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.engine.memory import MemoryManager
from app.engine.nodes.auto_correction import parse_and_repair_schema
from app.engine.schemas import PRDContractSchema
from app.engine.state import VentureState
from app.gateway.client import UnifiedLLMClient


class PMOutputEnvelope(BaseModel):
    """Wadah validasi gabungan untuk Lean PRD dan OpenAPI 3.1 Spec."""

    model_config = ConfigDict(extra="ignore")
    prd: PRDContractSchema
    openapi_spec: Dict[str, Any]


async def pm_spec_freeze_node(
    state: VentureState,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_mgr: Optional[MemoryManager] = None,
) -> Dict[str, Any]:
    """Eksekusi node Product Manager (PM) pada tahap PRD_AND_SPECS.

    Args:
        state: State aktif proyek venture.
        llm_client: Client gateway BYOK LLM opsional.
        memory_mgr: Manajer memori SQLite opsional.

    Returns:
        Dict update state berisi 'prd_spec', 'openapi_spec', dan 'project_name'.
    """
    client = llm_client or UnifiedLLMClient()
    model, provider = settings.get_agent_model_and_provider("PM")
    system_prompt = load_prompt("pm")

    logger.info(f"PM Node Executing for Project: [{state.project_id}] via {provider}/{model}")

    brief_data = state.business_brief.model_dump(mode="json") if state.business_brief else {}
    arch_data = state.system_architecture.model_dump(mode="json") if state.system_architecture else {}

    user_prompt = (
        f"Ide Bisnis Founder:\n\"\"\"{state.founder_idea}\"\"\"\n\n"
        f"Business Brief CoS:\n{json.dumps(brief_data, indent=2)}\n\n"
        f"Arsitektur Sistem CTO:\n{json.dumps(arch_data, indent=2)}\n\n"
        f"Rancang Lean PRD (Happy Path 3-5 langkah, user stories in-scope & out-of-scope) "
        f"serta kunci OpenAPI 3.1 Spec (auth, core data, transaction endpoint) dalam format JSON."
    )

    if memory_mgr:
        try:
            context_msgs = await memory_mgr.build_context_for_agent(
                project_id=state.project_id,
                target_role="PM",
                state=state,
            )
            chat_history = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in context_msgs])
            if chat_history.strip():
                user_prompt = f"Riwayat Konteks:\n{chat_history}\n\n{user_prompt}"
        except Exception as mem_err:
            logger.warning(f"Gagal mengambil konteks memori PM: {mem_err}")

    raw_response = await client.complete(
        prompt=user_prompt,
        system_prompt=system_prompt,
        model=model,
        provider=provider,
        temperature=0.4,
    )

    validated_envelope = await parse_and_repair_schema(
        llm_client=client,
        raw_response=raw_response,
        system_prompt=system_prompt,
        schema_cls=PMOutputEnvelope,
        model=model,
        provider=provider,
        max_repairs=2,
    )

    prd_spec = validated_envelope.prd
    openapi_spec = validated_envelope.openapi_spec

    if memory_mgr:
        try:
            summary = (
                f"PRD & OpenAPI Spec Terkunci. Produk: {prd_spec.product_name} | "
                f"Happy Path: {len(prd_spec.core_happy_path_steps)} langkah | "
                f"Endpoints: {list(openapi_spec.get('paths', {}).keys())}"
            )
            await memory_mgr.log_event(
                project_id=state.project_id,
                stage=state.stage,
                sender_role="PM",
                recipient_role="BROADCAST",
                event_type="ARTIFACT_PUBLISHED",
                content=summary,
                artifact_ref="openapi_spec",
                token_cost=0.015,
            )
        except Exception as log_err:
            logger.warning(f"Gagal mencatat event PM ke memory blackboard: {log_err}")

    return {
        "prd_spec": prd_spec,
        "openapi_spec": openapi_spec,
        "project_name": prd_spec.product_name,
    }
