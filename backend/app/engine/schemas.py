"""
Flexible Pydantic Data Contracts (Open Contract Paradigm).
Mendefinisikan skema kontrak terbuka (extra='allow') yang mendukung inovasi format,
desain UI/UX kaya, animasi, dan skema adaptif dari instruksi Founder di UI.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BusinessBriefSchema(BaseModel):
    """Kontrak keluaran Chief of Staff (CoS) Agent pada Fase 1."""

    model_config = ConfigDict(extra="allow")

    problem_statement: str = Field(description="Rumusan masalah pasar yang valid.")
    proposed_solution: str = Field(description="Deskripsi solusi produk yang ditawarkan.")
    target_audience: str = Field(description="Segmentasi target pelanggan utama.")
    monetization_model: str = Field(description="Model monetisasi (e.g. usage_credits, flat_monthly).")
    pricing_tiers: List[Dict[str, Any]] = Field(description="Daftar struktur paket harga.")
    projected_margin_percentage: float = Field(ge=0.0, le=100.0, description="Estimasi margin keuntungan.")
    market_feasibility_score: int = Field(ge=1, le=100, description="Skor kelayakan komersial pasar (1-100).")
    risks_and_mitigations: List[str] = Field(description="Daftar risiko dan rencana mitigasinya.")


class SystemArchitectureSchema(BaseModel):
    """Kontrak keluaran Chief Technology Officer (CTO) Agent pada Fase 1."""

    model_config = ConfigDict(extra="allow")

    archetype_id: Optional[int] = Field(default=1, description="Nomor katalog arketipe opsional/legacy.")
    frontend_framework: str = Field(default="Next.js 14 App Router")
    backend_framework: str = Field(default="FastAPI Python")
    database: str = Field(default="PostgreSQL")
    estimated_inference_cost_per_user: float = Field(default=0.0, ge=0.0, description="Estimasi biaya token per user ($).")
    circuit_breaker_limits: Dict[str, Any] = Field(
        default_factory=lambda: {"max_iterations": 5, "timeout_seconds": 90},
        description="Batasan pelindung token dan timeout.",
    )


class UserStory(BaseModel):
    """Representasi satuan fitur user story produk."""

    model_config = ConfigDict(extra="allow")

    role: str = Field(description="Sebagai siapa (e.g. Founder, Customer).")
    action: str = Field(description="Aksi yang ingin dilakukan.")
    benefit: str = Field(description="Manfaat yang diperoleh.")
    acceptance_criteria: List[str] = Field(description="Kriteria penerimaan fitur.")


class PRDContractSchema(BaseModel):
    """Kontrak keluaran Product Manager (PM) Agent pada Fase 2."""

    model_config = ConfigDict(extra="allow")

    product_name: str = Field(description="Nama resmi produk startup.")
    tagline: str = Field(description="Deskripsi singkat produk dalam 1 kalimat.")
    core_happy_path_steps: List[str] = Field(
        min_length=3, max_length=5, description="Alur utama 3-5 langkah inti demo."
    )
    in_scope_mvp_features: List[UserStory] = Field(description="Fitur yang masuk ruang lingkup MVP.")
    out_of_scope_features: List[str] = Field(description="Fitur yang ditunda ke versi lanjutan.")


class ComponentSpec(BaseModel):
    """Spesifikasi teknis satu komponen antarmuka pengguna."""

    model_config = ConfigDict(extra="allow")

    name: str = Field(description="Nama komponen React.")
    type: str = Field(description="Tipe elemen (e.g. button, form, table, chart).")
    props: Dict[str, Any] = Field(default_factory=dict, description="Properties komponen.")
    tailwind_classes: str = Field(description="Daftar utility class Tailwind CSS.")


class UIComponentSpecSchema(BaseModel):
    """Kontrak terbuka Lead UI/UX Designer Agent pada Fase 2."""

    model_config = ConfigDict(extra="allow")

    theme_colors: Dict[str, Any] = Field(description="Design tokens warna tema (primary, background, gradients, glows).")
    layout_type: str = Field(description="Tipe tata letak antarmuka (e.g. split_screen, dashboard, bento_grid).")
    screens: List[str] = Field(description="Daftar nama halaman antarmuka.")
    components: List[ComponentSpec] = Field(description="Daftar spesifikasi komponen inti.")


class QualityGateScorecard(BaseModel):
    """Kontrak keluaran QA Automation & AI Evals Agent pada Fase 3."""

    model_config = ConfigDict(extra="allow")

    unit_test_passed: bool = Field(description="Apakah seluruh unit test lolos.")
    test_coverage_percentage: float = Field(ge=0.0, le=100.0, description="Cakupan pengujian kode.")
    owasp_vulnerabilities_count: int = Field(ge=0, description="Jumlah celah OWASP yang ditemukan.")
    hallucination_rate: float = Field(ge=0.0, le=1.0, description="Rasio halusinasi output model AI.")
    status: str = Field(description="Hasil gerbang kualitas: 'PASSED' atau 'FAILED'.")
    reasons: List[str] = Field(default_factory=list, description="Catatan evaluasi.")
