"""Pull Request & Peer Review API Router.

Menyediakan endpoint REST API untuk pembuatan, peninjauan, penelaahan Git unified diff,
dan penggabungan (merge) Pull Request internal antar-karyawan AI.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.db.pr_repo import pr_repo
from app.engine.quality.peer_reviewer import peer_reviewer
from app.engine.quality.diff_engine import compute_multi_file_diff


router = APIRouter(prefix="/pull-requests", tags=["pull-requests"])


class CreatePRRequest(BaseModel):
    """Payload pendaftaran Pull Request baru."""
    project_id: str
    ticket_id: Optional[str] = None
    title: str
    description: str = ""
    source_branch: str
    author_role_id: str
    target_branch: str = "branch_main"
    files_delta: List[Dict[str, str]] = Field(..., description="Daftar berkas dengan path, old_content, new_content")
    quorum_required: int = 2


class ReviewSubmissionRequest(BaseModel):
    """Payload penyerahan tinjauan kode manual (misal CEO Veto/Approval)."""
    reviewer_role_id: str = "role_ceo"
    reviewer_name: str = "Founder / CEO"
    verdict: str = Field(..., description="APPROVED, CHANGES_REQUESTED, COMMENT")
    summary: str
    inline_comments: Optional[List[Dict[str, Any]]] = None


@router.get("/project/{project_id}", response_model=List[Dict[str, Any]])
async def list_project_prs(
    project_id: str,
    status: Optional[str] = Query(None, description="Filter status PR (OPEN, APPROVED, MERGED, dll.)"),
) -> List[Dict[str, Any]]:
    """Mengambil daftar seluruh Pull Request untuk suatu proyek venture."""
    return await pr_repo.list_pull_requests(project_id=project_id, status=status)


@router.get("/{pr_id}", response_model=Dict[str, Any])
async def get_pr_details(pr_id: str) -> Dict[str, Any]:
    """Mengambil detail lengkap satu PR beserta riwayat review rekanan AI."""
    pr = await pr_repo.get_pull_request(pr_id)
    if not pr:
        raise HTTPException(status_code=404, detail=f"PR '{pr_id}' tidak ditemukan.")

    reviews = await pr_repo.get_reviews(pr_id)
    return {**pr, "reviews": reviews}


@router.post("", response_model=Dict[str, Any])
async def create_pull_request(payload: CreatePRRequest) -> Dict[str, Any]:
    """Membuka Pull Request baru dan menghitung git-style unified diff secara otomatis."""
    diff_res = compute_multi_file_diff(payload.files_delta)
    pr = await pr_repo.create_pull_request(
        project_id=payload.project_id,
        ticket_id=payload.ticket_id,
        title=payload.title,
        description=payload.description,
        source_branch=payload.source_branch,
        author_role_id=payload.author_role_id,
        files_changed=diff_res["files"],
        diff_unified=diff_res["unified_diff"],
        additions_count=diff_res["total_additions"],
        deletions_count=diff_res["total_deletions"],
        target_branch=payload.target_branch,
        quorum_required=payload.quorum_required,
    )
    return pr


@router.post("/{pr_id}/auto-review", response_model=Dict[str, Any])
async def trigger_autonomous_peer_review(pr_id: str) -> Dict[str, Any]:
    """Memicu siklus peninjauan kode otomatis oleh QA, CTO, dan Peer Specialist."""
    try:
        res = await peer_reviewer.run_full_autonomous_review(pr_id)
        return res
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))


@router.post("/{pr_id}/review", response_model=Dict[str, Any])
async def submit_manual_review(pr_id: str, payload: ReviewSubmissionRequest) -> Dict[str, Any]:
    """Menyimpan review manual (misal approval atau masukan dari Founder/CEO)."""
    pr = await pr_repo.get_pull_request(pr_id)
    if not pr:
        raise HTTPException(status_code=404, detail=f"PR '{pr_id}' tidak ditemukan.")

    rev = await pr_repo.add_review(
        pr_id=pr_id,
        reviewer_role_id=payload.reviewer_role_id,
        reviewer_name=payload.reviewer_name,
        verdict=payload.verdict,
        summary=payload.summary,
        inline_comments=payload.inline_comments,
    )
    return rev


@router.post("/{pr_id}/merge", response_model=Dict[str, Any])
async def merge_pull_request(
    pr_id: str,
    force: bool = Query(False, description="Paksa merge tanpa menunggu kuorum (CEO Override)"),
) -> Dict[str, Any]:
    """Menggabungkan (merge) kode PR ke target branch jika kuorum terpenuhi atau dipaksa CEO."""
    pr = await pr_repo.get_pull_request(pr_id)
    if not pr:
        raise HTTPException(status_code=404, detail=f"PR '{pr_id}' tidak ditemukan.")

    if pr["status"] == "MERGED":
        return {"status": "ALREADY_MERGED", "pr": pr}

    if pr["status"] != "APPROVED" and not force:
        raise HTTPException(
            status_code=400,
            detail=f"PR belum disetujui kuorum (Status: {pr['status']}, Approvals: {pr['approvals_count']}/{pr['quorum_required']}). Gunakan ?force=true untuk CEO veto override.",
        )

    merged = await pr_repo.update_pr_status(pr_id, "MERGED")
    logger.info(f"PR '{pr_id}' berhasil di-merge ke {pr['target_branch']}.")

    try:
        from app.engine.tools.git_exporter import git_exporter
        await git_exporter.export_project_checkpoint(
            project_id=pr["project_id"],
            commit_message=f"feat(pr): merge PR #{pr_id} - {pr.get('title', '')}",
        )
    except Exception as g_err:
        logger.warning(f"Git export untuk PR [{pr_id}] dilewati: {g_err}")

    return {"status": "MERGED", "pr": merged}
