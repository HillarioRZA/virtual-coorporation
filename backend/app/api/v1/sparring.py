"""
Sparring & Streaming API Router.
Menangani interaksi chat langsung Founder dengan CoS/CTO dan Server-Sent Events (SSE).
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.core.stream import stream_manager
from app.engine.memory import MemoryManager

router = APIRouter(prefix="/projects", tags=["Sparring"])


class SparringChatRequest(BaseModel):
    """Payload pesan Founder ke Executive Sparring Room."""

    message: str = Field(..., min_length=1, description="Instruksi atau tanggapan dari Founder.")
    target_agent: Optional[str] = Field(
        default=None,
        description="Peran agen sasaran opsional: 'COS', 'CTO', atau None (Broadcast).",
    )


@router.post("/{project_id}/sparring/chat", status_code=status.HTTP_200_OK)
async def post_sparring_chat(project_id: str, payload: SparringChatRequest) -> Dict[str, Any]:
    """Menerima pesan Founder dan mencatatnya ke blackboard event store."""
    mem = MemoryManager()
    state = await mem.load_latest_checkpoint(project_id)
    if not state:
        logger.warning(f"Sparring chat ditolak: Proyek [{project_id}] tidak ditemukan.")
        raise HTTPException(status_code=404, detail=f"Proyek '{project_id}' tidak ditemukan.")

    target = payload.target_agent.upper() if payload.target_agent else "BROADCAST"

    try:
        # Catat pesan Founder ke Blackboard
        await mem.log_event(
            project_id=project_id,
            stage=state.stage,
            sender_role="CEO",
            recipient_role=target,
            event_type="CHAT",
            content=payload.message,
        )

        # Publikasikan ke stream real-time untuk dashboard UI
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
