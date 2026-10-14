"""Division Repository Layer.

Mengelola siklus hidup divisi korporat, relasi departemen, dan skema warna/ikon pada SQLite.
"""

from typing import Any, Dict, List, Optional
import uuid

import aiosqlite
from app.core.logger import logger
from app.db.session import get_db_connection
from app.db.branch_repo import branch_repo


class DivisionRepository:
    """Repositori asinkron untuk operasi entitas divisi korporat."""

    async def get_divisions(
        self, branch_id: Optional[str] = None, custom_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Mengambil seluruh divisi pada branch tertentu (default ke branch aktif)."""
        target_branch = branch_id
        if not target_branch:
            active_branch = await branch_repo.get_active_branch(custom_path)
            target_branch = active_branch["id"] if active_branch else "branch_main"

        query = """
            SELECT d.id, d.branch_id, d.name, d.slug, d.description, d.accent_color, d.icon_name, 
                   d.is_system_default, COALESCE(d.order_index, 0) as order_index, d.created_at, d.updated_at,
                   COUNT(r.id) as roles_count
            FROM corporate_divisions d
            LEFT JOIN corporate_roles r ON d.id = r.division_id AND r.is_active = 1
            WHERE d.branch_id = ?
            GROUP BY d.id
            ORDER BY COALESCE(d.order_index, 0) ASC, d.is_system_default DESC, d.created_at ASC;
        """
        async with get_db_connection(custom_path) as conn:
            async with conn.execute(query, (target_branch,)) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "id": row["id"],
                        "branch_id": row["branch_id"],
                        "name": row["name"],
                        "slug": row["slug"],
                        "description": row["description"],
                        "accent_color": row["accent_color"],
                        "icon_name": row["icon_name"],
                        "is_system_default": bool(row["is_system_default"]),
                        "order_index": int(row["order_index"]),
                        "roles_count": int(row["roles_count"]),
                        "created_at": str(row["created_at"]),
                        "updated_at": str(row["updated_at"]),
                    }
                    for row in rows
                ]

    async def get_division_by_id(
        self, division_id: str, custom_path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Mengambil data satu divisi berdasarkan ID."""
        query = """
            SELECT id, branch_id, name, slug, description, accent_color, icon_name, 
                   is_system_default, COALESCE(order_index, 0) as order_index, created_at, updated_at
            FROM corporate_divisions
            WHERE id = ?;
        """
        async with get_db_connection(custom_path) as conn:
            async with conn.execute(query, (division_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                return {
                    "id": row["id"],
                    "branch_id": row["branch_id"],
                    "name": row["name"],
                    "slug": row["slug"],
                    "description": row["description"],
                    "accent_color": row["accent_color"],
                    "icon_name": row["icon_name"],
                    "is_system_default": bool(row["is_system_default"]),
                    "order_index": int(row["order_index"]),
                    "created_at": str(row["created_at"]),
                    "updated_at": str(row["updated_at"]),
                }

    async def create_division(
        self,
        branch_id: str,
        name: str,
        slug: str,
        description: Optional[str] = None,
        accent_color: str = "#cbd5e1",
        icon_name: str = "FolderTree",
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mendaftarkan divisi baru pada branch tertentu."""
        div_id = f"div_{uuid.uuid4().hex[:8]}"
        async with get_db_connection(custom_path) as conn:
            async with conn.execute(
                "SELECT id FROM corporate_divisions WHERE branch_id = ? AND slug = ?;", (branch_id, slug)
            ) as cur:
                if await cur.fetchone():
                    raise ValueError(f"Divisi dengan slug '{slug}' sudah ada pada branch ini.")

            await conn.execute(
                """
                INSERT INTO corporate_divisions 
                (id, branch_id, name, slug, description, accent_color, icon_name, is_system_default)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0);
                """,
                (div_id, branch_id, name, slug, description, accent_color, icon_name),
            )
            await conn.commit()
            logger.info(f"Divisi baru '{name}' ({div_id}) berhasil dibuat pada branch '{branch_id}'.")

        res = await self.get_division_by_id(div_id, custom_path)
        if not res:
            raise RuntimeError(f"Gagal mengambil divisi '{div_id}' yang baru dibuat.")
        return res

    async def update_division(
        self,
        division_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        accent_color: Optional[str] = None,
        icon_name: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Memperbarui metadata divisi."""
        existing = await self.get_division_by_id(division_id, custom_path)
        if not existing:
            return None

        new_name = name if name is not None else existing["name"]
        new_desc = description if description is not None else existing["description"]
        new_color = accent_color if accent_color is not None else existing["accent_color"]
        new_icon = icon_name if icon_name is not None else existing["icon_name"]

        async with get_db_connection(custom_path) as conn:
            await conn.execute(
                """
                UPDATE corporate_divisions 
                SET name = ?, description = ?, accent_color = ?, icon_name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (new_name, new_desc, new_color, new_icon, division_id),
            )
            await conn.commit()

        return await self.get_division_by_id(division_id, custom_path)

    async def delete_division(self, division_id: str, custom_path: Optional[str] = None) -> bool:
        """Menghapus divisi kustom. Melindungi divisi bawaan sistem pada branch main."""
        existing = await self.get_division_by_id(division_id, custom_path)
        if not existing:
            raise ValueError(f"Divisi '{division_id}' tidak ditemukan.")

        if existing["is_system_default"] and existing["branch_id"] == "branch_main":
            raise ValueError("Divisi bawaan sistem pada branch main tidak dapat dihapus.")

        async with get_db_connection(custom_path) as conn:
            await conn.execute("DELETE FROM corporate_divisions WHERE id = ?;", (division_id,))
            await conn.commit()
            logger.info(f"Divisi '{division_id}' berhasil dihapus.")
            return True


division_repo = DivisionRepository()
