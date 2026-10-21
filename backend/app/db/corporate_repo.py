"""Corporate Repository Facade.

Menyatukan akses repositori Branch, Divisi, dan Peran AI melalui antarmuka tunggal (Facade Pattern)
yang mematuhi Single Responsibility Principle (SRP) dan batas modularitas berkas.
"""

from typing import Any, Dict, List, Optional

from app.db.branch_repo import branch_repo, BranchRepository
from app.db.division_repo import division_repo, DivisionRepository
from app.db.role_repo import role_repo, RoleRepository


class CorporateRepository:
    """Facade terpadu yang mendelegasikan operasi domain ke repositori terspesialisasi."""

    def __init__(
        self,
        branches: Optional[BranchRepository] = None,
        divisions: Optional[DivisionRepository] = None,
        roles: Optional[RoleRepository] = None,
    ) -> None:
        self.branches = branches or branch_repo
        self.divisions = divisions or division_repo
        self.roles = roles or role_repo

    # --- Branch Delegations ---
    async def get_branches(self, custom_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mengambil seluruh daftar branch alur kerja."""
        return await self.branches.get_branches(custom_path)

    async def get_active_branch(self, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Mengambil branch alur kerja aktif saat ini."""
        return await self.branches.get_active_branch(custom_path)

    async def get_branch_by_id(self, branch_id: str, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Mengambil detail branch berdasarkan ID."""
        return await self.branches.get_branch_by_id(branch_id, custom_path)

    async def fork_branch(
        self,
        name: str,
        slug: str,
        description: Optional[str] = None,
        source_branch_id: str = "branch_main",
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Kloning struktur alur kerja lengkap ke branch baru."""
        return await self.branches.fork_branch(name, slug, description, source_branch_id, custom_path)

    async def activate_branch(self, branch_id: str, custom_path: Optional[str] = None) -> Dict[str, Any]:
        """Promosikan branch target menjadi active main workflow."""
        return await self.branches.activate_branch(branch_id, custom_path)

    async def delete_branch(self, branch_id: str, custom_path: Optional[str] = None) -> bool:
        """Hapus branch draft dari sistem."""
        return await self.branches.delete_branch(branch_id, custom_path)

    # --- Division Delegations ---
    async def get_divisions(
        self, branch_id: Optional[str] = None, custom_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Mengambil seluruh divisi pada branch."""
        return await self.divisions.get_divisions(branch_id, custom_path)

    async def get_division_by_id(
        self, division_id: str, custom_path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Mengambil detail divisi berdasarkan ID."""
        return await self.divisions.get_division_by_id(division_id, custom_path)

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
        """Membuat divisi baru."""
        return await self.divisions.create_division(
            branch_id, name, slug, description, accent_color, icon_name, custom_path
        )

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
        return await self.divisions.update_division(
            division_id, name, description, accent_color, icon_name, custom_path
        )

    async def delete_division(self, division_id: str, custom_path: Optional[str] = None) -> bool:
        """Menghapus divisi non-sistem."""
        return await self.divisions.delete_division(division_id, custom_path)

    # --- Role Delegations ---
    async def get_roles(
        self,
        branch_id: Optional[str] = None,
        division_id: Optional[str] = None,
        active_only: bool = False,
        custom_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mengambil seluruh role karyawan AI."""
        return await self.roles.get_roles(branch_id, division_id, active_only, custom_path)

    async def get_role_by_id(self, role_id: str, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Mengambil detail role berdasarkan ID."""
        return await self.roles.get_role_by_id(role_id, custom_path)

    async def create_role(
        self, branch_id: str, division_id: str, name: str, system_prompt_template: str,
        job_description: Optional[str] = "", persona_prompt: Optional[str] = "",
        model_provider: str = "openrouter", model_name: str = "deepseek/deepseek-r1:free",
        temperature: float = 0.2, tool_permissions: Optional[List[str]] = None,
        token_budget_per_task: int = 8000, is_active: bool = True,
        thinking_level: str = "medium", custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mendaftarkan role karyawan AI baru dengan persona_prompt Layer 1."""
        return await self.roles.create_role(
            branch_id=branch_id, division_id=division_id, name=name,
            system_prompt_template=system_prompt_template, job_description=job_description or "",
            persona_prompt=persona_prompt or "", model_provider=model_provider,
            model_name=model_name, temperature=temperature, tool_permissions=tool_permissions,
            token_budget_per_task=token_budget_per_task, is_active=is_active,
            thinking_level=thinking_level, custom_path=custom_path,
        )

    async def update_role(
        self, role_id: str, division_id: Optional[str] = None, name: Optional[str] = None,
        job_description: Optional[str] = None, persona_prompt: Optional[str] = None,
        system_prompt_template: Optional[str] = None, model_provider: Optional[str] = None,
        model_name: Optional[str] = None, temperature: Optional[float] = None,
        tool_permissions: Optional[List[str]] = None, token_budget_per_task: Optional[int] = None,
        is_active: Optional[bool] = None, fallback_chain: Optional[List[Dict[str, Any]]] = None,
        thinking_level: Optional[str] = None, custom_path: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Memperbarui konfigurasi role karyawan AI."""
        return await self.roles.update_role(
            role_id=role_id, division_id=division_id, name=name,
            job_description=job_description, persona_prompt=persona_prompt,
            system_prompt_template=system_prompt_template, model_provider=model_provider,
            model_name=model_name, temperature=temperature, tool_permissions=tool_permissions,
            token_budget_per_task=token_budget_per_task, is_active=is_active,
            fallback_chain=fallback_chain, thinking_level=thinking_level,
            custom_path=custom_path,
        )

    async def delete_role(self, role_id: str, custom_path: Optional[str] = None) -> bool:
        """Menghapus role karyawan AI kustom."""
        return await self.roles.delete_role(role_id, custom_path)


corporate_repo = CorporateRepository()
