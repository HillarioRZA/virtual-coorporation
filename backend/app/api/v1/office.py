"""
REST API Router untuk Virtual World Corporate Office Simulator.
Menyediakan inspeksi denah kampus, state agen, dan operasi intervensi langsung CEO.
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.engine.office_simulator import office_sim_engine

router = APIRouter(prefix="/corporate/office", tags=["Corporate Office Simulator"])


class AgentInterventionRequest(BaseModel):
    """Payload untuk intervensi langsung instruksi Founder ke agen spesifik."""
    role_id: str = Field(..., description="ID peran agen sasaran (e.g. role_fe, role_be)")
    instruction: str = Field(..., description="Teks arahan atau instruksi Founder")


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
