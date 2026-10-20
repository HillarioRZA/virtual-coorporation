"""
Autonomous Kanban Task Runner Subsystem.
Memindai papan tugas virtual, memeriksa ketergantungan DAG tiket,
dan mengeksekusi tiket berstatus 'TODO' secara otonom dengan claim atomik SQLite.
"""

import asyncio
from typing import Any, Dict, List, Optional, Set
from loguru import logger

from app.db.ticket_repo import ticket_repo
from app.engine.runtime.state import VentureState
from app.engine.roles.dynamic_node import execute_dynamic_role_node


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

    async def execute_ticket(
        self,
        ticket: Dict[str, Any],
        custom_path: Optional[str] = None,
    ) -> bool:
        """Mengeksekusi satu tiket secara mandiri dengan perlindungan semafor dan lock."""
        ticket_id = ticket["id"]
        role_id = ticket.get("assigned_role_id", "backend")
        project_id = ticket.get("project_id", "default_proj")

        async with self.semaphore:
            self.active_ticket_ids.add(ticket_id)
            logger.info(f"Memulai eksekusi otonom tiket [{ticket_id}] oleh peran @{role_id}")
            try:
                from app.engine.memory.memory import MemoryManager
                mem = MemoryManager(db_path=custom_path)
                state = await mem.load_latest_checkpoint(project_id)
                if not state:
                    state = VentureState(project_id=project_id, project_name=ticket.get("title", ""))

                # Eksekusi peran dinamis dengan context memory
                out = await execute_dynamic_role_node(role_identifier=role_id, state=state, memory_mgr=mem)

                # Persistensikan snapshot checkpoint terkini
                await mem.save_checkpoint(state)

                # Kumpulkan referensi artefak dinamis
                art_refs = [f"artifact_{role_id}"]
                if state.artifacts and role_id in state.artifacts:
                    art_refs.append(f"artifact_{role_id}_{ticket_id}")

                # Tandai selesai
                await ticket_repo.transition_ticket_status(
                    ticket_id=ticket_id,
                    new_status="DONE",
                    artifact_refs=art_refs,
                    custom_path=custom_path,
                )
                logger.info(f"Tiket [{ticket_id}] sukses dieksekusi -> DONE")
                return True
            except Exception as err:
                logger.error(f"Kegagalan eksekusi tiket [{ticket_id}]: {err}")
                await ticket_repo.transition_ticket_status(
                    ticket_id=ticket_id,
                    new_status="FAILED",
                    custom_path=custom_path,
                )
                return False
            finally:
                self.active_ticket_ids.discard(ticket_id)

    async def scan_and_dispatch_once(
        self,
        project_id: str,
        branch_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> List[str]:
        """Melakukan satu siklus pemindaian tiket siap jalan dan mendistribusikan eksekusi."""
        todo_tickets = await ticket_repo.get_tickets(
            project_id=project_id,
            branch_id=branch_id,
            status="TODO",
            custom_path=custom_path,
        )

        dispatched_ids: List[str] = []
        for t in todo_tickets:
            t_id = t["id"]
            if t_id in self.active_ticket_ids:
                continue

            if not await self.are_dependencies_met(t, project_id, custom_path):
                continue

            # Atomic Claim
            claimed = await ticket_repo.claim_ticket_atomic(t_id, custom_path)
            if claimed:
                dispatched_ids.append(t_id)
                asyncio.create_task(self.execute_ticket(claimed, custom_path))

        return dispatched_ids

    async def _loop(self, project_id: str, branch_id: Optional[str] = None, custom_path: Optional[str] = None) -> None:
        """Loop latar belakang untuk polling tugas secara berkala."""
        while self._is_running:
            try:
                await self.scan_and_dispatch_once(project_id, branch_id, custom_path)
            except Exception as err:
                logger.error(f"Error pada loop Kanban Runner: {err}")
            await asyncio.sleep(self.poll_interval)

    def start_background_runner(self, project_id: str, branch_id: Optional[str] = None, custom_path: Optional[str] = None) -> None:
        """Memulai runner latar belakang."""
        if self._is_running:
            return
        self._is_running = True
        self._runner_task = asyncio.create_task(self._loop(project_id, branch_id, custom_path))
        logger.info(f"Autonomous Kanban Runner aktif untuk project [{project_id}].")

    def stop_background_runner(self) -> None:
        """Menghentikan runner latar belakang."""
        self._is_running = False
        if self._runner_task:
            self._runner_task.cancel()
            self._runner_task = None
        logger.info("Autonomous Kanban Runner dihentikan.")


kanban_runner = AutonomousKanbanRunner()
