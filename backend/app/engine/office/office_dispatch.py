"""
Office Directive Dispatcher.
Menangani eksekusi asinkron respons agen AI terhadap arahan Founder di Oasis Command HQ.
"""

import asyncio
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.db.role_repo import role_repo
from app.engine.schemas.corporate_schemas import CorporateMessageCreate
from app.engine.runtime.event_bus import corporate_event_bus
from app.engine.memory.memory import MemoryManager
from app.engine.roles.mention_relay import can_relay, extract_relay_mentions
from app.engine.office.office_simulator import office_sim_engine
from app.gateway.client import UnifiedLLMClient


async def dispatch_office_agent_response(
    project_id: str,
    role_id: str,
    instruction: str,
    attachments: Optional[List[Dict[str, Any]]] = None,
    relay_hop: int = 0,
    ticket_id: Optional[str] = None,
) -> None:
    """Menghasilkan tanggapan otomatis LLM dari agen sasaran di Oasis Live Command HQ."""
    agent = office_sim_engine.agents.get(role_id)
    try:
        role_info = await role_repo.resolve_role(role_id)
        role_name = role_info["name"] if role_info else role_id.replace("role_", "").replace("_", " ").title()
        actual_role_id = role_info["id"] if role_info else role_id

        if agent:
            agent.activity_state = "CONSULTING"
            agent.speech_bubble = "🤔 Menelaah arahan..."

        # Update event bus agar websocket menyiarkan status thinking
        await corporate_event_bus.publish(CorporateMessageCreate(
            branch_id="branch_main",
            project_id=project_id,
            channel_type="LOUNGE",
            sender_role_id=actual_role_id,
            recipient_role_id="role_founder",
            event_type="AGENT_THINKING",
            content=f"[{role_name}] sedang menelaah arahan Founder: \"{instruction}\"...",
        ))

        model = (role_info.get("model_name") if role_info else None) or "deepseek/deepseek-r1:free"
        provider = (role_info.get("model_provider") if role_info else None) or "openrouter"
        thinking_level = (role_info.get("thinking_level") if role_info else None) or "medium"
        sys_prompt = (role_info.get("system_prompt_template") if role_info else None) or (
            f"Anda adalah {role_name}. Tanggapi arahan Founder secara profesional, taktis, dan solutif."
        )

        mem = MemoryManager()
        state = await mem.load_latest_checkpoint(project_id)
        context_msgs = []
        if state:
            context_msgs = await mem.build_context_for_agent(project_id=project_id, target_role=role_name, state=state)

        prompt_parts = []
        if state and state.founder_idea:
            prompt_parts.append(f"Ide Proyek:\n\"\"\"{state.founder_idea}\"\"\"")
        if context_msgs:
            recent_hist = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in context_msgs[-4:]])
            prompt_parts.append(f"Riwayat Diskusi:\n{recent_hist}")

        if attachments:
            att_snippets = []
            for a in attachments:
                fn = a.get("filename", "berkas")
                cp = a.get("content_preview") or ""
                att_snippets.append(f"--- [Lampiran: {fn}] ---\n{cp}\n-------------------" if cp else f"[Lampiran: {fn}]")
            prompt_parts.append("Berkas Lampiran dari Founder:\n" + "\n\n".join(att_snippets))

        prompt_parts.append(f"Founder: {instruction}\n\nBerikan tanggapan taktis, padat, dan solutif sebagai {role_name} (maksimal 2-3 paragraf).")

        client = UnifiedLLMClient()
        logger.info(f"Oasis LLM Response diproses untuk [{role_name}] via {provider}/{model}...")
        from app.engine.runtime.model_router import sovereign_router
        try:
            reply, _ = await sovereign_router.execute_routed_completion(
                prompt="\n\n".join(prompt_parts),
                system_prompt=sys_prompt,
                primary_provider=provider,
                primary_model=model,
                thinking_level=thinking_level,
                role_id=role_id,
                project_id=project_id,
                ticket_id=ticket_id,
            )
        except Exception as route_err:
            logger.warning(f"Sovereign router fallback di Oasis: {route_err}")
            reply = await client.complete(
                prompt="\n\n".join(prompt_parts),
                system_prompt=sys_prompt,
                model=model,
                provider=provider,
                thinking_level=thinking_level,
            )

        # CoV Gatekeeper Pre-Flight Inspection
        from app.engine.sentinel.verifier import cov_gatekeeper
        inspection = await cov_gatekeeper.inspect(
            project_id=project_id,
            agent_role=role_name,
            candidate_content=reply,
            stage=state.stage if state else "ideation",
        )

        current_reply = reply
        current_inspection = inspection
        attempts = 0
        while not current_inspection.approved and current_inspection.repair_feedback and attempts < settings.COV_MAX_REPAIRS:
            attempts += 1
            logger.info(f"Koreksi mandiri [{role_name}] dipicu CoV ({attempts}/{settings.COV_MAX_REPAIRS}): {current_inspection.repair_feedback}")
            repair_prompt = (
                f"{current_reply}\n\n"
                f"[TEGURAN COV GATEKEEPER]:\n{current_inspection.repair_feedback}\n\n"
                f"Sebagai {role_name}, perbaiki format perkakas atau parameter Anda di atas sekarang."
            )
            current_reply = await client.complete(
                prompt=repair_prompt,
                system_prompt=sys_prompt,
                model=model,
                provider=provider,
                thinking_level=thinking_level,
            )
            current_inspection = await cov_gatekeeper.inspect(
                project_id=project_id,
                agent_role=role_name,
                candidate_content=current_reply,
                stage=state.stage if state else "ideation",
            )
            if current_inspection.approved:
                current_inspection.status = "REPAIRED"
                break

        final_reply = current_reply

        # Non-hijacking Tool Execution: CoV menyetujui, dieksekusi atas nama agen asli
        if current_inspection.tool_call:
            from app.engine.tools.agent_tool_dispatcher import agent_tool_dispatcher
            import json
            t_name = current_inspection.tool_call.get("tool", "")
            t_params = current_inspection.tool_call.get("parameters", {})
            obs = await agent_tool_dispatcher.execute_tool(project_id, t_name, t_params)
            final_reply += f"\n\n🛠️ **[Observasi Perkakas `{t_name}`]**:\n```json\n{json.dumps(obs, indent=2)}\n```"

        if agent:
            agent.activity_state = "IDLE"
            agent.speech_bubble = f"💬 {final_reply[:30]}..."

        await mem.log_event(
            project_id=project_id,
            stage=state.stage if state else 1,
            sender_role=role_name,
            recipient_role="CEO",
            event_type="DIRECTIVE_RESPONSE",
            content=final_reply,
        )

        await corporate_event_bus.publish(CorporateMessageCreate(
            branch_id="branch_main",
            project_id=project_id,
            channel_type="LOUNGE",
            sender_role_id=actual_role_id,
            recipient_role_id="role_founder",
            event_type="DIRECTIVE_RESPONSE",
            content=final_reply,
        ))

        from app.engine.office.office_relay import relay_office_mentions
        await relay_office_mentions(
            project_id=project_id,
            sender_role_name=role_name,
            reply_content=final_reply,
            relay_hop=relay_hop,
            dispatch_fn=dispatch_office_agent_response,
            ticket_id=ticket_id,
        )
    except Exception as err:
        logger.error(f"Gagal memproses respons agen [{role_id}] di Oasis: {err}")
        if agent:
            agent.activity_state = "IDLE"
            agent.speech_bubble = "⚠️ Terkendala"
        await corporate_event_bus.publish(CorporateMessageCreate(
            branch_id="branch_main",
            project_id=project_id,
            channel_type="LOUNGE",
            sender_role_id=role_id,
            recipient_role_id="role_founder",
            event_type="DIRECTIVE_RESPONSE",
            content=f"Mohon maaf Founder, saya mengalami kendala saat memproses respons: {err}",
        ))
