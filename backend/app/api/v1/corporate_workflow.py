"""
Corporate Workflow Pipeline & Sequential Reordering Endpoints.
Menyediakan REST API untuk mengelola multi-pipeline produk (Software, Edukasi, Copywriting),
rantai eksekusi peran (Pipeline Builder), dan penyusunan ulang urutan alur kerja.
"""

from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, HTTPException, Query, status

from app.core.logger import logger
from app.db.corporate_repo import corporate_repo
from app.db.pipeline_repo import pipeline_repo
from app.db.workflow_repo import workflow_repo
from app.engine.schemas.corporate_schemas import CorporateMessageCreate
from app.engine.runtime.event_bus import corporate_event_bus
from app.engine.schemas.workflow_schemas import (
    PipelineCreate,
    PipelineResponse,
    PipelineStageItem,
    PipelineStageResponse,
    ReorderDivisionsRequest,
    ReorderPipelineRequest,
    SavePipelineStagesRequest,
)

router = APIRouter(prefix="/corporate/branches/{branch_id}", tags=["Corporate Workflow Pipeline"])


@router.get("/pipelines", response_model=List[PipelineResponse])
async def get_pipelines(branch_id: str) -> List[PipelineResponse]:
    """Mengambil seluruh pipeline alur kerja lini produk yang terdaftar pada branch."""
    branch = await corporate_repo.get_branch_by_id(branch_id)
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Branch '{branch_id}' tidak ditemukan.")
    pipes = await pipeline_repo.get_pipelines(branch_id)
    return [PipelineResponse(**p) for p in pipes]


@router.post("/pipelines", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(branch_id: str, payload: PipelineCreate) -> PipelineResponse:
    """Membuat rantai pipeline alur kerja baru untuk lini produk (misal: Edukasi, Copywriting)."""
    branch = await corporate_repo.get_branch_by_id(branch_id)
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Branch '{branch_id}' tidak ditemukan.")
    created = await pipeline_repo.create_pipeline(
        branch_id=branch_id,
        name=payload.name,
        slug=payload.slug,
        product_line=payload.product_line,
        description=payload.description,
    )
    return PipelineResponse(**created)


@router.delete("/pipelines/{pipeline_id}")
async def delete_pipeline(branch_id: str, pipeline_id: str) -> Dict[str, Any]:
    """Menghapus pipeline produk non-default dari branch."""
    success = await pipeline_repo.delete_pipeline(branch_id=branch_id, pipeline_id=pipeline_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pipeline default Tech Core tidak dapat dihapus.")
    return {"status": "success", "message": f"Pipeline '{pipeline_id}' berhasil dihapus."}


@router.get("/pipeline", response_model=List[PipelineStageResponse])
async def get_workflow_pipeline(
    branch_id: str, pipeline_id: Optional[str] = Query(None, description="ID pipeline spesifik.")
) -> List[PipelineStageResponse]:
    """Mengambil urutan sekuensial tahapan peran & gerbang CEO dalam pipeline branch."""
    branch = await corporate_repo.get_branch_by_id(branch_id)
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Branch '{branch_id}' tidak ditemukan.")
    raw_stages = await workflow_repo.get_workflow_pipeline(branch_id, pipeline_id=pipeline_id)
    return [PipelineStageResponse(**s) for s in raw_stages]


@router.put("/pipeline", response_model=List[PipelineStageResponse])
async def save_or_reorder_workflow_pipeline(
    branch_id: str,
    payload: Union[SavePipelineStagesRequest, ReorderPipelineRequest],
    pipeline_id: Optional[str] = Query(None, description="ID pipeline sasaran."),
) -> List[PipelineStageResponse]:
    """Menyimpan seluruh konfigurasi tahapan alur kerja baru (looping peran & kartu CEO)."""
    branch = await corporate_repo.get_branch_by_id(branch_id)
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Branch '{branch_id}' tidak ditemukan.")

    if branch_id == "branch_main" or branch.get("slug") == "main":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Branch 'branch_main' dilindungi (Gold Standard). Silakan Fork Workflow terlebih dahulu.",
        )

    try:
        target_pipe = pipeline_id or getattr(payload, "pipeline_id", None)
        if isinstance(payload, SavePipelineStagesRequest) or hasattr(payload, "stages"):
            stage_dicts = [s.model_dump() for s in payload.stages]
            updated = await workflow_repo.save_workflow_pipeline_stages(branch_id, stage_dicts, pipeline_id=target_pipe)
            stage_count = len(payload.stages)
        else:
            updated = await workflow_repo.reorder_workflow_pipeline(
                branch_id=branch_id, ordered_role_ids=payload.ordered_role_ids, pipeline_id=target_pipe
            )
            stage_count = len(payload.ordered_role_ids)

        await corporate_event_bus.publish(
            CorporateMessageCreate(
                branch_id=branch_id,
                project_id="workspace_corporate",
                channel_type="LOUNGE",
                sender_role_id="chairman",
                event_type="SCHEMA_CHANGE",
                content=f"Alur kerja peran pada branch '{branch['name']}' berhasil disusun ulang ({stage_count} tahapan).",
            )
        )
        return [PipelineStageResponse(**s) for s in updated]
    except Exception as err:
        logger.error(f"Gagal menyimpan workflow pipeline pada branch '{branch_id}': {err}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.post("/pipeline/reset", response_model=List[PipelineStageResponse])
async def reset_workflow_pipeline(
    branch_id: str, pipeline_id: Optional[str] = Query(None)
) -> List[PipelineStageResponse]:
    """Mereset alur kerja branch eksperimen kembali ke baseline Tech Core resmi."""
    branch = await corporate_repo.get_branch_by_id(branch_id)
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Branch '{branch_id}' tidak ditemukan.")
    if branch_id == "branch_main" or branch.get("slug") == "main":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Branch 'branch_main' sudah baseline.")

    try:
        main_stages = await workflow_repo.get_workflow_pipeline("branch_main", pipeline_id=pipeline_id)
        branch_roles = await corporate_repo.get_roles(branch_id=branch_id)
        name_to_role_id = {r["name"].lower().strip(): r["id"] for r in branch_roles}
        mapped_stages = []
        for stg in main_stages:
            stg_dict = dict(stg)
            role_name = (stg_dict.get("role_name") or "").lower().strip()
            if role_name and role_name in name_to_role_id:
                stg_dict["role_id"] = name_to_role_id[role_name]
            mapped_stages.append(stg_dict)
        updated = await workflow_repo.save_workflow_pipeline_stages(branch_id, mapped_stages, pipeline_id=pipeline_id)
        return [PipelineStageResponse(**s) for s in updated]
    except Exception as err:
        logger.error(f"Gagal reset workflow pipeline pada branch '{branch_id}': {err}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.put("/reorder-divisions")
async def reorder_divisions(branch_id: str, payload: ReorderDivisionsRequest) -> Dict[str, Any]:
    """Menyusun ulang urutan tampilan divisi dalam struktur organisasi."""
    branch = await corporate_repo.get_branch_by_id(branch_id)
    if not branch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Branch '{branch_id}' tidak ditemukan.")
    if branch_id == "branch_main" or branch.get("slug") == "main":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Branch 'branch_main' dilindungi. Fork workflow terlebih dahulu.")

    try:
        await workflow_repo.reorder_divisions(branch_id, payload.ordered_division_ids)
        return {"status": "success", "message": f"Urutan divisi pada branch '{branch['name']}' berhasil diperbarui."}
    except Exception as err:
        logger.error(f"Gagal reorder divisi pada branch '{branch_id}': {err}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
