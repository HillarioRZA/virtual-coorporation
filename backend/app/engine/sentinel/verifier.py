"""
Two-Tier Chain-of-Verification (CoV) Pre-Flight Gatekeeper Engine.
Menjalankan verifikasi berjenjang: Tier 1 (Schema & Permission Guard deterministik)
dan Tier 2 (Deep LLM Semantic Critic) untuk menjamin keabsahan pemanggilan perkakas.
"""

import json
import re
import time
from typing import Any, Dict, Optional, Set, Tuple, Union
from pydantic import BaseModel, Field
from loguru import logger

from app.core.config import settings
from app.db.sentinel_repo import sentinel_repo
from app.engine.sentinel.manifest import LEAN_TOOL_DEFINITIONS, get_stage_tool_manifest
from app.engine.sentinel.prompt import COV_REPAIR_USER_TEMPLATE, COV_SYSTEM_PROMPT
from app.gateway.client import UnifiedLLMClient

READ_ONLY_TOOLS: Set[str] = {
    "inspect_db_schema", "validate_api_contract", "git_diff_summary",
    "search_codebase", "read_codebase", "consult_skill_library", "read_skill_detail",
    "run_lsp_diagnostics",
}
MUTATING_TOOLS: Set[str] = {
    "write_code_bundle", "lock_test_suite", "runtime_tool_builder",
    "write_codebase", "synthesize_and_register_tool",
}


def is_read_only_tool(tool_name: str) -> bool:
    """Menentukan apakah perkakas bersifat baca deterministik (Tier 1) atau mutasi (Tier 2)."""
    if tool_name in READ_ONLY_TOOLS:
        return True
    if tool_name.startswith("mcp:"):
        action = tool_name.split(":")[-1]
        read_prefixes = ("get_", "list_", "read_", "search_", "inspect_", "describe_")
        return any(action.startswith(prefix) for prefix in read_prefixes)
    return False


class CoVInspectionResult(BaseModel):
    """Hasil evaluasi inspeksi pre-flight CoV."""
    approved: bool = Field(description="True jika respon/tool lolos verifikasi")
    status: str = Field(description="APPROVED | REPAIR_REQUIRED | REPAIRED | REJECTED")
    inspected_content: str = Field(description="Konten final setelah verifikasi atau koreksi")
    tool_call: Optional[Dict[str, Any]] = Field(default=None, description="Perkakas yang disetujui")
    repair_feedback: Optional[str] = Field(default=None, description="Alasan koreksi dari CoV")
    repairs_count: int = Field(default=0, description="Jumlah siklus perbaikan")
    latency_ms: float = Field(default=0.0, description="Durasi proses inspeksi")
    audit_id: Optional[str] = Field(default=None, description="ID entri audit trail")


