"""
API v1 Router Aggregator.
Mengonsolidasikan seluruh router sub-sistem API v1.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.corporate import router as corporate_router
from app.api.v1.corporate_events import router as corporate_events_router
from app.api.v1.corporate_tickets import router as corporate_tickets_router
from app.api.v1.corporate_ws import router as corporate_ws_router
from app.api.v1.gates import router as gates_router
from app.api.v1.governance import router as governance_router
from app.api.v1.projects import router as projects_router
from app.api.v1.sandbox_snapshots import router as sandbox_snapshots_router
from app.api.v1.sandbox_terminal_ws import router as sandbox_terminal_router
from app.api.v1.settings import router as settings_router
from app.api.v1.sparring import router as sparring_router
from app.api.v1.vault import router as vault_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.pull_requests import router as pull_requests_router
from app.api.v1.wisdom import router as wisdom_router
from app.api.v1.sandbox_network import router as sandbox_network_router
from app.api.v1.office import router as office_router
from app.api.v1.office_ws import router as office_ws_router
from app.api.v1.project_artifacts import router as project_artifacts_router
from app.api.v1.frontier_radar import router as frontier_radar_router
from app.api.v1.files import router as files_router
from app.api.v1.sentinel import router as sentinel_router

api_v1_router = APIRouter()

api_v1_router.include_router(files_router)
api_v1_router.include_router(sentinel_router)

api_v1_router.include_router(projects_router)
api_v1_router.include_router(project_artifacts_router)
api_v1_router.include_router(frontier_radar_router)
api_v1_router.include_router(sparring_router)

api_v1_router.include_router(gates_router)
api_v1_router.include_router(vault_router)
api_v1_router.include_router(settings_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(corporate_router)
api_v1_router.include_router(corporate_events_router)
api_v1_router.include_router(corporate_tickets_router)
api_v1_router.include_router(corporate_ws_router)
api_v1_router.include_router(sandbox_snapshots_router)
api_v1_router.include_router(sandbox_terminal_router)
api_v1_router.include_router(sandbox_network_router)
api_v1_router.include_router(governance_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(pull_requests_router)
api_v1_router.include_router(wisdom_router)
api_v1_router.include_router(office_router)
api_v1_router.include_router(office_ws_router)

from app.api.v1.mcp_routes import router as mcp_router
from app.api.v1.skills_routes import router as skills_router

api_v1_router.include_router(mcp_router)
api_v1_router.include_router(skills_router)

__all__ = ["api_v1_router"]


