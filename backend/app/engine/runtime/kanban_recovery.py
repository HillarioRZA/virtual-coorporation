"""
Kanban Ticket Execution and Checkpoint Recovery Subsystem.
Menangani siklus percobaan eksekusi tiket dengan checkpoint recovery
dan injeksi log diagnostik kontainer runtime saat terjadi kegagalan.
"""

from typing import Any, Dict, Optional, Tuple
from app.core.logger import logger
from app.engine.memory.memory import MemoryManager
from app.engine.roles.dynamic_node import execute_dynamic_role_node
from app.engine.runtime.state import VentureState
from app.sandbox.log_collector import sandbox_log_collector


async def execute_ticket_with_recovery(
    ticket: Dict[str, Any],
    custom_path: Optional[str] = None,
    max_retries: int = 2,
) -> Tuple[bool, VentureState, Optional[Exception]]:
    """
    Mengeksekusi node peran dengan mekanisme retry checkpoint recovery.
    Mengembalikan (success: bool, final_state: VentureState, last_error: Optional[Exception]).
    """
    ticket_id = ticket["id"]
    role_id = ticket.get("assigned_role_id", "role_be")
    project_id = ticket.get("project_id", "default_proj")
    title = ticket.get("title", "Tugas Kanban")

    mem = MemoryManager(db_path=custom_path)
    state = await mem.load_latest_checkpoint(project_id)
    if not state:
        state = VentureState(project_id=project_id, project_name=title, founder_idea=title)

    current_attempt = 0
    success = False
    last_err: Optional[Exception] = None
    working_ticket = dict(ticket)

    while current_attempt <= max_retries and not success:
        try:
            await execute_dynamic_role_node(
                role_identifier=role_id,
                state=state,
                ticket_context=working_ticket,
                memory_mgr=mem,
                custom_path=custom_path,
            )
            await mem.save_checkpoint(state)
            success = True
            last_err = None
        except Exception as err:
            last_err = err
            current_attempt += 1
            logger.warning(f"Percobaan ke-{current_attempt} tiket [{ticket_id}] gagal: {err}")
            if current_attempt <= max_retries:
                service_target = "frontend" if "fe" in role_id.lower() or "front" in role_id.lower() else "backend"
                runtime_logs = await sandbox_log_collector.build_runtime_error_context(project_id, service=service_target)
                repair_desc = (
                    f"{ticket.get('description', '')}\n\n"
                    f"[PERBAIKAN CHECKPOINT ITERASI {current_attempt}]:\nError sebelumnya: {err}"
                )
                if runtime_logs:
                    repair_desc += f"\n\n{runtime_logs}"
                working_ticket["description"] = repair_desc
                restored = await mem.load_latest_checkpoint(project_id)
                if restored:
                    state = restored

    return success, state, last_err
