"""
VentureState Container.
Mendefinisikan wadah state terpusat yang dialirkan antar-node pada Native State Machine.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.engine.schemas.schemas import (
    BusinessBriefSchema,
    PRDContractSchema,
    QualityGateScorecard,
    SystemArchitectureSchema,
    UIComponentSpecSchema,
)


class VentureState(BaseModel):
    """Container data state tunggal yang diproses oleh Native State Machine."""

    project_id: str = Field(description="Identitas unik proyek.")
    project_name: str = Field(description="Nama resmi proyek.")
    stage: str = Field(default="SPARRING_ROOM", description="Tahapan aktif state machine saat ini.")
    founder_idea: str = Field(description="Ide bisnis mentah yang diinput Founder.")
    selected_archetype: Optional[int] = Field(default=1, description="Nomor arketipe legacy/opsional.")

    # Artefak Hasil Kerja Agen (Tervalidasi Skema Ketat)
    business_brief: Optional[BusinessBriefSchema] = None
    system_architecture: Optional[SystemArchitectureSchema] = None
    prd_spec: Optional[PRDContractSchema] = None
    openapi_spec: Optional[Dict[str, Any]] = None
    ui_spec: Optional[UIComponentSpecSchema] = None
    quality_scorecard: Optional[QualityGateScorecard] = None
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Penyimpanan artefak fleksibel per role/task.")

    # Telemetri & Status Operasional
    preview_url: Optional[str] = None
    read_only_files: List[str] = Field(default_factory=list, description="Daftar berkas read-only yang tidak boleh dimodifikasi developer.")
    gate_decision: Optional[str] = Field(default=None, description="Keputusan gate terakhir dari Founder ('APPROVE', 'REVISE', 'KILL').")
    gate_feedback: Optional[str] = Field(default=None, description="Catatan umpan balik Founder pada gate.")
    token_usage: Dict[str, float] = Field(default_factory=dict, description="Akumulasi biaya token per peran ($).")
    event_logs: List[str] = Field(default_factory=list, description="Riwayat ringkas eksekusi langkah.")


    def record_event(self, message: str) -> None:
        """Mencatat ringkasan aksi ke dalam riwayat eksekusi state.

        Args:
            message: Deskripsi event yang terjadi.
        """
        self.event_logs.append(message)
        logger.debug(f"State Event Recorded [{self.project_id}]: {message}")

    def add_token_cost(self, role: str, cost: float) -> None:
        """Menambahkan biaya token untuk peran agen tertentu.

        Args:
            role: Nama peran agen (misal: 'COS', 'CTO').
            cost: Biaya inferensi dalam USD.
        """
        current_cost = self.token_usage.get(role, 0.0)
        self.token_usage[role] = round(current_cost + max(0.0, cost), 4)

    def set_artifact(self, key: str, value: Any) -> None:
        """Menyimpan artefak ke dictionary terpusat dan menyinkronkan atribut state terkait."""
        self.artifacts[key] = value
        if key in ("cos", "business_brief") and isinstance(value, BusinessBriefSchema):
            self.business_brief = value
        elif key in ("cto", "system_architecture") and isinstance(value, SystemArchitectureSchema):
            self.system_architecture = value
        elif key in ("pm", "prd_spec") and isinstance(value, PRDContractSchema):
            self.prd_spec = value
        elif key in ("ui_ux", "ui_spec") and isinstance(value, UIComponentSpecSchema):
            self.ui_spec = value
        elif key in ("qa", "quality_scorecard") and isinstance(value, QualityGateScorecard):
            self.quality_scorecard = value

    def to_dict(self) -> Dict[str, Any]:
        """Mengonversi VentureState ke dictionary JSON-serializable.

        Returns:
            Dictionary data lengkap state.
        """
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VentureState":
        """Membuat instance VentureState dari dictionary dengan validasi Pydantic.

        Args:
            data: Data mentah dictionary.

        Returns:
            Instance VentureState tervalidasi.

        Raises:
            ValueError: Jika data tidak sesuai skema.
        """
        try:
            return cls.model_validate(data)
        except Exception as err:
            logger.error(f"Gagal memvalidasi data VentureState: {err}")
            raise ValueError(f"Invalid VentureState data: {err}") from err
