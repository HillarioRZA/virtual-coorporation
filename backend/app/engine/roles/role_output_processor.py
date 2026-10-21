"""
Dynamic Contract-Driven Role Output Processor Module.
Menyimpan dan memetakan artefak yang dihasilkan agen secara otonom ke dalam VentureState
menggunakan Polimorfik Contract Handlers dan pencatatan biaya token dinamis.
"""

import json
from typing import Any, Dict, Optional
from app.core.logger import logger
from app.engine.roles.contract_handlers import contract_handler_registry
from app.engine.roles.role_event_logger import log_role_event
from app.engine.runtime.state import VentureState


def _calculate_token_cost(raw_text: str, model_name: str) -> float:
    """Menghitung perkiraan biaya token secara dinamis berdasarkan model dan panjang luaran."""
    if "free" in model_name.lower():
        return 0.0
    approx_tokens = max(1, len(raw_text) // 4)
    # Rata-rata blended rate $1.50 per 1M token output untuk model berbayar standar
    return round(approx_tokens * 0.0000015, 6)


def _try_parse_payload(raw: str) -> Any:
    """Mengekstrak JSON terstruktur dari teks luaran model jika ada."""
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except Exception:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except Exception:
                pass
        return None


async def process_role_output(
    role_id: str,
    raw: str,
    state: VentureState,
    client: Any,
    sys_p: str,
    model: str,
    provider: str,
    mem: Optional[Any] = None,
    sbx: Optional[Any] = None,
    proxy: Optional[Any] = None,
    vault: Optional[Any] = None,
    actual_cost: Optional[float] = None,
) -> Dict[str, Any]:
    """Menyimpan artefak peran ke state dan mendistribusikan kontrak ke handlers polimorfik."""
    parsed_payload: Any = _try_parse_payload(raw)
    state.set_artifact(role_id, parsed_payload if parsed_payload is not None else raw)

    if isinstance(parsed_payload, dict):
        await contract_handler_registry.dispatch_sync(
            payload=parsed_payload,
            state=state,
            sbx=sbx,
            proxy=proxy,
            vault=vault,
        )

    cost_usd = actual_cost if actual_cost is not None else _calculate_token_cost(raw, model)
    state.add_token_cost(role_id.upper(), cost_usd)
    state.record_event(f"Agen @{role_id.upper()}: Tugas selesai dieksekusi ($ {cost_usd:.4f})")
    await log_role_event(mem, role_id, state, parsed_payload if parsed_payload is not None else raw, cost_usd)

    ret: Dict[str, Any] = {
        "artifact": parsed_payload if parsed_payload is not None else raw,
        "token_usage": state.token_usage,
        "event_logs": state.event_logs,
    }
    if state.business_brief:
        ret["business_brief"] = state.business_brief
    if state.system_architecture:
        ret["system_architecture"] = state.system_architecture
        ret["selected_archetype"] = state.selected_archetype
    if state.prd_spec:
        ret["prd_spec"] = state.prd_spec
    if state.openapi_spec:
        ret["openapi_spec"] = state.openapi_spec
    if state.ui_spec:
        ret["ui_spec"] = state.ui_spec
    if state.preview_url:
        ret["preview_url"] = state.preview_url
    if state.quality_scorecard:
        ret["quality_scorecard"] = state.quality_scorecard
    if state.project_name:
        ret["project_name"] = state.project_name

    return ret
