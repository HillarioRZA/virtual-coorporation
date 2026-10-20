"""
Task Concurrency Dispatcher & DAG Orchestrator.
Mengeksekusi tugas-tugas independen (misal: Frontend dan Backend) secara paralel
menggunakan asyncio.gather() dan memancarkan status eksekusi ke CorporateEventBus.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

from app.core.logger import logger
from app.db.ticket_repo import ticket_repo
from app.engine.schemas.corporate_schemas import CorporateMessageCreate
from app.engine.runtime.event_bus import corporate_event_bus
from app.engine.memory.memory import MemoryManager
from app.engine.roles.dynamic_node import execute_dynamic_role_node
from app.engine.runtime.state import VentureState
from app.gateway.client import UnifiedLLMClient
from app.sandbox.proxy import ProxyManager
from app.sandbox.runner import SandboxManager


class TaskConcurrencyDispatcher:
    """Orkestrator konkurensi tugas independen berbasis Directed Acyclic Graph (DAG)."""

    async def dispatch_parallel_engineering(
        self,
        state: VentureState,
        branch_id: str = "branch_main",
        llm_client: Optional[UnifiedLLMClient] = None,
        memory_mgr: Optional[MemoryManager] = None,
        sandbox_mgr: Optional[SandboxManager] = None,
        proxy_mgr: Optional[ProxyManager] = None,
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Menjalankan sintesis Frontend dan Backend secara paralel (konkuren non-blocking).

        Args:
            state: Instance VentureState aktif.
            branch_id: ID branch alur kerja organisasi.
            llm_client: Gateway LLM terpadu opsional.
            memory_mgr: Manajer memori SQLite opsional.
            sandbox_mgr: Manajer sandbox opsional.
            proxy_mgr: Manajer reverse proxy opsional.
            custom_path: Path basis data khusus opsional.

        Returns:
            Dict hasil agregasi eksekusi termasuk durasi dan rasio efisiensi konkurensi.

        Raises:
            ValueError: Jika kontrak OpenAPI belum tersedia pada state.
        """
        if not state.openapi_spec:
            logger.error(f"Gagal dispatch paralel: OpenAPI Spec belum dikunci untuk {state.project_id}")
            raise ValueError("OpenAPI Spec belum tersedia. Jalankan tahap PRD terlebih dahulu.")

        start_time = time.perf_counter()
        logger.info(f"Memulai Parallel Engineering Dispatcher untuk proyek [{state.project_id}]...")

        # 1. Siarkan event tugas dimulai ke Event Bus
        await corporate_event_bus.publish(
            CorporateMessageCreate(
                branch_id=branch_id,
                project_id=state.project_id,
                channel_type="LOUNGE",
                sender_role_id="role_cto",
                event_type="TASK_STARTED",
                content="Memulai sintesis paralel: Frontend & Backend Engineer bekerja bersamaan.",
            ),
            custom_path=custom_path,
        )

        # 1b. Transisi tiket Kanban Frontend & Backend ke IN_PROGRESS
        try:
            current_tickets = await ticket_repo.get_tickets(state.project_id, branch_id=branch_id, custom_path=custom_path)
            for t in current_tickets:
                is_eng = t.get("division_id") == "div_eng" or t.get("assigned_role_id") in ("role_fe", "role_be")
                if is_eng and t["status"] in ("BACKLOG", "TODO"):
                    await ticket_repo.transition_ticket_status(t["id"], "IN_PROGRESS", custom_path=custom_path)
        except Exception as e:
            logger.debug(f"Pembaruan tiket dispatch: {e}")

        client = llm_client or UnifiedLLMClient()
        mem = memory_mgr or MemoryManager()
        sbx = sandbox_mgr or SandboxManager()
        proxy = proxy_mgr or ProxyManager()

        # 2. Definisikan coroutine paralel peran dinamis
        fe_coro = execute_dynamic_role_node(
            role_identifier="fe",
            state=state,
            llm_client=client,
            memory_mgr=mem,
            sandbox_mgr=sbx,
            proxy_mgr=proxy,
            custom_path=custom_path,
        )
        be_coro = execute_dynamic_role_node(
            role_identifier="be",
            state=state,
            llm_client=client,
            memory_mgr=mem,
            custom_path=custom_path,
        )

        # 3. Eksekusi bersamaan via asyncio.gather
        try:
            fe_result, be_result = await asyncio.gather(fe_coro, be_coro)
        except Exception as err:
            logger.error(f"Kegagalan pada eksekusi paralel engineering: {err}")
            await corporate_event_bus.publish(
                CorporateMessageCreate(
                    branch_id=branch_id,
                    project_id=state.project_id,
                    channel_type="LOUNGE",
                    sender_role_id="role_cto",
                    event_type="TEST_ALERT",
                    content=f"Eksekusi paralel gagal: {str(err)}",
                ),
                custom_path=custom_path,
            )
            raise

        elapsed = round(time.perf_counter() - start_time, 2)
        logger.info(f"Parallel Engineering selesai dalam {elapsed}s untuk [{state.project_id}]")

        # 4. Gabungkan updates ke state
        if fe_result and isinstance(fe_result, dict):
            for k, v in fe_result.items():
                if hasattr(state, k):
                    setattr(state, k, v)

        # 4b. Transisi tiket ke DONE beserta referensi artefak
        try:
            current_tickets = await ticket_repo.get_tickets(state.project_id, branch_id=branch_id, custom_path=custom_path)
            for t in current_tickets:
                if t["status"] == "IN_PROGRESS":
                    r_id = t.get("assigned_role_id", "").lower()
                    if "fe" in r_id or "frontend" in r_id:
                        await ticket_repo.transition_ticket_status(
                            t["id"], "DONE", artifact_refs=[f"projects_output/{state.project_id}/frontend"], custom_path=custom_path
                        )
                    elif "be" in r_id or "backend" in r_id:
                        await ticket_repo.transition_ticket_status(
                            t["id"], "DONE", artifact_refs=[f"projects_output/{state.project_id}/backend"], custom_path=custom_path
                        )
                    elif t.get("division_id") == "div_eng":
                        await ticket_repo.transition_ticket_status(
                            t["id"], "DONE", artifact_refs=[f"projects_output/{state.project_id}/code"], custom_path=custom_path
                        )
        except Exception as e:
            logger.debug(f"Pembaruan tiket selesai: {e}")

        # 5. Siarkan event konvergensi sinkronisasi artefak
        await corporate_event_bus.publish(
            CorporateMessageCreate(
                branch_id=branch_id,
                project_id=state.project_id,
                channel_type="LOUNGE",
                sender_role_id="role_cto",
                event_type="TASK_COMPLETED",
                content=f"Frontend & Backend siap dalam {elapsed}s. Artefak siap untuk audit QA & SecOps.",
            ),
            custom_path=custom_path,
        )

        return {
            "status": "success",
            "elapsed_seconds": elapsed,
            "preview_url": state.preview_url,
            "project_id": state.project_id,
        }


task_dispatcher = TaskConcurrencyDispatcher()
