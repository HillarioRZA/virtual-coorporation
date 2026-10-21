"""
Auto-Correction Loop for Structured LLM Outputs.
Memvalidasi keluaran LLM terhadap skema Pydantic dan melakukan perbaikan otomatis jika gagal.
"""

import json
import re
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

from app.core.logger import logger
from app.gateway.client import UnifiedLLMClient

T = TypeVar("T", bound=BaseModel)


def extract_json_payload(raw_text: str) -> str:
    """Mengekstrak blok JSON murni dari teks mentah atau blok markdown."""
    text = raw_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text


async def parse_and_repair_schema(
    llm_client: UnifiedLLMClient,
    raw_response: str,
    system_prompt: str,
    schema_cls: Type[T],
    model: str,
    provider: str,
    max_repairs: int = 2,
) -> T:
    """Memvalidasi JSON keluaran terhadap skema Pydantic dengan auto-correction loop."""
    current_response = raw_response
    last_error: Optional[Exception] = None

    for attempt in range(max_repairs + 1):
        try:
            cleaned_json = extract_json_payload(current_response)
            parsed_data: Dict[str, Any] = json.loads(cleaned_json)
            validated_obj = schema_cls.model_validate(parsed_data)
            if attempt > 0:
                logger.info(f"Auto-correction berhasil pada iterasi ke-{attempt} untuk {schema_cls.__name__}")
            return validated_obj
        except (json.JSONDecodeError, ValidationError) as err:
            last_error = err
            logger.warning(
                f"Validasi skema [{schema_cls.__name__}] gagal (Percobaan {attempt + 1}/{max_repairs + 1}): {err}"
            )

            if attempt < max_repairs:
                repair_prompt = (
                    f"Respon sebelumnya tidak valid terhadap skema JSON yang diharapkan.\n\n"
                    f"Detail Error:\n{str(err)}\n\n"
                    f"Keluaran Anda sebelumnya:\n{current_response}\n\n"
                    f"Perbaiki respon di atas dan keluarkan HANYA JSON murni yang lolos validasi skema."
                )
                try:
                    current_response = await llm_client.complete(
                        prompt=repair_prompt,
                        system_prompt=system_prompt,
                        model=model,
                        provider=provider,
                        temperature=0.2,
                    )
                except Exception as llm_err:
                    logger.error(f"Gagal memanggil LLM saat auto-correction: {llm_err}")
                    raise RuntimeError(f"LLM failure during auto-correction: {llm_err}") from llm_err

    logger.error(f"Auto-correction loop habis ({max_repairs}x). Gagal memvalidasi {schema_cls.__name__}: {last_error}")
    raise ValueError(f"Failed to produce valid {schema_cls.__name__} after {max_repairs} repairs: {last_error}")
