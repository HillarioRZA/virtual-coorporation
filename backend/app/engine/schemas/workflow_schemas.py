"""
Corporate Workflow Pipeline Schemas & DTOs.
Mendefinisikan skema Pydantic untuk tahapan eksekusi alur kerja berurutan (Pipeline Sequence),
keputusan mandiri agen (AgentDecisionEnvelope), dan Executive Governance Hub.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class PipelineCreate(BaseModel):
    """Payload pembuatan rantai pipeline alur kerja baru untuk lini produk tertentu."""

    name: str = Field(..., min_length=2, description="Nama pipeline (misal: 'Edukasi & Kursus Online').")
    slug: str = Field(..., min_length=2, description="Slug unik pipeline (misal: 'education').")
    product_line: str = Field("CUSTOM", description="Lini produk (SOFTWARE, EDUCATION, COPYWRITING, MARKET_RESEARCH, CUSTOM).")
    description: Optional[str] = Field(None, description="Deskripsi tujuan dan cakupan pipeline.")


class PipelineResponse(BaseModel):
    """Representasi respon informasi rantai pipeline alur kerja."""

    id: str
    branch_id: str
    name: str
    slug: str
    product_line: str = "SOFTWARE"
    description: Optional[str] = None
    is_default: bool = False
    stages_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PipelineStageItem(BaseModel):
    """Representasi respon dan request satu langkah dalam rantai alur kerja korporat."""

    model_config = ConfigDict(protected_namespaces=())

    id: Optional[str] = Field(None, description="ID unik tahapan (misal: stg_xxxx).")
    pipeline_id: Optional[str] = Field("pipe_software_main", description="ID pipeline induk tahapan ini.")
    stage_index: int = Field(0, description="Nomor urut sekuensial tahapan.")
    order_index: int = Field(0, description="Nomor urut sekuensial tahapan (alias stage_index).")
    stage_type: Literal["ROLE_EXECUTION", "CEO_GATE"] = Field(
        "ROLE_EXECUTION", description="Tipe tahapan: eksekusi peran atau gerbang CEO."
    )
    role_id: Optional[str] = Field(None, description="ID unik role pelaksana tugas jika ROLE_EXECUTION.")
    role_name: Optional[str] = Field(None, description="Nama peran karyawan AI.")
    role_slug: Optional[str] = Field(None, description="Slug unik role.")
    division_id: Optional[str] = Field(None, description="ID divisi penanggung jawab.")
    division_name: Optional[str] = Field(None, description="Nama divisi penanggung jawab.")
    division_color: Optional[str] = Field("#cbd5e1", description="Aksen warna divisi.")
    model_name: Optional[str] = Field(None, description="Model AI yang digunakan.")
    ceo_gate_type: Optional[Literal["APPROVAL_GATE", "STRATEGIC_MEETING", "DIRECTION_INPUT"]] = Field(
        None, description="Mode gerbang CEO jika stage_type == 'CEO_GATE'."
    )
    custom_label: Optional[str] = Field(None, description="Label kustom tahapan.")
    custom_instructions: Optional[str] = Field(None, description="Instruksi tambahan khusus tahapan.")
    is_active: bool = Field(True, description="Status aktif peran.")
    is_system_default: bool = Field(False, description="Penanda peran bawaan Tech Core.")


# Backward compatibility alias
PipelineStageResponse = PipelineStageItem


class SavePipelineStagesRequest(BaseModel):
    """Payload penyimpanan seluruh konfigurasi tahapan alur kerja baru pada branch."""

    pipeline_id: Optional[str] = Field(None, description="ID pipeline sasaran penyimpanan.")
    stages: List[PipelineStageItem] = Field(
        ...,
        min_length=1,
        description="Daftar tahapan baru yang terurut (mendukung looping & CEO gates).",
    )


class ReorderPipelineRequest(BaseModel):
    """Payload penyusunan ulang sederhana urutan eksekusi alur kerja peran."""

    ordered_role_ids: List[str] = Field(
        ...,
        min_length=1,
        description="Daftar ID role yang diurutkan dari tahap pertama hingga akhir.",
    )


class ReorderDivisionsRequest(BaseModel):
    """Payload penyusunan ulang urutan divisi dalam bagan organisasi."""

    ordered_division_ids: List[str] = Field(
        ...,
        min_length=1,
        description="Daftar ID divisi yang diurutkan secara sekuensial.",
    )


class AgentDecisionDetail(BaseModel):
    """Detail keputusan tindakan mikro yang diambil oleh agen."""

    action: Literal["PROCEED", "CONSULT_ROLE", "ESCALATE_TO_C_LEVEL", "REQUEST_REWORK"] = Field(
        ..., description="Aksi yang diputuskan agen."
    )
    target_role: Optional[str] = Field(None, description="Slug peran yang dituju (misal: 'pm', 'cto').")
    cc_roles: List[str] = Field(default_factory=list, description="Daftar peran tembusan/pengawas.")
    urgency: Literal["NORMAL", "HIGH", "BLOCKING"] = Field("NORMAL", description="Tingkat urgensi hambatan.")


class AgentDialogue(BaseModel):
    """Isi pesan komunikasi inter-agen atau pertanyaan klarifikasi."""

    summary: str = Field(..., description="Ringkasan kendala atau topik bahasan.")
    question_to_target: Optional[str] = Field(None, description="Pertanyaan spesifik kepada target peran.")
    suggested_solution: Optional[str] = Field(None, description="Usulan rekomendasi solusi dari agen.")


class AgentDecisionEnvelope(BaseModel):
    """Kontrak amplop keputusan mandiri agen saat memproses tugas."""

    step_id: str = Field(..., description="ID langkah/tugas saat ini.")
    status: Literal["IN_PROGRESS", "NEED_CLARIFICATION", "COMPLETED", "ESCALATED"] = Field(
        ..., description="Status evaluasi tugas oleh agen."
    )
    decision: AgentDecisionDetail
    dialogue: Optional[AgentDialogue] = None
    work_in_progress: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Berkas yang selesai atau terblokir."
    )


class CircuitBreakerStatus(BaseModel):
    """Status pengawas anti-infinite loop pada sebuah tiket atau proyek."""

    ticket_id: str = Field(..., description="ID tiket sasaran.")
    project_id: str = Field(..., description="ID proyek venture.")
    turn_count: int = Field(0, description="Jumlah giliran klarifikasi berturut-turut.")
    is_blocked: bool = Field(False, description="Apakah circuit breaker sedang aktif membekukan tugas.")
    reason: Optional[str] = Field(None, description="Alasan pembekuan loop.")


class CircuitBreakerOverrideRequest(BaseModel):
    """Payload intervensi manual CEO untuk mengambil alih tugas yang terblokir."""

    action: Literal["FORCE_PROCEED", "INTERVENE", "REASSIGN"] = Field(
        ..., description="Tindakan intervensi CEO: bypass/proceed, intervensi chat, atau reassign."
    )
    directive: Optional[str] = Field(None, description="Instruksi langsung dari CEO.")
    target_role_id: Optional[str] = Field(None, description="ID peran baru jika dialihkan.")


class ExecutiveEscalationReport(BaseModel):
    """Model laporan insiden atau rekomendasi strategis C-Level ke meja CEO."""

    id: Optional[str] = Field(None, description="ID unik laporan eskalasi.")
    project_id: str = Field(..., description="ID proyek venture.")
    reporter_role: str = Field(..., description="Slug peran pelapor ('cto' atau 'cos').")
    title: str = Field(..., description="Judul ringkas insiden atau opsi strategis.")
    summary: str = Field(..., description="Ringkasan eksekutif masalah.")
    options: List[Dict[str, str]] = Field(
        default_factory=list, description="Pilihan solusi konkret (option_id, label, impact)."
    )
    urgency: Literal["NORMAL", "HIGH", "CRITICAL"] = Field("HIGH", description="Tingkat urgensi.")
    selected_option_id: Optional[str] = Field(None, description="Opsi yang dipilih oleh CEO.")


class ExecutiveDecisionRequest(BaseModel):
    """Payload keputusan CEO atas laporan eskalasi C-Level."""

    selected_option_id: str = Field(..., description="ID opsi yang dipilih (e.g. 'A', 'B').")
    feedback: Optional[str] = Field(None, description="Catatan tambahan dari CEO.")
