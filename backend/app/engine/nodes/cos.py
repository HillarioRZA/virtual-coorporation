"""
Chief of Staff (CoS) Agent Node.
Menganalisis ide bisnis mentah Founder dan menghasilkan BusinessBriefSchema tervalidasi.
"""

from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.engine.memory import MemoryManager
from app.engine.nodes.auto_correction import parse_and_repair_schema
from app.engine.schemas import BusinessBriefSchema
from app.engine.state import VentureState
from app.gateway.client import UnifiedLLMClient


async def cos_sparring_node(
    state: VentureState,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_mgr: Optional[MemoryManager] = None,
) -> Dict[str, Any]:
    """Eksekusi node Chief of Staff (CoS) pada Fase 1 Sparring Room.

    Args:
        state: State aktif proyek venture.
        llm_client: Client gateway BYOK LLM opsional.
        memory_mgr: Manajer memori SQLite opsional.

    Returns:
        Dict update state berisi 'business_brief'.
    """
    client = llm_client or UnifiedLLMClient()
    model, provider = settings.get_agent_model_and_provider("COS")
    try:
        from app.db.role_repo import role_repo
        role_data = await role_repo.get_role_by_id("role_cos")
        if role_data and role_data.get("model_name") and role_data.get("model_provider"):
            model = role_data["model_name"]
            provider = role_data["model_provider"]
    except Exception as db_err:
        logger.debug(f"Menggunakan default settings CoS: {db_err}")
    system_prompt = load_prompt("cos")

    logger.info(f"CoS Node Executing for Project: [{state.project_id}] via {provider}/{model}")

    # Susun prompt input dari ide bisnis Founder dan riwayat percakapan jika ada
    user_prompt = (
        f"Ide Bisnis Founder:\n\"\"\"{state.founder_idea}\"\"\"\n\n"
        f"Sebagai Chief of Staff (Business Co-Founder), analisis kelayakan komersial ide di atas. "
        f"Tentukan rumusan masalah, solusi produk, segmentasi ICP, model monetisasi, struktur tier harga, "
        f"estimasi margin keuntungan (%), skor kelayakan pasar (1-100), serta daftar risiko dan mitigasinya."
    )

    if memory_mgr:
        try:
            context_msgs = await memory_mgr.build_context_for_agent(
                project_id=state.project_id,
                target_role="COS",
                state=state,
            )
            # Tambahkan riwayat direct mentions / feedback sebelumnya ke prompt
            chat_history = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in context_msgs])
            if chat_history.strip():
                user_prompt = f"Riwayat Diskusi Sparring:\n{chat_history}\n\n{user_prompt}"
        except Exception as mem_err:
            logger.warning(f"Gagal mengambil konteks memori CoS: {mem_err}")

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
        logger.error(f"Gagal memanggil model LLM CoS: {llm_err}")
        raise RuntimeError(f"CoS LLM completion failed: {llm_err}") from llm_err

    # Validasi output terhadap BusinessBriefSchema dengan auto-correction loop
    validated_brief = await parse_and_repair_schema(
        llm_client=client,
        raw_response=raw_response,
        system_prompt=system_prompt,
        schema_cls=BusinessBriefSchema,
        model=model,
        provider=provider,
        max_repairs=2,
    )

    # Catat event ke Blackboard Memory jika memory_mgr aktif
    if memory_mgr:
        try:
            summary = (
                f"Business Brief disusun. Model: {validated_brief.monetization_model} | "
                f"Margin: {validated_brief.projected_margin_percentage}% | "
                f"Feasibility Score: {validated_brief.market_feasibility_score}/100"
            )
            await memory_mgr.log_event(
                project_id=state.project_id,
                stage=state.stage,
                sender_role="COS",
                recipient_role="BROADCAST",
                event_type="ARTIFACT_PUBLISHED",
                content=summary,
                artifact_ref="business_brief",
                token_cost=0.02,
            )
        except Exception as log_err:
            logger.warning(f"Gagal mencatat event CoS ke memory blackboard: {log_err}")

    return {"business_brief": validated_brief}
