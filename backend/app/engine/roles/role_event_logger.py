"""
Role Event Logger Module.
Bertanggung jawab mencatat publikasi artefak agen ke blackboard memory secara dinamis.
"""

from typing import Any, Optional
from app.core.logger import logger
from app.engine.runtime.state import VentureState


async def log_role_event(mem: Optional[Any], role_id: str, state: VentureState, res: Any, cost: float) -> None:
    """Mencatat artefak yang dipublikasikan ke blackboard memory tanpa hardcode peran."""
    if not mem:
        return
    try:
        from app.engine.memory.memory import MemoryManager
        mem_instance = mem if isinstance(mem, MemoryManager) else MemoryManager()
        stage = state.stage
        ref = role_id
        ev_type = "ARTIFACT_PUBLISHED"
        recipient = "BROADCAST"

        if isinstance(res, dict):
            if "monetization_model" in res or "market_feasibility_score" in res:
                ref = "business_brief"
            elif "frontend_framework" in res or "backend_framework" in res:
                ref = "system_architecture"
            elif "prd" in res or "openapi_spec" in res:
                ref = "openapi_spec"
            elif "layout_type" in res:
                ref = "ui_spec"
            elif "preview_url" in res or "page_code" in res:
                ref = "preview_url"
                ev_type = "PREVIEW_READY"
            elif "quality_scorecard" in res or "owasp_vulnerabilities_count" in res:
                ref = "quality_scorecard"
        elif isinstance(res, str) and (res.startswith("http") or (state.preview_url and res == state.preview_url)):
            ref = "preview_url"
            ev_type = "PREVIEW_READY"

        summary_text = getattr(res, "summary", "") or getattr(res, "title", "")
        if not summary_text:
            if isinstance(res, dict):
                summary_text = res.get("summary") or res.get("title") or res.get("product_name") or ""
            elif isinstance(res, str):
                summary_text = res[:120].strip()

        summary = f"Artefak @{role_id.upper()} dipublikasikan."
        if summary_text:
            summary = f"{summary} ({summary_text})"

        await mem_instance.log_event(
            project_id=state.project_id,
            stage=stage,
            sender_role=role_id.upper(),
            recipient_role=recipient,
            event_type=ev_type,
            content=summary,
            artifact_ref=ref,
            token_cost=cost,
        )
    except Exception as err:
        logger.warning(f"Gagal mencatat event [{role_id}] ke memory blackboard: {err}")
