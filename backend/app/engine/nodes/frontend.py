"""
Frontend Engineer Agent Node.
Menghasilkan kode Next.js modular berbasis MockServiceAdapter dan meluncurkan preview sandbox.
"""

from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict

from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.engine.memory import MemoryManager
from app.engine.nodes.auto_correction import parse_and_repair_schema
from app.engine.state import VentureState
from app.gateway.client import UnifiedLLMClient
from app.sandbox.proxy import ProxyManager
from app.sandbox.runner import SandboxManager

PROJECTS_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "projects_output"


class FrontendCodeBundle(BaseModel):
    """Wadah kode Next.js terstruktur keluaran Frontend Engineer."""

    model_config = ConfigDict(extra="ignore")
    api_client_code: str
    core_feature_component_code: str
    page_code: str


from app.engine.scaffolding import scaffold_standalone_frontend


def write_frontend_files(project_id: str, bundle: FrontendCodeBundle) -> Path:
    """Menyimpan berkas-berkas Next.js yang dihasilkan ke projects_output/<id>/frontend."""
    fe_dir = PROJECTS_OUTPUT_DIR / project_id / "frontend"
    src_services = fe_dir / "src" / "services"
    src_components = fe_dir / "src" / "components"
    src_app = fe_dir / "src" / "app"

    for d in [src_services, src_components, src_app]:
        d.mkdir(parents=True, exist_ok=True)

    # 1. Tulis kode komponen utama dari LLM
    (src_services / "apiClient.ts").write_text(bundle.api_client_code, encoding="utf-8")
    (src_components / "CoreFeature.tsx").write_text(bundle.core_feature_component_code, encoding="utf-8")
    (src_app / "page.tsx").write_text(bundle.page_code, encoding="utf-8")

    # 2. Tulis berkas konfigurasi build mandiri (package.json, tsconfig, tailwind, dsb.)
    scaffold_standalone_frontend(fe_dir, project_id)

    logger.info(f"Proyek Next.js mandiri berhasil ditulis ke: {fe_dir}")
    return fe_dir


async def frontend_prototyping_node(
    state: VentureState,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_mgr: Optional[MemoryManager] = None,
    sandbox_mgr: Optional[SandboxManager] = None,
    proxy_mgr: Optional[ProxyManager] = None,
) -> Dict[str, Any]:
    """Eksekusi node Frontend Engineer pada tahap MOCK_PROTOTYPING.

    Args:
        state: State aktif proyek venture.
        llm_client: Client gateway BYOK LLM opsional.
        memory_mgr: Manajer memori SQLite opsional.
        sandbox_mgr: Manajer kontainer sandbox opsional.
        proxy_mgr: Manajer routing reverse proxy Caddy opsional.

    Returns:
        Dict update state berisi 'preview_url'.
    """
    client = llm_client or UnifiedLLMClient()
    sbx = sandbox_mgr or SandboxManager()
    proxy = proxy_mgr or ProxyManager()
    model, provider = settings.get_agent_model_and_provider("FRONTEND")
    system_prompt = load_prompt("frontend")

    logger.info(f"Frontend Node Executing for Project: [{state.project_id}] via {provider}/{model}")

    context_prompt = (
        f"Proyek: {state.project_name}\n"
        f"OpenAPI Spec:\n{state.openapi_spec}\n\n"
        f"UI Spec:\n{state.ui_spec.model_dump(mode='json') if state.ui_spec else {}}\n\n"
        f"Bangun aplikasi Next.js berbasis Adapter Pattern: 'api_client_code', "
        f"'core_feature_component_code', dan 'page_code' dalam format JSON murni."
    )

    raw_response = await client.complete(
        prompt=context_prompt,
        system_prompt=system_prompt,
        model=model,
        provider=provider,
        temperature=0.3,
    )

    bundle = await parse_and_repair_schema(
        llm_client=client,
        raw_response=raw_response,
        system_prompt=system_prompt,
        schema_cls=FrontendCodeBundle,
        model=model,
        provider=provider,
        max_repairs=2,
    )

    # Simpan kode ke disk host
    fe_path = write_frontend_files(state.project_id, bundle)

    # Luncurkan kontainer sandbox ephemeral
    sandbox_info = await sbx.run_frontend_sandbox(state.project_id, str(fe_path))
    port = sandbox_info["port"]

    # Daftarkan rute ke Reverse Proxy Caddy
    preview_url = await proxy.register_route(state.project_id, port)
    state.preview_url = preview_url

    if memory_mgr:
        try:
            summary = f"Mock Prototyping selesai. Preview URL aktif: {preview_url} (Port: {port})"
            await memory_mgr.log_event(
                project_id=state.project_id,
                stage=state.stage,
                sender_role="FRONTEND",
                recipient_role="BROADCAST",
                event_type="PREVIEW_READY",
                content=summary,
                artifact_ref="preview_url",
                token_cost=0.03,
            )
        except Exception as log_err:
            logger.warning(f"Gagal mencatat event Frontend ke memory blackboard: {log_err}")

    return {"preview_url": preview_url}
