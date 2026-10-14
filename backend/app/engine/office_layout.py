"""
Data-Driven Corporate Campus Layout & Spatial Hierarchy Schema.
Mendefinisikan skema kampus Silicon Valley (Apple Park & Googleplex), 4-tier kasta kemewahan, dan auto-slotting.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SpatialTier(str, Enum):
    """Tingkat kasta kemewahan hierarki korporat spasial."""
    EXECUTIVE = "EXECUTIVE"          # Tier 1: Founder, CoS, CFO (Penthouse Marmer Emas)
    LEAD_MANAGEMENT = "LEAD_MANAGEMENT"  # Tier 2: CTO, PM, Growth (Suites Kaca Buram)
    WORKER_SPECIALIST = "WORKER_SPECIALIST"  # Tier 3: Dev, QA, UI/UX, Copy (Collaborative Lab)
    COMMONS = "COMMONS"              # Tier 4: All Roles (Courtyard & Boba Lounge)


class FurnitureItem(BaseModel):
    """Representasi perabot atau meja kerja dalam denah ruangan."""
    id: str
    type: str = Field(..., description="desk, table, sofa, watercooler, server_rack, fountain")
    x: float
    y: float
    width: float = 60.0
    height: float = 40.0
    assigned_role: Optional[str] = None
    label: Optional[str] = None


class OfficeRoom(BaseModel):
    """Representasi satu zona/ruangan dalam sayap gedung."""
    id: str
    name: str
    tier: SpatialTier
    theme_id: str = "cyberpunk"
    bounds: Dict[str, float] = Field(..., description="x, y, width, height")
    color: str = "#06b6d4"
    furniture: List[FurnitureItem] = Field(default_factory=list)


class CampusBuilding(BaseModel):
    """Representasi satu sayap gedung atau area terpisah dalam kampus."""
    id: str
    name: str
    tier: SpatialTier
    theme_id: str
    description: str
    rooms: List[OfficeRoom] = Field(default_factory=list)


def get_canonical_campus_layout() -> Dict[str, Any]:
    """Menghasilkan denah tata letak default kampus Silicon Valley 4-tier.

    Returns:
        Struktur data skema kampus siap pakai dalam format dictionary serializable.
    """
    return {
        "campus_name": "Sovereign Silicon Campus",
        "style": "apple_park_curved",
        "dimensions": {"width": 1376, "height": 768},
        "wings": [
            {
                "id": "wing_penthouse",
                "name": "The Executive Penthouse",
                "tier": SpatialTier.EXECUTIVE.value,
                "theme_id": "luxury_marble",
                "bounds": {"x": 960, "y": 40, "width": 360, "height": 240},
                "color": "#eab308",
                "furniture": [
                    {"id": "desk_founder", "type": "desk", "x": 1120, "y": 120, "assigned_role": "role_founder", "label": "Founder Desk"},
                    {"id": "desk_cos", "type": "desk", "x": 1240, "y": 120, "assigned_role": "role_cos", "label": "CoS Desk"},
                    {"id": "desk_cfo", "type": "desk", "x": 1040, "y": 180, "assigned_role": "role_cfo", "label": "CFO Desk"},
                    {"id": "boardroom_table", "type": "table", "x": 1140, "y": 190, "width": 140, "height": 60, "label": "Boardroom Table"},
                    {"id": "espresso_bar", "type": "watercooler", "x": 1280, "y": 50, "label": "Private Barista Bar"},
                ],
            },
            {
                "id": "wing_management",
                "name": "Product & Strategy Suites",
                "tier": SpatialTier.LEAD_MANAGEMENT.value,
                "theme_id": "scandinavian_wood",
                "bounds": {"x": 760, "y": 310, "width": 560, "height": 240},
                "color": "#a855f7",
                "furniture": [
                    {"id": "desk_cto", "type": "desk", "x": 860, "y": 380, "assigned_role": "role_cto", "label": "CTO Suite"},
                    {"id": "desk_pm", "type": "desk", "x": 1020, "y": 380, "assigned_role": "role_pm", "label": "PM Suite"},
                    {"id": "desk_growth", "type": "desk", "x": 1180, "y": 380, "assigned_role": "role_growth", "label": "Growth Lead"},
                    {"id": "kpi_screen", "type": "server_rack", "x": 1020, "y": 470, "label": "Wall KPI Display"},
                ],
            },
            {
                "id": "wing_engineering",
                "name": "Silicon Collaborative Lab",
                "tier": SpatialTier.WORKER_SPECIALIST.value,
                "theme_id": "cyberpunk",
                "bounds": {"x": 60, "y": 310, "width": 660, "height": 240},
                "color": "#06b6d4",
                "furniture": [
                    {"id": "desk_fe", "type": "desk", "x": 140, "y": 370, "assigned_role": "role_fe", "label": "Frontend Pod"},
                    {"id": "desk_be", "type": "desk", "x": 280, "y": 370, "assigned_role": "role_be", "label": "Backend Pod"},
                    {"id": "desk_qa", "type": "desk", "x": 420, "y": 370, "assigned_role": "role_qa", "label": "QA Testing Pod"},
                    {"id": "desk_devsecops", "type": "desk", "x": 560, "y": 370, "assigned_role": "role_devsecops", "label": "DevSecOps Pod"},
                    {"id": "desk_ui_ux", "type": "desk", "x": 140, "y": 460, "assigned_role": "role_ui_ux", "label": "UI/UX Station"},
                    {"id": "desk_copywriter", "type": "desk", "x": 280, "y": 460, "assigned_role": "role_copywriter", "label": "Copywriting Desk"},
                    {"id": "desk_seo", "type": "desk", "x": 420, "y": 460, "assigned_role": "role_seo", "label": "SEO Growth Desk"},
                    {"id": "server_cluster", "type": "server_rack", "x": 560, "y": 460, "label": "HPC Server Cluster"},
                ],
            },
            {
                "id": "wing_courtyard",
                "name": "The Ring Courtyard & Oasis",
                "tier": SpatialTier.COMMONS.value,
                "theme_id": "kawaii",
                "bounds": {"x": 60, "y": 570, "width": 840, "height": 170},
                "color": "#10b981",
                "furniture": [
                    {"id": "zen_fountain", "type": "fountain", "x": 880, "y": 480, "width": 80, "height": 80, "label": "Circular Water Fountain"},
                    {"id": "boba_counter", "type": "watercooler", "x": 600, "y": 640, "label": "Boba Barista Counter"},
                    {"id": "lounge_sofa", "type": "sofa", "x": 240, "y": 640, "width": 100, "height": 40, "label": "Plush Velvet Sofa"},
                ],
            },
        ],
    }


def auto_slot_role(layout: Dict[str, Any], role_id: str, label: str, tier: SpatialTier) -> Dict[str, Any]:
    """Menempatkan peran baru ke meja yang sesuai atau memperluas denah tanpa hardcode.

    Args:
        layout: Objek layout kampus aktif.
        role_id: ID peran baru.
        label: Nama tampilan peran.
        tier: Kasta hierarki peran sasaran.

    Returns:
        Layout yang telah diperbarui dengan meja baru.
    """
    for wing in layout.get("wings", []):
        if wing.get("tier") == tier.value:
            existing_roles = [f.get("assigned_role") for f in wing.get("furniture", [])]
            if role_id not in existing_roles:
                count = len([f for f in wing.get("furniture", []) if f.get("type") == "desk"])
                new_x = wing["bounds"]["x"] + 60 + (count % 4) * 120
                new_y = wing["bounds"]["y"] + 80 + (count // 4) * 100
                new_desk = {
                    "id": f"desk_{role_id}",
                    "type": "desk",
                    "x": new_x,
                    "y": new_y,
                    "assigned_role": role_id,
                    "label": f"{label} Workstation",
                }
                wing["furniture"].append(new_desk)
            break
    return layout
