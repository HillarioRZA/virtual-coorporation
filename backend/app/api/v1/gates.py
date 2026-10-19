"""
Stage-Gates API Router.
Menangani eksekusi keputusan Founder pada Stage-Gate 1, 2, dan 3 (APPROVE, REVISE, KILL).
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Path, status
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.core.stream import stream_manager
from app.db.session import get_db_connection
from app.engine.memory.memory import MemoryManager
from app.engine.runtime.routers import router_gate_1, router_gate_2, router_gate_3

router = APIRouter(prefix="/projects", tags=["Stage Gates"])


class GateDecisionRequest(BaseModel):
    """Payload keputusan Founder pada gerbang persetujuan."""

    action: str = Field(..., pattern="^(APPROVE|REVISE|KILL)$", description="Keputusan Founder.")
    feedback: Optional[str] = Field(default=None, description="Catatan umpan balik Founder.")


@router.post("/{project_id}/gates/{gate_id}/decision", status_code=status.HTTP_200_OK)
async def post_gate_decision(
    project_id: str,
    gate_id: str = Path(..., pattern="^(gate_1|gate_2|gate_3)$"),
    payload: GateDecisionRequest = ...,
) -> Dict[str, Any]:
    """Mengeksekusi keputusan Founder pada gerbang stage tertentu."""
    mem = MemoryManager()
    state = await mem.load_latest_checkpoint(project_id)
    if not state:
        logger.warning(f"Keputusan gate ditolak: Proyek [{project_id}] tidak ditemukan.")
        raise HTTPException(status_code=404, detail=f"Proyek '{project_id}' tidak ditemukan.")

    previous_stage = state.stage
    action = payload.action.upper()
    state.gate_decision = action
    state.gate_feedback = payload.feedback

    # Evaluasi transisi state berdasarkan router deterministik
    if gate_id == "gate_1":
        next_stage = router_gate_1(state)
    elif gate_id == "gate_2":
        next_stage = router_gate_2(state)
    else:  # gate_3
        next_stage = router_gate_3(state)

    state.stage = next_stage
    status_label = "KILLED" if action == "KILL" else "ACTIVE"

    try:
        # Perbarui tabel proyek di SQLite
        async with get_db_connection() as conn:
            await conn.execute(
                "UPDATE projects SET stage = ?, status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (next_stage, status_label, project_id),
            )
            await conn.commit()

        # Simpan snapshot state dan log event keputusan CEO
        await mem.save_checkpoint(state)
        await mem.log_event(
            project_id=project_id,
            stage=previous_stage,
            sender_role="CEO",
            recipient_role="BROADCAST",
            event_type="GATE_DECISION",
            content=f"Keputusan {gate_id.upper()}: {action}. Feedback: {payload.feedback or '-'}",
        )

        # Pancarkan notifikasi SSE state change
        await stream_manager.publish(
            project_id=project_id,
            event_type="state_change",
            data={
                "from_stage": previous_stage,
                "to_stage": next_stage,
                "action": action,
                "gate_id": gate_id,
            },
        )
        logger.info(f"Gate [{gate_id}] Executed for [{project_id}]: {previous_stage} -> {next_stage}")

        return {
            "status": "success",
            "data": {
                "project_id": project_id,
                "previous_stage": previous_stage,
                "current_stage": next_stage,
                "message": f"Gerbang {gate_id} berhasil diproses ({action}).",
            },
        }
    except Exception as err:
        logger.error(f"Gagal memproses keputusan gate [{gate_id}]: {err}")
        raise HTTPException(status_code=500, detail=f"Gagal memproses keputusan gate: {err}") from err
