"""
State Machine Routers & Gate Transition Rules.
Menentukan logika percabangan deterministik antar-tahap dan evaluasi keputusan CEO.
"""

from typing import Optional
from app.core.logger import logger
from app.engine.runtime.state import VentureState

VALID_GATE_DECISIONS = {"APPROVE", "REVISE", "KILL", "GO_PRODUCTION", "ITERATE"}


def router_sparring(state: VentureState) -> str:
    """Router transisi setelah node Sparring Room (CoS + CTO) selesai."""
    if state.business_brief and state.system_architecture:
        logger.info(f"Sparring selesai untuk [{state.project_id}]. Menuju GATE_1_WAITING.")
        return "GATE_1_WAITING"
    return "SPARRING_ROOM"


def router_gate_1(state: VentureState) -> str:
    """Router transisi untuk Stage-Gate 1 berdasarkan keputusan Founder/CEO."""
    decision = (state.gate_decision or "").upper().strip()

    if not decision:
        return "GATE_1_WAITING"

    if decision not in VALID_GATE_DECISIONS:
        raise ValueError(f"Invalid Gate 1 decision '{decision}'.")

    if decision in ["APPROVE", "GO_PRODUCTION"]:
        logger.info(f"Stage-Gate 1 APPROVED untuk [{state.project_id}]. Lanjut ke PRD_AND_SPECS.")
        return "PRD_AND_SPECS"
    elif decision in ["REVISE", "ITERATE"]:
        logger.info(f"Stage-Gate 1 REVISE diminta untuk [{state.project_id}]. Kembali ke SPARRING_ROOM.")
        return "SPARRING_ROOM"
    else:  # KILL
        logger.info(f"Stage-Gate 1 KILLED untuk [{state.project_id}]. Proyek dihentikan.")
        return "PROJECT_KILLED"


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
    """Router transisi untuk Stage-Gate 2 (CEO Demo Day).

    Keputusan:
        APPROVE / GO_PRODUCTION -> 'PRODUCTION_HARDENING'
        REVISE / ITERATE        -> 'MOCK_PROTOTYPING'
        KILL                    -> 'PROJECT_KILLED'
    """
    decision = (state.gate_decision or "").upper().strip()

    if not decision:
        return "GATE_2_WAITING"

    if decision not in VALID_GATE_DECISIONS:
        raise ValueError(f"Invalid Gate 2 decision '{decision}'.")

    if decision in ["APPROVE", "GO_PRODUCTION"]:
        logger.info(f"Stage-Gate 2 APPROVED untuk [{state.project_id}]. Lanjut ke PRODUCTION_HARDENING.")
        return "PRODUCTION_HARDENING"
    elif decision in ["REVISE", "ITERATE"]:
        logger.info(f"Stage-Gate 2 REVISE diminta untuk [{state.project_id}]. Kembali ke MOCK_PROTOTYPING.")
        return "MOCK_PROTOTYPING"
    else:  # KILL
        logger.info(f"Stage-Gate 2 KILLED untuk [{state.project_id}]. Proyek dihentikan.")
        return "PROJECT_KILLED"


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
    decision = (state.gate_decision or "REVISE").upper().strip()

    if decision not in VALID_GATE_DECISIONS:
        raise ValueError(f"Invalid Gate 3 decision '{decision}'.")

    if decision in ["APPROVE", "GO_PRODUCTION"]:
        logger.info(f"Stage-Gate 3 APPROVED untuk [{state.project_id}]. Lanjut ke DEPLOY_LIVE.")
        return "DEPLOY_LIVE"
    elif decision in ["REVISE", "ITERATE"]:
        logger.info(f"Stage-Gate 3 REVISE diminta untuk [{state.project_id}]. Kembali ke PRODUCTION_HARDENING.")
        return "PRODUCTION_HARDENING"
    else:  # KILL
        logger.info(f"Stage-Gate 3 KILLED untuk [{state.project_id}]. Proyek dihentikan.")
        return "PROJECT_KILLED"


def router_deploy_live(state: VentureState) -> str:
    """Router transisi setelah paket dideploy ke PaaS menuju observability live."""
    logger.info(f"Deployment Live selesai untuk [{state.project_id}]. Lanjut ke LIVE_OBSERVABILITY.")
    return "LIVE_OBSERVABILITY"
