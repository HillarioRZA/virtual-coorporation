"""
Dispatcher Eksekusi Respons Sparring Agen.
Mengeksekusi generasi respons AI otonom, streaming token SSE, CoV gatekeeper,
pencatatan memori blackboard, dan relay mention antar agen.
"""

import asyncio
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.core.stream import stream_manager
from app.db.role_repo import role_repo
from app.engine.memory.memory import MemoryManager
from app.engine.roles.mention_relay import can_relay, extract_relay_mentions
from app.engine.roles.org_context import build_organization_context_prompt
from app.gateway.client import UnifiedLLMClient


async def dispatch_sparring_response(
    project_id: str,
    role_info: Dict[str, Any],
    user_message: str,
    attachments: Optional[List[Dict[str, Any]]] = None,
    relay_hop: int = 0,
) -> None:
    """Mengeksekusi respons sparring untuk satu peran agen secara asinkron."""
    mem = MemoryManager()
    role_name = role_info.get("name", "Unknown Role")
    role_id = role_info.get("id", "role_unknown")

    try:
        state = await mem.load_latest_checkpoint(project_id)
        model = role_info.get("model_name") or "deepseek/deepseek-r1:free"
        provider = role_info.get("model_provider") or "openrouter"
        thinking_level = role_info.get("thinking_level") or "medium"
        sys_template = role_info.get("system_prompt_template")
        system_prompt = sys_template or load_prompt(role_name.lower())

        org_ctx = await build_organization_context_prompt()
        if org_ctx:
            system_prompt = f"{system_prompt}\n\n{org_ctx}"

        context_msgs: List[Dict[str, Any]] = []
        if state:
            context_msgs = await mem.build_context_for_agent(project_id=project_id, target_role=role_name, state=state)

        prompt_parts: List[str] = []
        if state and state.founder_idea:
            prompt_parts.append(f"Ide Bisnis / Proyek Founder:\n\"\"\"{state.founder_idea}\"\"\"")
        if context_msgs:
            recent_hist = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in context_msgs[-6:]])
            prompt_parts.append(f"Riwayat Diskusi:\n{recent_hist}")

        if attachments:
            att_snippets = []
            for a in attachments:
                fn = a.get("filename", "berkas")
                cp = a.get("content_preview") or ""
                att_snippets.append(f"--- [Lampiran: {fn}] ---\n{cp}\n-------------------" if cp else f"[Lampiran: {fn}]")
            prompt_parts.append("Berkas Lampiran dari Founder:\n" + "\n\n".join(att_snippets))

        prompt_parts.append(f"CEO (Founder): {user_message}\n\nBerikan respons kritis, konstruktif, dan solutif sebagai {role_name}.")

        client = UnifiedLLMClient()
        logger.info(f"Memproses sparring response dari [{role_name}] via {provider}/{model}...")

        await stream_manager.publish(
            project_id=project_id,
            event_type="agent_status",
            data={"status": f"{role_name} sedang merumuskan analisis...", "agent": role_name, "is_thinking": True},
        )

        full_reply = ""
        is_first = True
        try:
            async for tok in client.stream_tokens(
                prompt="\n\n".join(prompt_parts), system_prompt=system_prompt,
                model=model, provider=provider, thinking_level=thinking_level,
            ):
                full_reply += tok
                await stream_manager.publish(
                    project_id=project_id, event_type="sparring_token",
                    data={"sender_role": role_name, "recipient_role": "CEO", "token": tok, "is_first": is_first},
                )
                is_first = False
        except Exception as str_err:
            logger.warning(f"Fallback complete() [{role_name}]: {str_err}")
            full_reply = await client.complete(
                prompt="\n\n".join(prompt_parts), system_prompt=system_prompt,
                model=model, provider=provider, thinking_level=thinking_level,
            )
            await stream_manager.publish(
                project_id=project_id, event_type="sparring_token",
                data={"sender_role": role_name, "recipient_role": "CEO", "token": full_reply, "is_first": True},
            )

        # CoV Gatekeeper Pre-Flight Inspection
        from app.engine.sentinel.verifier import cov_gatekeeper
        inspection = await cov_gatekeeper.inspect(
            project_id=project_id, agent_role=role_name,
            candidate_content=full_reply, stage=state.stage if state else "ideation",
        )
        final_reply = inspection.inspected_content
        if inspection.tool_call:
            from app.engine.tools.agent_tool_dispatcher import agent_tool_dispatcher
            import json
            t_name = inspection.tool_call.get("tool", "")
            obs = await agent_tool_dispatcher.execute_tool(project_id, t_name, inspection.tool_call.get("parameters", {}))
            obs_str = f"\n\n🛠️ **[Observasi Perkakas `{t_name}`]**:\n```json\n{json.dumps(obs, indent=2)}\n```"
            final_reply += obs_str
            await stream_manager.publish(
                project_id=project_id, event_type="sparring_token",
                data={"sender_role": role_name, "recipient_role": "CEO", "token": obs_str, "is_first": False},
            )

        await mem.log_event(
            project_id=project_id, stage=state.stage if state else 1,
            sender_role=role_name, recipient_role="CEO", event_type="CHAT", content=final_reply,
        )
        await stream_manager.publish(
            project_id=project_id, event_type="done", data={"sender_role": role_name, "status": "completed"},
        )

        # Baton Relay untuk mention agen lain dalam balasan
        if can_relay(relay_hop):
            active_roles = await role_repo.get_roles(active_only=True)
            mentioned_ids = extract_relay_mentions(final_reply, role_name, active_roles)
            for m_id in mentioned_ids:
                tgt_role = next((r for r in active_roles if r["id"] == m_id or r["name"].lower() == m_id.lower()), None)
                if tgt_role:
                    logger.info(f"Relaying baton dari [{role_name}] ke [{tgt_role['name']}] (Hop: {relay_hop + 1})...")
                    relay_msg = f"Tanggapan dari @{role_name}: \"{final_reply[:300]}\". Berikan pandangan/tindak lanjut."
                    asyncio.create_task(
                        dispatch_sparring_response(project_id, tgt_role, relay_msg, relay_hop=relay_hop + 1)
                    )
    except Exception as err:
        logger.error(f"Gagal menghasilkan sparring response [{role_name}]: {err}")
        err_msg = f"Mohon maaf Founder, saya ({role_name}) mengalami kendala saat memproses respons: {err}"
        await stream_manager.publish(
            project_id=project_id, event_type="sparring_token",
            data={"sender_role": role_name, "recipient_role": "CEO", "token": err_msg, "is_first": True},
        )
