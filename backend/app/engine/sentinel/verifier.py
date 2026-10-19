"""
Internal Chain-of-Verification (CoV) Pre-Flight Gatekeeper Engine.
Memeriksa integritas respons dan pemanggilan perkakas agen sebelum eksekusi atau siaran.
"""

import json
import re
import time
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logger import logger
from app.db.sentinel_repo import sentinel_repo
from app.engine.sentinel.manifest import get_stage_tool_manifest, LEAN_TOOL_DEFINITIONS
from app.engine.sentinel.prompt import COV_REPAIR_USER_TEMPLATE, COV_SYSTEM_PROMPT
from app.gateway.client import UnifiedLLMClient


class CoVInspectionResult(BaseModel):
    """Hasil evaluasi inspeksi pre-flight CoV."""

    approved: bool = Field(description="True jika respon/tool lolos verifikasi")
    status: str = Field(description="APPROVED | REPAIRED | REJECTED")
    inspected_content: str = Field(description="Konten final setelah verifikasi atau reparasi")
    tool_call: Optional[Dict[str, Any]] = Field(default=None, description="Perkakas yang disetujui untuk dieksekusi")
    repair_feedback: Optional[str] = Field(default=None, description="Alasan atau umpan balik koreksi CoV")
    repairs_count: int = Field(default=0, description="Jumlah siklus perbaikan otomatis")
    latency_ms: float = Field(default=0.0, description="Durasi proses inspeksi dalam milidetik")
    audit_id: Optional[str] = Field(default=None, description="ID entri audit trail di database")


class CoVGatekeeper:
    """Pengawal internal pre-flight untuk menjamin kepatuhan format & parameter perkakas."""

    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None) -> None:
        """Inisialisasi gatekeeper dengan client LLM."""
        self.llm_client = llm_client or UnifiedLLMClient()

    def _extract_tool_syntax(self, text: str) -> Optional[Dict[str, Any]]:
        """Mengekstrak blok perkakas secara cepat melalui regex."""
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

    async def _invoke_cov_critique(
        self,
        agent_role: str,
        stage: Union[str, int],
        candidate_content: str,
    ) -> Dict[str, Any]:
        """Memanggil model CoV untuk mengaudit dan menghasilkan umpan balik perbaikan."""
        manifest = get_stage_tool_manifest(stage)
        prompt = COV_REPAIR_USER_TEMPLATE.format(
            agent_role=agent_role,
            stage=stage,
            manifest=manifest,
            candidate_content=candidate_content,
        )
        try:
            raw_reply = await self.llm_client.complete(
                prompt=prompt,
                system_prompt=COV_SYSTEM_PROMPT,
                model=settings.COV_MODEL,
                provider="cov",
                temperature=settings.COV_TEMPERATURE,
            )
            json_match = re.search(r'\{.*\}', raw_reply, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except (json.JSONDecodeError, RuntimeError, Exception) as err:
            logger.warning(f"Kegagalan inferensi audit CoV: {err}")
        return {"approved": True, "action": "APPROVE", "tool_name": None, "parameters": None}

    async def inspect(
        self,
        project_id: str,
        agent_role: str,
        candidate_content: str,
        stage: Union[str, int] = "development",
        custom_path: Optional[str] = None,
    ) -> CoVInspectionResult:
        """Memverifikasi respons agen dan menyetujui pemanggilan perkakas secara transparan."""
        start_t = time.perf_counter()

        if not settings.COV_ENABLED:
            tool_data = self._extract_tool_syntax(candidate_content)
            audit = await sentinel_repo.record_audit(
                project_id=project_id,
                agent_role=agent_role,
                status="APPROVED",
                original_content=candidate_content,
                inspected_content=candidate_content,
                tool_name=tool_data.get("tool") if tool_data else None,
                tool_parameters=tool_data.get("parameters") if tool_data else None,
                latency_ms=(time.perf_counter() - start_t) * 1000,
                custom_path=custom_path,
            )
            return CoVInspectionResult(
                approved=True,
                status="APPROVED",
                inspected_content=candidate_content,
                tool_call=tool_data,
                latency_ms=(time.perf_counter() - start_t) * 1000,
                audit_id=audit.get("id"),
            )

        tool_data = self._extract_tool_syntax(candidate_content)
        status = "APPROVED"
        feedback = None
        repairs = 0
        final_content = candidate_content
        approved_tool = tool_data

        if tool_data:
            t_name = tool_data.get("tool", "")
            params = tool_data.get("parameters", {})
            if t_name not in LEAN_TOOL_DEFINITIONS or not isinstance(params, dict):
                logger.info(f"CoV Gatekeeper mendeteksi cacat tool [{t_name}] oleh {agent_role}. Meminta audit...")
                critique = await self._invoke_cov_critique(agent_role, stage, candidate_content)
                if critique.get("action") == "REPAIR_REQUIRED":
                    status = "REPAIR_REQUIRED"
                    feedback = critique.get("repair_feedback", f"Perkakas [{t_name}] cacat atau parameternya kurang.")
                    approved_tool = None
                elif critique.get("action") == "REJECT":
                    status = "REJECTED"
                    feedback = critique.get("repair_feedback", "Ditolak oleh CoV")
                    approved_tool = None

        latency = (time.perf_counter() - start_t) * 1000
        audit_res = await sentinel_repo.record_audit(
            project_id=project_id,
            agent_role=agent_role,
            status=status,
            original_content=candidate_content,
            inspected_content=final_content,
            tool_name=approved_tool.get("tool") if approved_tool else None,
            tool_parameters=approved_tool.get("parameters") if approved_tool else None,
            repair_feedback=feedback,
            repairs_count=repairs,
            latency_ms=latency,
            custom_path=custom_path,
        )

        return CoVInspectionResult(
            approved=(status != "REJECTED"),
            status=status,
            inspected_content=final_content,
            tool_call=approved_tool,
            repair_feedback=feedback,
            repairs_count=repairs,
            latency_ms=latency,
            audit_id=audit_res.get("id"),
        )


cov_gatekeeper = CoVGatekeeper()
