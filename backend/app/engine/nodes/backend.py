"""
Backend Engineer Node.
Menghasilkan kode produksi FastAPI, model SQLAlchemy, skrip migrasi Alembic, dan adapter produksi.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logger import logger
from app.core.prompts import load_prompt
from app.engine.memory import MemoryManager
from app.engine.nodes.auto_correction import parse_and_repair_schema
from app.engine.state import VentureState
from app.gateway.client import UnifiedLLMClient


class BackendOutputEnvelope(BaseModel):
    """Skema validasi ketat untuk keluaran kode Backend Engineer."""

    main_code: str = Field(..., min_length=20, description="Kode utama main.py FastAPI.")
    models_code: str = Field(..., min_length=20, description="Kode models.py SQLAlchemy.")
    routers_code: str = Field(..., min_length=20, description="Kode routers.py CRUD endpoints.")
    migration_code: str = Field(..., min_length=20, description="Skrip migrasi alembic_migration.py.")
    requirements_content: str = Field(..., min_length=10, description="Daftar dependensi requirements.txt.")


from app.engine.scaffolding import scaffold_standalone_backend


PROJECTS_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "projects_output"


def write_backend_files(
    project_id: str,
    envelope: BackendOutputEnvelope,
    read_only_files: Optional[List[str]] = None,
) -> Path:
    """Menulis berkas kode backend produksi dan switching adapter frontend."""
    output_dir = PROJECTS_OUTPUT_DIR / project_id / "backend"
    output_dir.mkdir(parents=True, exist_ok=True)

    read_only = set(read_only_files or [])
    targets = {
        "main.py": envelope.main_code,
        "models.py": envelope.models_code,
        "routers.py": envelope.routers_code,
        "alembic_migration.py": envelope.migration_code,
        "requirements.txt": envelope.requirements_content,
    }

    for fname, code in targets.items():
        if fname in read_only or f"backend/{fname}" in read_only or fname.startswith("test_"):
            logger.warning(f"Adversarial TDD Guardrail: Modifikasi berkas {fname} diblokir (Read-Only).")
            continue
        (output_dir / fname).write_text(code, encoding="utf-8")

    # Tulis berkas pendukung FastAPI mandiri (database.py, schemas.py, README.md)
    scaffold_standalone_backend(output_dir, project_id)

    # TASK-6.1.4: Update konfigurasi frontend untuk beralih ke HttpServiceAdapter di produksi
    fe_dir = PROJECTS_OUTPUT_DIR / project_id / "frontend"
    if fe_dir.exists():
        prod_env = fe_dir / ".env.production"
        prod_env.write_text("NEXT_PUBLIC_APP_STAGE=production\nNEXT_PUBLIC_API_URL=http://localhost:8000/api/v1\n", encoding="utf-8")
        logger.info(f"Frontend stage switched to PRODUCTION in {prod_env}")

    logger.info(f"Kode backend produksi tersimpan di: {output_dir}")
    return output_dir



async def backend_engineering_node(
    state: VentureState,
    llm_client: Optional[UnifiedLLMClient] = None,
    memory_manager: Optional[MemoryManager] = None,
) -> Dict[str, Any]:
    """Node eksekusi Backend Engineer untuk mensintesis kode produksi."""
    logger.info(f"Memulai Backend Engineering Node untuk [{state.project_id}]")
    client = llm_client or UnifiedLLMClient()
    mem = memory_manager or MemoryManager()

    system_prompt = load_prompt("backend_prompt")
    model, provider = settings.get_agent_model_and_provider("BACKEND")

    user_instruction = (
        f"Proyek: {state.project_name}\n"
        f"OpenAPI Spec: {state.openapi_spec or {}}\n"
        f"Tech Stack: {state.system_architecture.model_dump() if state.system_architecture else {}}\n"
        "Hasilkan kode backend produksi FastAPI lengkap, model SQLAlchemy, router, dan skrip migrasi."
    )

    raw_response = await client.complete(
        prompt=user_instruction,
        system_prompt=system_prompt,
        model=model,
        provider=provider,
    )

    from app.engine.agent_tool_dispatcher import agent_tool_dispatcher
    step_count = 0
    prompt_accum = user_instruction
    while step_count < agent_tool_dispatcher.max_steps:
        tool_call = agent_tool_dispatcher.parse_tool_call(raw_response)
        if not tool_call:
            break
        obs = await agent_tool_dispatcher.execute_tool(state.project_id, tool_call["tool"], tool_call["parameters"])
        prompt_accum += f"\n[OBSERVATION dari {tool_call['tool']}]: {obs}\nLanjutkan menyusun kode backend final."
        raw_response = await client.complete(prompt=prompt_accum, system_prompt=system_prompt, model=model, provider=provider)
        step_count += 1

    envelope = await parse_and_repair_schema(
        llm_client=client,
        raw_response=raw_response,
        system_prompt=system_prompt,
        schema_cls=BackendOutputEnvelope,
        model=model,
        provider=provider,
        max_repairs=2,
    )

    write_backend_files(state.project_id, envelope, state.read_only_files)
    cost = 0.02
    state.add_token_cost("BACKEND", cost)


    await mem.log_event(
        project_id=state.project_id,
        stage="PRODUCTION_HARDENING",
        sender_role="BACKEND",
        recipient_role="QA",
        event_type="ARTIFACT_PUBLISHED",
        content="Backend Engineer berhasil menyusun FastAPI endpoints, SQLAlchemy models, dan skrip migrasi.",
        artifact_ref="backend_code",
        token_cost=cost,
    )

    state.record_event(f"Backend Node: Kode produksi backend berhasil disintesis ($ {cost:.4f})")
    return {"token_usage": state.token_usage, "event_logs": state.event_logs}