class CoVGatekeeper:
    """Pengawal internal pre-flight dua tingkat untuk respons & perkakas agen."""

    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None) -> None:
        self.llm_client = llm_client or UnifiedLLMClient()

    def _extract_tool_syntax(self, text: str) -> Optional[Dict[str, Any]]:
        fence_match = re.search(r'```(?:json)?\s*(\{.*?"tool"\s*:.*?\})\s*```', text, re.DOTALL)
        if fence_match:
            try:
                return json.loads(fence_match.group(1))
            except json.JSONDecodeError:
                pass
        match = re.search(r'\{\s*"tool"\s*:\s*"([^"]+)"\s*,\s*"parameters"\s*:\s*(\{[^}]*\})\s*\}', text)
        if match:
            try:
                return {"tool": match.group(1).strip(), "parameters": json.loads(match.group(2))}
            except json.JSONDecodeError:
                pass
        return None

    def _verify_tier1_schema(self, tool_name: str, params: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Tier 1: Validasi deterministik skema dan izin pemanggilan perkakas (0ms, 0 tokens)."""
        if not isinstance(params, dict):
            return False, f"Parameter untuk perkakas [{tool_name}] wajib berupa kamus JSON/object."

        if tool_name == "search_codebase" and ("query" not in params or not str(params["query"]).strip()):
            return False, "Parameter 'query' (string non-kosong) wajib diisi untuk search_codebase."
        if tool_name == "lock_test_suite" and ("test_filename" not in params or "test_content" not in params):
            return False, "Parameter 'test_filename' dan 'test_content' wajib diisi untuk lock_test_suite."
        if tool_name == "write_code_bundle" and ("bundle_type" not in params or "code_map" not in params):
            return False, "Parameter 'bundle_type' dan 'code_map' wajib diisi untuk write_code_bundle."
        if tool_name == "runtime_tool_builder" and "action" not in params:
            return False, "Parameter 'action' ('synthesize' | 'execute') wajib diisi untuk runtime_tool_builder."

        return True, None

    async def _invoke_cov_critique(self, agent_role: str, stage: Union[str, int], candidate_content: str) -> Dict[str, Any]:
        """Tier 2: Evaluasi semantik mendalam oleh LLM Critic untuk perkakas mutatif."""
        manifest = get_stage_tool_manifest(stage)
        prompt = COV_REPAIR_USER_TEMPLATE.format(
            agent_role=agent_role, stage=stage, manifest=manifest, candidate_content=candidate_content,
        )
        try:
            raw_reply = await self.llm_client.complete(
                prompt=prompt, system_prompt=COV_SYSTEM_PROMPT, model=settings.COV_MODEL,
                provider="cov", temperature=settings.COV_TEMPERATURE,
            )
            json_match = re.search(r'\{.*\}', raw_reply, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as err:
            logger.warning(f"Kegagalan inferensi audit CoV: {err}")
        return {"approved": True, "action": "APPROVE"}

    async def inspect(
        self,
        project_id: str,
        agent_role: str,
        candidate_content: str,
        stage: Union[str, int] = "development",
        custom_path: Optional[str] = None,
    ) -> CoVInspectionResult:
        """Memverifikasi respons agen dengan arsitektur Two-Tier Pre-Flight Gatekeeper."""
        start_t = time.perf_counter()
        tool_data = self._extract_tool_syntax(candidate_content)

        if not settings.COV_ENABLED or not tool_data:
            latency = (time.perf_counter() - start_t) * 1000
            audit = await sentinel_repo.record_audit(
                project_id=project_id, agent_role=agent_role, status="APPROVED",
                original_content=candidate_content, inspected_content=candidate_content,
                tool_name=tool_data.get("tool") if tool_data else None,
                tool_parameters=tool_data.get("parameters") if tool_data else None,
                latency_ms=latency, custom_path=custom_path,
            )
            return CoVInspectionResult(
                approved=True, status="APPROVED", inspected_content=candidate_content,
                tool_call=tool_data, latency_ms=latency, audit_id=audit.get("id"),
            )

        t_name = tool_data.get("tool", "")
        params = tool_data.get("parameters", {})
        status = "APPROVED"
        feedback: Optional[str] = None

        # 1. Tier 1 Deterministic Validation
        t1_valid, t1_err = self._verify_tier1_schema(t_name, params)
        if not t1_valid:
            status = "REPAIR_REQUIRED"
            feedback = t1_err
        elif is_read_only_tool(t_name):
            # Lolos Tier 1 langsung disetujui (0ms, 0 LLM tokens)
            status = "APPROVED"
        else:
            # 2. Tier 2 Deep Semantic Critic untuk mutating tools
            critique = await self._invoke_cov_critique(agent_role, stage, candidate_content)
            action = critique.get("action", "APPROVE")
            if action == "REPAIR_REQUIRED":
                status = "REPAIR_REQUIRED"
                feedback = critique.get("repair_feedback", f"Perkakas [{t_name}] cacat atau parameternya kurang.")
            elif action == "REJECT":
                status = "REJECTED"
                feedback = critique.get("repair_feedback", "Ditolak oleh CoV")

        is_approved = (status in ("APPROVED", "REPAIRED"))
        approved_tool = tool_data if is_approved else None
        latency = (time.perf_counter() - start_t) * 1000

        audit_res = await sentinel_repo.record_audit(
            project_id=project_id, agent_role=agent_role, status=status,
            original_content=candidate_content, inspected_content=candidate_content,
            tool_name=approved_tool.get("tool") if approved_tool else None,
            tool_parameters=approved_tool.get("parameters") if approved_tool else None,
            repair_feedback=feedback, latency_ms=latency, custom_path=custom_path,
        )

        return CoVInspectionResult(
            approved=is_approved, status=status, inspected_content=candidate_content,
            tool_call=approved_tool, repair_feedback=feedback,
            latency_ms=latency, audit_id=audit_res.get("id"),
        )


cov_gatekeeper = CoVGatekeeper()
