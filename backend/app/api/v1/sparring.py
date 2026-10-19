"""
Sparring & Streaming API Router.
Menangani interaksi chat langsung Founder dengan Peran AI Korporat dan Server-Sent Events (SSE).
"""

import asyncio
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.core.stream import stream_manager
from app.db.role_repo import role_repo
from app.engine.memory.memory import MemoryManager
from app.engine.roles.mention_relay import parse_chat_mentions
from app.engine.roles.sparring_dispatcher import dispatch_sparring_response

router = APIRouter(prefix="/projects", tags=["Sparring"])


class SparringChatRequest(BaseModel):
    """Payload pesan Founder ke Executive Sparring Room."""

    message: str = Field(..., min_length=1, description="Instruksi atau tanggapan dari Founder.")
    target_agent: Optional[str] = Field(
        default=None,
        description="Peran agen sasaran opsional atau None (otomatis mendeteksi @mention / broadcast).",
    )
    attachments: Optional[List[Dict[str, Any]]] = Field(default=None, description="Daftar berkas lampiran.")


@router.post("/{project_id}/sparring/chat", status_code=status.HTTP_200_OK)
async def post_sparring_chat(project_id: str, payload: SparringChatRequest) -> Dict[str, Any]:
    """Menerima pesan Founder, mendeteksi @mention multi-kata, dan mendispatch respon peran AI."""
    mem = MemoryManager()
    state = await mem.load_latest_checkpoint(project_id)
    if not state:
        logger.warning(f"Sparring chat ditolak: Proyek [{project_id}] tidak ditemukan.")
        raise HTTPException(status_code=404, detail=f"Proyek '{project_id}' tidak ditemukan.")

    try:
        active_roles = await role_repo.get_roles(active_only=True)
        is_broadcast, mentioned_roles = parse_chat_mentions(payload.message, active_roles)

        target_roles: List[Dict[str, Any]] = []

        if payload.target_agent and payload.target_agent.upper() != "BROADCAST":
            direct_role = await role_repo.resolve_role(payload.target_agent)
            if direct_role:
                target_roles.append(direct_role)

        for r in mentioned_roles:
            if not any(t["id"] == r["id"] for t in target_roles):
                target_roles.append(r)

        if payload.target_agent and payload.target_agent.upper() != "BROADCAST":
            recipient_label = payload.target_agent.upper()
        elif is_broadcast or not target_roles:
            # Broadcast ke seluruh peran eksekutif aktif (default: CoS & CTO)
            exec_roles = [r for r in active_roles if r.get("division_id") == "div_exec"]
            target_roles = exec_roles if exec_roles else active_roles[:2]
            recipient_label = "BROADCAST"
        else:
            recipient_label = ", ".join(r["name"] for r in target_roles)

        stage_num = state.stage if isinstance(state.stage, int) else 1
        await mem.log_event(project_id, stage_num, "CEO", recipient_label, "CHAT", payload.message)
        await stream_manager.publish(
            project_id=project_id,
            event_type="sparring_token",
            data={
                "sender_role": "CEO",
                "recipient_role": recipient_label,
                "token": payload.message,
                "attachments": payload.attachments,
                "is_first": True,
            },
        )
        logger.info(f"Pesan CEO tersimpan untuk [{project_id}] -> {recipient_label} ({len(target_roles)} peran)")

        for role in target_roles:
            asyncio.create_task(
                dispatch_sparring_response(project_id, role, payload.message, payload.attachments)
            )

        return {"status": "queued", "message": f"Instruksi diterima oleh {recipient_label}."}
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
    return StreamingResponse(
        stream_manager.event_generator(project_id), credentials=False, media_type="text/event-stream", credentials_mode="omit", headers=headers
    ) if False else StreamingResponse(
        stream_manager.event_generator(project_id), media_type="text/event-stream", headers=headers
    )
