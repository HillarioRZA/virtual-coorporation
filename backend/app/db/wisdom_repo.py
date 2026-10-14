"""
Repositori Akses Data SQLite untuk Corporate Wisdom Base.
Menangani persistensi memori institusional, metadata, dan vektor embedding.
"""

import json
from typing import Any, Dict, List, Optional
import aiosqlite

from app.core.logger import logger
from app.db.session import get_db_connection


class CorporateWisdomRepo:
    """Manajer persistensi basis data untuk tabel corporate_wisdom."""

    async def save_wisdom(
        self,
        wisdom_id: str,
        namespace: str,
        title: str,
        problem_pattern: str,
        solution_guideline: str,
        tags: List[str],
        embedding: List[float],
        source_venture_id: str = "global",
        source_pr_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Menyimpan atau memperbarui catatan wisdom ke basis data."""
        query = """
        INSERT INTO corporate_wisdom 
        (id, namespace, title, problem_pattern, solution_guideline, tags, embedding, source_venture_id, source_pr_id, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            namespace=excluded.namespace, title=excluded.title, problem_pattern=excluded.problem_pattern,
            solution_guideline=excluded.solution_guideline, tags=excluded.tags, embedding=excluded.embedding,
            source_venture_id=excluded.source_venture_id, source_pr_id=excluded.source_pr_id, updated_at=CURRENT_TIMESTAMP;
        """
        try:
            async with get_db_connection(custom_path) as conn:
                await conn.execute(
                    query,
                    (wisdom_id, namespace, title, problem_pattern, solution_guideline, json.dumps(tags), json.dumps(embedding), source_venture_id, source_pr_id),
                )
                await conn.commit()
            return await self.get_wisdom_by_id(wisdom_id, custom_path=custom_path) or {}
        except aiosqlite.Error as err:
            logger.error(f"Gagal menyimpan wisdom [{wisdom_id}]: {err}")
            raise

    async def get_wisdom_by_id(self, wisdom_id: str, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Mengambil satu entri wisdom aktif berdasarkan ID."""
        try:
            async with get_db_connection(custom_path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute("SELECT * FROM corporate_wisdom WHERE id = ? AND is_active = 1;", (wisdom_id,)) as cur:
                    row = await cur.fetchone()
                    return self._map_row(row) if row else None
        except aiosqlite.Error as err:
            logger.error(f"Gagal mengambil wisdom [{wisdom_id}]: {err}")
            raise

    async def list_wisdom(
        self,
        namespace: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 50,
        custom_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mendaftar entri wisdom dengan filter namespace dan tag."""
        conditions, params = ["is_active = 1"], []
        if namespace:
            conditions.append("namespace = ?")
            params.append(namespace)
        if tag:
            conditions.append("tags LIKE ?")
            params.append(f'%"{tag}"%')

        sql = f"SELECT * FROM corporate_wisdom WHERE {' AND '.join(conditions)} ORDER BY usage_count DESC, created_at DESC LIMIT ?;"
        params.append(limit)

        try:
            async with get_db_connection(custom_path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute(sql, tuple(params)) as cur:
                    rows = await cur.fetchall()
                    return [self._map_row(r) for r in rows]
        except aiosqlite.Error as err:
            logger.error(f"Gagal mendaftar wisdom: {err}")
            raise

    async def get_all_embeddings(
        self,
        namespace: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mengambil seluruh vektor embedding dan metadata untuk pencarian kosinus."""
        sql = "SELECT id, namespace, title, problem_pattern, solution_guideline, tags, embedding, source_venture_id, usage_count FROM corporate_wisdom WHERE is_active = 1"
        params: List[Any] = []
        if namespace:
            sql += " AND namespace = ?"
            params.append(namespace)

        try:
            async with get_db_connection(custom_path) as conn:
                conn.row_factory = aiosqlite.Row
                async with conn.execute(sql, tuple(params)) as cur:
                    rows = await cur.fetchall()
                    return [self._map_row(r) for r in rows]
        except aiosqlite.Error as err:
            logger.error(f"Gagal mengambil vektor wisdom: {err}")
            raise

    async def increment_usage(self, wisdom_id: str, custom_path: Optional[str] = None) -> None:
        """Menaikkan penghitung penggunaan wisdom saat disuntikkan ke konteks agen."""
        try:
            async with get_db_connection(custom_path) as conn:
                await conn.execute("UPDATE corporate_wisdom SET usage_count = usage_count + 1 WHERE id = ?;", (wisdom_id,))
                await conn.commit()
        except aiosqlite.Error as err:
            logger.warning(f"Gagal menaikkan usage count wisdom [{wisdom_id}]: {err}")

    async def delete_wisdom(self, wisdom_id: str, custom_path: Optional[str] = None) -> bool:
        """Menghapus entri wisdom (soft delete via is_active = 0)."""
        try:
            async with get_db_connection(custom_path) as conn:
                cur = await conn.execute("UPDATE corporate_wisdom SET is_active = 0 WHERE id = ?;", (wisdom_id,))
                await conn.commit()
                return cur.rowcount > 0
        except aiosqlite.Error as err:
            logger.error(f"Gagal menghapus wisdom [{wisdom_id}]: {err}")
            raise

    def _map_row(self, row: aiosqlite.Row) -> Dict[str, Any]:
        """Memetakan baris aiosqlite ke struktur Dict Python."""
        d = dict(row)
        for field in ("tags", "embedding"):
            try:
                d[field] = json.loads(d.get(field) or "[]")
            except json.JSONDecodeError:
                d[field] = []
        return d


wisdom_repo = CorporateWisdomRepo()
