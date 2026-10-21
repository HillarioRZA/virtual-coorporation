"""Internal Sovereign Corporate AI Model Router (ala 9router).

Menyediakan orkestrator perutean multi-kanal cerdas, pre-flight rate limiter (RPM/TPM/RPD),
pelacak status kesehatan kanal (health & cooldown), dan failover cascade otomatis per peran.
"""

import asyncio
from datetime import datetime, timedelta
import time
from typing import Any, Dict, List, Optional, Tuple
import httpx

from app.core.logger import logger
from app.db.token_ledger_repo import token_ledger_repo
from app.gateway.client import UnifiedLLMClient


class UpstreamChannel:
    """Representasi kanal penyedia hulu dengan metrik batas kuota dinamis."""

    def __init__(self, provider: str, model: str, rpm_limit: int = 30, tpm_limit: int = 60000) -> None:
        self.provider = provider
        self.model = model
        self.rpm_limit = rpm_limit
        self.tpm_limit = tpm_limit
        self.cooldown_until: Optional[float] = None
        self.request_timestamps: List[float] = []
        self.token_window: List[Tuple[float, int]] = []

    def is_healthy(self) -> bool:
        """Memeriksa apakah kanal tidak sedang dalam status cooldown."""
        if self.cooldown_until and time.time() < self.cooldown_until:
            return False
        self.cooldown_until = None
        return True

    def set_cooldown(self, seconds: int = 60) -> None:
        """Mengaktifkan cooldown pada kanal setelah menerima 429 atau 402."""
        self.cooldown_until = time.time() + seconds
        logger.warning(f"Kanal [{self.provider}/{self.model}] di-cooldown selama {seconds}s.")

    async def throttle_if_needed(self, estimated_tokens: int = 2000) -> None:
        """Menahan request sejenak jika laju request mendekati batas RPM/TPM."""
        now = time.time()
        self.request_timestamps = [t for t in self.request_timestamps if now - t < 60]
        self.token_window = [(t, tok) for t, tok in self.token_window if now - t < 60]
        current_rpm, current_tpm = len(self.request_timestamps), sum(tok for _, tok in self.token_window)

        if current_rpm >= self.rpm_limit or (current_tpm + estimated_tokens) >= self.tpm_limit:
            logger.info(f"Pre-flight throttling kanal [{self.provider}] (RPM: {current_rpm}/{self.rpm_limit}).")
            await asyncio.sleep(2.0)

        self.request_timestamps.append(time.time())
        self.token_window.append((time.time(), estimated_tokens))


