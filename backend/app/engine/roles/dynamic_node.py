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
    role_identifier: str,
    state: VentureState,
    ticket_context: Optional[Dict[str, Any]] = None,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_mgr: Optional[Any] = None,
    sandbox_mgr: Optional[Any] = None,
    proxy_mgr: Optional[Any] = None,
    vault_mgr: Optional[Any] = None,
    custom_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Eksekutor otonom tunggal untuk peran apa pun di dalam organisasi."""
    norm_id = role_identifier.replace("role_", "").lower()
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
    raw = await client.complete(
        prompt=user_prompt, system_prompt=system_prompt, model=model, provider=provider, temperature=temperature
    )
    raw = await _handle_agent_tools(
        state.project_id, raw, client, system_prompt, user_prompt, model, provider, temperature
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


async def _handle_agent_tools(
    project_id: str,
    raw_response: str,
    client: Any,
    sys_p: str,
    usr_p: str,
    model: str,
    provider: str,
    temp: float,
) -> str:
    """Menjalankan loop perkakas agen jika model memanggil tool call."""
    from app.engine.tools.agent_tool_dispatcher import agent_tool_dispatcher

    step_count, cur_resp, accum = 0, raw_response, usr_p
    while step_count < agent_tool_dispatcher.max_steps:
        tc = agent_tool_dispatcher.parse_tool_call(cur_resp)
        if not tc:
            break
        obs = await agent_tool_dispatcher.execute_tool(project_id, tc["tool"], tc["parameters"])
        accum += f"\n[OBSERVATION dari {tc['tool']}]: {obs}\nLanjutkan tugas Anda."
        cur_resp = await client.complete(
            prompt=accum, system_prompt=sys_p, model=model, provider=provider, temperature=temp
        )
        step_count += 1
    return cur_resp
