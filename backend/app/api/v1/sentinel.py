"""
Sentinel CoV Observability & Audit Trail API Router.
Menyediakan endpoint untuk memantau log verifikasi pre-flight, riwayat reparasi perkakas, dan skor reliabilitas.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.core.logger import logger
from app.db.sentinel_repo import sentinel_repo

router = APIRouter(prefix="/sentinel", tags=["Sentinel CoV Observability"])


@router.get("/{project_id}/audit-logs", status_code=status.HTTP_200_OK)
async def get_sentinel_audit_logs(
    project_id: str,
    limit: int = Query(default=50, ge=1, le=200, description="Jumlah maksimal log"),
    role: Optional[str] = Query(default=None, description="Filter peran agen sasaran"),
    audit_status: Optional[str] = Query(default=None, alias="status", description="Filter status: APPROVED, REPAIRED, REJECTED"),
) -> List[Dict[str, Any]]:
    """Mengambil riwayat log inspeksi CoV Sentinel untuk proyek tertentu.

    Args:
        project_id: ID proyek sasaran.
        limit: Batas jumlah rekaman.
        role: Filter opsional berdasarkan peran agen (misal 'CTO', 'FRONTEND').
        audit_status: Filter status opsional.

    Returns:
        List data log audit dengan diff dan parameter perkakas.
    """
    try:
        logs = await sentinel_repo.get_audit_logs(
            project_id=project_id,
            limit=limit,
            role=role,
            status=audit_status,
        )
        return logs
    except Exception as err:
        logger.error(f"Gagal mengambil audit logs Sentinel [{project_id}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membaca audit log Sentinel: {err}",
        ) from err


@router.get("/{project_id}/stats", status_code=status.HTTP_200_OK)
async def get_sentinel_stats(project_id: str) -> Dict[str, Any]:
    """Mengambil metrik statistik reliabilitas dan latensi CoV Sentinel.

    Args:
        project_id: ID proyek sasaran.

    Returns:
        Dict berisi total inspeksi, approval rate, repair rate, dan rata-rata latensi.
    """
    try:
        stats = await sentinel_repo.get_audit_stats(project_id=project_id)
        return stats
    except Exception as err:
        logger.error(f"Gagal menghitung statistik Sentinel [{project_id}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membaca statistik Sentinel: {err}",
        ) from err
