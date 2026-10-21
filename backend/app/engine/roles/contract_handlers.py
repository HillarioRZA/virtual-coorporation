"""
Polymorphic Contract Handlers Subsystem.
Menangani pemetaan artefak dan pembaruan kanonikal state ventura
berdasarkan kontrak payload keluaran agen tanpa nested-if konvensional.
"""

from typing import Any, Dict, List, Optional
from app.core.logger import logger
from app.engine.runtime.state import VentureState
from app.engine.roles.contract_base import BaseContractHandler
from app.engine.roles.code_contract_handlers import (
    FrontendBundleContractHandler,
    BackendBundleContractHandler,
    QualityScorecardContractHandler,
)


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
