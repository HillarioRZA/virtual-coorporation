"""
Autonomous Three-Way Branch Merge Engine.
Menghitung Lowest Common Ancestor (LCA), perbandingan 3-way, dan penggabungan atomik alur kerja korporat.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import json
import uuid
import aiosqlite

from app.core.logger import logger
from app.db.session import get_db_connection


class ThreeWayBranchMergeEngine:
    """Mesin penggabungan cabang alur kerja Git-Style dengan deteksi konflik dan resolusi cerdas."""

    async def find_lca(self, source_id: str, target_id: str, custom_path: Optional[str] = None) -> str:
        """Menemukan Lowest Common Ancestor (LCA) antara dua cabang alur kerja."""
        if source_id == target_id:
            return source_id

        async with get_db_connection(custom_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute("SELECT id, parent_branch_id FROM corporate_branches;") as cur:
                rows = await cur.fetchall()
                parents = {r["id"]: r["parent_branch_id"] or "branch_main" for r in rows if "parent_branch_id" in r.keys()}

        if parents.get(source_id) == target_id:
            return target_id
        if parents.get(target_id) == source_id:
            return source_id

        ancestors_source: Set[str] = {source_id}
        curr = source_id
        for _ in range(10):
            p = parents.get(curr)
            if not p or p == curr:
                break
            ancestors_source.add(p)
            curr = p

        curr = target_id
        for _ in range(10):
            if curr in ancestors_source:
                return curr
            p = parents.get(curr)
            if not p or p == curr:
                break
            curr = p

        return "branch_main"

    async def preview_merge(
        self,
        source_id: str,
        target_id: str = "branch_main",
        strategy: str = "auto",
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Melakukan simulasi (dry-run) perbandingan 3-way sebelum dieksekusi."""
        lca_id = await self.find_lca(source_id, target_id, custom_path)

        async with get_db_connection(custom_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute("SELECT * FROM corporate_roles WHERE branch_id IN (?, ?, ?);", (source_id, target_id, lca_id)) as cur:
                all_roles = [dict(r) for r in await cur.fetchall()]
            async with conn.execute("SELECT * FROM corporate_pipeline_stages WHERE branch_id IN (?, ?, ?);", (source_id, target_id, lca_id)) as cur:
                all_stages = [dict(r) for r in await cur.fetchall()]
            async with conn.execute("SELECT roles_snapshot FROM corporate_branches WHERE id = ?;", (source_id,)) as cur:
                sb_row = await cur.fetchone()
                snapshot_str = sb_row["roles_snapshot"] if sb_row and "roles_snapshot" in sb_row.keys() else "{}"

        theirs_roles = {r["name"]: r for r in all_roles if r["branch_id"] == source_id}
        ours_roles = {r["name"]: r for r in all_roles if r["branch_id"] == target_id}
        
        base_roles = {}
        if lca_id == target_id and snapshot_str and snapshot_str != "{}":
            try:
                base_roles = json.loads(snapshot_str)
            except Exception:
                base_roles = {r["name"]: r for r in all_roles if r["branch_id"] == lca_id}
        else:
            base_roles = {r["name"]: r for r in all_roles if r["branch_id"] == lca_id}

        added_roles, updated_roles, conflicts = [], [], []

        for name, t_role in theirs_roles.items():
            if name not in ours_roles:
                added_roles.append({"name": name, "model_name": t_role["model_name"]})
            else:
                o_role = ours_roles[name]
                b_role = base_roles.get(name, {})
                t_changed = t_role.get("temperature") != b_role.get("temperature") or t_role.get("model_name") != b_role.get("model_name")
                o_changed = o_role.get("temperature") != b_role.get("temperature") or o_role.get("model_name") != b_role.get("model_name")

                if t_changed and not o_changed:
                    updated_roles.append({"name": name, "field": "model/temp", "from": o_role["model_name"], "to": t_role["model_name"]})
                elif t_changed and o_changed and (t_role["model_name"] != o_role["model_name"] or t_role.get("temperature") != o_role.get("temperature")):
                    conflicts.append({
                        "entity": "role", "name": name,
                        "ours": {"model": o_role["model_name"], "temp": o_role["temperature"]},
                        "theirs": {"model": t_role["model_name"], "temp": t_role["temperature"]},
                    })

        theirs_stage_roles = [s["role_id"] for s in all_stages if s["branch_id"] == source_id and s["role_id"]]
        ours_stage_roles = [s["role_id"] for s in all_stages if s["branch_id"] == target_id and s["role_id"]]
        new_stages_count = max(0, len(theirs_stage_roles) - len(ours_stage_roles))

        return {
            "source_branch_id": source_id,
            "target_branch_id": target_id,
            "lca_branch_id": lca_id,
            "can_fast_forward": (lca_id == target_id and len(conflicts) == 0),
            "added_roles": added_roles,
            "updated_roles": updated_roles,
            "new_stages_count": new_stages_count,
            "conflicts": conflicts,
            "has_conflicts": len(conflicts) > 0,
            "strategy": strategy,
        }

    async def execute_merge(
        self,
        source_id: str,
        target_id: str = "branch_main",
        strategy: str = "auto",
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mengeksekusi penggabungan cabang secara atomik dalam transaksi SQLite WAL."""
        preview = await self.preview_merge(source_id, target_id, strategy, custom_path)
        if preview["has_conflicts"] and strategy == "auto":
            raise ValueError(f"Terdapat {len(preview['conflicts'])} konflik konfigurasi. Tentukan strategi 'prefer_theirs' atau 'prefer_ours'.")

        updated_names = {u["name"] for u in preview["updated_roles"]}

        async with get_db_connection(custom_path) as conn:
            conn.row_factory = aiosqlite.Row
            try:
                async with conn.execute("SELECT * FROM corporate_roles WHERE branch_id = ?;", (source_id,)) as cur:
                    theirs_roles = [dict(r) for r in await cur.fetchall()]

                async with conn.execute("SELECT name FROM corporate_roles WHERE branch_id = ?;", (target_id,)) as cur:
                    ours_names = {r["name"] for r in await cur.fetchall()}

                async with conn.execute("SELECT id FROM corporate_divisions WHERE branch_id = ? ORDER BY order_index ASC LIMIT 1;", (target_id,)) as cur:
                    def_div = await cur.fetchone()
                    target_div_id = def_div["id"] if def_div else "div_eng"

                for r in theirs_roles:
                    jd = r["job_description"] if "job_description" in r.keys() else ""
                    tl = r["thinking_level"] if "thinking_level" in r.keys() else "medium"
                    if r["name"] not in ours_names:
                        new_r_id = f"role_{uuid.uuid4().hex[:8]}"
                        await conn.execute(
                            "INSERT INTO corporate_roles (id, branch_id, division_id, name, job_description, system_prompt_template, model_provider, model_name, temperature, tool_permissions, token_budget_per_task, is_active, is_system_default, order_index, thinking_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?);",
                            (new_r_id, target_id, target_div_id, r["name"], jd, r["system_prompt_template"], r["model_provider"], r["model_name"], r["temperature"], r["tool_permissions"], r["token_budget_per_task"], r["is_active"], r["order_index"] if "order_index" in r.keys() else 0, tl),
                        )
                    elif strategy == "prefer_theirs" or (strategy != "prefer_ours" and r["name"] in updated_names):
                        await conn.execute(
                            "UPDATE corporate_roles SET model_name = ?, model_provider = ?, temperature = ?, system_prompt_template = ?, updated_at = CURRENT_TIMESTAMP WHERE branch_id = ? AND name = ?;",
                            (r["model_name"], r["model_provider"], r["temperature"], r["system_prompt_template"], target_id, r["name"]),
                        )

                await conn.commit()
                logger.info(f"Berhasil merge alur kerja dari '{source_id}' ke '{target_id}' (Strategi: {strategy}).")
                return {
                    "status": "MERGED",
                    "source_branch_id": source_id,
                    "target_branch_id": target_id,
                    "added_roles_count": len(preview["added_roles"]),
                    "updated_roles_count": len(preview["updated_roles"]),
                    "strategy": strategy,
                }
            except Exception as err:
                await conn.rollback()
                logger.error(f"Gagal mengeksekusi merge '{source_id}' -> '{target_id}': {err}")
                raise


branch_merge_engine = ThreeWayBranchMergeEngine()
