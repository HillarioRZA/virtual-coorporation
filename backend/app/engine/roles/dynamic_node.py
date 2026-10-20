"""
Dynamic Polymorphic Role Node Engine.
Mengeksekusi peran agen secara otonom berdasarkan konfigurasi tabel corporate_roles
dan corporate wisdom institutional knowledge tanpa hardcode nama jabatan.
"""

from typing import Any, Dict, Optional
from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.db.role_repo import role_repo
from app.engine.roles.role_output_processor import process_role_output
from app.engine.runtime.state import VentureState
from app.engine.memory.wisdom_engine import wisdom_engine
from app.gateway.client import UnifiedLLMClient


async def execute_dynamic_role_node(
    role_identifier: str = "",
    state: Optional[VentureState] = None,
    ticket_context: Optional[Dict[str, Any]] = None,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_mgr: Optional[Any] = None,
    sandbox_mgr: Optional[Any] = None,
    proxy_mgr: Optional[Any] = None,
    vault_mgr: Optional[Any] = None,
    custom_path: Optional[str] = None,
    role_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Eksekutor otonom tunggal untuk peran apa pun di dalam organisasi."""
    effective_role = role_id or role_identifier
    if not effective_role:
        raise ValueError("Parameter role_identifier atau role_id wajib disertakan.")
    norm_id = effective_role.replace("role_", "").lower()
    client = llm_client or UnifiedLLMClient()
    model, provider = settings.get_agent_model_and_provider(norm_id.upper())
    temperature = 0.5
    system_prompt = load_prompt(norm_id)

    try:
        role_data = await role_repo.resolve_role(role_identifier, custom_path=custom_path)
        if role_data:
            model = role_data.get("model_name") or model
            provider = role_data.get("model_provider") or provider
            temperature = float(role_data.get("temperature", temperature))
            if role_data.get("system_prompt_template"):
                system_prompt = role_data["system_prompt_template"]
            elif role_data.get("system_prompt"):
                system_prompt = role_data["system_prompt"]
            if role_data.get("job_description"):
                system_prompt = f"{system_prompt}\n\nFokus Tugas & Jobdesk: {role_data['job_description']}"
    except Exception as db_err:
        logger.debug(f"Fallback konfigurasi peran [{role_identifier}]: {db_err}")

    # Ambil corporate wisdom & institutional knowledge terkait
    try:
        wisdom_items = await wisdom_engine.query_wisdom(
            query="organisasi divisi peran tugas kapasitas",
            namespace="wisdom:organization",
            top_k=1,
            custom_path=custom_path,
        )
        wisdom_block = wisdom_engine.format_wisdom_for_prompt(wisdom_items)
        if wisdom_block:
            system_prompt = f"{system_prompt}\n\n{wisdom_block}"
    except Exception as w_err:
        logger.debug(f"Wisdom query skip: {w_err}")

    user_prompt = _build_task_prompt(state, ticket_context)
    if memory_mgr:
        try:
            msgs = await memory_mgr.build_context_for_agent(state.project_id, norm_id.upper(), state)
            history = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in msgs])
            if history.strip():
                user_prompt = f"Riwayat Diskusi:\n{history}\n\n{user_prompt}"
        except Exception as e:
            logger.warning(f"Konteks memori [{norm_id}] gagal dimuat: {e}")

    logger.info(f"Dynamic Node [@{norm_id.upper()}] executing for [{state.project_id}] via {provider}/{model}")
    from app.engine.runtime.model_router import sovereign_router
    actual_cost: Optional[float] = None
    try:
        raw, ledger_entry = await sovereign_router.execute_routed_completion(
            prompt=user_prompt,
            system_prompt=system_prompt,
            primary_provider=provider,
            primary_model=model,
            temperature=temperature,
            role_id=norm_id,
            project_id=state.project_id if state else None,
            ticket_id=ticket_context.get("id") if ticket_context else None,
            custom_path=custom_path,
        )
        if ledger_entry and "cost_usd" in ledger_entry:
            actual_cost = ledger_entry["cost_usd"]
    except Exception as route_err:
        logger.warning(f"Sovereign router fallback ke client.complete() untuk [{norm_id}]: {route_err}")
        raw = await client.complete(
            prompt=user_prompt, system_prompt=system_prompt, model=model, provider=provider, temperature=temperature
        )

    from app.engine.roles.dynamic_node_tools import handle_agent_tools

    raw = await handle_agent_tools(
        project_id=state.project_id if state else "default_proj",
        raw_response=raw,
        client=client,
        sys_p=system_prompt,
        usr_p=user_prompt,
        model=model,
        provider=provider,
        temp=temperature,
        agent_role=norm_id,
        stage=state.stage if state else "development",
        custom_path=custom_path,
    )
    return await process_role_output(
        role_id=norm_id,
        raw=raw,
        state=state,
        client=client,
        sys_p=system_prompt,
        model=model,
        provider=provider,
        mem=memory_mgr,
        sbx=sandbox_mgr,
        proxy=proxy_mgr,
        vault=vault_mgr,
        actual_cost=actual_cost,
    )


def _build_task_prompt(state: VentureState, ticket_context: Optional[Dict[str, Any]] = None) -> str:
    """Membangun task prompt kontekstual tanpa hardcode peran."""
    artifacts_info = state.get_artifacts_summary() if hasattr(state, "get_artifacts_summary") else ""
    if ticket_context:
        title = ticket_context.get("title", "Tugas Kanban")
        desc = ticket_context.get("description", "")
        crit = ticket_context.get("acceptance_criteria", "-")
        return (
            f"Proyek: {state.project_name} (ID: {state.project_id})\n"
            f"Tugas Ditugaskan: {title}\n"
            f"Deskripsi Tugas:\n{desc}\n"
            f"Acceptance Criteria:\n{crit}\n"
            f"{artifacts_info}\n"
            "Kerjakan tugas ini secara tuntas sesuai mandat peran dan keahlian spesifik Anda."
        )
    return (
        f"Proyek: {state.project_name} (ID: {state.project_id})\n"
        f"Ide Founder:\n\"\"\"{state.founder_idea}\"\"\"\n\n"
        f"{artifacts_info}\n"
        "Jalankan analisis, perancangan, atau produksi sesuai mandat peran Anda."
    )

