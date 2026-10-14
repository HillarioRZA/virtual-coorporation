"""
DevSecOps & Deployment Specialist Node.
Membungkus kode ke dalam kontainer multi-service, menginjeksi kredensial Secret Vault, dan mengelola PaaS deploy.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import httpx
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.core.security import SecretVaultManager
from app.engine.memory import MemoryManager
from app.engine.nodes.auto_correction import parse_and_repair_schema
from app.engine.state import VentureState
from app.gateway.client import UnifiedLLMClient


class DevSecOpsEnvelope(BaseModel):
    """Skema validasi untuk paket orkestrasi kontainer dan deployment."""

    docker_compose_yaml: str = Field(..., min_length=30, description="Konfigurasi docker-compose.yml multi-service.")
    production_env_sample: str = Field(..., min_length=10, description="Template environment variables produksi.")
    deployment_payload: Dict[str, Any] = Field(default_factory=dict, description="Metadata payload PaaS deploy.")


def write_deployment_bundle(
    project_id: str,
    envelope: DevSecOpsEnvelope,
    injected_secrets: Optional[Dict[str, str]] = None,
) -> Path:
    """Menulis berkas docker-compose.yml dan .env.production ke direktori proyek."""
    output_dir = Path("projects_output") / project_id
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "docker-compose.yml").write_text(envelope.docker_compose_yaml, encoding="utf-8")

    env_lines = [envelope.production_env_sample.strip()]
    if injected_secrets:
        env_lines.append("\n# --- Injected Production Secrets (Zero-Trust Vault) ---")
        for k, v in injected_secrets.items():
            env_lines.append(f"{k}={v}")

    (output_dir / ".env.production").write_text("\n".join(env_lines) + "\n", encoding="utf-8")
    logger.info(f"Paket deployment docker-compose berhasil ditulis ke: {output_dir}")
    return output_dir


async def dispatch_paas_deployment(
    project_id: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """Mengirim webhook deployment ke platform PaaS (Coolify / Railway) atau fallback simulasi."""
    paas_url = settings.PAAS_API_URL
    paas_token = settings.PAAS_API_TOKEN

    if paas_url and paas_token:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    paas_url,
                    json=payload,
                    headers={"Authorization": f"Bearer {paas_token}"},
                )
                logger.info(f"PaaS Deploy Request terkirim ke {paas_url} (HTTP {res.status_code})")
                return {"status": "dispatched", "http_status": res.status_code}
        except Exception as err:
            logger.warning(f"Gagal mengirim request ke live PaaS API, fallback simulasi: {err}")

    # Fallback status sukses jika PaaS API belum dihubungkan ke server live
    return {
        "status": "simulated_success",
        "provider": settings.PAAS_PROVIDER,
        "message": f"Deploy live simulasi berhasil untuk project [{project_id}]",
    }


async def devsecops_packaging_node(
    state: VentureState,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_manager: Optional[MemoryManager] = None,
    vault_manager: Optional[SecretVaultManager] = None,
) -> Dict[str, Any]:
    """Node eksekusi DevSecOps untuk merakit bundle kontainer dan memicu deployment."""
    logger.info(f"Memulai DevSecOps Packaging Node untuk [{state.project_id}]")
    client = llm_client or UnifiedLLMClient()
    mem = memory_manager or MemoryManager()
    vault = vault_manager or SecretVaultManager()

    system_prompt = load_prompt("devsecops_prompt")
    model, provider = settings.get_agent_model_and_provider("DEVSECOPS")

    user_instruction = (
        f"Proyek: {state.project_name}\n"
        f"Arketipe: {state.selected_archetype}\n"
        f"PaaS Provider: {settings.PAAS_PROVIDER}\n"
        "Hasilkan konfigurasi docker-compose.yml multi-service (frontend, backend, postgres) dan .env.production."
    )

    raw_response = await client.complete(
        prompt=user_instruction,
        system_prompt=system_prompt,
        model=model,
        provider=provider,
    )

    envelope = await parse_and_repair_schema(
        llm_client=client,
        raw_response=raw_response,
        system_prompt=system_prompt,
        schema_cls=DevSecOpsEnvelope,
        model=model,
        provider=provider,
        max_repairs=2,
    )

    cost = 0.02

    # Ambil kunci rahasia terenkripsi dari vault untuk diinjeksi ke env kontainer
    injected_secrets = await vault.get_all_decrypted(state.project_id)
    write_deployment_bundle(state.project_id, envelope, injected_secrets)

    deploy_res = await dispatch_paas_deployment(state.project_id, envelope.deployment_payload)
    state.add_token_cost("DEVSECOPS", cost)

    await mem.log_event(
        project_id=state.project_id,
        stage="DEPLOY_LIVE",
        sender_role="DEVSECOPS",
        recipient_role="BROADCAST",
        event_type="DEPLOYMENT_DISPATCHED",
        content=f"DevSecOps berhasil membungkus kontainer dan memicu deployment ({deploy_res['status']}).",
        artifact_ref="deployment_bundle",
        token_cost=cost,
    )

    state.record_event(f"DevSecOps Node: Deployment terkirim ({deploy_res['status']}) ($ {cost:.4f})")
    return {"token_usage": state.token_usage, "event_logs": state.event_logs}
