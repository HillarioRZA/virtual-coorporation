"""
Projects API Router.
Menangani siklus hidup proyek venture: inisialisasi, pemantauan portofolio, dan inspeksi state.
"""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.db.session import get_db_connection
from app.engine.memory.memory import MemoryManager
from app.engine.runtime.state import VentureState

router = APIRouter(prefix="/projects", tags=["Projects"])


class CreateProjectRequest(BaseModel):
    """Payload pendaftaran proyek venture baru."""

    name: str = Field(..., min_length=2, max_length=100, description="Nama proyek startup.")
    founder_idea: str = Field(..., min_length=10, description="Deskripsi ide bisnis mentah dari Founder.")
    archetype_id: Optional[int] = Field(default=1, description="Nomor arketipe opsional/legacy.")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(payload: CreateProjectRequest) -> Dict[str, Any]:
    """Mendaftarkan proyek venture baru dan menginisialisasi checkpoint awal."""
    project_id = f"proj_{uuid.uuid4().hex[:8]}"
    mem = MemoryManager()

    try:
        await mem.ensure_project(
            project_id=project_id,
            name=payload.name,
            founder_idea=payload.founder_idea,
            archetype_id=payload.archetype_id,
            stage="SPARRING_ROOM",
        )
        state = VentureState(
            project_id=project_id,
            project_name=payload.name,
            founder_idea=payload.founder_idea,
            selected_archetype=payload.archetype_id,
            stage="SPARRING_ROOM",
        )
        await mem.save_checkpoint(state)
        await mem.log_event(
            project_id=project_id,
            stage="SPARRING_ROOM",
            sender_role="CEO",
            recipient_role="COS",
            event_type="PROJECT_CREATED",
            content=f"Founder menginisiasi proyek '{payload.name}': {payload.founder_idea}",
        )
        logger.info(f"Proyek baru diinisialisasi: [{project_id}] {payload.name}")

        return {
            "status": "success",
            "data": {
                "project_id": project_id,
                "name": payload.name,
                "stage": "SPARRING_ROOM",
                "archetype_id": payload.archetype_id,
            },
        }
    except Exception as err:
        logger.error(f"Gagal membuat proyek baru: {err}")
        raise HTTPException(status_code=500, detail=f"Gagal membuat proyek: {err}") from err


@router.get("", status_code=status.HTTP_200_OK)
async def list_projects() -> Dict[str, Any]:
    """Mengambil daftar seluruh proyek untuk kartu Portfolio Hub di dashboard."""
    try:
        async with get_db_connection() as conn:
            proj_cursor = await conn.execute(
                "SELECT id, name, stage, archetype_id, status, created_at FROM projects ORDER BY created_at DESC"
            )
            proj_rows = await proj_cursor.fetchall()

            cost_cursor = await conn.execute(
                "SELECT project_id, SUM(token_cost) as total_cost FROM agent_event_logs GROUP BY project_id"
            )
            cost_rows = await cost_cursor.fetchall()
            cost_map = {row["project_id"]: float(row["total_cost"] or 0.0) for row in cost_rows}

        results: List[Dict[str, Any]] = []
        for row in proj_rows:
            p_id = row["id"]
            tokens_cost = round(cost_map.get(p_id, 0.0), 4)
            results.append(
                {
                    "project_id": p_id,
                    "name": row["name"],
                    "stage": row["stage"],
                    "archetype_id": row["archetype_id"],
                    "tokens_cost": tokens_cost,
                    "gross_revenue": 0.0,
                    "net_profit": round(-tokens_cost, 4),
                    "status": row["status"],
                }
            )

        return {"status": "success", "data": results}
    except Exception as err:
        logger.error(f"Gagal mengambil daftar proyek: {err}")
        raise HTTPException(status_code=500, detail=f"Gagal mengambil daftar proyek: {err}") from err


@router.get("/{project_id}", status_code=status.HTTP_200_OK)
async def get_project(project_id: str) -> Dict[str, Any]:
    """Mengambil snapshot detail state aktif proyek."""
    mem = MemoryManager()
    state = await mem.load_latest_checkpoint(project_id)
    if not state:
        logger.warning(f"Proyek tidak ditemukan: [{project_id}]")
        raise HTTPException(status_code=404, detail=f"Proyek '{project_id}' tidak ditemukan.")

    data = state.to_dict()
    data["preview_url"] = state.preview_url or f"http://demo-{project_id}.local.sandbox"
    try:
        raw_logs = await mem.get_event_logs(project_id)
        if raw_logs:
            data["event_logs"] = [f"[{l['sender_role']}] {l['content']}" for l in raw_logs]
    except Exception as log_err:
        logger.warning(f"Gagal memuat event logs proyek [{project_id}]: {log_err}")
    return {"status": "success", "data": data}


@router.get("/{project_id}/preview/status", status_code=status.HTTP_200_OK)
async def get_preview_status(project_id: str) -> Dict[str, Any]:
    """Memeriksa kesiapan kontainer sandbox dan status URL preview."""
    mem = MemoryManager()
    state = await mem.load_latest_checkpoint(project_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Proyek '{project_id}' tidak ditemukan.")

    is_running = state.preview_url is not None
    port = 4000
    preview_url = state.preview_url or f"http://demo-{project_id}.local.sandbox"

    return {
        "status": "success",
        "data": {
            "is_running": is_running,
            "port": port,
            "preview_url": preview_url,
            "uptime_seconds": 60 if is_running else 0,
        },
    }


@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(project_id: str) -> Dict[str, Any]:
    """Menghapus proyek venture dan seluruh data riwayatnya secara permanen."""
    try:
        import shutil
        from pathlib import Path
        async with get_db_connection() as conn:
            cursor = await conn.execute("SELECT id, name FROM projects WHERE id = ?", (project_id,))
            proj = await cursor.fetchone()
            if not proj:
                raise HTTPException(status_code=404, detail=f"Proyek '{project_id}' tidak ditemukan.")

            proj_name = proj["name"]
            tables = [
                ("projects", "id"),
                ("project_checkpoints", "project_id"),
                ("agent_event_logs", "project_id"),
                ("corporate_tickets", "project_id"),
                ("corporate_messages", "project_id"),
                ("corporate_financial_ledger", "project_id"),
                ("corporate_pull_requests", "project_id"),
                ("sandbox_snapshots", "project_id"),
                ("sentinel_findings", "project_id"),
            ]
            for tbl, col in tables:
                try:
                    await conn.execute(f"DELETE FROM {tbl} WHERE {col} = ?", (project_id,))
                except Exception:
                    pass
            await conn.commit()

        for base_dir in ["workspaces", "sandbox_storage"]:
            target_dir = Path(base_dir) / project_id
            if target_dir.exists() and target_dir.is_dir():
                shutil.rmtree(target_dir, ignore_errors=True)

        logger.info(f"Proyek [{project_id}] '{proj_name}' berhasil dihapus permanen.")
        return {"status": "success", "message": f"Proyek '{proj_name}' ({project_id}) berhasil dihapus."}
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Gagal menghapus proyek [{project_id}]: {err}")
        raise HTTPException(status_code=500, detail=f"Gagal menghapus proyek: {err}") from err
