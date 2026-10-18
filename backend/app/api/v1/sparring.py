"""
Sparring & Streaming API Router.
Menangani interaksi chat langsung Founder dengan CoS/CTO dan Server-Sent Events (SSE).
"""

import asyncio
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.core.stream import stream_manager
from app.db.role_repo import role_repo
from app.engine.memory import MemoryManager
from app.gateway.client import UnifiedLLMClient

router = APIRouter(prefix="/projects", tags=["Sparring"])


class SparringChatRequest(BaseModel):
    """Payload pesan Founder ke Executive Sparring Room."""

    message: str = Field(..., min_length=1, description="Instruksi atau tanggapan dari Founder.")
    target_agent: Optional[str] = Field(
        default=None,
        description="Peran agen sasaran opsional: 'COS', 'CTO', atau None (Broadcast).",
    )


async def _dispatch_sparring_response(project_id: str, target: str, user_message: str) -> None:
    """Menghasilkan tanggapan otomatis dari agen sasaran (CoS / CTO) di background."""
    agent_role = "CTO" if target == "CTO" else "COS"
    role_id = "role_cto" if agent_role == "CTO" else "role_cos"
    mem = MemoryManager()

    try:
        state = await mem.load_latest_checkpoint(project_id)
        role_info = await role_repo.get_role_by_id(role_id)

        model = (role_info.get("model_name") if role_info else None) or settings.get_agent_model_and_provider(agent_role)[0]
        provider = (role_info.get("model_provider") if role_info else None) or settings.get_agent_model_and_provider(agent_role)[1]
        thinking_level = (role_info.get("thinking_level") if role_info else None) or "medium"
        sys_template = role_info.get("system_prompt_template") if role_info else None
        system_prompt = sys_template or load_prompt(agent_role.lower())

        context_msgs = []
        if state:
            context_msgs = await mem.build_context_for_agent(project_id=project_id, target_role=agent_role, state=state)

        prompt_parts = []
        if state and state.founder_idea:
            prompt_parts.append(f"Ide Bisnis / Proyek Founder:\n\"\"\"{state.founder_idea}\"\"\"")
        if context_msgs:
            recent_hist = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in context_msgs[-6:]])
            prompt_parts.append(f"Riwayat Diskusi:\n{recent_hist}")
        prompt_parts.append(f"CEO (Founder): {user_message}\n\nBerikan respons kritis, konstruktif, dan solutif sebagai {agent_role}.")

        client = UnifiedLLMClient()
        logger.info(f"Memproses sparring response dari [{agent_role}] via {provider}/{model}...")
        reply = await client.complete(
            prompt="\n\n".join(prompt_parts),
            system_prompt=system_prompt,
            model=model,
            provider=provider,
            thinking_level=thinking_level,
        )

        await mem.log_event(
            project_id=project_id,
            stage=state.stage if state else 1,
            sender_role=agent_role,
            recipient_role="CEO",
            event_type="CHAT",
            content=reply,
        )

        await stream_manager.publish(
            project_id=project_id,
            event_type="sparring_token",
            data={
                "sender_role": agent_role,
                "recipient_role": "CEO",
                "token": reply,
                "is_first": True,
            },
        )
        await stream_manager.publish(
            project_id=project_id,
            event_type="done",
            data={"sender_role": agent_role, "status": "completed"},
        )
    except Exception as err:
        logger.error(f"Gagal menghasilkan sparring response [{agent_role}]: {err}")
        err_msg = f"Mohon maaf Founder, saya ({agent_role}) mengalami kendala saat memproses respons: {err}"
        await stream_manager.publish(
            project_id=project_id,
            event_type="sparring_token",
            data={
                "sender_role": agent_role,
                "recipient_role": "CEO",
                "token": err_msg,
                "is_first": True,
            },
        )


@router.post("/{project_id}/sparring/chat", status_code=status.HTTP_200_OK)
async def post_sparring_chat(project_id: str, payload: SparringChatRequest) -> Dict[str, Any]:
    """Menerima pesan Founder, mencatat ke blackboard, dan mendispatch respon agen."""
    mem = MemoryManager()
    state = await mem.load_latest_checkpoint(project_id)
    if not state:
        logger.warning(f"Sparring chat ditolak: Proyek [{project_id}] tidak ditemukan.")
        raise HTTPException(status_code=404, detail=f"Proyek '{project_id}' tidak ditemukan.")

    target = payload.target_agent.upper() if payload.target_agent else "BROADCAST"

    try:
        await mem.log_event(
            project_id=project_id,
            stage=state.stage,
            sender_role="CEO",
            recipient_role=target,
            event_type="CHAT",
            content=payload.message,
        )

        await stream_manager.publish(
            project_id=project_id,
            event_type="sparring_token",
            data={
                "sender_role": "CEO",
                "recipient_role": target,
                "token": payload.message,
                "is_first": True,
            },
        )
        logger.info(f"Pesan CEO tersimpan untuk [{project_id}] -> {target}")

        asyncio.create_task(_dispatch_sparring_response(project_id, target, payload.message))

        return {
            "status": "queued",
            "message": "Instruksi diterima, agen sedang memproses feedback.",
        }
    except Exception as err:
        logger.error(f"Gagal memproses sparring chat: {err}")
        raise HTTPException(status_code=500, detail=f"Gagal mengirim pesan: {err}") from err


@router.get("/{project_id}/stream")
async def stream_project_events(project_id: str) -> StreamingResponse:
    """Membuka koneksi HTTP persisten Server-Sent Events (SSE) untuk update live."""
    mem = MemoryManager()
    state = await mem.load_latest_checkpoint(project_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Proyek '{project_id}' tidak ditemukan.")

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
        "Content-Type": "text/event-stream",
    }

    logger.info(f"Membuka koneksi SSE untuk project [{project_id}]")
    return StreamingResponse(
        stream_manager.event_generator(project_id),
        media_type="text/event-stream",
        headers=headers,
    )
