"""
REST API Endpoints untuk Manajemen Perpustakaan Skills & Kategorisasi Dinamis.
Menyediakan katalog pencarian FTS5 dan instalasi playbook domain tanpa membebani model ONNX.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.engine.skills.skills_hub import skills_hub

router = APIRouter(prefix="/skills", tags=["Skills Library & Taxonomy"])


class SkillInstallRequest(BaseModel):
    name: str = Field(description="Nama unik skill (misal: flutter-clean-architecture)")
    category_name: str = Field(description="Nama kategori (dibuat otomatis jika belum ada)")
    description: Optional[str] = Field(default=None, description="Ringkasan skill")
    skill_md_content: str = Field(description="Isi konten SKILL.md dalam markdown")
    additional_files: Optional[Dict[str, str]] = Field(default=None, description="Berkas scripts/assets")


class SkillGitImportRequest(BaseModel):
    repo_url: str = Field(description="URL repositori Git publik (misal: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)")
    category_name: Optional[str] = Field(default=None, description="Kategori kustom opsional")
    name: Optional[str] = Field(default=None, description="Nama skill kustom opsional")


@router.get("/categories")
async def get_categories() -> List[Dict[str, Any]]:
    """Mendapatkan daftar seluruh kategori skills yang tersedia di sistem."""
    try:
        return await skills_hub.list_categories()
    except Exception as err:
        logger.error(f"Gagal memuat kategori skills: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.get("")
async def search_skills(
    q: Optional[str] = None, category: Optional[str] = None, limit: int = 20
) -> List[Dict[str, Any]]:
    """Mencari skills menggunakan pencarian FTS5 atau menyaring berdasarkan kategori."""
    try:
        query_text = q.strip() if q else ""
        return await skills_hub.search_skills(query=query_text, category_slug=category, top_k=limit)
    except Exception as err:
        logger.error(f"Gagal mencari skills: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/install", status_code=status.HTTP_201_CREATED)
async def install_skill(req: SkillInstallRequest) -> Dict[str, Any]:
    """Menginstal playbook skill baru dan mendaftarkannya ke kategori dan indeks FTS5."""
    try:
        files: Dict[str, Any] = {"SKILL.md": req.skill_md_content}
        if req.additional_files:
            files.update(req.additional_files)

        res = await skills_hub.install_skill_bundle(
            name=req.name,
            category_name=req.category_name,
            files=files,
            description=req.description,
        )
        return {"status": "SUCCESS", "skill": res}
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as err:
        logger.error(f"Gagal menginstal skill: {err}")
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/import-git", status_code=status.HTTP_201_CREATED)
async def import_skill_git(req: SkillGitImportRequest) -> Dict[str, Any]:
    """Mengkloning repositori Git publik (seperti ui-ux-pro-max-skill) dan mendaftarkan bundle berkasnya."""
    from app.engine.skills.git_importer import import_skill_from_git
    try:
        res = await import_skill_from_git(
            repo_url=req.repo_url,
            custom_name=req.name,
            custom_category=req.category_name,
        )
        return {"status": "SUCCESS", "skill": res}
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as err:
        logger.error(f"Gagal mengimpor skill dari Git: {err}")
        raise HTTPException(status_code=500, detail=f"Gagal mengimpor skill Git: {err}")
