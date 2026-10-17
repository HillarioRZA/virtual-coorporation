"""
Real-Time Activity Simulation Engine for Corporate Oasis Command HQ.
Mengelola status aktivitas kognitif agen, transisi state, dan translasi event bus korporat.
"""

from typing import Any, Dict, Optional
from app.core.logger import logger
from app.engine.office_layout import SpatialTier, get_canonical_campus_layout


class AgentSpatialState:
    """Status kognitif dan aktivitas satu agen di markas korporat."""

    def __init__(
        self,
        role_id: str,
        name: str,
        tier: SpatialTier,
        color: str = "#06b6d4",
    ) -> None:
        """Inisialisasi atribut identitas dan status awal agen."""
        self.role_id = role_id
        self.name = name
        self.tier = tier
        self.activity_state = "IDLE"  # IDLE, CODING, REVIEWING, MEETING, CONSULTING, BLOCKED
        self.active_file = ""
        self.scratchpad = "Standby menunggu delegasi tiket..."
        self.speech_bubble: Optional[str] = None
        self.color = color

    def to_dict(self) -> Dict[str, Any]:
        """Konversi state ke dictionary untuk payload API dan WebSocket."""
        return {
            "role_id": self.role_id,
            "name": self.name,
            "tier": self.tier.value,
            "activity_state": self.activity_state,
            "active_file": self.active_file,
            "scratchpad": self.scratchpad,
            "speech_bubble": self.speech_bubble,
            "color": self.color,
        }


class OfficeSimulatorEngine:
    """Mesin pengelola state kehadiran dan reaktivitas event bus agen kantor korporat."""

    def __init__(self) -> None:
        """Inisialisasi registry agen berdasarkan skema layout kanonikal."""
        self.layout = get_canonical_campus_layout()
        self.agents: Dict[str, AgentSpatialState] = {}
        self._init_agents_from_layout()

    def _init_agents_from_layout(self) -> None:
        """Membangun registry agen dari workstation yang didefinisikan pada layout."""
        for wing in self.layout.get("wings", []):
            tier = SpatialTier(wing.get("tier", "WORKER_SPECIALIST"))
            color = wing.get("color", "#06b6d4")
            for item in wing.get("furniture", []):
                role = item.get("assigned_role")
                if role:
                    name = item.get("label", role).replace(" Desk", "").replace(" Pod", "").replace(" Workstation", "")
                    self.agents[role] = AgentSpatialState(
                        role_id=role,
                        name=name,
                        tier=tier,
                        color=color,
                    )

    def handle_bus_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Menerjemahkan event bus korporat menjadi mutasi aktivitas dan status agen."""
        role_id = payload.get("role_id")
        agent = self.agents.get(role_id) if role_id else None

        if event_type == "TASK_STARTED" and agent:
            agent.activity_state = "CODING"
            agent.active_file = payload.get("target_file", "synthesis.py")
            agent.scratchpad = f"Menulis kode untuk tiket: {payload.get('ticket_id', 'T-ACTIVE')}"
            agent.speech_bubble = "💻 Coding..."
        elif event_type in ("STAGE_GATE_TRIGGERED", "CALL_MEETING"):
            for a in self.agents.values():
                a.activity_state = "MEETING"
                a.speech_bubble = "🏛️ All-Hands Meeting"
        elif event_type == "CONSULT_ROLE" and agent:
            agent.activity_state = "CONSULTING"
            agent.speech_bubble = "☕ Diskusi di Oasis..."
            agent.scratchpad = f"Konsultasi inter-agen terkait tiket {payload.get('ticket_id', 'aktif')}..."
        elif event_type == "CIRCUIT_BREAKER_TRIGGERED" and agent:
            agent.activity_state = "BLOCKED"
            agent.speech_bubble = "⚠️ Circuit Breaker!"
            agent.scratchpad = f"Terkunci: {payload.get('reason', 'Safety Guardrail Violation')}"
        elif event_type == "TASK_COMPLETED" and agent:
            agent.activity_state = "IDLE"
            agent.active_file = ""
            agent.speech_bubble = "✅ Selesai"

    def step_simulation(self) -> None:
        """Melakukan siklus pembaruan detak simulasi (heartbeat tick)."""
        for a in self.agents.values():
            if a.activity_state == "CONSULTING":
                a.activity_state = "IDLE"
                a.speech_bubble = None

    def intervene_agent(self, role_id: str, instruction: str) -> Dict[str, Any]:
        """Menyuntikkan instruksi langsung Founder ke agen tertentu."""
        agent = self.agents.get(role_id)
        if not agent:
            return {"status": "ERROR", "message": f"Agen [{role_id}] tidak ditemukan."}

        agent.scratchpad = f"Instruksi CEO: {instruction}"
        agent.speech_bubble = "📢 Instruksi Diterima!"
        agent.activity_state = "CODING"
        logger.info(f"Intervensi Founder diterapkan pada [{role_id}]: {instruction}")
        return {"status": "SUCCESS", "role_id": role_id, "agent": agent.to_dict()}

    def get_snapshot(self) -> Dict[str, Any]:
        """Mengambil snapshot seluruh state aktivitas agen dan layout zonasi kampus."""
        return {
            "layout": self.layout,
            "agents": [a.to_dict() for a in self.agents.values()],
        }


office_sim_engine = OfficeSimulatorEngine()
