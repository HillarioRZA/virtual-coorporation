"""
Polymorphic Contract Handlers Subsystem.
Menangani pemetaan artefak dan pembaruan kanonikal state ventura
berdasarkan kontrak payload keluaran agen tanpa nested-if konvensional.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from loguru import logger
from app.engine.runtime.state import VentureState


class BaseContractHandler(ABC):
    """Kelas abstrak dasar untuk penangan kontrak spesifik artefak."""

    @abstractmethod
    def can_handle(self, payload: Dict[str, Any]) -> bool:
        """Memeriksa apakah kontrak payload cocok ditangani oleh handler ini."""
        pass

    @abstractmethod
    async def handle(
        self,
        payload: Dict[str, Any],
        state: VentureState,
        sbx: Optional[Any] = None,
        proxy: Optional[Any] = None,
        vault: Optional[Any] = None,
    ) -> None:
        """Mengeksekusi penyelarasan state dan side-effect berdasarkan payload."""
        pass


class ArchitectureContractHandler(BaseContractHandler):
    """Penangan kontrak arsitektur sistem dan seleksi arketipe."""

    def can_handle(self, payload: Dict[str, Any]) -> bool:
        return "frontend_framework" in payload or "backend_framework" in payload

    async def handle(
        self,
        payload: Dict[str, Any],
        state: VentureState,
        sbx: Optional[Any] = None,
        proxy: Optional[Any] = None,
        vault: Optional[Any] = None,
    ) -> None:
        from app.engine.schemas.schemas import SystemArchitectureSchema
        try:
            arch = SystemArchitectureSchema(**payload)
            state.system_architecture = arch
            state.selected_archetype = arch.archetype_id
        except Exception as err:
            logger.debug(f"Arsitektur payload sync diabaikan: {err}")


class BusinessBriefContractHandler(BaseContractHandler):
    """Penangan kontrak ringkasan bisnis dan model monetisasi."""

    def can_handle(self, payload: Dict[str, Any]) -> bool:
        return "monetization_model" in payload or "market_feasibility_score" in payload

    async def handle(
        self,
        payload: Dict[str, Any],
        state: VentureState,
        sbx: Optional[Any] = None,
        proxy: Optional[Any] = None,
        vault: Optional[Any] = None,
    ) -> None:
        from app.engine.schemas.schemas import BusinessBriefSchema
        try:
            brief = BusinessBriefSchema(**payload)
            state.business_brief = brief
        except Exception as err:
            logger.debug(f"Brief payload sync diabaikan: {err}")


class PRDContractHandler(BaseContractHandler):
    """Penangan kontrak spesifikasi PRD dan OpenAPI."""

    def can_handle(self, payload: Dict[str, Any]) -> bool:
        return "prd" in payload or "openapi_spec" in payload

    async def handle(
        self,
        payload: Dict[str, Any],
        state: VentureState,
        sbx: Optional[Any] = None,
        proxy: Optional[Any] = None,
        vault: Optional[Any] = None,
    ) -> None:
        state.openapi_spec = payload.get("openapi_spec", state.openapi_spec)
        prd_obj = payload.get("prd")
        if isinstance(prd_obj, dict):
            from app.engine.schemas.schemas import PRDSpecSchema
            try:
                state.prd_spec = PRDSpecSchema(**prd_obj)
                state.project_name = state.prd_spec.product_name
            except Exception as err:
                logger.debug(f"PRD spec sync diabaikan: {err}")


class UIComponentContractHandler(BaseContractHandler):
    """Penangan kontrak tata letak dan komponen visual antarmuka pengguna."""

    def can_handle(self, payload: Dict[str, Any]) -> bool:
        return "layout_type" in payload or "components" in payload

    async def handle(
        self,
        payload: Dict[str, Any],
        state: VentureState,
        sbx: Optional[Any] = None,
        proxy: Optional[Any] = None,
        vault: Optional[Any] = None,
    ) -> None:
        from app.engine.schemas.schemas import UIComponentSpecSchema
        try:
            state.ui_spec = UIComponentSpecSchema(**payload)
        except Exception as err:
            logger.debug(f"UI spec sync diabaikan: {err}")


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


class ContractHandlerRegistry:
    """Registri polimorfik untuk penangan kontrak payload."""

    def __init__(self, handlers: Optional[List[BaseContractHandler]] = None) -> None:
        self.handlers: List[BaseContractHandler] = handlers or [
            ArchitectureContractHandler(),
            BusinessBriefContractHandler(),
            PRDContractHandler(),
            UIComponentContractHandler(),
            FrontendBundleContractHandler(),
            BackendBundleContractHandler(),
            QualityScorecardContractHandler(),
        ]

    async def dispatch_sync(
        self,
        payload: Dict[str, Any],
        state: VentureState,
        sbx: Optional[Any] = None,
        proxy: Optional[Any] = None,
        vault: Optional[Any] = None,
    ) -> None:
        """Mengirimkan payload ke seluruh handler yang memenuhi kriteria kontrak."""
        for handler in self.handlers:
            if handler.can_handle(payload):
                await handler.handle(payload, state, sbx=sbx, proxy=proxy, vault=vault)


contract_handler_registry = ContractHandlerRegistry()
