"""
REST API Router untuk Manajemen Filesystem Snapshot & 1-Click Rollback.
Menyediakan operasi pencatatan checkpoint dan pemulihan direktori proyek.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.sandbox.snapshot_manager import snapshot_manager

router = APIRouter(prefix="/sandbox/snapshots", tags=["Sandbox Snapshots"])


class SnapshotCreateRequest(BaseModel):
    """Payload untuk pembuatan snapshot baru."""
    tag: str = Field(default="MANUAL", description="Tag/kategori snapshot")
    description: str = Field(default="", description="Deskripsi atau catatan snapshot")


@router.get("/{project_id}", response_model=List[Dict[str, Any]])
async def list_project_snapshots(project_id: str) -> List[Dict[str, Any]]:
    """Mendapatkan daftar seluruh snapshot yang tersedia untuk proyek tertentu."""
    try:
        return snapshot_manager.list_snapshots(project_id)
    except Exception as err:
        logger.error(f"Gagal mengambil snapshot proyek [{project_id}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil snapshot: {str(err)}",
        )


@router.post("/{project_id}", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_project_snapshot(project_id: str, payload: SnapshotCreateRequest) -> Dict[str, Any]:
    """Membekukan direktori proyek saat ini ke snapshot baru."""
    try:
        meta = snapshot_manager.create_snapshot(
            project_id=project_id,
            tag=payload.tag,
            description=payload.description,
        )
        return meta
    except Exception as err:
        logger.error(f"Gagal membuat snapshot proyek [{project_id}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membuat snapshot: {str(err)}",
        )


@router.post("/{project_id}/rollback/{snapshot_id}", response_model=Dict[str, Any])
async def rollback_project_snapshot(project_id: str, snapshot_id: str) -> Dict[str, Any]:
    """Memulihkan berkas proyek ke kondisi snapshot yang dipilih (1-Click Rollback)."""
    try:
        res = await snapshot_manager.rollback_snapshot(project_id, snapshot_id)
        return res
    except FileNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        )
    except Exception as err:
        logger.error(f"Gagal melakukan rollback [{snapshot_id}] pada [{project_id}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rollback gagal: {str(err)}",
        )


@router.delete("/{project_id}/{snapshot_id}", response_model=Dict[str, Any])
async def delete_project_snapshot(project_id: str, snapshot_id: str) -> Dict[str, Any]:
    """Menghapus data snapshot tertentu dari proyek."""
    success = snapshot_manager.delete_snapshot(project_id, snapshot_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot [{snapshot_id}] tidak ditemukan",
        )
    return {"status": "deleted", "snapshot_id": snapshot_id}
