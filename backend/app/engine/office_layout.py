"""
Data-Driven Corporate Campus Layout & Workstation Hierarchy Schema.
Mendefinisikan skema hierarki 4-tier kasta korporat, zonasi sayap kerja, dan auto-slotting agen.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SpatialTier(str, Enum):
    """Tingkat kasta hierarki korporat dan pembagian zona kerja."""
    EXECUTIVE = "EXECUTIVE"          # Tier 1: Founder, CoS, CFO (Executive Penthouse)
    LEAD_MANAGEMENT = "LEAD_MANAGEMENT"  # Tier 2: CTO, PM, Growth (Strategy Suites)
    WORKER_SPECIALIST = "WORKER_SPECIALIST"  # Tier 3: Dev, QA, UI/UX, Copy (Collaborative Lab)
    COMMONS = "COMMONS"              # Tier 4: All Roles (Ring Courtyard & Oasis)


class WorkstationItem(BaseModel):
    """Representasi workstation atau stasiun kerja peran agen."""
    id: str
    type: str = Field(..., description="desk, table, sofa, watercooler, server_rack, fountain")
    assigned_role: Optional[str] = None
    label: Optional[str] = None


class CampusWing(BaseModel):
    """Representasi satu sayap divisi atau zonasi dalam markas korporat."""
    id: str
    name: str
    tier: SpatialTier
    theme_id: str
    description: str
    color: str = "#06b6d4"
    furniture: List[WorkstationItem] = Field(default_factory=list)


def get_canonical_campus_layout() -> Dict[str, Any]:
    """Menghasilkan denah hierarki default kampus Silicon Valley 4-tier."""
    return {
        "campus_name": "Sovereign Silicon Campus",
        "style": "oasis_command_hq",
        "wings": [
            {
                "id": "wing_penthouse",
                "name": "The Executive Penthouse",
                "tier": SpatialTier.EXECUTIVE.value,
                "theme_id": "luxury_marble",
                "color": "#eab308",
                "description": "Boardroom eksekutif untuk Founder, CoS, dan CFO.",
                "furniture": [
                    {"id": "desk_founder", "type": "desk", "assigned_role": "role_founder", "label": "Founder Desk"},
                    {"id": "desk_cos", "type": "desk", "assigned_role": "role_cos", "label": "CoS Desk"},
                    {"id": "desk_cfo", "type": "desk", "assigned_role": "role_cfo", "label": "CFO Desk"},
                    {"id": "boardroom_table", "type": "table", "label": "Boardroom Table"},
                    {"id": "espresso_bar", "type": "watercooler", "label": "Private Barista Bar"},
                ],
            },
            {
                "id": "wing_management",
                "name": "Product & Strategy Suites",
                "tier": SpatialTier.LEAD_MANAGEMENT.value,
                "theme_id": "scandinavian_wood",
                "color": "#a855f7",
                "description": "Ruang koordinasi pimpinan teknis, produk, dan pertumbuhan.",
                "furniture": [
                    {"id": "desk_cto", "type": "desk", "assigned_role": "role_cto", "label": "CTO Suite"},
                    {"id": "desk_pm", "type": "desk", "assigned_role": "role_pm", "label": "PM Suite"},
                    {"id": "desk_growth", "type": "desk", "assigned_role": "role_growth", "label": "Growth Lead"},
                    {"id": "kpi_screen", "type": "server_rack", "label": "Wall KPI Display"},
                ],
            },
            {
                "id": "wing_engineering",
                "name": "Silicon Collaborative Lab",
                "tier": SpatialTier.WORKER_SPECIALIST.value,
                "theme_id": "cyberpunk",
                "color": "#06b6d4",
                "description": "Pod rekayasa kolaboratif untuk tim pengembang dan auditor.",
                "furniture": [
                    {"id": "desk_fe", "type": "desk", "assigned_role": "role_fe", "label": "Frontend Pod"},
                    {"id": "desk_be", "type": "desk", "assigned_role": "role_be", "label": "Backend Pod"},
                    {"id": "desk_qa", "type": "desk", "assigned_role": "role_qa", "label": "QA Testing Pod"},
                    {"id": "desk_devsecops", "type": "desk", "assigned_role": "role_devsecops", "label": "DevSecOps Pod"},
                    {"id": "desk_ui_ux", "type": "desk", "assigned_role": "role_ui_ux", "label": "UI/UX Station"},
                    {"id": "desk_copywriter", "type": "desk", "assigned_role": "role_copywriter", "label": "Copywriting Desk"},
                    {"id": "desk_seo", "type": "desk", "assigned_role": "role_seo", "label": "SEO Growth Desk"},
                    {"id": "server_cluster", "type": "server_rack", "label": "HPC Server Cluster"},
                ],
            },
            {
                "id": "wing_courtyard",
                "name": "The Ring Courtyard & Oasis",
                "tier": SpatialTier.COMMONS.value,
                "theme_id": "oasis_lounge",
                "color": "#10b981",
                "description": "Area komunal terbuka untuk istirahat dan diskusi lintas divisi.",
                "furniture": [
                    {"id": "zen_fountain", "type": "fountain", "label": "Circular Water Fountain"},
                    {"id": "boba_counter", "type": "watercooler", "label": "Boba Barista Counter"},
                    {"id": "lounge_sofa", "type": "sofa", "label": "Plush Velvet Sofa"},
                ],
            },
        ],
    }


def auto_slot_role(layout: Dict[str, Any], role_id: str, label: str, tier: SpatialTier) -> Dict[str, Any]:
    """Menempatkan peran baru ke workstation yang sesuai pada zonasi sayap kerja."""
    for wing in layout.get("wings", []):
        if wing.get("tier") == tier.value:
            existing_roles = [f.get("assigned_role") for f in wing.get("furniture", [])]
            if role_id not in existing_roles:
                new_workstation = {
                    "id": f"desk_{role_id}",
                    "type": "desk",
                    "assigned_role": role_id,
                    "label": f"{label} Workstation",
                }
                wing["furniture"].append(new_workstation)
            break
    return layout
