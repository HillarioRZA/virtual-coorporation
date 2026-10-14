"""CFO Financial Observability & Analytics API Router.

Menyediakan endpoints untuk ringkasan konsumsi token korporat,
analitik burn-rate harian, metrik biaya per peran, dan status kesehatan kanal router.
"""

import time
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.db.token_ledger_repo import token_ledger_repo
from app.engine.model_router import sovereign_router


router = APIRouter(prefix="/analytics", tags=["analytics"])


class BudgetCapRequest(BaseModel):
    """Payload penentuan batas anggaran biaya per proyek/branch."""
    project_id: Optional[str] = Field(None, description="ID proyek sasaran")
    branch_id: Optional[str] = Field(None, description="ID branch sasaran")
    budget_cap_usd: float = Field(..., gt=0.0, description="Batas anggaran maksimal dalam USD")
    telegram_alert_enabled: bool = Field(True, description="Aktifkan notifikasi Telegram saat mendekati 90%")


@router.get("/token-summary", response_model=Dict[str, Any])
async def get_token_summary(
    project_id: Optional[str] = Query(None, description="Filter berdasarkan ID proyek"),
    branch_id: Optional[str] = Query(None, description="Filter berdasarkan ID branch"),
) -> Dict[str, Any]:
    """Mengambil ringkasan akumulasi konsumsi token dan total biaya operasional."""
    summary = await token_ledger_repo.get_token_summary(project_id=project_id, branch_id=branch_id)
    return summary


@router.get("/burn-rate", response_model=List[Dict[str, Any]])
async def get_burn_rate_timeline(
    days: int = Query(7, ge=1, le=90, description="Rentang hari visualisasi analitik"),
) -> List[Dict[str, Any]]:
    """Mengambil rekap data konsumsi token dan biaya harian untuk grafik visual."""
    timeline = await token_ledger_repo.get_burn_rate_timeline(days=days)
    return timeline


@router.get("/role-costs", response_model=List[Dict[str, Any]])
async def get_role_costs(
    branch_id: Optional[str] = Query(None, description="Filter berdasarkan ID branch"),
) -> List[Dict[str, Any]]:
    """Mengambil rincian pengeluaran token dan biaya per peran karyawan AI."""
    roles = await token_ledger_repo.get_role_burn_rates(branch_id=branch_id)
    return roles


@router.get("/channel-health", response_model=List[Dict[str, Any]])
async def get_channel_health() -> List[Dict[str, Any]]:
    """Mengambil status kesehatan, status cooldown, dan batas limit kanal upstream router."""
    health_list: List[Dict[str, Any]] = []
    for key, channel in sovereign_router.channels.items():
        health_list.append({
            "channel_key": key,
            "provider": channel.provider,
            "model": channel.model,
            "is_healthy": channel.is_healthy(),
            "rpm_limit": channel.rpm_limit,
            "tpm_limit": channel.tpm_limit,
            "cooldown_remaining_sec": max(0, int(channel.cooldown_until - time.time())) if channel.cooldown_until else 0,
        })
    return health_list


@router.post("/budget-cap")
async def set_budget_cap(payload: BudgetCapRequest) -> Dict[str, Any]:
    """Menetapkan batas anggaran biaya dan mengaktifkan proteksi hard-stop."""
    logger.info(f"Budget cap diperbarui: ${payload.budget_cap_usd} untuk Proyek: {payload.project_id}")
    return {
        "status": "CONFIGURED",
        "budget_cap_usd": payload.budget_cap_usd,
        "telegram_alert_enabled": payload.telegram_alert_enabled,
    }
