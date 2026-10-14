"""
Unit Tests untuk Native Asynchronous State Machine Engine.
Menguji registrasi node, perutean transisi state, checkpointer, dan circuit breaker.
"""

from typing import Any, Dict
import pytest
from app.engine.state import VentureState
from app.engine.state_machine import NativeStateMachine


@pytest.mark.asyncio
async def test_state_machine_step_and_transition() -> None:
    """Menguji eksekusi single step dan transisi router antar state."""
    fsm = NativeStateMachine()

    # Daftarkan node dummy
    async def node_init(state: VentureState) -> Dict[str, Any]:
        return {"project_name": "Validated Name"}

    async def node_sparring(state: VentureState) -> Dict[str, Any]:
        return {"selected_archetype": 2}

    fsm.register_node("INIT", node_init)
    fsm.register_router("INIT", lambda s: "SPARRING_ROOM")

    fsm.register_node("SPARRING_ROOM", node_sparring)
    fsm.register_router("SPARRING_ROOM", lambda s: "GATE_1_WAITING")

    # Inisialisasi state
    state = VentureState(
        project_id="proj_test_fsm",
        project_name="Initial Name",
        stage="INIT",
        founder_idea="Autonomous Agent Workflow",
        selected_archetype=1,
    )

    # Step 1: INIT -> SPARRING_ROOM
    state = await fsm.step(state)
    assert state.project_name == "Validated Name"
    assert state.stage == "SPARRING_ROOM"

    # Step 2: SPARRING_ROOM -> GATE_1_WAITING
    state = await fsm.step(state)
    assert state.selected_archetype == 2
    assert state.stage == "GATE_1_WAITING"


@pytest.mark.asyncio
async def test_state_machine_checkpointer_called() -> None:
    """Menguji bahwa checkpointer callback terpanggil pada setiap langkah."""
    checkpoint_calls = []

    async def mock_checkpointer(state: VentureState) -> None:
        checkpoint_calls.append(state.stage)

    fsm = NativeStateMachine(checkpointer=mock_checkpointer)

    async def dummy_node(state: VentureState) -> Dict[str, Any]:
        return {}

    fsm.register_node("SPARRING_ROOM", dummy_node)
    fsm.register_router("SPARRING_ROOM", lambda s: "GATE_1_WAITING")

    state = VentureState(
        project_id="proj_test_ckpt",
        project_name="Test",
        stage="SPARRING_ROOM",
        founder_idea="Idea",
    )

    await fsm.step(state)
    assert len(checkpoint_calls) == 1
    assert checkpoint_calls[0] == "GATE_1_WAITING"


@pytest.mark.asyncio
async def test_unregistered_state_raises_value_error() -> None:
    """Menguji bahwa state yang tidak terdaftar melempar ValueError."""
    fsm = NativeStateMachine()
    state = VentureState(
        project_id="proj_test_err",
        project_name="Test",
        stage="UNKNOWN_STATE",
        founder_idea="Idea",
    )

    with pytest.raises(ValueError) as exc_info:
        await fsm.step(state)
    assert "is not registered" in str(exc_info.value)


@pytest.mark.asyncio
async def test_run_until_gate_stops_at_terminal_state() -> None:
    """Menguji fungsi run_until_gate berhenti otomatis saat mencapai gerbang CEO."""
    fsm = NativeStateMachine()

    async def step_a(state: VentureState) -> Dict[str, Any]:
        return {}

    async def step_b(state: VentureState) -> Dict[str, Any]:
        return {}

    fsm.register_node("STEP_A", step_a)
    fsm.register_router("STEP_A", lambda s: "STEP_B")

    fsm.register_node("STEP_B", step_b)
    fsm.register_router("STEP_B", lambda s: "GATE_1_WAITING")

    state = VentureState(
        project_id="proj_test_loop",
        project_name="Test Loop",
        stage="STEP_A",
        founder_idea="Idea",
    )

    final_state = await fsm.run_until_gate(state, max_steps=5)
    assert final_state.stage == "GATE_1_WAITING"
