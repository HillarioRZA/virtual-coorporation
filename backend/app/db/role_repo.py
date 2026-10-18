"""Role Repository Layer.

Mengelola siklus hidup peran karyawan AI, parameter LLM, dan izin tools pada SQLite.
"""

import json
from typing import Any, Dict, List, Optional
import uuid

import aiosqlite
from app.core.logger import logger
from app.db.session import get_db_connection
from app.db.branch_repo import branch_repo


ROLE_COLS = (
    "id, branch_id, division_id, name, slug, system_prompt_template, model_provider, "
    "model_name, temperature, tool_permissions, token_budget_per_task, is_active, "
    "is_system_default, COALESCE(order_index, 0) as order_index, "
    "COALESCE(fallback_chain, '[]') as fallback_chain, "
    "COALESCE(thinking_level, 'medium') as thinking_level, created_at, updated_at"
)


class RoleRepository:
    """Repositori asinkron untuk operasi entitas peran karyawan AI."""

    def _map_role(self, row: aiosqlite.Row) -> Dict[str, Any]:
        """Memetakan baris basis data ke dictionary entitas peran."""
        try:
            perms = json.loads(row["tool_permissions"])
        except Exception:
            perms = ["read_file", "write_file"]
        try:
            raw_chain = row["fallback_chain"] if "fallback_chain" in row.keys() else "[]"
            fallback = json.loads(raw_chain) if raw_chain else []
        except Exception:
            fallback = []
        return {
            "id": row["id"],
            "branch_id": row["branch_id"],
            "division_id": row["division_id"],
            "name": row["name"],
            "slug": row["slug"],
            "system_prompt_template": row["system_prompt_template"],
            "model_provider": row["model_provider"],
            "model_name": row["model_name"],
            "temperature": float(row["temperature"]),
            "tool_permissions": perms,
            "token_budget_per_task": int(row["token_budget_per_task"]),
            "is_active": bool(row["is_active"]),
            "is_system_default": bool(row["is_system_default"]),
            "order_index": int(row["order_index"]),
            "fallback_chain": fallback,
            "thinking_level": str(row["thinking_level"]) if "thinking_level" in row.keys() else "medium",
            "created_at": str(row["created_at"]),
            "updated_at": str(row["updated_at"]),
        }

    async def get_roles(
        self, branch_id: Optional[str] = None, division_id: Optional[str] = None,
        active_only: bool = False, custom_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Mengambil seluruh role karyawan AI pada branch tertentu."""
        target_branch = branch_id
        if not target_branch:
            active_branch = await branch_repo.get_active_branch(custom_path)
            target_branch = active_branch["id"] if active_branch else "branch_main"

        conditions = ["branch_id = ?"]
        params: List[Any] = [target_branch]
        if division_id:
            conditions.append("division_id = ?")
            params.append(division_id)
        if active_only:
            conditions.append("is_active = 1")

        query = f"SELECT {ROLE_COLS} FROM corporate_roles WHERE {' AND '.join(conditions)} ORDER BY COALESCE(order_index, 0) ASC, is_system_default DESC, created_at ASC;"
        async with get_db_connection(custom_path) as conn:
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [self._map_role(r) for r in rows]

    async def get_role_by_id(self, role_id: str, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Mengambil data satu role berdasarkan ID."""
        query = f"SELECT {ROLE_COLS} FROM corporate_roles WHERE id = ?;"
        async with get_db_connection(custom_path) as conn:
            async with conn.execute(query, (role_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                return self._map_role(row)

    async def create_role(
        self, branch_id: str, division_id: str, name: str, slug: str, system_prompt_template: str,
        model_provider: str = "openrouter", model_name: str = "deepseek/deepseek-r1:free",
        temperature: float = 0.2, tool_permissions: Optional[List[str]] = None,
        token_budget_per_task: int = 8000, is_active: bool = True,
        thinking_level: str = "medium", custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mendaftarkan role baru pada branch dan divisi tertentu."""
        role_id = f"role_{uuid.uuid4().hex[:8]}"
        perms_json = json.dumps(tool_permissions or ["read_file", "write_file"])

        async with get_db_connection(custom_path) as conn:
            async with conn.execute(
                "SELECT id FROM corporate_divisions WHERE id = ? AND branch_id = ?;", (division_id, branch_id)
            ) as cur:
                if not await cur.fetchone():
                    raise ValueError(f"Divisi '{division_id}' tidak ditemukan pada branch '{branch_id}'.")

            async with conn.execute(
                "SELECT id FROM corporate_roles WHERE branch_id = ? AND slug = ?;", (branch_id, slug)
            ) as cur:
                if await cur.fetchone():
                    raise ValueError(f"Role dengan slug '{slug}' sudah ada pada branch ini.")

            ins_sql = (
                "INSERT INTO corporate_roles (id, branch_id, division_id, name, slug, system_prompt_template, "
                "model_provider, model_name, temperature, tool_permissions, token_budget_per_task, is_active, "
                "is_system_default, thinking_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?);"
            )
            await conn.execute(
                ins_sql,
                (role_id, branch_id, division_id, name, slug, system_prompt_template,
                 model_provider, model_name, temperature, perms_json, token_budget_per_task,
                 1 if is_active else 0, thinking_level),
            )
            await conn.commit()
            logger.info(f"Role baru '{name}' ({role_id}) berhasil didaftarkan.")

        res = await self.get_role_by_id(role_id, custom_path)
        if not res:
            raise RuntimeError(f"Gagal mengambil role '{role_id}' yang baru dibuat.")
        return res

    async def update_role(
        self, role_id: str, name: Optional[str] = None, system_prompt_template: Optional[str] = None,
        model_provider: Optional[str] = None, model_name: Optional[str] = None,
        temperature: Optional[float] = None, tool_permissions: Optional[List[str]] = None,
        token_budget_per_task: Optional[int] = None, is_active: Optional[bool] = None,
        fallback_chain: Optional[List[Dict[str, Any]]] = None,
        thinking_level: Optional[str] = None, custom_path: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Memperbarui konfigurasi role dan rantai model cadangan (fallback chain)."""
        existing = await self.get_role_by_id(role_id, custom_path)
        if not existing:
            return None

        fields = {
            "name": name if name is not None else existing["name"],
            "system_prompt_template": system_prompt_template if system_prompt_template is not None else existing["system_prompt_template"],
            "model_provider": model_provider if model_provider is not None else existing["model_provider"],
            "model_name": model_name if model_name is not None else existing["model_name"],
            "temperature": temperature if temperature is not None else existing["temperature"],
            "tool_permissions": json.dumps(tool_permissions if tool_permissions is not None else existing["tool_permissions"]),
            "token_budget_per_task": token_budget_per_task if token_budget_per_task is not None else existing["token_budget_per_task"],
            "is_active": 1 if (is_active if is_active is not None else existing["is_active"]) else 0,
            "fallback_chain": json.dumps(fallback_chain if fallback_chain is not None else existing.get("fallback_chain", [])),
            "thinking_level": thinking_level if thinking_level is not None else existing.get("thinking_level", "medium"),
        }

        upd_sql = (
            "UPDATE corporate_roles SET name = :name, system_prompt_template = :system_prompt_template, "
            "model_provider = :model_provider, model_name = :model_name, temperature = :temperature, "
            "tool_permissions = :tool_permissions, token_budget_per_task = :token_budget_per_task, "
            "is_active = :is_active, fallback_chain = :fallback_chain, thinking_level = :thinking_level, "
            "updated_at = CURRENT_TIMESTAMP WHERE id = :id;"
        )
        async with get_db_connection(custom_path) as conn:
            await conn.execute(upd_sql, {**fields, "id": role_id})
            await conn.commit()

        return await self.get_role_by_id(role_id, custom_path)

    async def delete_role(self, role_id: str, custom_path: Optional[str] = None) -> bool:
        """Menghapus role kustom. Melindungi role bawaan sistem pada branch main."""
        existing = await self.get_role_by_id(role_id, custom_path)
        if not existing:
            raise ValueError(f"Role '{role_id}' tidak ditemukan.")

        if existing["is_system_default"] and existing["branch_id"] == "branch_main":
            raise ValueError("Role bawaan sistem pada branch main tidak dapat dihapus.")

        async with get_db_connection(custom_path) as conn:
            await conn.execute("DELETE FROM corporate_roles WHERE id = ?;", (role_id,))
            await conn.commit()
            logger.info(f"Role '{role_id}' berhasil dihapus.")
            return True


role_repo = RoleRepository()
