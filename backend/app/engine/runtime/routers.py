"""
State Machine Routers & Table-Driven Gate Transition Rules.
Menentukan logika transisi deterministik antar-tahap siklus hidup ventura
dan evaluasi keputusan CEO berbasis Transition Table Matrix O(1).
"""

from typing import Dict, Optional, Tuple
from app.core.logger import logger
from app.engine.runtime.state import VentureState

VALID_GATE_DECISIONS = {"APPROVE", "REVISE", "KILL", "GO_PRODUCTION", "ITERATE"}

GATE_TRANSITION_TABLE: Dict[Tuple[str, str], str] = {
    # Gate 1: Kelayakan Bisnis & Arsitektur Sistem
    ("GATE_1_WAITING", "APPROVE"): "PRD_AND_SPECS",
    ("GATE_1_WAITING", "GO_PRODUCTION"): "PRD_AND_SPECS",
    ("GATE_1_WAITING", "REVISE"): "SPARRING_ROOM",
    ("GATE_1_WAITING", "ITERATE"): "SPARRING_ROOM",
    ("GATE_1_WAITING", "KILL"): "PROJECT_KILLED",

    # Gate 2: Purwarupa Visual UI & Mock Next.js
    ("GATE_2_WAITING", "APPROVE"): "PRODUCTION_HARDENING",
    ("GATE_2_WAITING", "GO_PRODUCTION"): "PRODUCTION_HARDENING",
    ("GATE_2_WAITING", "REVISE"): "MOCK_PROTOTYPING",
    ("GATE_2_WAITING", "ITERATE"): "MOCK_PROTOTYPING",
    ("GATE_2_WAITING", "KILL"): "PROJECT_KILLED",

    # Gate 3: Pra-Rilis Produksi, Brankas Kredensial & PaaS Deploy
    ("GATE_3_WAITING", "APPROVE"): "DEPLOY_LIVE",
    ("GATE_3_WAITING", "GO_PRODUCTION"): "DEPLOY_LIVE",
    ("GATE_3_WAITING", "REVISE"): "PRODUCTION_HARDENING",
    ("GATE_3_WAITING", "ITERATE"): "PRODUCTION_HARDENING",
    ("GATE_3_WAITING", "KILL"): "PROJECT_KILLED",
}


def evaluate_gate_transition(current_gate: str, decision: Optional[str]) -> str:
    """Mengevaluasi keputusan stage-gate secara deterministik berbasis Transition Table Matrix O(1).

    Args:
        current_gate: Nama tahap gerbang saat ini (e.g. 'GATE_1_WAITING').
        decision: Keputusan Founder/CEO ('APPROVE', 'REVISE', 'KILL', dll).

    Returns:
        Nama tahap berikutnya yang dituju.

    Raises:
        ValueError: Jika keputusan yang diberikan tidak terdaftar di VALID_GATE_DECISIONS.
    """
    if not decision:
        return current_gate

    action = decision.upper().strip()
    if action not in VALID_GATE_DECISIONS:
        raise ValueError(f"Invalid Gate decision '{decision}'. Must be one of {VALID_GATE_DECISIONS}")

    next_state = GATE_TRANSITION_TABLE.get((current_gate, action))
    if not next_state:
        return current_gate

    logger.info(f"Stage-Gate [{current_gate}] diputuskan [{action}] -> Transisi ke [{next_state}].")
    return next_state


def router_sparring(state: VentureState) -> str:
    """Router transisi setelah node Sparring Room (CoS + CTO) selesai."""
    if state.business_brief and state.system_architecture:
        logger.info(f"Sparring selesai untuk [{state.project_id}]. Menuju GATE_1_WAITING.")
        return "GATE_1_WAITING"
    return "SPARRING_ROOM"


def router_gate_1(state: VentureState) -> str:
    """Router transisi untuk Stage-Gate 1 berdasarkan keputusan Founder/CEO."""
    return evaluate_gate_transition("GATE_1_WAITING", state.gate_decision)


def router_prd_and_specs(state: VentureState) -> str:
    """Router transisi setelah PRD dan UI Spec selesai dirancang."""
    if state.prd_spec and state.ui_spec and state.openapi_spec:
        logger.info(f"Spesifikasi lengkap untuk [{state.project_id}]. Lanjut ke MOCK_PROTOTYPING.")
        return "MOCK_PROTOTYPING"
    return "PRD_AND_SPECS"


def router_mock_prototyping(state: VentureState) -> str:
    """Router transisi setelah prototipe Next.js selesai termount ke sandbox."""
    if state.preview_url:
        logger.info(f"Preview aktif untuk [{state.project_id}]. Menuju GATE_2_WAITING.")
        return "GATE_2_WAITING"
    return "MOCK_PROTOTYPING"


def router_gate_2(state: VentureState) -> str:
    """Router transisi untuk Stage-Gate 2 (CEO Demo Day)."""
    return evaluate_gate_transition("GATE_2_WAITING", state.gate_decision)


def apply_gate_decision(
    state: VentureState,
    action: str,
    feedback: Optional[str] = None,
) -> VentureState:
    """Menerapkan keputusan dan feedback CEO ke dalam VentureState."""
    act = action.upper().strip()
    if act not in VALID_GATE_DECISIONS:
        raise ValueError(f"Invalid gate action '{action}'. Must be one of {VALID_GATE_DECISIONS}")

    state.gate_decision = act
    state.gate_feedback = feedback
    state.record_event(f"CEO Gate Decision: [{act}] - Feedback: {feedback or 'None'}")
    return state


def router_production_hardening(state: VentureState) -> str:
    """Router transisi setelah fase Production Hardening selesai menuju Stage-Gate 3."""
    logger.info(f"Production Hardening selesai untuk [{state.project_id}]. Lanjut ke GATE_3_WAITING.")
    return "GATE_3_WAITING"


def router_gate_3(state: VentureState) -> str:
    """Evaluasi deterministik keputusan Founder pada Stage-Gate 3 (Vault Injection & PaaS Deploy)."""
    return evaluate_gate_transition("GATE_3_WAITING", state.gate_decision or "REVISE")


def router_deploy_live(state: VentureState) -> str:
    """Router transisi setelah paket dideploy ke PaaS menuju observability live."""
    logger.info(f"Deployment Live selesai untuk [{state.project_id}]. Lanjut ke LIVE_OBSERVABILITY.")
    return "LIVE_OBSERVABILITY"
