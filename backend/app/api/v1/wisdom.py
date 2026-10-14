"""
REST API Router untuk Corporate Wisdom Base & Vector Memory.
Menyediakan endpoint pencarian semantik kosinus, katalog wisdom, dan distilasi otomatis.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.db.pr_repo import pr_repo
from app.db.wisdom_repo import wisdom_repo
from app.engine.wisdom_engine import wisdom_engine

router = APIRouter(prefix="/wisdom", tags=["Corporate Wisdom Base"])


class WisdomCreate(BaseModel):
    """Skema pembuatan entri wisdom baru."""
    namespace: str = Field(default="wisdom:architecture", description="Namespace kategori")
    title: str = Field(..., min_length=3, description="Judul ringkas panduan")
    problem_pattern: str = Field(..., min_length=5, description="Pola masalah yang dihadapi")
    solution_guideline: str = Field(..., min_length=5, description="Arahan solusi preskriptif")
    tags: List[str] = Field(default_factory=list, description="Tag kata kunci")
    source_venture_id: str = Field(default="global", description="ID venture asal")


class WisdomSearchRequest(BaseModel):
    """Skema payload pencarian semantik."""
    query: str = Field(..., min_length=2, description="Teks query pencarian")
    namespace: Optional[str] = Field(None, description="Filter namespace spesifik")
    target_role: Optional[str] = Field(None, description="Peran agen target")
    top_k: int = Field(default=3, ge=1, le=10, description="Jumlah hasil maksimal")
    min_similarity: float = Field(default=0.20, ge=0.0, le=1.0, description="Skor minimal")


@router.get("", status_code=status.HTTP_200_OK)
async def list_wisdom(
    namespace: Optional[str] = Query(None, description="Filter namespace"),
    tag: Optional[str] = Query(None, description="Filter tag kata kunci"),
    limit: int = Query(50, ge=1, le=100, description="Batas entri"),
) -> List[Dict[str, Any]]:
    """Mendaftar seluruh entri wisdom yang aktif."""
    try:
        return await wisdom_repo.list_wisdom(namespace=namespace, tag=tag, limit=limit)
    except Exception as err:
        logger.error(f"Gagal memuat daftar wisdom: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_wisdom(payload: WisdomCreate) -> Dict[str, Any]:
    """Mendaftarkan entri wisdom baru secara manual oleh Founder."""
    try:
        return await wisdom_engine.record_wisdom(
            title=payload.title,
            problem_pattern=payload.problem_pattern,
            solution_guideline=payload.solution_guideline,
            namespace=payload.namespace,
            tags=payload.tags,
            source_venture_id=payload.source_venture_id,
        )
    except Exception as err:
        logger.error(f"Gagal mencatat wisdom: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))


@router.post("/search", status_code=status.HTTP_200_OK)
async def search_wisdom(payload: WisdomSearchRequest) -> List[Dict[str, Any]]:
    """Melakukan pencarian semantik berbasis Cosine Similarity 128-dimensi."""
    try:
        return await wisdom_engine.query_wisdom(
            query=payload.query,
            target_role=payload.target_role,
            namespace=payload.namespace,
            top_k=payload.top_k,
            min_similarity=payload.min_similarity,
        )
    except Exception as err:
        logger.error(f"Pencarian semantik wisdom gagal: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))


@router.get("/summary", status_code=status.HTTP_200_OK)
async def get_wisdom_summary() -> Dict[str, Any]:
    """Mengambil ringkasan metrik memori korporat lintas-venture."""
    try:
        items = await wisdom_repo.list_wisdom(limit=200)
        total = len(items)
        ns_counts: Dict[str, int] = {}
        for it in items:
            ns = it.get("namespace", "other")
            ns_counts[ns] = ns_counts.get(ns, 0) + 1

        top_used = sorted(items, key=lambda x: x.get("usage_count", 0), reverse=True)[:5]
        return {
            "total_count": total,
            "namespace_breakdown": ns_counts,
            "top_reused_wisdom": top_used,
        }
    except Exception as err:
        logger.error(f"Gagal memuat summary wisdom: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))


@router.post("/distill/{pr_id}", status_code=status.HTTP_201_CREATED)
async def distill_wisdom_from_pr(pr_id: str) -> Dict[str, Any]:
    """Mengekstraksi pembelajaran dari Pull Request yang telah di-merge."""
    try:
        pr = await pr_repo.get_pull_request(pr_id)
        if not pr:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"PR [{pr_id}] tidak ditemukan.")

        reviews = await pr_repo.get_reviews(pr_id)
        created = await wisdom_engine.distill_from_pr(pr, reviews)
        if not created:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gagal menyarikan wisdom dari PR.")
        return created
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Gagal mendistilasi PR [{pr_id}]: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))


@router.delete("/{wisdom_id}", status_code=status.HTTP_200_OK)
async def delete_wisdom(wisdom_id: str) -> Dict[str, Any]:
    """Menghapus entri wisdom (soft delete)."""
    try:
        success = await wisdom_repo.delete_wisdom(wisdom_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Wisdom [{wisdom_id}] tidak ditemukan.")
        return {"status": "success", "message": f"Wisdom [{wisdom_id}] berhasil dinonaktifkan."}
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Gagal menghapus wisdom [{wisdom_id}]: {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
