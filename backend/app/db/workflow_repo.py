"""
Workflow Pipeline & Sequential Stage Reordering Repository.
Mengelola urutan tahapan eksekusi alur kerja peran dan gerbang CEO
pada branch organisasi dan multi-pipeline produk (Software, Edukasi, Copywriting).
"""

from typing import Any, Dict, List, Optional
import uuid
import aiosqlite

from app.core.logger import logger
from app.db.session import get_db_connection


class WorkflowRepository:
    """Repositori asinkron untuk querying dan reordering rantai alur kerja korporat."""

    def _map_stage(self, r: aiosqlite.Row) -> Dict[str, Any]:
        """Format baris database stage ke dictionary respons API."""
        is_ceo = r["stage_type"] == "CEO_GATE"
        return {
            "id": r["stage_id"], "pipeline_id": r["pipeline_id"] if "pipeline_id" in r.keys() else "pipe_software_main",
            "stage_index": int(r["stage_index"]), "order_index": int(r["stage_index"]),
            "stage_type": r["stage_type"], "role_id": r["role_id"],
            "role_name": r["role_name"] or ("CEO Human Gate" if is_ceo else "Unknown Role"),
            "role_slug": None,
            "division_id": r["division_id"] or "div_exec",
            "division_name": r["division_name"] or ("Executive Suite" if is_ceo else "General"),
            "division_color": r["division_color"] or "#eab308",
            "model_name": r["model_name"] or ("Human-in-the-Loop" if is_ceo else "default"),
            "ceo_gate_type": r["ceo_gate_type"], "custom_label": r["custom_label"],
            "custom_instructions": r["custom_instructions"],
            "is_active": bool(r["is_active"]), "is_system_default": bool(r["is_system_default"]),
        }

    async def _resolve_pipeline_id(
        self, conn: aiosqlite.Connection, branch_id: str, pipeline_id: Optional[str] = None
    ) -> str:
        """Menemukan ID pipeline default atau terdaftar untuk branch jika tidak dispesifikasikan."""
        if pipeline_id:
            return pipeline_id
        async with conn.execute(
            "SELECT id FROM corporate_pipelines WHERE branch_id = ? AND is_default = 1 LIMIT 1;",
            (branch_id,),
        ) as cur:
            row = await cur.fetchone()
            if row and row["id"]:
                return str(row["id"])
        return "pipe_software_main"

    async def get_workflow_pipeline(
        self,
        branch_id: str,
        pipeline_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mengambil urutan sekuensial tahapan peran pada pipeline dan branch tertentu."""
        try:
            async with get_db_connection(custom_path) as conn:
                target_pipe = await self._resolve_pipeline_id(conn, branch_id, pipeline_id)
                query = """
                    SELECT s.id AS stage_id, s.pipeline_id, s.stage_index, s.stage_type, s.role_id,
                           s.ceo_gate_type, s.custom_label, s.custom_instructions,
                           r.name AS role_name, r.model_name,
                           COALESCE(r.is_active, 1) AS is_active,
                           COALESCE(r.is_system_default, 0) AS is_system_default,
                           d.id AS division_id, d.name AS division_name, d.accent_color AS division_color
                    FROM corporate_pipeline_stages s
                    LEFT JOIN corporate_roles r ON s.role_id = r.id
                    LEFT JOIN corporate_divisions d ON r.division_id = d.id
                    WHERE s.branch_id = ? AND s.pipeline_id = ?
                    ORDER BY s.stage_index ASC;
                """
                async with conn.execute(query, (branch_id, target_pipe)) as cur:
                    rows = await cur.fetchall()
                    if rows:
                        return [self._map_stage(row) for row in rows]

                # Fallback jika tahap belum terisi di pipeline_stages
                q_roles = """
                    SELECT r.id AS role_id, r.name AS role_name,
                           r.division_id, d.name AS division_name, d.accent_color AS division_color,
                           COALESCE(r.order_index, 0) AS order_index, r.model_name,
                           r.is_active, r.is_system_default
                    FROM corporate_roles r
                    JOIN corporate_divisions d ON r.division_id = d.id
                    WHERE r.branch_id = ?
                    ORDER BY COALESCE(r.order_index, 0) ASC, r.created_at ASC;
                """
                async with conn.execute(q_roles, (branch_id,)) as cur:
                    fb = await cur.fetchall()
                    return [
                        {
                            "id": f"stg_{r['role_id']}", "pipeline_id": target_pipe,
                            "stage_index": int(r["order_index"]), "order_index": int(r["order_index"]),
                            "stage_type": "ROLE_EXECUTION", "role_id": r["role_id"],
                            "role_name": r["role_name"], "role_slug": None,
                            "division_id": r["division_id"], "division_name": r["division_name"],
                            "division_color": r["division_color"], "model_name": r["model_name"],
                            "ceo_gate_type": None, "custom_label": None, "custom_instructions": None,
                            "is_active": bool(r["is_active"]), "is_system_default": bool(r["is_system_default"]),
                        }
                        for r in fb
                    ]
        except aiosqlite.Error as err:
            logger.error(f"Gagal mengambil pipeline untuk branch '{branch_id}': {err}")
            raise

    async def save_workflow_pipeline_stages(
        self,
        branch_id: str,
        stages: List[Dict[str, Any]],
        pipeline_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Menyimpan seluruh rantai tahapan alur kerja untuk pipeline target."""
        try:
            async with get_db_connection(custom_path) as conn:
                target_pipe = await self._resolve_pipeline_id(
                    conn,
                    branch_id,
                    pipeline_id or (stages[0].get("pipeline_id") if stages else None),
                )
                await conn.execute(
                    "DELETE FROM corporate_pipeline_stages WHERE branch_id = ? AND pipeline_id = ?;",
                    (branch_id, target_pipe),
                )
                stmt = """
                    INSERT INTO corporate_pipeline_stages
                    (id, branch_id, pipeline_id, stage_index, stage_type, role_id, ceo_gate_type, custom_label, custom_instructions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """
                records = [
                    (
                        f"stg_{uuid.uuid4().hex[:8]}", branch_id, target_pipe, idx,
                        stg.get("stage_type", "ROLE_EXECUTION"), stg.get("role_id"),
                        stg.get("ceo_gate_type"), stg.get("custom_label"), stg.get("custom_instructions"),
                    )
                    for idx, stg in enumerate(stages)
                ]
                await conn.executemany(stmt, records)
                await conn.commit()
            return await self.get_workflow_pipeline(branch_id, pipeline_id=target_pipe, custom_path=custom_path)
        except aiosqlite.Error as err:
            logger.error(f"Gagal menyimpan pipeline pada branch '{branch_id}': {err}")
            raise

    async def reorder_workflow_pipeline(
        self,
        branch_id: str,
        ordered_role_ids: List[str],
        pipeline_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Memperbarui nomor urut eksekusi alur kerja untuk daftar peran yang diberikan."""
        try:
            async with get_db_connection(custom_path) as conn:
                target_pipe = await self._resolve_pipeline_id(conn, branch_id, pipeline_id)
                for idx, r_id in enumerate(ordered_role_ids):
                    await conn.execute(
                        "UPDATE corporate_roles SET order_index = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND branch_id = ?;",
                        (idx, r_id, branch_id),
                    )
                await conn.execute(
                    "DELETE FROM corporate_pipeline_stages WHERE branch_id = ? AND pipeline_id = ?;",
                    (branch_id, target_pipe),
                )
                records = [
                    (f"stg_{uuid.uuid4().hex[:8]}", branch_id, target_pipe, idx, "ROLE_EXECUTION", r_id, None, None, None)
                    for idx, r_id in enumerate(ordered_role_ids)
                ]
                await conn.executemany(
                    "INSERT INTO corporate_pipeline_stages (id, branch_id, pipeline_id, stage_index, stage_type, role_id, ceo_gate_type, custom_label, custom_instructions) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
                    records,
                )
                await conn.commit()
            return await self.get_workflow_pipeline(branch_id, pipeline_id=target_pipe, custom_path=custom_path)
        except aiosqlite.Error as err:
            logger.error(f"Gagal reorder workflow pada branch '{branch_id}': {err}")
            raise

    async def reorder_divisions(
        self, branch_id: str, ordered_division_ids: List[str], custom_path: Optional[str] = None
    ) -> bool:
        """Memperbarui urutan sekuensial divisi dalam branch."""
        try:
            async with get_db_connection(custom_path) as conn:
                for idx, div_id in enumerate(ordered_division_ids):
                    await conn.execute(
                        "UPDATE corporate_divisions SET order_index = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND branch_id = ?;",
                        (idx, div_id, branch_id),
                    )
                await conn.commit()
            return True
        except aiosqlite.Error as err:
            logger.error(f"Gagal reorder divisi pada branch '{branch_id}': {err}")
            raise


workflow_repo = WorkflowRepository()
