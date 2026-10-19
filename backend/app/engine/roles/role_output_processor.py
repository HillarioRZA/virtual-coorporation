"""
Dynamic Contract-Driven Role Output Processor Module.
Menyimpan dan memetakan artefak yang dihasilkan agen secara otonom ke dalam VentureState.
"""

import json
from typing import Any, Dict, Optional
from app.core.logger import logger
from app.engine.roles.role_event_logger import log_role_event
from app.engine.runtime.state import VentureState


async def process_role_output(
    role_id: str,
    raw: str,
    state: VentureState,
    client: Any,
    sys_p: str,
    model: str,
    provider: str,
    mem: Optional[Any] = None,
    sbx: Optional[Any] = None,
    proxy: Optional[Any] = None,
    vault: Optional[Any] = None,
) -> Dict[str, Any]:
    """Menyimpan artefak tugas peran ke state dan mengeksekusi side-effect berdasarkan payload kontrak."""
    parsed_payload: Any = _try_parse_payload(raw)

    state.set_artifact(role_id, parsed_payload if parsed_payload is not None else raw)

    if isinstance(parsed_payload, dict):
        await _sync_canonical_state_fields(role_id, parsed_payload, state, sbx, proxy, vault)

    state.add_token_cost(role_id.upper(), 0.02)
    state.record_event(f"Agen @{role_id.upper()}: Tugas selesai dieksekusi ($ 0.0200)")
    await log_role_event(mem, role_id, state, parsed_payload if parsed_payload is not None else raw, 0.02)

    ret = {
        "artifact": parsed_payload if parsed_payload is not None else raw,
        "token_usage": state.token_usage,
        "event_logs": state.event_logs,
    }
    if state.business_brief:
        ret["business_brief"] = state.business_brief
    if state.system_architecture:
        ret["system_architecture"] = state.system_architecture
        ret["selected_archetype"] = state.selected_archetype
    if state.prd_spec:
        ret["prd_spec"] = state.prd_spec
    if state.openapi_spec:
        ret["openapi_spec"] = state.openapi_spec
    if state.ui_spec:
        ret["ui_spec"] = state.ui_spec
    if state.preview_url:
        ret["preview_url"] = state.preview_url
    if state.quality_scorecard:
        ret["quality_scorecard"] = state.quality_scorecard
    if state.project_name:
        ret["project_name"] = state.project_name
    return ret


def _try_parse_payload(raw: str) -> Any:
    """Mengekstrak JSON terstruktur dari teks luaran model jika ada."""
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except Exception:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except Exception:
                pass
        return None


async def _sync_canonical_state_fields(
    role_id: str,
    payload: Dict[str, Any],
    state: VentureState,
    sbx: Optional[Any],
    proxy: Optional[Any],
    vault: Optional[Any],
) -> None:
    """Menyelaraskan field state ventura berdasarkan kontrak isi payload (contract-driven)."""
    if "frontend_framework" in payload or "backend_framework" in payload:
        from app.engine.schemas.schemas import SystemArchitectureSchema
        try:
            arch = SystemArchitectureSchema(**payload)
            state.system_architecture = arch
            state.selected_archetype = arch.archetype_id
        except Exception as e:
            logger.debug(f"Arsitektur payload sync: {e}")

    if "monetization_model" in payload or "market_feasibility_score" in payload:
        from app.engine.schemas.schemas import BusinessBriefSchema
        try:
            brief = BusinessBriefSchema(**payload)
            state.business_brief = brief
        except Exception as e:
            logger.debug(f"Brief payload sync: {e}")

    if "prd" in payload or "openapi_spec" in payload:
        state.openapi_spec = payload.get("openapi_spec", state.openapi_spec)
        prd_obj = payload.get("prd")
        if isinstance(prd_obj, dict):
            from app.engine.schemas.schemas import PRDSpecSchema
            try:
                state.prd_spec = PRDSpecSchema(**prd_obj)
                state.project_name = state.prd_spec.product_name
            except Exception:
                pass

    if "layout_type" in payload or "components" in payload:
        from app.engine.schemas.schemas import UIComponentSpecSchema
        try:
            state.ui_spec = UIComponentSpecSchema(**payload)
        except Exception:
            pass

    if "page_code" in payload or "core_feature_component_code" in payload:
        from app.engine.tools.code_bundle_writer import write_frontend_files
        from app.engine.schemas.envelope_schemas import FrontendCodeBundle
        try:
            bundle = FrontendCodeBundle(**payload)
            fe_path = write_frontend_files(state.project_id, bundle, state.read_only_files)
            from app.sandbox.runner import SandboxManager
            from app.sandbox.proxy import ProxyManager
            s_mgr = sbx or SandboxManager()
            p_mgr = proxy or ProxyManager()
            info = await s_mgr.run_frontend_sandbox(state.project_id, str(fe_path))
            state.preview_url = await p_mgr.register_route(state.project_id, info["port"])
        except Exception as e:
            logger.warning(f"Frontend bundle handling: {e}")

    if "fastapi_app_code" in payload or "sqlalchemy_models_code" in payload:
        from app.engine.tools.code_bundle_writer import write_backend_files
        from app.engine.schemas.envelope_schemas import BackendOutputEnvelope
        try:
            b_env = BackendOutputEnvelope(**payload)
            write_backend_files(state.project_id, b_env, state.read_only_files)
        except Exception as e:
            logger.warning(f"Backend bundle handling: {e}")

    if "owasp_vulnerabilities_count" in payload or "unit_test_passed" in payload:
        from app.engine.schemas.schemas import QualityGateScorecard
        try:
            scorecard = QualityGateScorecard(**payload)
            state.quality_scorecard = scorecard
        except Exception as e:
            logger.warning(f"QA scorecard handling: {e}")
