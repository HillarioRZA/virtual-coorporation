"""
Dynamic Node Agent Tool Handling Module.
Menjalankan loop eksekusi perkakas dengan Two-Tier CoV Gatekeeper Pre-Flight Inspection
dan Worker Self-Repair Loop untuk menjamin determinisme instruksi.
"""

from typing import Any, Optional
from app.core.config import settings
from app.core.logger import logger
from app.engine.tools.agent_tool_dispatcher import agent_tool_dispatcher
from app.engine.sentinel.verifier import cov_gatekeeper


async def handle_agent_tools(
    project_id: str,
    raw_response: str,
    client: Any,
    sys_p: str,
    usr_p: str,
    model: str,
    provider: str,
    temp: float,
    agent_role: str = "agent",
    stage: str = "development",
    custom_path: Optional[str] = None,
) -> str:
    """Menjalankan loop perkakas agen dengan Two-Tier CoV Gatekeeper & Worker Repair Loop."""
    step_count, cur_resp, accum = 0, raw_response, usr_p
    while step_count < agent_tool_dispatcher.max_steps:
        tc = agent_tool_dispatcher.parse_tool_call(cur_resp)
        if not tc:
            break

        # 1. CoV Pre-Flight Inspection (Tier 1 & Tier 2)
        inspection = await cov_gatekeeper.inspect(
            project_id=project_id,
            agent_role=agent_role,
            candidate_content=cur_resp,
            stage=stage,
            custom_path=custom_path,
        )

        # 2. Worker Self-Repair Loop jika status REPAIR_REQUIRED
        repair_attempts = 0
        while not inspection.approved and inspection.repair_feedback and repair_attempts < settings.COV_MAX_REPAIRS:
            repair_attempts += 1
            logger.info(
                f"Koreksi mandiri CoV [{agent_role}] ({repair_attempts}/{settings.COV_MAX_REPAIRS}): {inspection.repair_feedback}"
            )
            repair_prompt = (
                f"{cur_resp}\n\n"
                f"[TEGURAN COV GATEKEEPER]:\n{inspection.repair_feedback}\n\n"
                "Sebagai agen peran, perbaiki format perkakas atau parameter Anda di atas sekarang."
            )
            cur_resp = await client.complete(
                prompt=repair_prompt, system_prompt=sys_p, model=model, provider=provider, temperature=temp
            )
            inspection = await cov_gatekeeper.inspect(
                project_id=project_id,
                agent_role=agent_role,
                candidate_content=cur_resp,
                stage=stage,
                custom_path=custom_path,
            )
            if inspection.approved:
                break

        # 3. Non-Hijacking Tool Execution setelah disetujui CoV
        active_tc = inspection.tool_call or agent_tool_dispatcher.parse_tool_call(cur_resp)
        if active_tc and inspection.approved:
            obs = await agent_tool_dispatcher.execute_tool(project_id, active_tc["tool"], active_tc["parameters"])
            accum += f"\n[OBSERVATION dari {active_tc['tool']}]: {obs}\nLanjutkan tugas Anda."
            cur_resp = await client.complete(
                prompt=accum, system_prompt=sys_p, model=model, provider=provider, temperature=temp
            )
        else:
            break
        step_count += 1
    return cur_resp
