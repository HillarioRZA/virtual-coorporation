"""
Chief Technology Officer (CTO) Agent Node.
Memilih arketipe solusi teknis (1-4) dan menghasilkan SystemArchitectureSchema tervalidasi.
"""

import json
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.engine.memory import MemoryManager
from app.engine.nodes.auto_correction import parse_and_repair_schema
from app.engine.schemas import SystemArchitectureSchema
from app.engine.state import VentureState
from app.gateway.client import UnifiedLLMClient


async def cto_architecture_node(
    state: VentureState,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_mgr: Optional[MemoryManager] = None,
) -> Dict[str, Any]:
    """Eksekusi node Chief Technology Officer (CTO) pada Fase 1 Sparring Room.

    Args:
        state: State aktif proyek venture.
        llm_client: Client gateway BYOK LLM opsional.
        memory_mgr: Manajer memori SQLite opsional.

    Returns:
        Dict update state berisi 'system_architecture' dan 'selected_archetype'.
    """
    client = llm_client or UnifiedLLMClient()
    model, provider = settings.get_agent_model_and_provider("CTO")
    system_prompt = load_prompt("cto")

    logger.info(f"CTO Node Executing for Project: [{state.project_id}] via {provider}/{model}")

    brief_info = ""
    if state.business_brief:
        brief_data = state.business_brief.model_dump(mode="json")
        brief_info = f"Business Brief dari CoS:\n{json.dumps(brief_data, indent=2)}\n\n"

    user_prompt = (
        f"Ide Bisnis Founder:\n\"\"\"{state.founder_idea}\"\"\"\n\n"
        f"{brief_info}"
        f"Sebagai Chief Technology Officer (CTO), pilih 1 dari 4 Arketipe Golden Path terbaik untuk ide di atas:\n"
        f"1. Standard Web/Mobile SaaS (CRUD)\n"
        f"2. Autonomous Agentic AI Systems\n"
        f"3. Conversational RAG & Multimodal AI\n"
        f"4. Data Science & Predictive Analytics\n\n"
        f"Tentukan arketipe (1-4), framework frontend, framework backend, database, "
        f"estimasi biaya inferensi LLM per user ($), serta batasan circuit breaker (max_iterations, timeout_seconds)."
    )

    if memory_mgr:
        try:
            context_msgs = await memory_mgr.build_context_for_agent(
                project_id=state.project_id,
                target_role="CTO",
                state=state,
            )
            chat_history = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in context_msgs])
            if chat_history.strip():
                user_prompt = f"Riwayat Diskusi Sparring:\n{chat_history}\n\n{user_prompt}"
        except Exception as mem_err:
            logger.warning(f"Gagal mengambil konteks memori CTO: {mem_err}")

    # Eksekusi pemanggilan LLM awal
    try:
        raw_response = await client.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model=model,
            provider=provider,
            temperature=0.7,
        )
    except Exception as llm_err:
        logger.error(f"Gagal memanggil model LLM CTO: {llm_err}")
        raise RuntimeError(f"CTO LLM completion failed: {llm_err}") from llm_err

    # Validasi output terhadap SystemArchitectureSchema dengan auto-correction loop
    validated_arch = await parse_and_repair_schema(
        llm_client=client,
        raw_response=raw_response,
        system_prompt=system_prompt,
        schema_cls=SystemArchitectureSchema,
        model=model,
        provider=provider,
        max_repairs=2,
    )

    # Catat event ke Blackboard Memory jika memory_mgr aktif
    if memory_mgr:
        try:
            summary = (
                f"Arsitektur Sistem Terkunci. Arketipe: {validated_arch.archetype_id} | "
                f"Frontend: {validated_arch.frontend_framework} | "
                f"Backend: {validated_arch.backend_framework} | "
                f"DB: {validated_arch.database} | "
                f"Est Cost/User: ${validated_arch.estimated_inference_cost_per_user}"
            )
            await memory_mgr.log_event(
                project_id=state.project_id,
                stage=state.stage,
                sender_role="CTO",
                recipient_role="BROADCAST",
                event_type="ARTIFACT_PUBLISHED",
                content=summary,
                artifact_ref="system_architecture",
                token_cost=0.02,
            )
        except Exception as log_err:
            logger.warning(f"Gagal mencatat event CTO ke memory blackboard: {log_err}")

    return {
        "system_architecture": validated_arch,
        "selected_archetype": validated_arch.archetype_id,
    }
