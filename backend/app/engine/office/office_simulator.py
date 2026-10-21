"""
Real-Time Activity Simulation Engine for Corporate Oasis Command HQ.
Mengelola status aktivitas kognitif agen, transisi state, dan translasi event bus korporat.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from app.core.logger import logger


class SpatialTier(str, Enum):
    """Tingkat kasta hierarki korporat dan pembagian zona kerja."""
    EXECUTIVE = "EXECUTIVE"                  # Founder, CoS, CFO, Secretary
    LEAD_MANAGEMENT = "LEAD_MANAGEMENT"      # CTO, PM
    WORKER_SPECIALIST = "WORKER_SPECIALIST"  # FE, BE, QA, UI/UX, DevSecOps, Legal
    COMMONS = "COMMONS"                      # All Roles (Oasis Lounge)


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


DEFAULT_ROSTER: List[Dict[str, Any]] = [
    {"role_id": "role_founder", "name": "Founder & CEO", "tier": SpatialTier.EXECUTIVE, "color": "#eab308"},
    {"role_id": "role_cos", "name": "Chief of Staff", "tier": SpatialTier.EXECUTIVE, "color": "#eab308"},
    {"role_id": "role_cfo", "name": "Chief Financial Officer", "tier": SpatialTier.EXECUTIVE, "color": "#eab308"},
    {"role_id": "role_secretary", "name": "Executive Secretary", "tier": SpatialTier.EXECUTIVE, "color": "#a855f7"},
    {"role_id": "role_cto", "name": "Chief Technology Officer", "tier": SpatialTier.LEAD_MANAGEMENT, "color": "#3b82f6"},
    {"role_id": "role_pm", "name": "Product Manager", "tier": SpatialTier.LEAD_MANAGEMENT, "color": "#3b82f6"},
    {"role_id": "role_fe", "name": "Frontend Engineer", "tier": SpatialTier.WORKER_SPECIALIST, "color": "#06b6d4"},
    {"role_id": "role_be", "name": "Backend Engineer", "tier": SpatialTier.WORKER_SPECIALIST, "color": "#10b981"},
    {"role_id": "role_qa", "name": "QA Specialist", "tier": SpatialTier.WORKER_SPECIALIST, "color": "#f43f5e"},
    {"role_id": "role_ui_ux", "name": "UI/UX Designer", "tier": SpatialTier.WORKER_SPECIALIST, "color": "#8b5cf6"},
    {"role_id": "role_devsecops", "name": "DevSecOps Engineer", "tier": SpatialTier.WORKER_SPECIALIST, "color": "#f59e0b"},
    {"role_id": "role_legal", "name": "Legal Counsel", "tier": SpatialTier.WORKER_SPECIALIST, "color": "#64748b"},
]


class OfficeSimulatorEngine:
    """Mesin pengelola state kehadiran dan reaktivitas event bus agen kantor korporat."""

    def __init__(self) -> None:
        """Inisialisasi registry agen berdasarkan roster dinamis terpadu."""
        self.layout: Dict[str, Any] = {
            "campus_name": "Sovereign Silicon Campus",
            "style": "oasis_command_hq",
            "tiers": [t.value for t in SpatialTier],
            "wings": [
                {"id": "wing_penthouse", "name": "The Executive Penthouse", "tier": SpatialTier.EXECUTIVE.value, "furniture": [{"id": "desk_founder", "assigned_role": "role_founder"}, {"id": "desk_cos", "assigned_role": "role_cos"}]},
                {"id": "wing_management", "name": "Strategy Suites", "tier": SpatialTier.LEAD_MANAGEMENT.value, "furniture": [{"id": "desk_cto", "assigned_role": "role_cto"}, {"id": "desk_pm", "assigned_role": "role_pm"}]},
                {"id": "wing_engineering", "name": "Collaborative Engineering Lab", "tier": SpatialTier.WORKER_SPECIALIST.value, "furniture": [{"id": "desk_fe", "assigned_role": "role_fe"}, {"id": "desk_be", "assigned_role": "role_be"}]},
                {"id": "wing_commons", "name": "Oasis Commons Lounge", "tier": SpatialTier.COMMONS.value, "furniture": []},
            ],
        }
        self.agents: Dict[str, AgentSpatialState] = {}
        self._init_default_roster()

    def _init_default_roster(self) -> None:
        """Membangun registry agen dari daftar roster default."""
        for r in DEFAULT_ROSTER:
            self.agents[r["role_id"]] = AgentSpatialState(
                role_id=r["role_id"],
                name=r["name"],
                tier=r["tier"],
                color=r["color"],
            )

    def register_dynamic_role(self, role_id: str, name: str, tier: SpatialTier = SpatialTier.WORKER_SPECIALIST, color: str = "#06b6d4") -> None:
        """Mendaftarkan peran baru ke dalam simulator secara dinamis."""
        self.agents[role_id] = AgentSpatialState(role_id=role_id, name=name, tier=tier, color=color)
        logger.info(f"Peran [{role_id}] berhasil didaftarkan ke Office Simulator.")

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
            r_lower = role_id.lower().strip()
            for k, a in self.agents.items():
                if k.lower() == r_lower or a.name.lower() == r_lower or k.replace("role_", "") == r_lower.replace("role_", ""):
                    agent = a
                    break
        if not agent:
            return {"status": "ERROR", "message": f"Agen [{role_id}] tidak ditemukan."}

        agent.scratchpad = f"Instruksi CEO: {instruction}"
        agent.speech_bubble = "📢 Instruksi Diterima!"
        agent.activity_state = "CODING"
        logger.info(f"Intervensi Founder diterapkan pada [{agent.role_id}]: {instruction}")
        return {"status": "SUCCESS", "role_id": agent.role_id, "agent": agent.to_dict()}

    def get_snapshot(self) -> Dict[str, Any]:
        """Mengambil snapshot seluruh state aktivitas agen dan layout zonasi kampus."""
        return {
            "layout": self.layout,
            "agents": [a.to_dict() for a in self.agents.values()],
        }


office_sim_engine = OfficeSimulatorEngine()


def auto_slot_role(
    layout: Dict[str, Any],
    role_id: str,
    label: str,
    tier: SpatialTier = SpatialTier.WORKER_SPECIALIST,
) -> Dict[str, Any]:
    """Menambahkan slot peran baru ke denah kantor secara dinamis."""
    office_sim_engine.register_dynamic_role(role_id=role_id, name=label, tier=tier)
    for wing in layout.get("wings", []):
        if wing.get("tier") == tier.value:
            wing.setdefault("furniture", []).append({
                "id": f"desk_{role_id}",
                "type": "desk",
                "assigned_role": role_id,
                "label": label,
            })
            break
    return layout


def get_canonical_campus_layout() -> Dict[str, Any]:
    """Mengembalikan skema layout kantor kanonikal tanpa dependensi modul layout terpisah."""
    return office_sim_engine.layout
