"""
Corporate Pipeline Registry Repository.
Mengelola registri rantai alur kerja multi-produk (Multi-Pipeline)
seperti Software, Edukasi, Copywriting, dan Riset Pasar.
"""

from typing import Any, Dict, List, Optional
import uuid
import aiosqlite

from app.core.logger import logger
from app.db.session import get_db_connection


class PipelineRepository:
    """Repositori asinkron untuk operasi CRUD rantai pipeline produk."""

    async def get_pipelines(
        self, branch_id: str, custom_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Mengambil seluruh pipeline alur kerja yang terdaftar pada branch."""
        query = """
            SELECT p.*, COUNT(s.id) AS stages_count
            FROM corporate_pipelines p
            LEFT JOIN corporate_pipeline_stages s ON p.id = s.pipeline_id AND s.branch_id = p.branch_id
            WHERE p.branch_id = ?
            GROUP BY p.id
            ORDER BY p.is_default DESC, p.created_at ASC;
        """
        try:
            async with get_db_connection(custom_path) as conn:
                async with conn.execute(query, (branch_id,)) as cur:
                    rows = await cur.fetchall()
                    return [
                        {
                            "id": r["id"],
                            "branch_id": r["branch_id"],
                            "name": r["name"],
                            "slug": r["slug"],
                            "product_line": r["product_line"],
                            "description": r["description"],
                            "is_default": bool(r["is_default"]),
                            "stages_count": int(r["stages_count"]),
                            "created_at": str(r["created_at"]),
                            "updated_at": str(r["updated_at"]),
                        }
                        for r in rows
                    ]
        except aiosqlite.Error as err:
            logger.error(f"Gagal mengambil daftar pipeline branch '{branch_id}': {err}")
            raise

    async def get_pipeline_by_id(
        self, pipeline_id: str, custom_path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Mengambil satu pipeline berdasarkan ID."""
        query = "SELECT * FROM corporate_pipelines WHERE id = ?;"
        try:
            async with get_db_connection(custom_path) as conn:
                async with conn.execute(query, (pipeline_id,)) as cur:
                    r = await cur.fetchone()
                    if not r:
                        return None
                    return {
                        "id": r["id"],
                        "branch_id": r["branch_id"],
                        "name": r["name"],
                        "slug": r["slug"],
                        "product_line": r["product_line"],
                        "description": r["description"],
                        "is_default": bool(r["is_default"]),
                        "created_at": str(r["created_at"]),
                        "updated_at": str(r["updated_at"]),
                    }
        except aiosqlite.Error as err:
            logger.error(f"Gagal mengambil pipeline '{pipeline_id}': {err}")
            raise

    async def create_pipeline(
        self,
        branch_id: str,
        name: str,
        slug: str,
        product_line: str = "CUSTOM",
        description: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Membuat pipeline alur kerja baru untuk lini produk tertentu."""
        pipe_id = f"pipe_{uuid.uuid4().hex[:8]}"
        stmt = """
            INSERT INTO corporate_pipelines
            (id, branch_id, name, slug, product_line, description, is_default)
            VALUES (?, ?, ?, ?, ?, ?, 0);
        """
        try:
            async with get_db_connection(custom_path) as conn:
                await conn.execute(stmt, (pipe_id, branch_id, name, slug, product_line, description))
                await conn.commit()
            logger.info(f"Pipeline baru dibuat [{pipe_id}] '{name}' ({product_line})")
            return await self.get_pipeline_by_id(pipe_id, custom_path) or {}
        except aiosqlite.Error as err:
            logger.error(f"Gagal membuat pipeline '{slug}': {err}")
            raise

    async def delete_pipeline(
        self, branch_id: str, pipeline_id: str, custom_path: Optional[str] = None
    ) -> bool:
        """Menghapus pipeline non-default dari branch."""
        existing = await self.get_pipeline_by_id(pipeline_id, custom_path)
        if not existing or existing.get("is_default"):
            return False
        try:
            async with get_db_connection(custom_path) as conn:
                await conn.execute("DELETE FROM corporate_pipeline_stages WHERE pipeline_id = ?;", (pipeline_id,))
                cur = await conn.execute(
                    "DELETE FROM corporate_pipelines WHERE id = ? AND branch_id = ? AND is_default = 0;",
                    (pipeline_id, branch_id),
                )
                await conn.commit()
                return cur.rowcount > 0
        except aiosqlite.Error as err:
            logger.error(f"Gagal menghapus pipeline '{pipeline_id}': {err}")
            raise


pipeline_repo = PipelineRepository()
