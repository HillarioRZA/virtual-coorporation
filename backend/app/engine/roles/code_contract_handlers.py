"""
Code Bundle & Quality Scorecard Contract Handlers.
Menangani bundle kode frontend, backend, dan scorecard jaminan mutu OWASP.
"""

from typing import Any, Dict, Optional
from app.core.logger import logger
from app.engine.runtime.state import VentureState
from app.engine.roles.contract_base import BaseContractHandler


class FrontendBundleContractHandler(BaseContractHandler):
    """Penangan bundle kode frontend dan registrasi sandbox live preview."""

    def can_handle(self, payload: Dict[str, Any]) -> bool:
        return "page_code" in payload or "core_feature_component_code" in payload

    async def handle(
        self,
        payload: Dict[str, Any],
        state: VentureState,
        sbx: Optional[Any] = None,
        proxy: Optional[Any] = None,
        vault: Optional[Any] = None,
    ) -> None:
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
        except Exception as err:
            logger.warning(f"Frontend bundle handling exception: {err}")


class BackendBundleContractHandler(BaseContractHandler):
    """Penangan bundle kode backend dan penulisan berkas proyek."""

    def can_handle(self, payload: Dict[str, Any]) -> bool:
        return "fastapi_app_code" in payload or "sqlalchemy_models_code" in payload

    async def handle(
        self,
        payload: Dict[str, Any],
        state: VentureState,
        sbx: Optional[Any] = None,
        proxy: Optional[Any] = None,
        vault: Optional[Any] = None,
    ) -> None:
        from app.engine.tools.code_bundle_writer import write_backend_files
        from app.engine.schemas.envelope_schemas import BackendOutputEnvelope
        try:
            b_env = BackendOutputEnvelope(**payload)
            write_backend_files(state.project_id, b_env, state.read_only_files)
        except Exception as err:
            logger.warning(f"Backend bundle handling exception: {err}")


class QualityScorecardContractHandler(BaseContractHandler):
    """Penangan scorecard audit mutu dan keamanan OWASP."""

    def can_handle(self, payload: Dict[str, Any]) -> bool:
        return "owasp_vulnerabilities_count" in payload or "unit_test_passed" in payload

    async def handle(
        self,
        payload: Dict[str, Any],
        state: VentureState,
        sbx: Optional[Any] = None,
        proxy: Optional[Any] = None,
        vault: Optional[Any] = None,
    ) -> None:
        from app.engine.schemas.schemas import QualityGateScorecard
        try:
            scorecard = QualityGateScorecard(**payload)
            state.quality_scorecard = scorecard
        except Exception as err:
            logger.warning(f"QA scorecard handling exception: {err}")
