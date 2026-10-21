"""
Secretary Role Resolver & Telegram Tool Synthesizer Bridge.
Mendeteksi peran Sekretaris yang didaftarkan dari UI dengan izin 'chat_telegram'
dan menangani proposal pembuatan perkakas dinamis baru dari interaksi Founder.
"""

import json
import re
from typing import Any, Dict, Optional
from app.core.logger import logger
from app.db.role_repo import role_repo
from app.engine.tools.dynamic_tool_registry import dynamic_tool_registry


async def resolve_secretary_role(custom_path: Optional[str] = None) -> Dict[str, Any]:
    """Menemukan profil peran Sekretaris dari basis data corporate_roles."""
    try:
        roles = await role_repo.get_roles(custom_path=custom_path)
        for r in roles:
            perms = r.get("tool_permissions", [])
            # Prioritas 1: Peran dengan izin eksplisit 'chat_telegram' atau 'telegram'
            if "chat_telegram" in perms or "telegram" in perms:
                return r
            # Prioritas 2: ID atau nama peran Sekretaris / Chief of Staff
            if r.get("id") in ("role_secretary", "role_cos"):
                return r
            r_name = str(r.get("name", "")).lower()
            if "secretary" in r_name or "sekretaris" in r_name:
                return r
    except Exception as err:
        logger.warning(f"Gagal memuat peran sekretaris dari DB: {err}")

    # Fallback default profil sekretaris
    return {
        "id": "role_secretary",
        "name": "Sekretaris Eksekutif",
        "model_name": "deepseek/deepseek-r1:free",
        "model_provider": "openrouter",
        "temperature": 0.4,
        "system_prompt_template": "Anda adalah Sekretaris Eksekutif Founder di Silicon Sovereign Startup. Jawab ringkas, taktis, dan solutif.",
        "tool_permissions": ["chat_telegram", "runtime_tool_builder", "inspect_db_schema"],
    }


def build_secretary_prompt(role: Dict[str, Any]) -> str:
    """Menyusun system prompt sekretaris dengan instruksi sintesis tools otomatis."""
    base_prompt = role.get("system_prompt_template") or "Anda adalah Sekretaris Eksekutif Founder."
    job_desc = role.get("job_description", "")
    job_section = f"\n\nFokus Jobdesk: {job_desc}" if job_desc else ""

    instructions = (
        f"{base_prompt}{job_section}\n\n"
        "Keahlian & Mandat Tambahan:\n"
        "Anda memiliki otorisasi penuh untuk merancang perkakas (tools) baru bagi sistem atas arahan Founder.\n"
        "Bila Founder menginstruksikan pembuatan perkakas, Anda WAJIB menyertakan blok kode JSON pembuatan tool "
        "di akhir respons Anda persis dengan format berikut:\n"
        "```tool_proposal\n"
        "{\n"
        '  "name": "nama_tool_snake_case",\n'
        '  "description": "Deskripsi singkat fungsi perkakas",\n'
        '  "parameters_schema": {"param1": "str", "param2": "int"},\n'
        '  "python_code": "def nama_tool_snake_case(param1: str, param2: int) -> dict:\\n    return {\\"status\\": \\"success\\"}"\n'
        "}\n"
        "```\n"
        "Sistem akan langsung mendaftarkan perkakas tersebut ke registri korporat."
    )
    return instructions


async def extract_and_register_tool_proposal(
    llm_reply: str,
    creator_role_id: str = "role_secretary",
    custom_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Mengekstrak blok proposal perkakas dari respons LLM dan mendaftarkannya ke DynamicToolRegistry."""
    pattern = r"```(?:tool_proposal|json)?\s*(\{[\s\S]*?\"name\"[\s\S]*?\"python_code\"[\s\S]*?\})\s*```"
    match = re.search(pattern, llm_reply)
    if not match:
        return None

    try:
        raw_json = match.group(1)
        data = json.loads(raw_json)
        name = str(data.get("name", "")).strip().lower()
        if not name or not data.get("python_code"):
            return None

        # Daftarkan ke DynamicToolRegistry
        proposal = await dynamic_tool_registry.propose_tool(
            name=name,
            description=data.get("description", "Perkakas dinamis dibuat oleh Sekretaris via Telegram"),
            parameters_schema=data.get("parameters_schema", {}),
            python_code=data.get("python_code", ""),
            created_by=creator_role_id,
            custom_path=custom_path,
        )
        logger.info(f"Sekretaris berhasil mendaftarkan perkakas baru via Telegram: [{name}]")
        return proposal
    except json.JSONDecodeError as j_err:
        logger.debug(f"JSON proposal perkakas dari Telegram tidak valid: {j_err}")
    except Exception as err:
        logger.warning(f"Gagal memproses proposal perkakas dari Telegram: {err}")
    return None


async def execute_secretary_chat(
    llm_client: Any,
    text: str,
    custom_path: Optional[str] = None,
) -> str:
    """Menjalankan dialog eksekutif dengan Sekretaris dan mendaftarkan proposal perkakas bila ada."""
    sec_role = await resolve_secretary_role(custom_path=custom_path)
    sys_prompt = build_secretary_prompt(sec_role)
    model = sec_role.get("model_name") or "deepseek/deepseek-r1:free"
    provider = sec_role.get("model_provider") or "openrouter"
    temperature = float(sec_role.get("temperature", 0.4))

    try:
        reply = await llm_client.complete(
            prompt=text,
            system_prompt=sys_prompt,
            model=model,
            provider=provider,
            temperature=temperature,
        )
        proposal = await extract_and_register_tool_proposal(
            llm_reply=reply,
            creator_role_id=sec_role.get("id", "role_secretary"),
            custom_path=custom_path,
        )
        if proposal:
            p_name = proposal["name"]
            reply += (
                f"\n\n🛠️ *[Perkakas Baru Berhasil Diajukan]*:\n"
                f"Perkakas `{p_name}` telah didaftarkan ke sistem dengan status `PENDING_APPROVAL`.\n"
                f"Ketik `/approve {p_name}` untuk mengaktifkannya secara instan!"
            )
        return reply
    except Exception as err:
        logger.error(f"Error pada dialog sekretaris: {err}")
        return f"Maaf Founder, terdapat kendala saat memproses arahan: {err}"
