"""
Corporate Events & Concurrency Dispatching API Router.
Menyediakan REST endpoint untuk publikasi event inter-agent, inspeksi riwayat Lounge,
dan pemicu eksekusi paralel (Frontend + Backend) berbasis DAG.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.core.logger import logger
from app.engine.corporate_schemas import (
    CorporateMessageCreate,
    CorporateMessageResponse,
)
from app.engine.dispatcher import task_dispatcher
from app.engine.event_bus import corporate_event_bus
from app.engine.memory import MemoryManager
from app.engine.state import VentureState

router = APIRouter(prefix="/corporate", tags=["Corporate Event Bus & Dispatcher"])


@router.get("/events/{project_id}", response_model=List[CorporateMessageResponse])
async def get_project_events(
    project_id: str,
    limit: int = Query(50, ge=1, le=500, description="Maksimum riwayat event yang diambil"),
) -> List[CorporateMessageResponse]:
    """Mengambil riwayat event bus dan obrolan Lounge untuk suatu proyek.

    Args:
        project_id: ID proyek sasaran.
        limit: Batas jumlah pesan terambil.

    Returns:
        List representasi CorporateMessageResponse terurut waktu.
    """
    try:
        events = await corporate_event_bus.get_history(project_id=project_id, limit=limit)
        return [CorporateMessageResponse(**e) for e in events]
    except Exception as err:
        logger.error(f"Gagal mengambil riwayat event proyek {project_id}: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil event: {str(err)}",
        )


@router.post("/events", response_model=CorporateMessageResponse, status_code=status.HTTP_201_CREATED)
async def publish_event(payload: CorporateMessageCreate) -> CorporateMessageResponse:
    """Mempublikasikan event atau pesan baru ke Corporate Event Bus.

    Args:
        payload: DTO data pesan yang akan disiarkan.

    Returns:
        CorporateMessageResponse lengkap dengan ID yang tersimpan.
    """
    try:
        result = await corporate_event_bus.publish(payload)
        return CorporateMessageResponse(**result)
    except Exception as err:
        logger.error(f"Gagal menyiarkan pesan ke event bus: {err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Gagal mempublikasikan event: {str(err)}",
        )


@router.post("/dispatch/concurrent/{project_id}", status_code=status.HTTP_200_OK)
async def dispatch_concurrent_engineering(
    project_id: str,
    branch_id: str = Query("branch_main", description="ID branch alur kerja"),
) -> Dict[str, Any]:
    """Memicu eksekusi paralel konkuren untuk Frontend dan Backend pada proyek tertentu.

    Args:
        project_id: ID proyek sasaran.
        branch_id: ID branch alur kerja (default 'branch_main').

    Returns:
        Dict hasil agregasi eksekusi paralel dan durasi waktu.
    """
    mem = MemoryManager()
    state: Optional[VentureState] = None

    try:
        state = await mem.load_latest_checkpoint(project_id)
    except Exception as err:
        logger.error(f"Gagal memuat checkpoint proyek {project_id}: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kesalahan memuat checkpoint: {str(err)}",
        )

    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proyek '{project_id}' tidak ditemukan.",
        )

    if not state.openapi_spec:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAPI Spec belum tersedia. Jalankan tahap PRD terlebih dahulu sebelum paralel dispatch.",
        )

    try:
        result = await task_dispatcher.dispatch_parallel_engineering(
            state=state, branch_id=branch_id, memory_mgr=mem
        )
        await mem.save_checkpoint(state)
        return result
    except Exception as err:
        logger.error(f"Eksekusi paralel gagal untuk {project_id}: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eksekusi paralel gagal: {str(err)}",
        )