class SovereignModelRouter:
    """Router terpadu tingkat enterprise untuk routing LLM multi-kanal otonom."""

    def __init__(self, client: Optional[UnifiedLLMClient] = None) -> None:
        self.client = client or UnifiedLLMClient()
        self.channels: Dict[str, UpstreamChannel] = {}

    def _get_channel(self, provider: str, model: str) -> UpstreamChannel:
        """Mengambil atau menginisialisasi instance UpstreamChannel."""
        key = f"{provider.lower()}:{model}"
        if key not in self.channels:
            rpm = 15 if "free" in model.lower() else 40
            tpm = 30000 if "free" in model.lower() else 80000
            self.channels[key] = UpstreamChannel(provider, model, rpm_limit=rpm, tpm_limit=tpm)
        return self.channels[key]

    async def execute_routed_completion(
        self,
        prompt: str,
        system_prompt: str = "",
        primary_provider: str = "openrouter",
        primary_model: str = "deepseek/deepseek-r1:free",
        fallback_chain: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        role_id: Optional[str] = None,
        project_id: Optional[str] = None,
        branch_id: Optional[str] = None,
        pipeline_id: Optional[str] = None,
        custom_path: Optional[str] = None,
        turn_count: int = 1,
        ticket_id: Optional[str] = None,
        thinking_level: str = "medium",
    ) -> Tuple[str, Dict[str, Any]]:
        if ticket_id:
            try:
                from app.engine.governance.financial_guardrail import financial_guardrail
                if financial_guardrail.is_ticket_frozen(ticket_id):
                    raise RuntimeError(f"Tiket [{ticket_id}] dibekukan karena melebihi batas anggaran token/biaya.")
            except Exception as fg_err:
                if "dibekukan" in str(fg_err):
                    raise fg_err
                logger.debug(f"Pengecekan financial guardrail dilewati: {fg_err}")

        if ticket_id and turn_count == 1:
            try:
                from app.engine.governance.circuit_breaker import agent_circuit_breaker
                turn_count = agent_circuit_breaker.get_status(ticket_id).turn_count
            except Exception as cb_err:
                logger.debug(f"Pengecekan turn circuit breaker dilewati: {cb_err}")

        effective_thinking = "high" if turn_count >= 2 else thinking_level
        fb_candidates: List[Tuple[str, str]] = []
        tier1_candidates: List[Tuple[str, str]] = []
        if fallback_chain:
            for item in fallback_chain:
                if item.get("is_enabled", True):
                    cand = (item.get("provider", "openrouter"), item.get("model", "qwen/qwen-2.5-coder-32b-instruct:free"))
                    if item.get("tier") == 1 or item.get("is_escalation", False):
                        tier1_candidates.append(cand)
                    else:
                        fb_candidates.append(cand)

        # Cost-IQ Auto-Escalation: jika turn_count >= 2, eskalasikan ke kandidat cadangan/Tier 1 dinamis
        if turn_count >= 2:
            escalation = tier1_candidates or fb_candidates
            if escalation:
                candidates: List[Tuple[str, str]] = escalation + [(primary_provider, primary_model)]
                logger.info(f"Auto-Escalation Tier 1 aktif (Turn {turn_count}, Thinking: {effective_thinking}): model {candidates[0]} diprioritaskan.")
            else:
                candidates = [(primary_provider, primary_model)]
        else:
            candidates = [(primary_provider, primary_model)] + fb_candidates + tier1_candidates

        last_error: Optional[Exception] = None
        for idx, (prov, mdl) in enumerate(candidates):
            channel = self._get_channel(prov, mdl)
            if not channel.is_healthy():
                logger.info(f"Melewati kanal [{prov}/{mdl}] karena sedang dalam cooldown.")
                continue

            start_time = time.time()
            try:
                await channel.throttle_if_needed(estimated_tokens=len(prompt) // 4)
                try:
                    output = await self.client.complete(
                        prompt=prompt, system_prompt=system_prompt, model=mdl,
                        provider=prov, temperature=temperature, thinking_level=effective_thinking,
                    )
                except TypeError:
                    output = await self.client.complete(
                        prompt=prompt, system_prompt=system_prompt, model=mdl,
                        provider=prov, temperature=temperature,
                    )
                from app.engine.runtime.turn_guard import turn_guard
                is_valid, cleaned_output, err_msg = turn_guard.validate_turn_output(output, f"{prov}/{mdl}")
                if not is_valid:
                    logger.warning(f"Turn Guard menolak output [{prov}/{mdl}]: {err_msg}. Memilih kandidat fallback...")
                    channel.set_cooldown(seconds=30)
                    last_error = ValueError(err_msg)
                    continue
                output = cleaned_output

                latency = int((time.time() - start_time) * 1000)
                in_tok = len(prompt) // 4
                out_tok = len(output) // 4
                is_fb = (idx > 0)
                cost = 0.0 if "free" in mdl.lower() else (in_tok * 0.0000005 + out_tok * 0.0000015)

                ledger_entry = await token_ledger_repo.record_token_usage(
                    project_id=project_id,
                    branch_id=branch_id,
                    pipeline_id=pipeline_id,
                    role_id=role_id,
                    model_name=mdl,
                    provider=prov,
                    upstream_channel=f"{prov}:{mdl}",
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                    latency_ms=latency,
                    cost_usd=cost,
                    status="SUCCESS",
                    is_fallback=is_fb,
                    custom_path=custom_path,
                )

                if ticket_id:
                    try:
                        from app.engine.governance.financial_guardrail import financial_guardrail
                        financial_guardrail.record_usage(
                            ticket_id,
                            tokens=in_tok + out_tok,
                            cost_dollars=cost,
                            project_id=project_id,
                        )
                    except Exception as fg_err:
                        logger.debug(f"Pencatatan financial guardrail dilewati: {fg_err}")

                return output, ledger_entry
            except (httpx.HTTPError, RuntimeError, Exception) as err:
                last_error = err
                cooldown_sec = 60
                if isinstance(err, httpx.HTTPStatusError) and err.response is not None:
                    retry_header = err.response.headers.get("retry-after")
                    if retry_header and retry_header.isdigit():
                        cooldown_sec = int(retry_header)
                channel.set_cooldown(cooldown_sec)
                logger.warning(f"Kanal [{prov}/{mdl}] gagal: {err}. Melakukan auto-failover ke kandidat berikutnya...")

        raise RuntimeError(f"Semua kanal upstream pada fallback chain gagal: {last_error}")


sovereign_router = SovereignModelRouter()
