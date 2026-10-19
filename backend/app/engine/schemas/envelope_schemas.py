"""
Envelope Schemas for Multi-Agent Node Execution.
Mendefinisikan skema Pydantic untuk membungkus hasil keluaran terstruktur setiap peran.
"""

from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from app.engine.schemas.schemas import PRDContractSchema


class BackendOutputEnvelope(BaseModel):
    """Skema validasi ketat untuk keluaran kode Backend Engineer."""

    model_config = ConfigDict(extra="ignore")
    main_code: str = Field(..., min_length=20, description="Kode utama main.py FastAPI.")
    models_code: str = Field(..., min_length=20, description="Kode models.py SQLAlchemy.")
    routers_code: str = Field(..., min_length=20, description="Kode routers.py CRUD endpoints.")
    migration_code: str = Field(..., min_length=20, description="Skrip migrasi alembic_migration.py.")
    requirements_content: str = Field(..., min_length=10, description="Daftar dependensi requirements.txt.")


class FrontendCodeBundle(BaseModel):
    """Wadah kode Next.js terstruktur keluaran Frontend Engineer."""

    model_config = ConfigDict(extra="ignore")
    api_client_code: str
    core_feature_component_code: str
    page_code: str


class PMOutputEnvelope(BaseModel):
    """Wadah validasi gabungan untuk Lean PRD dan OpenAPI 3.1 Spec."""

    model_config = ConfigDict(extra="ignore")
    prd: PRDContractSchema
    openapi_spec: Dict[str, Any]


class DevSecOpsEnvelope(BaseModel):
    """Skema validasi untuk paket orkestrasi kontainer dan deployment."""

    model_config = ConfigDict(extra="ignore")
    docker_compose_yaml: str = Field(..., min_length=30, description="Konfigurasi docker-compose.yml multi-service.")
    production_env_sample: str = Field(..., min_length=10, description="Template environment variables produksi.")
    deployment_payload: Dict[str, Any] = Field(default_factory=dict, description="Metadata payload PaaS deploy.")


class LegalBundleEnvelope(BaseModel):
    """Skema validasi untuk dokumen hukum dan kepatuhan digital."""

    model_config = ConfigDict(extra="ignore")
    terms_of_service: str = Field(..., min_length=50, description="Dokumen Syarat dan Ketentuan layanan.")
    privacy_policy: str = Field(..., min_length=50, description="Dokumen Kebijakan Privasi (UU PDP/GDPR).")
    refund_policy: str = Field(..., min_length=30, description="Dokumen Kebijakan Pengembalian Dana.")
