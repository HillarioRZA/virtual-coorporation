"""
Legal & Compliance Counsel Node.
Menghasilkan dokumen kepatuhan hukum digital: Terms of Service, Privacy Policy, dan Refund Policy.
"""

from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.engine.memory import MemoryManager
from app.engine.nodes.auto_correction import parse_and_repair_schema
from app.engine.state import VentureState
from app.gateway.client import UnifiedLLMClient


class LegalBundleEnvelope(BaseModel):
    """Skema validasi untuk dokumen hukum dan kepatuhan digital."""

    terms_of_service: str = Field(..., min_length=50, description="Dokumen Syarat dan Ketentuan layanan.")
    privacy_policy: str = Field(..., min_length=50, description="Dokumen Kebijakan Privasi (UU PDP/GDPR).")
    refund_policy: str = Field(..., min_length=30, description="Dokumen Kebijakan Pengembalian Dana.")


def write_legal_bundle(project_id: str, bundle: LegalBundleEnvelope) -> Path:
    """Menulis seluruh berkas kebijakan hukum ke direktori legal proyek."""
    output_dir = Path("projects_output") / project_id / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "terms_of_service.md").write_text(bundle.terms_of_service, encoding="utf-8")
    (output_dir / "privacy_policy.md").write_text(bundle.privacy_policy, encoding="utf-8")
    (output_dir / "refund_policy.md").write_text(bundle.refund_policy, encoding="utf-8")

    logger.info(f"Dokumen legal berhasil disimpan di: {output_dir}")
    return output_dir


async def legal_compliance_node(
    state: VentureState,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_manager: Optional[MemoryManager] = None,
) -> Dict[str, Any]:
    """Node eksekusi Legal Counsel untuk menyusun dokumen kepatuhan hukum digital."""
    logger.info(f"Memulai Legal Counsel Node untuk [{state.project_id}]")
    client = llm_client or UnifiedLLMClient()
    mem = memory_manager or MemoryManager()

    system_prompt = load_prompt("legal_prompt")
    model, provider = settings.get_agent_model_and_provider("LEGAL")

    user_instruction = (
        f"Nama Perusahaan/Platform: {state.project_name}\n"
        f"Model Monetisasi: {state.business_brief.monetization_model if state.business_brief else 'usage_credits'}\n"
        f"Target Pengguna: {state.business_brief.target_audience if state.business_brief else 'Tech Startups'}\n"
        "Susun dokumen Terms of Service, Privacy Policy (patuh UU PDP / GDPR), dan Refund Policy yang sesuai."
    )

    raw_response = await client.complete(
        prompt=user_instruction,
        system_prompt=system_prompt,
        model=model,
        provider=provider,
    )

    bundle = await parse_and_repair_schema(
        llm_client=client,
        raw_response=raw_response,
        system_prompt=system_prompt,
        schema_cls=LegalBundleEnvelope,
        model=model,
        provider=provider,
        max_repairs=2,
    )

    write_legal_bundle(state.project_id, bundle)
    cost = 0.015
    state.add_token_cost("LEGAL", cost)

    await mem.log_event(
        project_id=state.project_id,
        stage="PRODUCTION_HARDENING",
        sender_role="LEGAL",
        recipient_role="DEVSECOPS",
        event_type="ARTIFACT_PUBLISHED",
        content="Legal Counsel telah menyelesaikan dokumen Terms of Service, Privacy Policy, dan Refund Policy.",
        artifact_ref="legal_bundle",
        token_cost=cost,
    )

    state.record_event(f"Legal Node: Dokumen kepatuhan hukum tersusun ($ {cost:.4f})")
    return {"token_usage": state.token_usage, "event_logs": state.event_logs}
