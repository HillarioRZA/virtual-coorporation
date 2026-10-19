"""
Code Bundle Writer & File Scaffolder Tool.
Menulis berkas implementasi kode Next.js, FastAPI, Docker, dan dokumen legal dengan perlindungan read-only.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from app.core.logger import logger
from app.engine.tools.scaffolding import scaffold_standalone_backend, scaffold_standalone_frontend


PROJECTS_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "projects_output"


def write_backend_files(
    project_id: str,
    envelope: Any,
    read_only_files: Optional[List[str]] = None,
) -> Path:
    """Menulis berkas backend FastAPI produksi dan scaffolding pendukung."""
    import sys
    base_dir = getattr(sys.modules.get("app.engine.nodes.backend"), "PROJECTS_OUTPUT_DIR", None) or PROJECTS_OUTPUT_DIR
    output_dir = Path(base_dir) / project_id / "backend"
    output_dir.mkdir(parents=True, exist_ok=True)
    read_only = set(read_only_files or [])

    targets = {
        "main.py": getattr(envelope, "main_code", ""),
        "models.py": getattr(envelope, "models_code", ""),
        "routers.py": getattr(envelope, "routers_code", ""),
        "alembic_migration.py": getattr(envelope, "migration_code", ""),
        "requirements.txt": getattr(envelope, "requirements_content", ""),
    }

    for fname, code in targets.items():
        if not code:
            continue
        if fname in read_only or f"backend/{fname}" in read_only or fname.startswith("test_"):
            logger.warning(f"Adversarial TDD Guardrail: Modifikasi berkas {fname} diblokir (Read-Only).")
            continue
        (output_dir / fname).write_text(code, encoding="utf-8")

    scaffold_standalone_backend(output_dir, project_id)
    return output_dir


def write_frontend_files(
    project_id: str,
    bundle: Any,
    read_only_files: Optional[List[str]] = None,
) -> Path:
    """Menyimpan berkas Next.js yang dihasilkan ke projects_output/<id>/frontend."""
    import sys
    base_dir = getattr(sys.modules.get("app.engine.nodes.frontend"), "PROJECTS_OUTPUT_DIR", None) or PROJECTS_OUTPUT_DIR
    fe_dir = Path(base_dir) / project_id / "frontend"
    for sub in ["src/services", "src/components", "src/app"]:
        (fe_dir / sub).mkdir(parents=True, exist_ok=True)

    read_only = set(read_only_files or [])
    targets = {
        fe_dir / "src/services/apiClient.ts": getattr(bundle, "api_client_code", ""),
        fe_dir / "src/components/CoreFeature.tsx": getattr(bundle, "core_feature_component_code", ""),
        fe_dir / "src/app/page.tsx": getattr(bundle, "page_code", ""),
    }

    for path_obj, code in targets.items():
        if not code:
            continue
        rel_path = str(path_obj.relative_to(fe_dir)).replace("\\", "/")
        if rel_path in read_only or path_obj.name in read_only or path_obj.name.startswith("test_"):
            logger.warning(f"Adversarial TDD Guardrail: Modifikasi {rel_path} diblokir (Read-Only).")
            continue
        path_obj.write_text(code, encoding="utf-8")

    scaffold_standalone_frontend(fe_dir, project_id)
    return fe_dir


def write_deployment_bundle(
    project_id: str,
    envelope: Any,
    injected_secrets: Optional[Dict[str, str]] = None,
) -> Path:
    """Menulis berkas docker-compose.yml dan .env.production ke direktori proyek."""
    output_dir = PROJECTS_OUTPUT_DIR / project_id
    output_dir.mkdir(parents=True, exist_ok=True)

    compose_yaml = getattr(envelope, "docker_compose_yaml", "")
    if compose_yaml:
        (output_dir / "docker-compose.yml").write_text(compose_yaml, encoding="utf-8")

    env_lines = [getattr(envelope, "production_env_sample", "").strip()]
    if injected_secrets:
        env_lines.append("\n# --- Injected Production Secrets (Zero-Trust Vault) ---")
        for k, v in injected_secrets.items():
            env_lines.append(f"{k}={v}")

    (output_dir / ".env.production").write_text("\n".join(env_lines) + "\n", encoding="utf-8")
    logger.info(f"Paket deployment docker-compose berhasil ditulis ke: {output_dir}")
    return output_dir


def write_legal_bundle(project_id: str, bundle: Any) -> Path:
    """Menulis seluruh berkas kebijakan hukum ke direktori legal proyek."""
    output_dir = PROJECTS_OUTPUT_DIR / project_id / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "terms_of_service.md").write_text(getattr(bundle, "terms_of_service", ""), encoding="utf-8")
    (output_dir / "privacy_policy.md").write_text(getattr(bundle, "privacy_policy", ""), encoding="utf-8")
    (output_dir / "refund_policy.md").write_text(getattr(bundle, "refund_policy", ""), encoding="utf-8")

    logger.info(f"Dokumen legal berhasil disimpan di: {output_dir}")
    return output_dir


async def dispatch_paas_deployment(project_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Mengirim webhook deployment ke platform PaaS atau fallback simulasi."""
    import httpx
    from app.core.config import settings

    paas_url = settings.PAAS_API_URL
    paas_token = settings.PAAS_API_TOKEN

    if paas_url and paas_token:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    paas_url, json=payload, headers={"Authorization": f"Bearer {paas_token}"}
                )
                logger.info(f"PaaS Deploy Request terkirim ke {paas_url} (HTTP {res.status_code})")
                return {"status": "dispatched", "http_status": res.status_code}
        except Exception as err:
            logger.warning(f"Gagal mengirim request ke live PaaS API, fallback simulasi: {err}")

    return {
        "status": "simulated_success",
        "provider": settings.PAAS_PROVIDER,
        "message": f"Deploy live simulasi berhasil untuk project [{project_id}]",
    }
