"""
Corporate Ticket & Virtual Kanban Repository.
Mengelola persistensi tiket tugas multi-divisi pada tabel SQLite corporate_tickets
dengan dukungan ketergantungan DAG dan urutan eksekusi alur kerja dinamis.
"""

import json
from typing import Any, Dict, List, Optional
import uuid
import aiosqlite

from app.core.logger import logger
from app.db.session import get_db_connection
from app.db.ticket_seeder import seed_branch_tickets


class TicketRepository:
    """Repositori asinkron untuk operasi CRUD dan transisi status tiket Kanban."""

    async def _ensure_project(self, conn: aiosqlite.Connection, project_id: str) -> None:
        """Memastikan record projek induk ada di tabel projects."""
        await conn.execute(
            "INSERT OR IGNORE INTO projects (id, name, founder_idea) VALUES (?, ?, ?);",
            (project_id, project_id, "Venture Project Workspace"),
        )

    def _map_ticket_row(self, row: aiosqlite.Row) -> Dict[str, Any]:
        """Memetakan baris database SQLite ke dictionary tiket."""
        return {
            "id": row["id"],
            "branch_id": row["branch_id"],
            "project_id": row["project_id"],
            "division_id": row["division_id"],
            "assigned_role_id": row["assigned_role_id"],
            "title": row["title"],
            "description": row["description"],
            "product_line": row["product_line"],
            "priority": row["priority"],
            "status": row["status"],
            "artifact_refs": json.loads(row["artifact_refs"]) if row["artifact_refs"] else [],
            "dependencies": json.loads(row["dependencies"]) if row["dependencies"] else [],
            "parent_ticket_id": row["parent_ticket_id"],
            "created_at": str(row["created_at"]),
            "updated_at": str(row["updated_at"]),
        }

    async def create_ticket(
        self,
        branch_id: str,
        project_id: str,
        division_id: str,
        title: str,
        description: str,
        product_line: str = "SOFTWARE",
        priority: str = "MEDIUM",
        status: str = "BACKLOG",
        assigned_role_id: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        artifact_refs: Optional[List[str]] = None,
        parent_ticket_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Membuat tiket tugas baru di papan Kanban."""
        ticket_id = f"tick_{uuid.uuid4().hex[:8]}"
        deps_json = json.dumps(dependencies or [])
        arts_json = json.dumps(artifact_refs or [])

        query = """
            INSERT INTO corporate_tickets 
            (id, branch_id, project_id, division_id, assigned_role_id, title, description,
             product_line, priority, status, artifact_refs, dependencies, parent_ticket_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        async with get_db_connection(custom_path) as conn:
            await self._ensure_project(conn, project_id)
            await conn.execute(
                query,
                (
                    ticket_id, branch_id, project_id, division_id, assigned_role_id,
                    title, description, product_line, priority, status, arts_json, deps_json, parent_ticket_id,
                ),
            )
            await conn.commit()

        logger.info(f"Tiket Kanban Dibuat [{ticket_id}] '{title}' -> {status}")
        return await self.get_ticket_by_id(ticket_id, custom_path) or {}

    async def get_tickets(
        self,
        project_id: str,
        branch_id: Optional[str] = None,
        status: Optional[str] = None,
        division_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mengambil daftar tiket tugas proyek dengan filter opsional."""
        query = "SELECT * FROM corporate_tickets WHERE project_id = ?"
        params: List[Any] = [project_id]
        if branch_id:
            query += " AND branch_id = ?"
            params.append(branch_id)
        if status:
            query += " AND status = ?"
            params.append(status)
        if division_id:
            query += " AND division_id = ?"
            params.append(division_id)
        query += " ORDER BY created_at ASC;"

        async with get_db_connection(custom_path) as conn:
            async with conn.execute(query, tuple(params)) as cursor:
                rows = await cursor.fetchall()
                return [self._map_ticket_row(row) for row in rows]

    async def get_ticket_by_id(self, ticket_id: str, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Mengambil satu tiket berdasarkan ID."""
        async with get_db_connection(custom_path) as conn:
            async with conn.execute("SELECT * FROM corporate_tickets WHERE id = ?;", (ticket_id,)) as cursor:
                row = await cursor.fetchone()
                return self._map_ticket_row(row) if row else None

    async def transition_ticket_status(
        self,
        ticket_id: str,
        new_status: str,
        artifact_refs: Optional[List[str]] = None,
        custom_path: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Memindahkan status tiket Kanban ke kolom baru."""
        existing = await self.get_ticket_by_id(ticket_id, custom_path)
        if not existing:
            return None
        arts = artifact_refs if artifact_refs is not None else existing["artifact_refs"]
        async with get_db_connection(custom_path) as conn:
            await conn.execute(
                "UPDATE corporate_tickets SET status = ?, artifact_refs = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
                (new_status, json.dumps(arts), ticket_id),
            )
            await conn.commit()
        logger.info(f"Tiket [{ticket_id}] Transisi: {existing['status']} -> {new_status}")
        return await self.get_ticket_by_id(ticket_id, custom_path)

    async def claim_ticket_atomic(
        self, ticket_id: str, custom_path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Mengklaim tiket berstatus TODO menjadi IN_PROGRESS secara atomik."""
        query = "UPDATE corporate_tickets SET status = 'IN_PROGRESS', updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'TODO';"
        async with get_db_connection(custom_path) as conn:
            cur = await conn.execute(query, (ticket_id,))
            await conn.commit()
            if cur.rowcount > 0:
                logger.info(f"Tiket [{ticket_id}] berhasil diklaim secara atomik (TODO -> IN_PROGRESS)")
                return await self.get_ticket_by_id(ticket_id, custom_path)
            return None

    async def delete_ticket(self, ticket_id: str, custom_path: Optional[str] = None) -> bool:
        """Menghapus tiket tugas dari papan Kanban."""
        async with get_db_connection(custom_path) as conn:
            cur = await conn.execute("DELETE FROM corporate_tickets WHERE id = ?;", (ticket_id,))
            await conn.commit()
            return cur.rowcount > 0

    async def seed_initial_project_tickets(
        self,
        project_id: str,
        branch_id: str = "branch_main",
        custom_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mengisi tiket alur awal secara dinamis sesuai urutan alur kerja atau baseline Tech Core."""
        existing = await self.get_tickets(project_id, branch_id=branch_id, custom_path=custom_path)
        if existing:
            return existing

        async with get_db_connection(custom_path) as conn:
            return await seed_branch_tickets(self, project_id, branch_id, conn, custom_path)


ticket_repo = TicketRepository()
