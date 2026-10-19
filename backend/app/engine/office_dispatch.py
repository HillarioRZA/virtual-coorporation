"""
Office Directive Dispatcher.
Menangani eksekusi asinkron respons agen AI terhadap arahan Founder di Oasis Command HQ.
"""

from typing import Optional
from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.db.role_repo import role_repo
from app.engine.corporate_schemas import CorporateMessageCreate
from app.engine.event_bus import corporate_event_bus
from app.engine.memory import MemoryManager
from app.engine.office_simulator import office_sim_engine
from app.gateway.client import UnifiedLLMClient


async def dispatch_office_agent_response(project_id: str, role_id: str, instruction: str) -> None:
    """Menghasilkan tanggapan otomatis LLM dari agen sasaran di Oasis Live Command HQ."""
    agent = office_sim_engine.agents.get(role_id)
    try:
        role_info = await role_repo.get_role_by_id(role_id)
        role_slug = role_info.get("slug", role_id.replace("role_", "")).upper() if role_info else role_id.replace("role_", "").upper()

        if agent:
            agent.activity_state = "CONSULTING"
            agent.speech_bubble = "🤔 Menelaah arahan..."

        # Update event bus agar websocket menyiarkan status thinking
        await corporate_event_bus.publish(CorporateMessageCreate(
            branch_id="branch_main",
            project_id=project_id,
            channel_type="LOUNGE",
            sender_role_id=role_id,
            recipient_role_id="role_founder",
            event_type="AGENT_THINKING",
            content=f"[{role_slug}] sedang menelaah arahan Founder: \"{instruction}\"...",
        ))

        model = (role_info.get("model_name") if role_info else None) or settings.get_agent_model_and_provider(role_slug)[0]
        provider = (role_info.get("model_provider") if role_info else None) or settings.get_agent_model_and_provider(role_slug)[1]
        thinking_level = (role_info.get("thinking_level") if role_info else None) or "medium"
        sys_prompt = (role_info.get("system_prompt_template") if role_info else None) or load_prompt(role_slug.lower())

        mem = MemoryManager()
        state = await mem.load_latest_checkpoint(project_id)
        context_msgs = []
        if state:
            context_msgs = await mem.build_context_for_agent(project_id=project_id, target_role=role_slug, state=state)

        prompt_parts = []
        if state and state.founder_idea:
            prompt_parts.append(f"Ide Proyek:\n\"\"\"{state.founder_idea}\"\"\"")
        if context_msgs:
            recent_hist = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in context_msgs[-4:]])
            prompt_parts.append(f"Riwayat Diskusi:\n{recent_hist}")
        prompt_parts.append(f"Founder: {instruction}\n\nBerikan tanggapan taktis, padat, dan solutif sebagai {role_slug} (maksimal 2-3 paragraf).")

        client = UnifiedLLMClient()
        logger.info(f"Oasis LLM Response diproses untuk [{role_slug}] via {provider}/{model}...")
        reply = await client.complete(
            prompt="\n\n".join(prompt_parts),
            system_prompt=sys_prompt,
            model=model,
            provider=provider,
            thinking_level=thinking_level,
        )

        if agent:
            agent.activity_state = "IDLE"
            agent.speech_bubble = f"💬 {reply[:30]}..."

        await mem.log_event(
            project_id=project_id,
            stage=state.stage if state else 1,
            sender_role=role_slug,
            recipient_role="CEO",
            event_type="DIRECTIVE_RESPONSE",
            content=reply,
        )

        await corporate_event_bus.publish(CorporateMessageCreate(
            branch_id="branch_main",
            project_id=project_id,
            channel_type="LOUNGE",
            sender_role_id=role_id,
            recipient_role_id="role_founder",
            event_type="DIRECTIVE_RESPONSE",
            content=reply,
        ))
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
