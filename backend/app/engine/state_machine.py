"""
Native Asynchronous State Machine Engine.
Mengorkestrasikan transisi state deterministik antar-node agen tanpa framework pihak ketiga.
"""

from typing import Any, Awaitable, Callable, Dict, List, Optional

from app.core.logger import logger
from app.engine.state import VentureState

NodeHandler = Callable[[VentureState], Awaitable[Dict[str, Any]]]
RouterHandler = Callable[[VentureState], str]
CheckpointerHandler = Callable[[VentureState], Awaitable[None]]


class NativeStateMachine:
    """Core Finite State Machine (FSM) untuk eksekusi multi-agen otonom."""

    def __init__(self, checkpointer: Optional[CheckpointerHandler] = None) -> None:
        """Inisialisasi engine state machine.

        Args:
            checkpointer: Fungsi async opsional untuk menyimpan snapshot state.
        """
        self.nodes: Dict[str, NodeHandler] = {}
        self.routers: Dict[str, RouterHandler] = {}
        self.checkpointer: Optional[CheckpointerHandler] = checkpointer

    def register_node(self, state_name: str, handler: NodeHandler) -> None:
        """Mendaftarkan fungsi handler untuk sebuah state.

        Args:
            state_name: Nama status (e.g. 'SPARRING_ROOM', 'PRD_AND_SPECS').
            handler: Fungsi async yang mengembalikan dict update atribut.
        """
        self.nodes[state_name] = handler
        logger.debug(f"Node terdaftar: [{state_name}]")

    def register_router(self, state_name: str, router_func: RouterHandler) -> None:
        """Mendaftarkan fungsi penentu state berikutnya setelah node selesai dieksekusi.

        Args:
            state_name: Nama status asal.
            router_func: Fungsi sinkron penentu nama state tujuan.
        """
        self.routers[state_name] = router_func
        logger.debug(f"Router terdaftar untuk state: [{state_name}]")

    def set_checkpointer(self, checkpointer: CheckpointerHandler) -> None:
        """Menyetel atau mengganti handler checkpointer persistence."""
        self.checkpointer = checkpointer

    async def step(self, state: VentureState) -> VentureState:
        """Mengeksekusi satu langkah node saat ini dan melakukan transisi state.

        Args:
            state: Instance VentureState aktif.

        Returns:
            VentureState yang telah diperbarui.

        Raises:
            ValueError: Jika stage saat ini tidak terdaftar di daftar node.
            RuntimeError: Jika eksekusi handler node mengalami kegagalan.
        """
        current_stage = state.stage
        if current_stage not in self.nodes:
            logger.error(f"State '{current_stage}' belum terdaftar di State Machine.")
            raise ValueError(f"State '{current_stage}' is not registered.")

        logger.info(f"FSM Executing Step: [{current_stage}] | Project: {state.project_id}")

        try:
            handler = self.nodes[current_stage]
            updates = await handler(state)
        except Exception as err:
            logger.error(f"Gagal mengeksekusi node [{current_stage}]: {err}")
            raise RuntimeError(f"Error during node [{current_stage}] execution: {err}") from err

        if updates and isinstance(updates, dict):
            for key, val in updates.items():
                if hasattr(state, key):
                    setattr(state, key, val)

        if current_stage in self.routers:
            next_stage = self.routers[current_stage](state)
            logger.info(f"FSM Transition: [{current_stage}] -> [{next_stage}]")
            state.stage = next_stage

        if self.checkpointer:
            try:
                await self.checkpointer(state)
            except Exception as checkpoint_err:
                logger.warning(f"Gagal menyimpan checkpoint untuk project {state.project_id}: {checkpoint_err}")

        return state

    async def run_until_gate(
        self,
        state: VentureState,
        stop_states: Optional[List[str]] = None,
        max_steps: int = 10,
    ) -> VentureState:
        """Mengeksekusi FSM secara berantai hingga mencapai gerbang keputusan atau limit.

        Args:
            state: Instance VentureState aktif.
            stop_states: Daftar nama state untuk berhenti menunggu aksi manusia.
            max_steps: Batas maksimal langkah (Circuit Breaker anti-infinite loop).

        Returns:
            VentureState pada status terakhir.
        """
        terminal_states = stop_states or [
            "GATE_1_WAITING",
            "GATE_2_WAITING",
            "GATE_3_WAITING",
            "PROJECT_KILLED",
            "LIVE_OBSERVABILITY",
        ]
        step_count = 0

        while state.stage not in terminal_states and step_count < max_steps:
            state = await self.step(state)
            step_count += 1

        if step_count >= max_steps and state.stage not in terminal_states:
            logger.warning(f"Circuit Breaker Triggered: max_steps ({max_steps}) reached for {state.project_id}")

        return state
