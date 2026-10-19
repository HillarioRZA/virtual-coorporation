"""
Multi-Agent Execution Nodes & Backward-Compatibility Registry.
Mengekspos seluruh handler node fungsional untuk peran agen yang dialihkan
secara dinamis ke execute_dynamic_role_node() serta meregistrasikan modul virtual.
"""

import sys
import types
from typing import Any, Dict, Optional

from app.engine.roles.dynamic_node import execute_dynamic_role_node
from app.engine.schemas.envelope_schemas import (
    BackendOutputEnvelope,
    DevSecOpsEnvelope,
    FrontendCodeBundle,
    LegalBundleEnvelope,
    PMOutputEnvelope,
)
from app.engine.nodes.auto_correction import extract_json_payload, parse_and_repair_schema
from app.engine.runtime.state import VentureState
from app.engine.tools.code_bundle_writer import (
    write_backend_files,
    write_deployment_bundle,
    write_frontend_files,
    write_legal_bundle,
)


async def cos_sparring_node(state: VentureState, llm_client: Optional[Any] = None, memory_mgr: Optional[Any] = None) -> Dict[str, Any]:
    """Thin wrapper backward-compatibility untuk Chief of Staff Node."""
    return await execute_dynamic_role_node("cos", state, llm_client=llm_client, memory_mgr=memory_mgr)


async def cto_architecture_node(state: VentureState, llm_client: Optional[Any] = None, memory_mgr: Optional[Any] = None) -> Dict[str, Any]:
    """Thin wrapper backward-compatibility untuk Chief Technology Officer Node."""
    return await execute_dynamic_role_node("cto", state, llm_client=llm_client, memory_mgr=memory_mgr)


async def pm_spec_freeze_node(state: VentureState, llm_client: Optional[Any] = None, memory_mgr: Optional[Any] = None) -> Dict[str, Any]:
    """Thin wrapper backward-compatibility untuk Product Manager Node."""
    return await execute_dynamic_role_node("pm", state, llm_client=llm_client, memory_mgr=memory_mgr)


async def ui_ux_spec_node(state: VentureState, llm_client: Optional[Any] = None, memory_mgr: Optional[Any] = None) -> Dict[str, Any]:
    """Thin wrapper backward-compatibility untuk Lead UI/UX Designer Node."""
    return await execute_dynamic_role_node("ui_ux", state, llm_client=llm_client, memory_mgr=memory_mgr)


async def frontend_prototyping_node(
    state: VentureState, llm_client: Optional[Any] = None, memory_mgr: Optional[Any] = None,
    sandbox_mgr: Optional[Any] = None, proxy_mgr: Optional[Any] = None,
) -> Dict[str, Any]:
    """Thin wrapper backward-compatibility untuk Frontend Engineer Node."""
    return await execute_dynamic_role_node(
        "frontend", state, llm_client=llm_client, memory_mgr=memory_mgr, sandbox_mgr=sandbox_mgr, proxy_mgr=proxy_mgr
    )


async def backend_engineering_node(state: VentureState, llm_client: Optional[Any] = None, memory_manager: Optional[Any] = None) -> Dict[str, Any]:
    """Thin wrapper backward-compatibility untuk Backend Engineer Node."""
    return await execute_dynamic_role_node("backend", state, llm_client=llm_client, memory_mgr=memory_manager)


async def qa_eval_node(state: VentureState, llm_client: Optional[Any] = None, memory_manager: Optional[Any] = None) -> Dict[str, Any]:
    """Thin wrapper backward-compatibility untuk QA & Security Auditor Node."""
    return await execute_dynamic_role_node("qa", state, llm_client=llm_client, memory_mgr=memory_manager)


async def devsecops_packaging_node(
    state: VentureState, llm_client: Optional[Any] = None, memory_manager: Optional[Any] = None, vault_manager: Optional[Any] = None,
) -> Dict[str, Any]:
    """Thin wrapper backward-compatibility untuk DevSecOps Node."""
    return await execute_dynamic_role_node("devsecops", state, llm_client=llm_client, memory_mgr=memory_manager, vault_mgr=vault_manager)


async def legal_compliance_node(state: VentureState, llm_client: Optional[Any] = None, memory_manager: Optional[Any] = None) -> Dict[str, Any]:
    """Thin wrapper backward-compatibility untuk Legal & Compliance Node."""
    return await execute_dynamic_role_node("legal", state, llm_client=llm_client, memory_mgr=memory_manager)


