"""
REST API Router untuk Git-Style Autonomous Three-Way Branch Merge.
Menyediakan endpoint simulasi dry-run dan eksekusi penggabungan cabang alur kerja.
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.engine.branch_merge import branch_merge_engine

router = APIRouter(prefix="/corporate/branches", tags=["Branch Merging"])


class BranchMergePreviewRequest(BaseModel):
    """Payload permintaan simulasi dry-run merge cabang."""
    source_branch_id: str = Field(..., description="ID cabang sumber (fitur/eksperimen)")
    target_branch_id: str = Field(default="branch_main", description="ID cabang target (biasanya branch_main)")
    strategy: str = Field(default="auto", description="Strategi resolusi: auto, prefer_theirs, prefer_ours")


class BranchMergeExecuteRequest(BaseModel):
    """Payload eksekusi penggabungan cabang alur kerja."""
    source_branch_id: str = Field(..., description="ID cabang sumber")
    target_branch_id: str = Field(default="branch_main", description="ID cabang target")
    strategy: str = Field(default="auto", description="Strategi resolusi konflik")


@router.post("/merge-preview", status_code=status.HTTP_200_OK)
async def preview_branch_merge(payload: BranchMergePreviewRequest) -> Dict[str, Any]:
    """Menghitung preview 3-way merge dan mendeteksi potensi konflik konfigurasi."""
    try:
        return await branch_merge_engine.preview_merge(
            source_id=payload.source_branch_id,
            target_id=payload.target_branch_id,
            strategy=payload.strategy,
        )
    except Exception as err:
        logger.error(f"Gagal menghasilkan preview merge: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))


@router.post("/merge", status_code=status.HTTP_200_OK)
async def execute_branch_merge(payload: BranchMergeExecuteRequest) -> Dict[str, Any]:
    """Mengeksekusi penggabungan cabang ke cabang target secara atomik."""
    try:
        return await branch_merge_engine.execute_merge(
            source_id=payload.source_branch_id,
            target_id=payload.target_branch_id,
            strategy=payload.strategy,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(val_err))
    except Exception as err:
        logger.error(f"Gagal mengeksekusi merge cabang: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
