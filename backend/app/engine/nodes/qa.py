"""
QA & Security Auditor Node.
Menjalankan audit OWASP Top 10, evaluasi akurasi logika, dan menghasilkan QualityGateScorecard.
"""

from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.core.stream import stream_manager
from app.engine.memory import MemoryManager
from app.engine.nodes.auto_correction import parse_and_repair_schema
from app.engine.schemas import QualityGateScorecard
from app.engine.security_scanner import security_scanner
from app.engine.state import VentureState
from app.gateway.client import UnifiedLLMClient


async def qa_eval_node(
    state: VentureState,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_manager: Optional[MemoryManager] = None,
) -> Dict[str, Any]:
    """Node eksekusi QA Lead untuk memindai keamanan dan mengevaluasi kualitas kode."""
    logger.info(f"Memulai QA & Security Auditor Node untuk [{state.project_id}]")
    client = llm_client or UnifiedLLMClient()
    mem = memory_manager or MemoryManager()

    # 1. Jalankan pemindaian keamanan statis otentik pada direktori kode yang dihasilkan
    scan_res = await security_scanner.scan_project(state.project_id)

    system_prompt = load_prompt("qa_prompt")
    model, provider = settings.get_agent_model_and_provider("QA")

    user_instruction = (
        f"Proyek: {state.project_name}\n"
        f"OpenAPI Spec: {state.openapi_spec or {}}\n"
        f"System Architecture: {state.system_architecture.model_dump() if state.system_architecture else {}}\n"
        f"Hasil Pemindaian Keamanan Statis Riil:\n"
        f"- Berkas Terpindai: {scan_res['scanned_files_count']}\n"
        f"- Total Temuan OWASP: {scan_res['vulnerabilities_count']}\n"
        f"- Rincian Kerentanan: {scan_res['findings']}\n"
        "Lakukan audit OWASP Top 10 dan validasi logika bisnis. "
        "Kembalikan QualityGateScorecard dengan status PASSED jika tidak ada celah keamanan kritis."
    )

    raw_response = await client.complete(
        prompt=user_instruction,
        system_prompt=system_prompt,
        model=model,
        provider=provider,
    )

    scorecard = await parse_and_repair_schema(
        llm_client=client,
        raw_response=raw_response,
        system_prompt=system_prompt,
        schema_cls=QualityGateScorecard,
        model=model,
        provider=provider,
        max_repairs=2,
    )

    # Sinkronisasi scorecard dengan temuan riil scanner
    scorecard.owasp_vulnerabilities_count = max(scorecard.owasp_vulnerabilities_count, scan_res["vulnerabilities_count"])
    if scan_res.get("critical_count", 0) > 0:
        scorecard.status = "FAILED"
        for finding in scan_res["findings"]:
            scorecard.reasons.append(f"[{finding['severity']}] {finding['title']} at {finding['file']}:{finding['line']}")

    state.quality_scorecard = scorecard
    cost = 0.015
    state.add_token_cost("QA", cost)

    # Adversarial TDD: Daftarkan berkas pengujian sebagai read-only & terapkan chmod 444
    from pathlib import Path
    test_files = ["tests/test_api.py", "tests/test_backend.py", "backend/tests/test_api.py"]
    for tf in test_files:
        if tf not in state.read_only_files:
            state.read_only_files.append(tf)
        full_tf = Path("projects_output") / state.project_id / tf
        if full_tf.exists():
            try:
                full_tf.chmod(0o444)
            except OSError:
                pass


    # Pancarkan event SSE eval_scorecard
    await stream_manager.publish(
        project_id=state.project_id,
        event_type="eval_scorecard",
        data={
            "unit_test_passed": scorecard.unit_test_passed,
            "owasp_vulnerabilities": scorecard.owasp_vulnerabilities_count,
            "hallucination_rate": scorecard.hallucination_rate,
            "status": scorecard.status,
        },
    )

    await mem.log_event(
        project_id=state.project_id,
        stage="PRODUCTION_HARDENING",
        sender_role="QA",
        recipient_role="LEGAL",
        event_type="QUALITY_SCORECARD_PUBLISHED",
        content=(
            f"QA Audit Selesai: Status={scorecard.status}, "
            f"OWASP Vulnerabilities={scorecard.owasp_vulnerabilities_count}, "
            f"Coverage={scorecard.test_coverage_percentage}%"
        ),
        artifact_ref="quality_scorecard",
        token_cost=cost,
    )

    state.record_event(f"QA Node: Audit OWASP selesai ({scorecard.status}) ($ {cost:.4f})")
    return {
        "quality_scorecard": scorecard,
        "token_usage": state.token_usage,
        "event_logs": state.event_logs,
    }
