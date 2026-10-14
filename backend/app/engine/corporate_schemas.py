"""
Corporate Schemas & Data Transfer Objects (DTOs).
Mendefinisikan skema Pydantic untuk Git-Style Branching, Divisi Dinamis,
Role Karyawan AI, Papan Tiket Kanban, dan Event Bus Messages.
"""

from datetime import datetime
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# 1. BRANCH SCHEMAS (Git-Style Workflow Branching)
# ============================================================================

class BranchCreate(BaseModel):
    """Payload pembuatan branch baru dari nol."""
    name: str = Field(..., min_length=2, max_length=100, description="Nama deskriptif branch organisasi.")
    slug: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9_\-]+$", description="Slug unik identifier URL.")
    description: Optional[str] = Field(None, max_length=500, description="Keterangan tujuan branch.")


class BranchForkRequest(BaseModel):
    """Payload kloning / forking branch seperti Git."""
    name: str = Field(..., min_length=2, max_length=100, description="Nama branch eksperimen baru.")
    slug: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9_\-]+$", description="Slug unik branch baru.")
    description: Optional[str] = Field(None, max_length=500, description="Keterangan tujuan forking.")
    source_branch_id: str = Field("branch_main", description="ID branch sumber yang dikloning.")


class BranchResponse(BaseModel):
    """Representasi respon branch organisasi."""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    is_active_main: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ============================================================================
# 2. DIVISION SCHEMAS
# ============================================================================

class DivisionCreate(BaseModel):
    """Payload pendaftaran divisi baru."""
    branch_id: str = Field("branch_main", description="ID branch pemilik divisi.")
    name: str = Field(..., min_length=2, max_length=100, description="Nama divisi.")
    slug: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9_\-]+$", description="Slug unik divisi dalam branch.")
    description: Optional[str] = Field(None, max_length=500, description="Mandat operasional divisi.")
    accent_color: str = Field("#cbd5e1", description="Kode warna hex aksen antarmuka.")
    icon_name: str = Field("FolderTree", description="Nama ikon Lucide React.")


class DivisionUpdate(BaseModel):
    """Payload pembaruan metadata divisi."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    accent_color: Optional[str] = None
    icon_name: Optional[str] = None


class DivisionResponse(BaseModel):
    """Representasi respon divisi korporat."""
    id: str
    branch_id: str
    name: str
    slug: str
    description: Optional[str] = None
    accent_color: str = "#cbd5e1"
    icon_name: str = "FolderTree"
    is_system_default: bool = False
    order_index: int = 0
    roles_count: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ============================================================================
# 3. ROLE SCHEMAS
# ============================================================================

class RoleCreate(BaseModel):
    """Payload pendaftaran role agen baru."""
    model_config = ConfigDict(protected_namespaces=())

    branch_id: str = Field("branch_main", description="ID branch pemilik role.")
    division_id: str = Field(..., description="ID divisi penanggung jawab.")
    name: str = Field(..., min_length=2, max_length=100, description="Nama peran karyawan AI.")
    slug: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9_\-]+$", description="Slug unik role dalam branch.")
    system_prompt_template: str = Field(..., min_length=10, description="System instruction persona.")
    model_provider: str = Field("openrouter", description="Provider LLM.")
    model_name: str = Field("deepseek/deepseek-r1:free", description="ID model LLM.")
    temperature: float = Field(0.2, ge=0.0, le=1.5, description="Sampling temperature.")
    tool_permissions: List[str] = Field(default_factory=lambda: ["read_file", "write_file"], description="Daftar izin alat.")
    token_budget_per_task: int = Field(8000, ge=1000, le=100000, description="Batas maksimal token.")
    is_active: bool = Field(True, description="Status aktif agen.")


class RoleUpdate(BaseModel):
    """Payload modifikasi spesifikasi role agen."""
    model_config = ConfigDict(protected_namespaces=())

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    system_prompt_template: Optional[str] = Field(None, min_length=10)
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=1.5)
    tool_permissions: Optional[List[str]] = None
    token_budget_per_task: Optional[int] = Field(None, ge=1000, le=100000)
    is_active: Optional[bool] = None


class RoleResponse(BaseModel):
    """Representasi respon role agen korporat."""
    model_config = ConfigDict(protected_namespaces=())

    id: str
    branch_id: str
    division_id: str
    name: str
    slug: str
    system_prompt_template: str
    model_provider: str
    model_name: str
    temperature: float
    tool_permissions: List[str]
    token_budget_per_task: int
    is_active: bool
    is_system_default: bool
    order_index: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ============================================================================
# 4. TICKET SCHEMAS (Virtual Kanban)
# ============================================================================

class TicketCreate(BaseModel):
    """Payload pembuatan tiket baru di papan Kanban."""
    branch_id: str = Field("branch_main", description="ID branch workflow.")
    project_id: str = Field(..., description="ID venture terkait.")
    division_id: str = Field(..., description="ID divisi pelaksana.")
    assigned_role_id: Optional[str] = Field(None, description="ID role agen yang ditugaskan.")
    title: str = Field(..., min_length=3, max_length=200, description="Judul tugas.")
    description: str = Field(..., min_length=5, description="Deskripsi instruksi tugas.")
    product_line: str = Field("SOFTWARE", description="SOFTWARE, EDUCATION, COPYWRITING, RESEARCH.")
    priority: str = Field("MEDIUM", description="LOW, MEDIUM, HIGH, CRITICAL.")
    dependencies: List[str] = Field(default_factory=list, description="List ticket_id prasyarat.")
    parent_ticket_id: Optional[str] = None


class TicketUpdate(BaseModel):
    """Payload update status atau konten tiket."""
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_role_id: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = Field(None, description="BACKLOG, TODO, IN_PROGRESS, REVIEW, DONE.")
    artifact_refs: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None


class TicketResponse(BaseModel):
    """Representasi respon tiket Kanban."""
    id: str
    branch_id: str
    project_id: str
    division_id: str
    assigned_role_id: Optional[str] = None
    title: str
    description: str
    product_line: str
    priority: str
    status: str
    artifact_refs: List[str] = []
    dependencies: List[str] = []
    parent_ticket_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ============================================================================
# 5. MESSAGE SCHEMAS (Corporate Lounge & Event Bus)
# ============================================================================

class CorporateMessageCreate(BaseModel):
    """Payload pesan obrolan antar-agen atau event."""
    branch_id: str = Field("branch_main", description="ID branch workflow.")
    project_id: str = Field(..., description="ID venture terkait.")
    channel_type: str = Field("LOUNGE", description="LOUNGE, P2P_DISPUTE, REVIEW_FEEDBACK.")
    sender_role_id: str = Field(..., description="ID role pengirim.")
    recipient_role_id: Optional[str] = Field(None, description="ID role penerima atau None (broadcast).")
    ticket_id: Optional[str] = None
    event_type: str = Field("MESSAGE", description="MESSAGE, TASK_COMPLETED, SCHEMA_CHANGE, TEST_ALERT.")
    content: str = Field(..., min_length=1, description="Isi teks pesan.")
    token_cost: float = Field(0.0, ge=0.0)


class CorporateMessageResponse(BaseModel):
    """Representasi respon pesan event log."""
    id: int
    branch_id: str
    project_id: str
    channel_type: str
    sender_role_id: str
    recipient_role_id: Optional[str] = None
    ticket_id: Optional[str] = None
    event_type: str
    content: str
    token_cost: float
    created_at: Optional[str] = None
