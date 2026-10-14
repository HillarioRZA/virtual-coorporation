"""
Real-Time Spatial Simulation Engine for Corporate Office HQ.
Mengelola status aktivitas spasial agen, interpolasi pergerakan, dan translasi event bus.
"""

import asyncio
from typing import Any, Dict, List, Optional
from app.core.logger import logger
from app.engine.office_layout import get_canonical_campus_layout, SpatialTier


class AgentSpatialState:
    """Status spasial dan kognitif satu agen di markas kantor."""

    def __init__(
        self,
        role_id: str,
        name: str,
        tier: SpatialTier,
        home_x: float,
        home_y: float,
        color: str = "#06b6d4",
    ) -> None:
        """Inisialisasi posisi awal dan atribut agen."""
        self.role_id = role_id
        self.name = name
        self.tier = tier
        self.home_x = home_x
        self.home_y = home_y
        self.x = home_x
        self.y = home_y
        self.target_x = home_x
        self.target_y = home_y
        self.activity_state = "IDLE"  # IDLE, CODING, REVIEWING, WALKING, MEETING, BLOCKED
        self.active_file = ""
        self.scratchpad = "Standby menunggu delegasi tiket..."
        self.speech_bubble: Optional[str] = None
        self.color = color

    def to_dict(self) -> Dict[str, Any]:
        """Konversi state ke dictionary untuk payload WebSocket."""
        return {
            "role_id": self.role_id,
            "name": self.name,
            "tier": self.tier.value,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "target_x": round(self.target_x, 1),
            "target_y": round(self.target_y, 1),
            "activity_state": self.activity_state,
            "active_file": self.active_file,
            "scratchpad": self.scratchpad,
            "speech_bubble": self.speech_bubble,
            "color": self.color,
        }


class OfficeSimulatorEngine:
    """Mesin simulasi koordinat spasial dan reaktivitas event bus kantor korporat."""

    def __init__(self) -> None:
        """Inisialisasi agen berdasarkan skema layout kanonikal."""
        self.layout = get_canonical_campus_layout()
        self.agents: Dict[str, AgentSpatialState] = {}
        self._init_agents_from_layout()

    def _init_agents_from_layout(self) -> None:
        """Membangun registry agen dari meja-meja yang didefinisikan pada layout."""
        for wing in self.layout.get("wings", []):
            tier = SpatialTier(wing.get("tier", "WORKER_SPECIALIST"))
            color = wing.get("color", "#06b6d4")
            for item in wing.get("furniture", []):
                role = item.get("assigned_role")
                if role:
                    name = item.get("label", role).replace(" Desk", "").replace(" Pod", "")
                    self.agents[role] = AgentSpatialState(
                        role_id=role,
                        name=name,
                        tier=tier,
                        home_x=float(item["x"] + 20),
                        home_y=float(item["y"] + 15),
                        color=color,
                    )

    def handle_bus_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Menerjemahkan event bus menjadi mutasi spasial dan aktivitas agen."""
        role_id = payload.get("role_id")
        agent = self.agents.get(role_id) if role_id else None

        if event_type == "TASK_STARTED" and agent:
            agent.activity_state = "CODING"
            agent.active_file = payload.get("target_file", "synthesis.py")
            agent.scratchpad = f"Menulis kode untuk tiket: {payload.get('ticket_id', 'T-ACTIVE')}"
            agent.speech_bubble = "💻 Coding..."
        elif event_type in ("STAGE_GATE_TRIGGERED", "CALL_MEETING"):
            for a in self.agents.values():
                a.target_x = 310.0 + (hash(a.role_id) % 80)
                a.target_y = 230.0 + (hash(a.role_id) % 40)
                a.activity_state = "MEETING"
                a.speech_bubble = "🏛️ All-Hands Meeting"
        elif event_type == "CONSULT_ROLE" and agent:
            agent.target_x = 880.0  # Menuju Courtyard Oasis
            agent.target_y = 480.0
            agent.activity_state = "WALKING"
            agent.speech_bubble = "☕ Diskusi di Oasis..."
        elif event_type == "CIRCUIT_BREAKER_TRIGGERED" and agent:
            agent.activity_state = "BLOCKED"
            agent.speech_bubble = "⚠️ Circuit Breaker!"
            agent.scratchpad = f"Terkunci: {payload.get('reason', 'Safety Guardrail Violation')}"
        elif event_type == "TASK_COMPLETED" and agent:
            agent.activity_state = "IDLE"
            agent.target_x = agent.home_x
            agent.target_y = agent.home_y
            agent.speech_bubble = "✅ Selesai"

    def step_simulation(self) -> None:
        """Menggerakkan agen menuju target koordinat secara linear (LERP)."""
        for a in self.agents.values():
            dx = a.target_x - a.x
            dy = a.target_y - a.y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > 2.0:
                a.x += dx * 0.15
                a.y += dy * 0.15
            else:
                a.x = a.target_x
                a.y = a.target_y
                if a.activity_state == "WALKING":
                    a.activity_state = "IDLE"

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
        """Mengambil snapshot seluruh state agen dan layout denah kampus."""
        return {
            "layout": self.layout,
            "agents": [a.to_dict() for a in self.agents.values()],
        }


office_sim_engine = OfficeSimulatorEngine()
