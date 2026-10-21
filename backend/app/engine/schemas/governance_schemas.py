"""Governance & Executive Decision Schemas.

Mendefinisikan skema Pydantic untuk Circuit Breaker, CEO Overrides,
dan Executive Escalations.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CircuitBreakerStatus(BaseModel):
    """Representasi status pemantauan loop circuit breaker pada tiket."""

    ticket_id: str = Field(..., description="ID tiket sasaran.")
    project_id: str = Field("", description="ID venture terkait.")
    turn_count: int = Field(0, description="Jumlah putaran diskusi berjalan.")
    is_blocked: bool = Field(False, description="Apakah tiket diblokir karena batas loop.")
    reason: Optional[str] = Field(None, description="Alasan pemblokiran jika aktif.")


class CircuitBreakerOverrideRequest(BaseModel):
    """Payload intervensi CEO untuk membuka blokir tiket atau mengarahkan role."""

    action: str = Field("UNBLOCK", description="Aksi override: UNBLOCK, RETRY, REASSIGN, CLOSE.")
    directive: Optional[str] = Field(None, description="Arahan atau instruksi langsung dari CEO.")
    target_role_id: Optional[str] = Field(None, description="Role tujuan jika dialihkan.")


class ExecutiveDecisionRequest(BaseModel):
    """Payload keputusan 1-klik eksekutif atas eskalasi masalah."""

    selected_option_id: str = Field(..., description="ID opsi solusi yang dipilih CEO.")
    feedback: Optional[str] = Field(None, description="Catatan arahan tambahan.")


class ExecutiveEscalationReport(BaseModel):
    """Laporan eskalasi insiden strategis ke meja CEO."""

    id: Optional[str] = Field(None, description="ID unik laporan.")
    project_id: str = Field(..., description="ID venture terkait.")
    reporter_role: str = Field("cto", description="Role pelapor (cto, cos, cpo).")
    title: str = Field(..., description="Judul ringkas insiden.")
    summary: str = Field(..., description="Deskripsi singkat masalah.")
    options: List[Dict[str, Any]] = Field(default_factory=list, description="Daftar opsi solusi.")
