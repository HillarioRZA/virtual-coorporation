"""
Executive Governance & CEO Control Tower REST API.
Menangani intervensi manual hak veto CEO, pelaporan eskalasi C-Level, dan status circuit breaker.
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.engine.governance.circuit_breaker import agent_circuit_breaker
from app.engine.schemas.corporate_schemas import CorporateMessageCreate
from app.engine.runtime.event_bus import corporate_event_bus
from app.engine.schemas.governance_schemas import (
    CircuitBreakerOverrideRequest,
    CircuitBreakerStatus,
    ExecutiveDecisionRequest,
    ExecutiveEscalationReport,
)

router = APIRouter(prefix="/governance", tags=["Executive Governance & CEO Tower"])


class CeoOverridePayload(BaseModel):
    """Payload pembungkus eksekusi override CEO pada tiket tertentu."""

    ticket_id: str = Field(..., description="ID tiket sasaran.")
    project_id: str = Field(..., description="ID proyek venture.")
    branch_id: str = Field("branch_main", description="ID branch alur kerja.")
    override: CircuitBreakerOverrideRequest


@router.post("/override")
async def execute_ceo_override(payload: CeoOverridePayload) -> Dict[str, Any]:
    """Mengeksekusi hak veto / intervensi langsung CEO atas tiket yang terblokir."""
    try:
        result = await agent_circuit_breaker.execute_ceo_override(
            ticket_id=payload.ticket_id,
            project_id=payload.project_id,
            branch_id=payload.branch_id,
            action=payload.override.action,
            directive=payload.override.directive,
            target_role_id=payload.override.target_role_id,
        )
        return result
    except Exception as err:
        logger.error(f"Gagal mengeksekusi CEO override: {err}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.post("/escalate", response_model=ExecutiveEscalationReport)
async def submit_executive_escalation(report: ExecutiveEscalationReport) -> ExecutiveEscalationReport:
    """Menerima laporan eskalasi insiden strategis dari CTO atau CoS ke meja CEO."""
    import uuid
    report_id = report.id or f"esc_{uuid.uuid4().hex[:8]}"
    report.id = report_id

    options_summary = " | ".join([f"[{o.get('option_id', '')}] {o.get('label', '')}" for o in report.options])
    escalation_content = (
        f"🚨 LAPORAN ESKALASI DIREKSI [{report.reporter_role.upper()}]: {report.title}\n"
        f"Ringkasan: {report.summary}\n"
        f"Pilihan Solusi: {options_summary}"
    )

    try:
        await corporate_event_bus.publish(
            CorporateMessageCreate(
                branch_id="branch_main",
                project_id=report.project_id,
                channel_type="LOUNGE",
                sender_role_id=f"role_{report.reporter_role}",
                event_type="EXECUTIVE_ESCALATION",
                content=escalation_content,
            )
        )
        logger.info(f"Laporan Eskalasi C-Level dipublikasikan [{report_id}] untuk project {report.project_id}")
        return report
    except Exception as err:
        logger.error(f"Gagal mempublikasikan eskalasi eksekutif: {err}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


class CeoDecisionPayload(BaseModel):
    """Payload pembungkus pemilihan opsi keputusan CEO atas eskalasi."""

    report_id: str = Field(..., description="ID laporan eskalasi.")
    project_id: str = Field(..., description="ID proyek venture.")
    branch_id: str = Field("branch_main", description="ID branch alur kerja.")
    decision: ExecutiveDecisionRequest


@router.post("/decision")
async def submit_ceo_decision(payload: CeoDecisionPayload) -> Dict[str, Any]:
    """Menerapkan keputusan 1-klik CEO atas opsi solusi yang diajukan direksi."""
    decision_msg = (
        f"👑 Keputusan CEO Ditetapkan atas Laporan [{payload.report_id}]: "
        f"Memilih Solusi [OPSI {payload.decision.selected_option_id}]. "
        f"Catatan Arahan: {payload.decision.feedback or 'Disetujui untuk dieksekusi segera.'}"
    )

    try:
        await corporate_event_bus.publish(
            CorporateMessageCreate(
                branch_id=payload.branch_id,
                project_id=payload.project_id,
                channel_type="LOUNGE",
                sender_role_id="chairman",
                event_type="CEO_ESCALATION_DECISION",
                content=decision_msg,
            )
        )
        logger.info(f"Keputusan CEO berhasil diterapkan untuk eskalasi [{payload.report_id}]")
        return {"status": "success", "report_id": payload.report_id, "selected_option": payload.decision.selected_option_id}
    except Exception as err:
        logger.error(f"Gagal menerapkan keputusan CEO: {err}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("/status/{ticket_id}", response_model=CircuitBreakerStatus)
async def get_circuit_breaker_status(
    ticket_id: str, project_id: str = Query("", description="ID proyek venture.")
) -> CircuitBreakerStatus:
    """Mengambil status pemantauan loop circuit breaker pada tiket tertentu."""
    return agent_circuit_breaker.get_status(ticket_id=ticket_id, project_id=project_id)
