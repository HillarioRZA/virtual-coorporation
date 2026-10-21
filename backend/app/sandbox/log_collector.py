"""
Sandbox Container Runtime Log Collector (Inspired by Cline / Roo Code).
Mengekstrak log runtime stdout/stderr dari kontainer sandbox untuk diagnostik
error Next.js (misal: hydration mismatch, window is not defined) secara real-time.
"""

import asyncio
from typing import Optional
from app.core.logger import logger


class SandboxLogCollector:
    """Pengumpul log eksekusi kontainer sandbox untuk umpan balik agen kognitif."""

    @staticmethod
    async def get_container_logs(
        project_id: str,
        service: str = "frontend",
        tail_lines: int = 50,
    ) -> Optional[str]:
        """
        Mengambil cuplikan log terakhir dari kontainer sandbox Docker.
        Format kontainer: sandbox_{project_id}_{service}.
        """
        container_name = f"sandbox_{project_id}_{service}"
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker",
                "logs",
                "--tail",
                str(tail_lines),
                container_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
            combined = (stdout.decode("utf-8", errors="ignore") + "\n" + stderr.decode("utf-8", errors="ignore")).strip()
            if combined:
                return combined
        except asyncio.TimeoutError:
            logger.debug(f"Timeout saat mengambil log kontainer [{container_name}].")
        except (OSError, Exception) as err:
            logger.debug(f"Pemeriksaan log kontainer [{container_name}] dilewati: {err}")

        return None

    @classmethod
    async def build_runtime_error_context(
        cls,
        project_id: str,
        service: str = "frontend",
        tail_lines: int = 40,
    ) -> Optional[str]:
        """Menyusun blok prompt diagnostik log runtime kontainer untuk perbaikan bug otonom."""
        raw_logs = await cls.get_container_logs(project_id, service, tail_lines)
        if not raw_logs:
            return None

        # Filter baris yang relevan dengan error atau warning
        filtered_lines = [
            line for line in raw_logs.splitlines()
            if any(term in line.lower() for term in ["error", "fail", "warn", "exception", "syntax", "cannot find"])
        ]
        log_sample = "\n".join(filtered_lines[-20:]) if filtered_lines else raw_logs[-1200:]

        return (
            f"[SANDBOX RUNTIME CONTAINER LOGS ({service.upper()})]:\n"
            f"```text\n{log_sample}\n```\n"
            f"Perhatikan diagnostik runtime di atas untuk memperbaiki bug."
        )


sandbox_log_collector = SandboxLogCollector()
