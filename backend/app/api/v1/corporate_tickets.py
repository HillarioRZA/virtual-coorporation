"""
Corporate Tickets REST API Endpoints.
Menyediakan antarmuka HTTP untuk manipulasi papan tugas Kanban multi-divisi.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.core.logger import logger
from app.db.ticket_repo import ticket_repo
from app.engine.schemas.corporate_schemas import TicketCreate, TicketResponse, TicketUpdate
from app.engine.runtime.event_bus import corporate_event_bus
from app.engine.schemas.corporate_schemas import CorporateMessageCreate

router = APIRouter(prefix="/corporate/tickets", tags=["Corporate Tickets & Kanban"])


@router.get("/{project_id}", response_model=List[TicketResponse])
async def list_project_tickets(
    project_id: str,
    branch_id: Optional[str] = Query(None, description="Filter branch"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter status kolom"),
    division_id: Optional[str] = Query(None, description="Filter divisi"),
) -> List[TicketResponse]:
    """Mengambil daftar seluruh tiket Kanban untuk proyek sasaran."""
    tickets = await ticket_repo.get_tickets(
        project_id=project_id,
        branch_id=branch_id,
        status=status_filter,
        division_id=division_id,
    )
    return [TicketResponse(**t) for t in tickets]


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_new_ticket(payload: TicketCreate) -> TicketResponse:
    """Membuat kartu tiket tugas baru pada papan Kanban."""
    try:
        created = await ticket_repo.create_ticket(
            branch_id=payload.branch_id,
            project_id=payload.project_id,
            division_id=payload.division_id,
            title=payload.title,
            description=payload.description,
            product_line=payload.product_line,
            priority=payload.priority,
            assigned_role_id=payload.assigned_role_id,
            dependencies=payload.dependencies,
            parent_ticket_id=payload.parent_ticket_id,
        )
        # Siarkan notifikasi pembuatan tiket ke Lounge Event Bus
        await corporate_event_bus.publish(
            CorporateMessageCreate(
                branch_id=payload.branch_id,
                project_id=payload.project_id,
                channel_type="LOUNGE",
                sender_role_id=payload.assigned_role_id or "system",
                ticket_id=created["id"],
                event_type="TASK_CREATED",
                content=f"Tiket baru [{created['id']}]: '{payload.title}' dibuat di kolom BACKLOG.",
            )
        )
        return TicketResponse(**created)
    except Exception as err:
        logger.error(f"Gagal membuat tiket: {err}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.post("/{ticket_id}/transition", response_model=TicketResponse)
async def transition_ticket(
    ticket_id: str,
    target_status: str = Query(..., description="BACKLOG, TODO, IN_PROGRESS, REVIEW, DONE"),
) -> TicketResponse:
    """Memindahkan tiket ke status / kolom Kanban yang baru."""
    valid_statuses = {"BACKLOG", "TODO", "IN_PROGRESS", "REVIEW", "DONE"}
    if target_status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Status tidak valid: {target_status}")

    updated = await ticket_repo.transition_ticket_status(ticket_id, target_status)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tiket '{ticket_id}' tidak ditemukan.")

    # Siarkan perpindahan status ke Event Bus
    await corporate_event_bus.publish(
        CorporateMessageCreate(
            branch_id=updated["branch_id"],
            project_id=updated["project_id"],
            channel_type="LOUNGE",
            sender_role_id=updated["assigned_role_id"] or "system",
            ticket_id=ticket_id,
            event_type="TASK_STATUS_CHANGED",
            content=f"Tiket [{ticket_id}] '{updated['title']}' berpindah status -> {target_status}.",
        )
    )
    return TicketResponse(**updated)


@router.delete("/{ticket_id}")
async def delete_ticket(ticket_id: str) -> Dict[str, Any]:
    """Menghapus kartu tiket dari papan Kanban."""
    success = await ticket_repo.delete_ticket(ticket_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tiket '{ticket_id}' tidak ditemukan.")
    return {"status": "success", "message": f"Tiket '{ticket_id}' berhasil dihapus."}


@router.post("/{project_id}/seed-initial", response_model=List[TicketResponse])
async def seed_initial_tickets(
    project_id: str,
    branch_id: str = Query("branch_main", description="Branch sasaran"),
) -> List[TicketResponse]:
    """Menginisialisasi tiket bawaan Tech Core (PRD, Arsitektur, Frontend, Backend, QA)."""
    tickets = await ticket_repo.seed_initial_project_tickets(project_id, branch_id=branch_id)
    return [TicketResponse(**t) for t in tickets]


@router.post("/{project_id}/dispatch")
async def dispatch_kanban_tickets(
    project_id: str,
    branch_id: str = Query("branch_main", description="Branch sasaran"),
) -> Dict[str, Any]:
    """Memicu pemindaian dan eksekusi otonom tiket TODO yang dependensinya telah selesai."""
    from app.engine.runtime.kanban_runner import kanban_runner
    dispatched = await kanban_runner.scan_and_dispatch_once(project_id, branch_id=branch_id)
    return {
        "status": "success",
        "project_id": project_id,
        "dispatched_count": len(dispatched),
        "dispatched_ticket_ids": dispatched,
    }
