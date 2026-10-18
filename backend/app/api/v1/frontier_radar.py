"""
Frontier Radar API Endpoints.
Menyediakan inspeksi Flight Recorder, status kuota finansial, top-up Founder, dan scorecard visual UI.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.engine.flight_recorder import agent_flight_recorder
from app.engine.financial_guardrail import financial_guardrail
from app.engine.visual_evaluator import visual_evaluator

router = APIRouter(prefix="/projects/{project_id}/frontier-radar", tags=["Frontier Radar"])


class BudgetTopupRequest(BaseModel):
    """Skema permintaan persetujuan penambahan anggaran token oleh Founder."""

    ticket_id: str
    additional_tokens: int = Field(default=150000, ge=1000)
    additional_dollars: float = Field(default=0.75, ge=0.1)


@router.get("/flight-logs")
async def get_flight_logs(project_id: str, limit: int = 100) -> Dict[str, Any]:
    """Mengambil riwayat stream peristiwa kotak hitam agen untuk time-travel replay."""
    logs = agent_flight_recorder.get_flight_log(project_id, limit=limit)
    return {
        "project_id": project_id,
        "total_events": len(logs),
        "events": logs,
    }


@router.get("/flight-logs/{step_index}")
async def replay_flight_step(project_id: str, step_index: int) -> Dict[str, Any]:
    """Mendapatkan detail snapshot state pada langkah tertentu."""
    step = agent_flight_recorder.replay_step(project_id, step_index)
    if not step:
        raise HTTPException(status_code=404, detail=f"Langkah ke-{step_index} tidak ditemukan.")
    return step


@router.get("/financial-status")
async def get_financial_status(project_id: str) -> Dict[str, Any]:
    """Mengambil status kuota pengeluaran token dan status pembekuan tiket."""
    ledger_data = await financial_guardrail.sync_with_ledger(project_id)
    return {
        "project_id": project_id,
        "max_tokens_per_ticket": financial_guardrail.max_tokens,
        "max_cost_per_ticket": financial_guardrail.max_cost,
        "ledger": ledger_data,
        "frozen_tickets": list(financial_guardrail._frozen_tickets),
        "ticket_spends": financial_guardrail._ticket_spend,
    }


@router.post("/financial-topup")
async def approve_financial_topup(project_id: str, payload: BudgetTopupRequest) -> Dict[str, Any]:
    """Founder menyetujui penambahan anggaran untuk mencairkan tiket yang dibekukan."""
    res = financial_guardrail.approve_founder_budget_topup(
        ticket_id=payload.ticket_id,
        additional_tokens=payload.additional_tokens,
        additional_dollars=payload.additional_dollars,
    )
    return {"project_id": project_id, "topup_result": res}


@router.get("/visual-scorecard")
async def get_visual_scorecard(project_id: str) -> Dict[str, Any]:
    """Mengevaluasi skor estetika visual berkas antarmuka frontend saat ini."""
    page_file = Path("projects_output") / project_id / "frontend" / "src" / "app" / "page.tsx"
    markup_sample = ""
    if page_file.exists():
        try:
            markup_sample = page_file.read_text(encoding="utf-8")
        except OSError as err:
            logger.warning(f"Gagal membaca page.tsx untuk visual scorecard: {err}")

    if not markup_sample:
        markup_sample = '<div className="flex flex-col p-8 bg-slate-900 text-white min-h-screen">Ready</div>'

    scorecard = visual_evaluator.evaluate_interface_layout(markup_sample)
    return {
        "project_id": project_id,
        "scorecard": scorecard.model_dump(),
    }
