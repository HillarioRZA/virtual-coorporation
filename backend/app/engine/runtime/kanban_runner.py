"""
Autonomous Kanban Task Runner Subsystem.
Memindai papan tugas virtual, memeriksa ketergantungan DAG tiket,
dan mengeksekusi tiket berstatus 'TODO' secara otonom dengan claim atomik SQLite.
"""

import asyncio
from typing import Any, Dict, List, Optional, Set
from app.core.logger import logger

from app.db.session import get_db_connection
from app.db.ticket_repo import ticket_repo
from app.engine.runtime.event_bus import corporate_event_bus
from app.engine.schemas.corporate_schemas import CorporateMessageCreate


class AutonomousKanbanRunner:
    """Runner otonom untuk mengeksekusi antrean tiket Kanban tanpa intervensi manual."""

    def __init__(self, max_concurrency: int = 3, poll_interval_sec: float = 2.0) -> None:
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.poll_interval = poll_interval_sec
        self.active_ticket_ids: Set[str] = set()
        self._is_running = False
        self._runner_task: Optional[asyncio.Task] = None

    async def are_dependencies_met(self, ticket: Dict[str, Any], project_id: str, custom_path: Optional[str] = None) -> bool:
        """Memeriksa apakah semua ID tiket prasyarat berstatus 'DONE'."""
        deps: List[str] = ticket.get("dependencies", [])
        if not deps:
            return True

        for dep_id in deps:
            dep_ticket = await ticket_repo.get_ticket_by_id(dep_id, custom_path)
            if not dep_ticket or dep_ticket.get("status") != "DONE":
                return False
        return True

    async def _publish_bus_event(
        self, branch_id: str, project_id: str, role_id: str, ticket_id: str, event_type: str, content: str
    ) -> None:
        """Helper untuk menyiarkan event eksekusi tiket ke event bus."""
        try:
            await corporate_event_bus.publish(
                CorporateMessageCreate(
                    branch_id=branch_id,
                    project_id=project_id,
                    channel_type="EXECUTION",
                    sender_role_id=role_id,
                    ticket_id=ticket_id,
                    event_type=event_type,
                    content=content,
                )
            )
        except Exception as b_err:
            logger.debug(f"Event bus publish ({event_type}) dilewati: {b_err}")

    async def execute_ticket(self, ticket: Dict[str, Any], custom_path: Optional[str] = None) -> bool:
        """Mengeksekusi satu tiket secara mandiri dengan perlindungan semafor dan lock."""
        ticket_id = ticket["id"]
        role_id = ticket.get("assigned_role_id", "role_be")
        project_id = ticket.get("project_id", "default_proj")
        branch_id = ticket.get("branch_id", "branch_main")
        title = ticket.get("title", "Tugas Kanban")

        async with self.semaphore:
            self.active_ticket_ids.add(ticket_id)
            logger.info(f"Memulai eksekusi otonom tiket [{ticket_id}] oleh peran @{role_id}")
            await self._publish_bus_event(branch_id, project_id, role_id, ticket_id, "TASK_STARTED", f"@{role_id} mulai mengeksekusi tiket [{ticket_id}]: '{title}'")
            try:
                from app.engine.runtime.kanban_recovery import execute_ticket_with_recovery
                success, state, last_err = await execute_ticket_with_recovery(ticket, custom_path=custom_path)

                if success:
                    art_refs = [f"artifact_{role_id}"]
                    if state.artifacts and role_id in state.artifacts:
                        art_refs.append(f"artifact_{role_id}_{ticket_id}")

                    await ticket_repo.transition_ticket_status(
                        ticket_id=ticket_id,
                        new_status="DONE",
                        artifact_refs=art_refs,
                        custom_path=custom_path,
                    )
                    logger.info(f"Tiket [{ticket_id}] sukses dieksekusi -> DONE")

                    # Git Exporter otomatis pada status DONE
                    try:
                        from app.engine.tools.git_exporter import git_exporter
                        await git_exporter.export_project_checkpoint(
                            project_id=project_id,
                            commit_message=f"feat(kanban): resolve ticket [{ticket_id}] - {title}",
                        )
                    except Exception as g_err:
                        logger.debug(f"Git export saat ticket DONE dilewati: {g_err}")

                    await self._publish_bus_event(branch_id, project_id, role_id, ticket_id, "TASK_COMPLETED", f"Tiket [{ticket_id}] '{title}' selesai oleh @{role_id} -> DONE.")
                    return True
                else:
                    logger.error(f"Kegagalan total eksekusi tiket [{ticket_id}] setelah {max_retries} perbaikan: {last_err}")
                    await ticket_repo.transition_ticket_status(ticket_id=ticket_id, new_status="FAILED", custom_path=custom_path)
                    await self._publish_bus_event(branch_id, project_id, role_id, ticket_id, "TASK_FAILED", f"Eksekusi tiket [{ticket_id}] gagal: {last_err}")
                    return False
            finally:
                self.active_ticket_ids.discard(ticket_id)

    async def scan_and_dispatch_once(
        self,
        project_id: Optional[str] = None,
        branch_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> List[str]:
        """Melakukan satu siklus pemindaian tiket siap jalan dan mendistribusikan eksekusi."""
        dispatched_ids: List[str] = []
        if project_id:
            targets = [(project_id, branch_id)]
        else:
            try:
                async with get_db_connection(custom_path) as conn:
                    cur = await conn.execute("SELECT DISTINCT project_id, branch_id FROM corporate_tickets WHERE status = 'TODO';")
                    rows = await cur.fetchall()
                    targets = [(r["project_id"], r["branch_id"]) for r in rows]
            except Exception as err:
                logger.debug(f"Gagal memindai target tiket TODO: {err}")
                targets = []

        for p_id, b_id in targets:
            todo_tickets = await ticket_repo.get_tickets(project_id=p_id, branch_id=b_id, status="TODO", custom_path=custom_path)
            for t in todo_tickets:
                t_id = t["id"]
                if t_id in self.active_ticket_ids or not await self.are_dependencies_met(t, p_id, custom_path):
                    continue
                claimed = await ticket_repo.claim_ticket_atomic(t_id, custom_path)
                if claimed:
                    dispatched_ids.append(t_id)
                    asyncio.create_task(self.execute_ticket(claimed, custom_path))

        return dispatched_ids

    async def _loop(
        self,
        project_id: Optional[str] = None,
        branch_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> None:
        """Loop latar belakang untuk polling tugas secara berkala."""
        while self._is_running:
            try:
                await self.scan_and_dispatch_once(project_id, branch_id, custom_path)
            except Exception as err:
                logger.error(f"Error pada loop Kanban Runner: {err}")
            await asyncio.sleep(self.poll_interval)

    def start_background_runner(
        self,
        project_id: Optional[str] = None,
        branch_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> None:
        """Memulai runner latar belakang untuk seluruh proyek atau proyek spesifik."""
        if self._is_running:
            return
        self._is_running = True
        self._runner_task = asyncio.create_task(self._loop(project_id, branch_id, custom_path))
        target_name = f"proyek [{project_id}]" if project_id else "seluruh proyek aktif"
        logger.info(f"Autonomous Kanban Runner aktif untuk {target_name}.")

    def stop_background_runner(self) -> None:
        """Menghentikan runner latar belakang."""
        self._is_running = False
        if self._runner_task:
            self._runner_task.cancel()
            self._runner_task = None
        logger.info("Autonomous Kanban Runner dihentikan.")


kanban_runner = AutonomousKanbanRunner()
