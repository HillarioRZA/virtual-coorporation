"""
REST API Router untuk Virtual World Corporate Office Simulator.
Menyediakan inspeksi denah kampus, state agen, dan operasi intervensi langsung CEO.
"""

import asyncio
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.core.logger import logger
from app.engine.corporate_schemas import CorporateMessageCreate
from app.engine.event_bus import corporate_event_bus
from app.engine.office_dispatch import dispatch_office_agent_response
from app.engine.office_simulator import office_sim_engine

router = APIRouter(prefix="/corporate/office", tags=["Corporate Office Simulator"])


class AgentInterventionRequest(BaseModel):
    """Payload untuk intervensi langsung instruksi Founder ke agen spesifik."""
    role_id: str = Field(..., description="ID peran agen sasaran (e.g. role_fe, role_be)")
    instruction: str = Field(..., description="Teks arahan atau instruksi Founder")


class OfficeDirectiveRequest(BaseModel):
    """Payload untuk arahan Oasis Live Command HQ ke agen atau sesi All Hands."""
    project_id: str = Field(..., alias="projectId", description="ID proyek sasaran")
    mentions: List[str] = Field(..., description="Daftar peran sasaran (e.g. ['role_fe'] atau ['all'])")
    instruction: str = Field(..., description="Instruksi Founder/CEO")
    ticket_id: Optional[str] = Field(None, alias="ticketId", description="ID tiket terkait jika ada")

    model_config = ConfigDict(populate_by_name=True)


@router.get("/layout/{project_id}", response_model=Dict[str, Any])
async def get_campus_layout(project_id: str) -> Dict[str, Any]:
    """Mengambil skema tata letak denah kampus Silicon Valley (ruangan, meja, perabot)."""
    try:
        return office_sim_engine.layout
    except Exception as err:
        logger.error(f"Gagal mengambil denah kantor [{project_id}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membaca denah: {str(err)}",
        )


@router.get("/state/{project_id}", response_model=Dict[str, Any])
async def get_office_state(project_id: str) -> Dict[str, Any]:
    """Mengambil snapshot koordinat spasial dan status kognitif seluruh agen di kantor."""
    try:
        return office_sim_engine.get_snapshot()
    except Exception as err:
        logger.error(f"Gagal membaca state kantor [{project_id}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membaca state kantor: {str(err)}",
        )


@router.post("/intervene", response_model=Dict[str, Any])
async def intervene_office_agent(payload: AgentInterventionRequest) -> Dict[str, Any]:
    """Menyuntikkan instruksi langsung Founder ke agen AI tertentu dari kanvas simulator."""
    try:
        res = office_sim_engine.intervene_agent(payload.role_id, payload.instruction)
        if res.get("status") == "ERROR":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=res.get("message", "Agen tidak ditemukan"),
            )
        return res
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Kesalahan intervensi agen [{payload.role_id}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memproses intervensi: {str(err)}",
        )


@router.post("/directive", response_model=Dict[str, Any])
async def dispatch_office_directive(payload: OfficeDirectiveRequest) -> Dict[str, Any]:
    """Mengirim arahan terarah (scoped) atau memicu Executive Gate untuk @all."""
    try:
        # 1. Executive Moderator Gate jika sasaran @all
        if "all" in payload.mentions:
            office_sim_engine.intervene_agent("role_cos", f"Executive Gate: {payload.instruction}")
            office_sim_engine.intervene_agent("role_cto", f"Technical Gate: {payload.instruction}")
            await corporate_event_bus.publish(CorporateMessageCreate(
                branch_id="branch_main",
                project_id=payload.project_id,
                channel_type="WAR_ROOM",
                sender_role_id="role_founder",
                recipient_role_id="role_cos",
                event_type="ALL_HANDS_DIRECTIVE",
                content=f"Founder All Hands: {payload.instruction}",
            ))
            return {
                "status": "SUCCESS",
                "mode": "EXECUTIVE_MODERATED",
                "message": "All-Hands dimoderasi oleh CoS dan CTO. Pekerja tidak dibangunkan sekaligus.",
            }

        # 2. Scoped Single-Agent Interruption (hemat context window & token)
        for role in payload.mentions:
            office_sim_engine.intervene_agent(role, payload.instruction)
            await corporate_event_bus.publish(CorporateMessageCreate(
                branch_id="branch_main",
                project_id=payload.project_id,
                channel_type="LOUNGE",
                sender_role_id="role_founder",
                recipient_role_id=role,
                ticket_id=payload.ticket_id,
                event_type="DIRECTIVE_INTERRUPTION",
                content=f"Instruksi terarah ke {role}: {payload.instruction}",
            ))
            asyncio.create_task(dispatch_office_agent_response(payload.project_id, role, payload.instruction))

        return {
            "status": "SUCCESS",
            "mode": "SCOPED_INTERRUPTION",
            "message": f"Arahan berhasil disuntikkan ke {len(payload.mentions)} agen sasaran.",
        }
    except Exception as err:
        logger.error(f"Gagal memproses directive: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengirim directive: {str(err)}",
        )


@router.post("/demo-step", response_model=Dict[str, Any])
async def step_office_demo() -> Dict[str, Any]:
    """Melakukan satu langkah pergerakan interpolasi spasial agen untuk mode demonstrasi."""
    try:
        office_sim_engine.step_simulation()
        return {"status": "SUCCESS", "snapshot": office_sim_engine.get_snapshot()}
    except Exception as err:
        logger.error(f"Gagal melangkah simulasi demo: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal simulasi demo: {str(err)}",
        )
