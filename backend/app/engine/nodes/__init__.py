"""
Multi-Agent Execution Nodes.
Mengekspos seluruh handler node fungsional untuk 11 peran agen.
"""

from app.engine.nodes.auto_correction import extract_json_payload, parse_and_repair_schema
from app.engine.nodes.backend import backend_engineering_node, write_backend_files
from app.engine.nodes.cos import cos_sparring_node
from app.engine.nodes.cto import cto_architecture_node
from app.engine.nodes.devsecops import devsecops_packaging_node, write_deployment_bundle
from app.engine.nodes.frontend import frontend_prototyping_node, write_frontend_files
from app.engine.nodes.hardening import production_hardening_node
from app.engine.nodes.legal import legal_compliance_node, write_legal_bundle
from app.engine.nodes.pm import pm_spec_freeze_node
from app.engine.nodes.prototyping import mock_prototyping_phase_node, prd_and_specs_phase_node
from app.engine.nodes.qa import qa_eval_node
from app.engine.nodes.sparring import sparring_room_node
from app.engine.nodes.ui_ux import ui_ux_spec_node

__all__ = [
    "cos_sparring_node",
    "cto_architecture_node",
    "sparring_room_node",
    "pm_spec_freeze_node",
    "ui_ux_spec_node",
    "frontend_prototyping_node",
    "write_frontend_files",
    "prd_and_specs_phase_node",
    "mock_prototyping_phase_node",
    "backend_engineering_node",
    "write_backend_files",
    "qa_eval_node",
    "legal_compliance_node",
    "write_legal_bundle",
    "devsecops_packaging_node",
    "write_deployment_bundle",
    "production_hardening_node",
    "parse_and_repair_schema",
    "extract_json_payload",
]
