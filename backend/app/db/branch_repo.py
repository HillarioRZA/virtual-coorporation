"""Branch Repository Layer.

Mengelola siklus hidup Git-Style Branching untuk alur kerja korporat pada basis data SQLite WAL.
"""

from typing import Any, Dict, List, Optional
import json
import uuid

import aiosqlite
from app.core.logger import logger
from app.db.session import get_db_connection


class BranchRepository:
    """Repositori asinkron untuk operasi Git-Style branching alur kerja."""

    def _map_branch(self, row: aiosqlite.Row) -> Dict[str, Any]:
        """Memetakan baris basis data ke dictionary entitas branch."""
        return {
            "id": row["id"],
            "name": row["name"],
            "slug": row["slug"],
            "description": row["description"],
            "is_active_main": bool(row["is_active_main"]),
            "parent_branch_id": row["parent_branch_id"] if "parent_branch_id" in row.keys() else "branch_main",
            "roles_snapshot": row["roles_snapshot"] if "roles_snapshot" in row.keys() else "{}",
            "created_at": str(row["created_at"]),
            "updated_at": str(row["updated_at"]),
        }

    async def get_branches(self, custom_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mengambil seluruh daftar branch alur kerja organisasi."""
        query = "SELECT * FROM corporate_branches ORDER BY is_active_main DESC, created_at ASC;"
        async with get_db_connection(custom_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(query) as cursor:
                return [self._map_branch(r) for r in await cursor.fetchall()]

    async def get_active_branch(self, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Mengambil branch alur kerja yang saat ini aktif untuk produksi."""
        query = "SELECT * FROM corporate_branches WHERE is_active_main = 1 LIMIT 1;"
        async with get_db_connection(custom_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(query) as cursor:
                row = await cursor.fetchone()
                return self._map_branch(row) if row else None

    async def get_branch_by_id(self, branch_id: str, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Mengambil metadata branch berdasarkan ID."""
        query = "SELECT * FROM corporate_branches WHERE id = ?;"
        async with get_db_connection(custom_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(query, (branch_id,)) as cursor:
                row = await cursor.fetchone()
                return self._map_branch(row) if row else None

    async def fork_branch(
        self,
        name: str,
        slug: str,
        description: Optional[str] = None,
        source_branch_id: str = "branch_main",
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Kloning / Forking seluruh struktur divisi, role, pipeline, dan stages ke branch baru."""
        new_branch_id = f"branch_{uuid.uuid4().hex[:8]}"

        async with get_db_connection(custom_path) as conn:
            try:
                # 1. Validasi source branch & slug
                async with conn.execute("SELECT id FROM corporate_branches WHERE id = ?;", (source_branch_id,)) as cur:
                    if not await cur.fetchone():
                        raise ValueError(f"Source branch '{source_branch_id}' tidak ditemukan.")

                async with conn.execute("SELECT id FROM corporate_branches WHERE slug = ?;", (slug,)) as cur:
                    if await cur.fetchone():
                        raise ValueError(f"Slug branch '{slug}' sudah digunakan.")

                # 2. Ambil snapshot peran sumber untuk LCA merge
                async with conn.execute("SELECT * FROM corporate_roles WHERE branch_id = ?;", (source_branch_id,)) as cur:
                    source_roles = await cur.fetchall()
                snap = json.dumps({r["name"]: {"model_name": r["model_name"], "temperature": r["temperature"]} for r in source_roles})

                await conn.execute(
                    "INSERT INTO corporate_branches (id, name, slug, description, is_active_main, parent_branch_id, roles_snapshot) VALUES (?, ?, ?, ?, 0, ?, ?);",
                    (new_branch_id, name, slug, description, source_branch_id, snap),
                )

                # 3. Kloning divisi
                async with conn.execute("SELECT * FROM corporate_divisions WHERE branch_id = ?;", (source_branch_id,)) as cur:
                    source_divisions = await cur.fetchall()

                div_map: Dict[str, str] = {}
                for div in source_divisions:
                    new_div_id = f"div_{uuid.uuid4().hex[:8]}"
                    div_map[div["id"]] = new_div_id
                    await conn.execute(
                        "INSERT INTO corporate_divisions (id, branch_id, name, slug, description, accent_color, icon_name, is_system_default, order_index) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?);",
                        (new_div_id, new_branch_id, div["name"], div["slug"], div["description"], div["accent_color"], div["icon_name"], div["order_index"] if "order_index" in div.keys() else 0),
                    )

                # 4. Kloning role
                role_map: Dict[str, str] = {}
                for r in source_roles:
                    new_role_id = f"role_{uuid.uuid4().hex[:8]}"
                    role_map[r["id"]] = new_role_id
                    target_div_id = div_map.get(r["division_id"])
                    if target_div_id:
                        jd = r["job_description"] if "job_description" in r.keys() else ""
                        tl = r["thinking_level"] if "thinking_level" in r.keys() else "medium"
                        await conn.execute(
                            "INSERT INTO corporate_roles (id, branch_id, division_id, name, job_description, system_prompt_template, model_provider, model_name, temperature, tool_permissions, token_budget_per_task, is_active, is_system_default, order_index, thinking_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?);",
                            (new_role_id, new_branch_id, target_div_id, r["name"], jd, r["system_prompt_template"], r["model_provider"], r["model_name"], r["temperature"], r["tool_permissions"], r["token_budget_per_task"], r["is_active"], r["order_index"] if "order_index" in r.keys() else 0, tl),
                        )

                # 5. Kloning pipeline
                async with conn.execute("SELECT * FROM corporate_pipelines WHERE branch_id = ?;", (source_branch_id,)) as cur:
                    source_pipelines = await cur.fetchall()

                pipe_map: Dict[str, str] = {}
                for pipe in source_pipelines:
                    new_pipe_id = f"pipe_{pipe['slug']}_{uuid.uuid4().hex[:6]}"
                    pipe_map[pipe["id"]] = new_pipe_id
                    await conn.execute(
                        "INSERT INTO corporate_pipelines (id, branch_id, name, slug, product_line, description, is_default) VALUES (?, ?, ?, ?, ?, ?, ?);",
                        (new_pipe_id, new_branch_id, pipe["name"], pipe["slug"], pipe["product_line"], pipe["description"], pipe["is_default"]),
                    )

                # 6. Kloning stages
                async with conn.execute("SELECT * FROM corporate_pipeline_stages WHERE branch_id = ?;", (source_branch_id,)) as cur:
                    source_stages = await cur.fetchall()

                for stg in source_stages:
                    new_stg_id = f"stg_{uuid.uuid4().hex[:8]}"
                    t_pipe_id = pipe_map.get(stg["pipeline_id"], "pipe_software_main")
                    new_r_id = role_map.get(stg["role_id"]) if stg["role_id"] else None
                    await conn.execute(
                        """
                        INSERT INTO corporate_pipeline_stages
                        (id, branch_id, pipeline_id, stage_index, stage_type, role_id, ceo_gate_type, custom_label, custom_instructions)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (new_stg_id, new_branch_id, t_pipe_id, stg["stage_index"], stg["stage_type"],
                         new_r_id, stg["ceo_gate_type"], stg["custom_label"], stg["custom_instructions"]),
                    )

                await conn.commit()
                logger.info(f"Berhasil forking branch baru '{new_branch_id}' ({name}) dari '{source_branch_id}'.")
            except Exception as err:
                await conn.rollback()
                logger.error(f"Gagal forking branch '{slug}': {err}")
                raise

        res = await self.get_branch_by_id(new_branch_id, custom_path)
        if not res:
            raise RuntimeError(f"Gagal mengambil branch '{new_branch_id}' yang baru di-fork.")
        return res

    async def activate_branch(self, branch_id: str, custom_path: Optional[str] = None) -> Dict[str, Any]:
        """Menjadikan branch ini sebagai active production main workflow."""
        async with get_db_connection(custom_path) as conn:
            async with conn.execute("SELECT id FROM corporate_branches WHERE id = ?;", (branch_id,)) as cur:
                if not await cur.fetchone():
                    raise ValueError(f"Branch '{branch_id}' tidak ditemukan.")

            await conn.execute("UPDATE corporate_branches SET is_active_main = 0;")
            await conn.execute(
                "UPDATE corporate_branches SET is_active_main = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
                (branch_id,),
            )
            await conn.commit()
            logger.info(f"Branch '{branch_id}' berhasil dipromosikan menjadi ACTIVE MAIN.")

        res = await self.get_branch_by_id(branch_id, custom_path)
        if not res:
            raise RuntimeError(f"Gagal mengambil branch '{branch_id}'.")
        return res

    async def delete_branch(self, branch_id: str, custom_path: Optional[str] = None) -> bool:
        """Menghapus branch draft. Melindungi branch default 'branch_main' atau branch yang sedang aktif."""
        async with get_db_connection(custom_path) as conn:
            async with conn.execute("SELECT is_active_main FROM corporate_branches WHERE id = ?;", (branch_id,)) as cur:
                row = await cur.fetchone()
                if not row:
                    raise ValueError(f"Branch '{branch_id}' tidak ditemukan.")
                if branch_id == "branch_main" or bool(row["is_active_main"]):
                    raise ValueError("Branch 'branch_main' atau branch yang sedang aktif tidak dapat dihapus.")

            await conn.execute("DELETE FROM corporate_branches WHERE id = ?;", (branch_id,))
            await conn.commit()
            logger.info(f"Branch '{branch_id}' berhasil dihapus.")
            return True


branch_repo = BranchRepository()
