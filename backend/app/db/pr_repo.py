"""Pull Request & Peer Review Repository Layer.

Menyimpan dan mengelola siklus hidup Pull Request, catatan inline reviews,
serta penghitungan kuorum persetujuan lintas peran AI pada SQLite WAL.
"""

import json
from typing import Any, Dict, List, Optional
import uuid
import aiosqlite

from app.core.logger import logger
from app.db.session import get_db_connection


class PullRequestRepository:
    """Repositori asinkron untuk operasi entitas internal Pull Request dan Peer Reviews."""

    def _map_pr(self, row: aiosqlite.Row) -> Dict[str, Any]:
        """Memetakan baris basis data ke dictionary objek Pull Request."""
        try:
            files = json.loads(row["files_changed_json"])
        except (json.JSONDecodeError, TypeError):
            files = []

        return {
            "id": row["id"],
            "project_id": row["project_id"],
            "ticket_id": row["ticket_id"],
            "title": row["title"],
            "description": row["description"],
            "source_branch": row["source_branch"],
            "target_branch": row["target_branch"],
            "author_role_id": row["author_role_id"],
            "status": row["status"],
            "files": files,
            "diff_unified": row["diff_unified"],
            "additions_count": int(row["additions_count"]),
            "deletions_count": int(row["deletions_count"]),
            "quorum_required": int(row["quorum_required"]),
            "approvals_count": int(row["approvals_count"]),
            "created_at": str(row["created_at"]),
            "updated_at": str(row["updated_at"]),
        }

    async def create_pull_request(
        self, project_id: str, ticket_id: Optional[str], title: str, description: str,
        source_branch: str, author_role_id: str, files_changed: List[Dict[str, Any]],
        diff_unified: str = "", additions_count: int = 0, deletions_count: int = 0,
        target_branch: str = "branch_main", quorum_required: int = 2, custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mendaftarkan objek Pull Request baru untuk ditinjau oleh rekanan AI."""
        pr_id = f"pr_{uuid.uuid4().hex[:10]}"
        files_json = json.dumps(files_changed)
        sql = (
            "INSERT INTO corporate_pull_requests (id, project_id, ticket_id, title, description, "
            "source_branch, target_branch, author_role_id, status, files_changed_json, diff_unified, "
            "additions_count, deletions_count, quorum_required, approvals_count) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?, ?, ?, ?, 0);"
        )
        params = (
            pr_id, project_id, ticket_id, title, description, source_branch,
            target_branch, author_role_id, files_json, diff_unified,
            additions_count, deletions_count, quorum_required
        )
        async with get_db_connection(custom_path) as conn:
            await conn.execute(sql, params)
            await conn.commit()
            logger.info(f"PR '{title}' ({pr_id}) berhasil dibuka oleh peran [{author_role_id}].")

        pr = await self.get_pull_request(pr_id, custom_path)
        if not pr:
            raise RuntimeError(f"Gagal mengambil data PR '{pr_id}'.")
        return pr

    async def get_pull_request(self, pr_id: str, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Mengambil data lengkap satu Pull Request berdasarkan ID."""
        sql = "SELECT * FROM corporate_pull_requests WHERE id = ?;"
        async with get_db_connection(custom_path) as conn:
            async with conn.execute(sql, (pr_id,)) as cur:
                row = await cur.fetchone()
                return self._map_pr(row) if row else None

    async def list_pull_requests(
        self,
        project_id: str,
        status: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mengambil daftar Pull Requests milik sebuah proyek venture."""
        conditions = ["project_id = ?"]
        params: List[Any] = [project_id]
        if status:
            conditions.append("status = ?")
            params.append(status)

        sql = f"SELECT * FROM corporate_pull_requests WHERE {' AND '.join(conditions)} ORDER BY created_at DESC;"
        async with get_db_connection(custom_path) as conn:
            async with conn.execute(sql, params) as cur:
                rows = await cur.fetchall()
                return [self._map_pr(r) for r in rows]

    async def add_review(
        self,
        pr_id: str,
        reviewer_role_id: str,
        reviewer_name: str,
        verdict: str,
        summary: str,
        inline_comments: Optional[List[Dict[str, Any]]] = None,
        security_score: int = 100,
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mencatat tinjauan kode rekanan (Peer Review) dan memperbarui kuorum PR."""
        rev_id = f"rev_{uuid.uuid4().hex[:10]}"
        comments_json = json.dumps(inline_comments or [])

        sql = """
        INSERT INTO corporate_pr_reviews
        (id, pr_id, reviewer_role_id, reviewer_name, verdict, summary, inline_comments_json, security_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        async with get_db_connection(custom_path) as conn:
            await conn.execute(sql, (rev_id, pr_id, reviewer_role_id, reviewer_name, verdict, summary, comments_json, security_score))
            await conn.commit()
            logger.info(f"Review ditambahkan pada {pr_id} oleh [{reviewer_role_id}]: {verdict}.")

        await self._evaluate_and_update_quorum(pr_id, custom_path)
        return {
            "id": rev_id,
            "pr_id": pr_id,
            "reviewer_role_id": reviewer_role_id,
            "verdict": verdict,
            "summary": summary,
            "inline_comments": inline_comments or [],
            "security_score": security_score,
        }

    async def get_reviews(self, pr_id: str, custom_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mengambil seluruh riwayat review rekanan untuk suatu Pull Request."""
        sql = "SELECT * FROM corporate_pr_reviews WHERE pr_id = ? ORDER BY created_at ASC;"
        async with get_db_connection(custom_path) as conn:
            async with conn.execute(sql, (pr_id,)) as cur:
                rows = await cur.fetchall()
                return [
                    {
                        "id": r["id"],
                        "pr_id": r["pr_id"],
                        "reviewer_role_id": r["reviewer_role_id"],
                        "reviewer_name": r["reviewer_name"],
                        "verdict": r["verdict"],
                        "summary": r["summary"],
                        "inline_comments": json.loads(r["inline_comments_json"]) if r["inline_comments_json"] else [],
                        "security_score": int(r["security_score"]),
                        "created_at": str(r["created_at"]),
                    }
                    for r in rows
                ]

    async def _evaluate_and_update_quorum(self, pr_id: str, custom_path: Optional[str] = None) -> None:
        """Menghitung kuorum persetujuan dan menentukan status kelayakan PR."""
        reviews = await self.get_reviews(pr_id, custom_path)
        approvals = sum(1 for r in reviews if r["verdict"] == "APPROVED")
        has_changes_req = any(r["verdict"] == "CHANGES_REQUESTED" for r in reviews)

        pr = await self.get_pull_request(pr_id, custom_path)
        if not pr:
            return

        if pr["status"] in ("MERGED", "CLOSED"):
            return

        new_status = "CHANGES_REQUESTED" if has_changes_req else ("APPROVED" if approvals >= pr["quorum_required"] else "OPEN")
        async with get_db_connection(custom_path) as conn:
            await conn.execute(
                "UPDATE corporate_pull_requests SET approvals_count = ?, status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
                (approvals, new_status, pr_id)
            )
            await conn.commit()

    async def update_pr_status(self, pr_id: str, status: str, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Memperbarui status Pull Request secara eksplisit (misal MERGED atau CLOSED)."""
        async with get_db_connection(custom_path) as conn:
            await conn.execute(
                "UPDATE corporate_pull_requests SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
                (status, pr_id)
            )
            await conn.commit()
        return await self.get_pull_request(pr_id, custom_path)


pr_repo = PullRequestRepository()
