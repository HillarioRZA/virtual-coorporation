"""Corporate Registry & Git-Style Workflow Branching API Endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.core.logger import logger
from app.db.corporate_repo import corporate_repo
from app.engine.memory.wisdom_engine import wisdom_engine
from app.engine.schemas.corporate_schemas import (
    BranchCreate,
    BranchForkRequest,
    BranchResponse,
    DivisionCreate,
    DivisionResponse,
    DivisionUpdate,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
)

router = APIRouter(prefix="/corporate", tags=["Corporate & Org Studio"])


async def _sync_wisdom() -> None:
    try:
        await wisdom_engine.sync_organization_knowledge()
    except Exception as e:
        logger.debug(f"Wisdom sync: {e}")


# 1. BRANCHING ENDPOINTS (Git-Style Workflows)
@router.get("/branches", response_model=List[BranchResponse])
async def list_branches() -> List[BranchResponse]:
    """Mengambil seluruh daftar branch alur kerja organisasi."""
    return await corporate_repo.get_branches()


@router.get("/branches/active", response_model=BranchResponse)
async def get_active_branch() -> BranchResponse:
    """Mengambil branch alur kerja yang saat ini aktif untuk produksi."""
    active = await corporate_repo.get_active_branch()
    if not active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active branch tidak ditemukan.")
    return active


@router.post("/branches/fork", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def fork_branch(payload: BranchForkRequest) -> BranchResponse:
    """Melakukan kloning / forking seluruh divisi & role dari branch sumber ke branch baru."""
    try:
        res = await corporate_repo.fork_branch(
            name=payload.name, slug=payload.slug,
            description=payload.description, source_branch_id=payload.source_branch_id,
        )
        await _sync_wisdom()
        return res
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.post("/branches/{branch_id}/activate", response_model=BranchResponse)
async def activate_branch(branch_id: str) -> BranchResponse:
    """Mempromosikan branch eksperimen menjadi active production main."""
    try:
        res = await corporate_repo.activate_branch(branch_id)
        await _sync_wisdom()
        return res
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

@router.delete("/branches/{branch_id}")
async def delete_branch(branch_id: str) -> Dict[str, Any]:
    """Menghapus branch eksperimen (branch main atau active dilindungi)."""
    try:
        await corporate_repo.delete_branch(branch_id)
        await _sync_wisdom()
        return {"status": "success", "message": f"Branch '{branch_id}' berhasil dihapus."}
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
# 2. DIVISION ENDPOINTS
@router.get("/divisions", response_model=List[DivisionResponse])
async def list_divisions(branch_id: Optional[str] = Query(None, description="Filter by branch ID")) -> List[DivisionResponse]:
    """Mengambil seluruh divisi pada branch tertentu."""
    return await corporate_repo.get_divisions(branch_id=branch_id)


@router.get("/divisions/{division_id}", response_model=DivisionResponse)
async def get_division(division_id: str) -> DivisionResponse:
    """Mengambil detail satu divisi."""
    division = await corporate_repo.get_division_by_id(division_id)
    if not division:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Divisi '{division_id}' tidak ditemukan.")
    return division


@router.post("/divisions", response_model=DivisionResponse, status_code=status.HTTP_201_CREATED)
async def create_division(payload: DivisionCreate) -> DivisionResponse:
    """Membuat divisi kustom baru pada branch tertentu."""
    try:
        res = await corporate_repo.create_division(
            branch_id=payload.branch_id, name=payload.name, slug=payload.slug,
            description=payload.description, accent_color=payload.accent_color, icon_name=payload.icon_name,
        )
        await _sync_wisdom()
        return res
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.put("/divisions/{division_id}", response_model=DivisionResponse)
async def update_division(division_id: str, payload: DivisionUpdate) -> DivisionResponse:
    """Memperbarui metadata divisi."""
    updated = await corporate_repo.update_division(
        division_id=division_id, name=payload.name, description=payload.description,
        accent_color=payload.accent_color, icon_name=payload.icon_name,
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Divisi '{division_id}' tidak ditemukan.")
    await _sync_wisdom()
    return updated


@router.delete("/divisions/{division_id}")
async def delete_division(division_id: str) -> Dict[str, Any]:
    """Menghapus divisi kustom (divisi bawaan sistem pada branch main dilindungi)."""
    try:
        await corporate_repo.delete_division(division_id)
        await _sync_wisdom()
        return {"status": "success", "message": f"Divisi '{division_id}' berhasil dihapus."}
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
# 3. ROLE ENDPOINTS
@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    division_id: Optional[str] = Query(None, description="Filter by division ID"),
    active_only: bool = Query(False, description="Hanya tampilkan role aktif"),
) -> List[RoleResponse]:
    """Mengambil seluruh role karyawan AI."""
    return await corporate_repo.get_roles(branch_id=branch_id, division_id=division_id, active_only=active_only)

@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: str) -> RoleResponse:
    """Mengambil detail satu role karyawan AI."""
    role = await corporate_repo.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role '{role_id}' tidak ditemukan.")
    return role

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(payload: RoleCreate) -> RoleResponse:
    """Mendaftarkan role karyawan AI baru pada branch dan divisi tertentu tanpa slug."""
    try:
        res = await corporate_repo.create_role(
            branch_id=payload.branch_id, division_id=payload.division_id,
            name=payload.name, job_description=payload.job_description or "",
            persona_prompt=payload.persona_prompt or "",
            system_prompt_template=payload.system_prompt_template, model_provider=payload.model_provider,
            model_name=payload.model_name, temperature=payload.temperature,
            tool_permissions=payload.tool_permissions, token_budget_per_task=payload.token_budget_per_task,
            is_active=payload.is_active, thinking_level=payload.thinking_level,
        )
        await _sync_wisdom()
        return res
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(role_id: str, payload: RoleUpdate) -> RoleResponse:
    """Memperbarui konfigurasi role."""
    try:
        updated = await corporate_repo.update_role(
            role_id=role_id, division_id=payload.division_id, name=payload.name,
            job_description=payload.job_description, persona_prompt=payload.persona_prompt,
            system_prompt_template=payload.system_prompt_template,
            model_provider=payload.model_provider, model_name=payload.model_name,
            temperature=payload.temperature, tool_permissions=payload.tool_permissions,
            token_budget_per_task=payload.token_budget_per_task, is_active=payload.is_active,
            thinking_level=payload.thinking_level,
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role '{role_id}' tidak ditemukan.")
        await _sync_wisdom()
        return updated
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.delete("/roles/{role_id}")
async def delete_role(role_id: str) -> Dict[str, Any]:
    """Menghapus role kustom."""
    try:
        await corporate_repo.delete_role(role_id)
        await _sync_wisdom()
        return {"status": "success", "message": f"Role '{role_id}' berhasil dihapus."}
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