async def sparring_room_node(state: VentureState, llm_client: Optional[Any] = None, memory_mgr: Optional[Any] = None) -> Dict[str, Any]:
    """Composite node Sparring Room (CoS lalu CTO)."""
    await execute_dynamic_role_node("cos", state, llm_client=llm_client, memory_mgr=memory_mgr)
    await execute_dynamic_role_node("cto", state, llm_client=llm_client, memory_mgr=memory_mgr)
    return {"business_brief": state.business_brief, "system_architecture": state.system_architecture, "selected_archetype": state.selected_archetype}


async def prd_and_specs_phase_node(state: VentureState, llm_client: Optional[Any] = None, memory_mgr: Optional[Any] = None) -> Dict[str, Any]:
    """Composite node PRD & Specs (PM lalu UI/UX)."""
    await execute_dynamic_role_node("pm", state, llm_client=llm_client, memory_mgr=memory_mgr)
    await execute_dynamic_role_node("ui_ux", state, llm_client=llm_client, memory_mgr=memory_mgr)
    return {"prd_spec": state.prd_spec, "openapi_spec": state.openapi_spec, "ui_spec": state.ui_spec, "project_name": state.project_name}


async def mock_prototyping_phase_node(state: VentureState, llm_client: Optional[Any] = None, memory_mgr: Optional[Any] = None, sandbox_mgr: Optional[Any] = None, proxy_mgr: Optional[Any] = None) -> Dict[str, Any]:
    """Composite node Mock Prototyping (Frontend & sandbox)."""
    return await execute_dynamic_role_node("frontend", state, llm_client=llm_client, memory_mgr=memory_mgr, sandbox_mgr=sandbox_mgr, proxy_mgr=proxy_mgr)


async def production_hardening_node(state: VentureState, llm_client: Optional[Any] = None, memory_manager: Optional[Any] = None) -> Dict[str, Any]:
    """Composite node Production Hardening (Backend -> QA -> Legal)."""
    await execute_dynamic_role_node("backend", state, llm_client=llm_client, memory_mgr=memory_manager)
    await execute_dynamic_role_node("qa", state, llm_client=llm_client, memory_mgr=memory_manager)
    await execute_dynamic_role_node("legal", state, llm_client=llm_client, memory_mgr=memory_manager)
    return {"quality_scorecard": state.quality_scorecard, "token_usage": state.token_usage, "event_logs": state.event_logs}


from app.engine.tools.code_bundle_writer import PROJECTS_OUTPUT_DIR, dispatch_paas_deployment

# Registrasi modul virtual backward-compatibility di sys.modules
_VIRTUAL_MODULES = {
    "cos": {"cos_sparring_node": cos_sparring_node},
    "cto": {"cto_architecture_node": cto_architecture_node},
    "pm": {"pm_spec_freeze_node": pm_spec_freeze_node, "PMOutputEnvelope": PMOutputEnvelope},
    "ui_ux": {"ui_ux_spec_node": ui_ux_spec_node},
    "frontend": {
        "frontend_prototyping_node": frontend_prototyping_node,
        "write_frontend_files": write_frontend_files,
        "FrontendCodeBundle": FrontendCodeBundle,
        "PROJECTS_OUTPUT_DIR": PROJECTS_OUTPUT_DIR,
    },
    "backend": {
        "backend_engineering_node": backend_engineering_node,
        "write_backend_files": write_backend_files,
        "BackendOutputEnvelope": BackendOutputEnvelope,
        "PROJECTS_OUTPUT_DIR": PROJECTS_OUTPUT_DIR,
    },
    "qa": {"qa_eval_node": qa_eval_node},
    "devsecops": {
        "devsecops_packaging_node": devsecops_packaging_node,
        "write_deployment_bundle": write_deployment_bundle,
        "dispatch_paas_deployment": dispatch_paas_deployment,
        "DevSecOpsEnvelope": DevSecOpsEnvelope,
    },
    "legal": {"legal_compliance_node": legal_compliance_node, "write_legal_bundle": write_legal_bundle, "LegalBundleEnvelope": LegalBundleEnvelope},
    "hardening": {"production_hardening_node": production_hardening_node},
    "prototyping": {"mock_prototyping_phase_node": mock_prototyping_phase_node, "prd_and_specs_phase_node": prd_and_specs_phase_node},
    "sparring": {"sparring_room_node": sparring_room_node},
}

for _mod_name, _symbols in _VIRTUAL_MODULES.items():
    _full_path = f"app.engine.nodes.{_mod_name}"
    _m = types.ModuleType(_full_path)
    for _k, _v in _symbols.items():
        setattr(_m, _k, _v)
    sys.modules[_full_path] = _m

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
    "execute_dynamic_role_node",
    "dispatch_paas_deployment",
    "BackendOutputEnvelope",
    "FrontendCodeBundle",
    "PMOutputEnvelope",
    "DevSecOpsEnvelope",
    "LegalBundleEnvelope",
]
