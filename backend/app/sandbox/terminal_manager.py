"""
Interactive Sandbox Terminal Process Manager.
Menjalankan perintah shell asinkron di dalam konteks folder proyek dengan streaming stdout/stderr instan dan guardrails.
"""

import asyncio
from datetime import datetime
import os
from pathlib import Path
import re
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.core.logger import logger

BLOCKED_PATTERNS: List[re.Pattern] = [
    re.compile(r"\brmdir\s+/[sS]\s+/[qQ]\s+[cC]:", re.IGNORECASE),
    re.compile(r"\bdel\s+/[fF]\s+/[sS]\s+/[qQ]\s+[cC]:\\windows", re.IGNORECASE),
    re.compile(r"\bformat\s+[a-zA-Z]:", re.IGNORECASE),
    re.compile(r"\bshutdown\s+/[sSrRtT]", re.IGNORECASE),
    re.compile(r"\brm\s+-rf\s+/(etc|boot|sys|usr|bin)?$", re.IGNORECASE),
    re.compile(r":\(\)\s*\{\s*:\|:&\s*\};:", re.IGNORECASE),
]


class TerminalManager:
    """Pengelola eksekusi terminal shell interaktif di direktori proyek."""

    def __init__(self, base_output_dir: Optional[Path] = None) -> None:
        """Inisialisasi TerminalManager."""
        self.base_output_dir = base_output_dir or Path("projects_output")

    def get_working_directory(self, project_id: str) -> Path:
        """Mendapatkan path direktori kerja proyek (membuat jika belum ada)."""
        p_dir = self.base_output_dir / project_id
        p_dir.mkdir(parents=True, exist_ok=True)
        return p_dir

    def is_command_safe(self, command: str) -> bool:
        """Memeriksa apakah perintah aman dari instruksi perusakan OS."""
        cmd_clean = command.strip()
        for pattern in BLOCKED_PATTERNS:
            if pattern.search(cmd_clean):
                return False
        return True

    def _terminate_proc(self, proc: asyncio.subprocess.Process) -> None:
        """Menghentikan proses dan seluruh child processes secara bersih."""
        try:
            proc.kill()
        except Exception:
            pass
        if os.name == "nt" and proc.pid:
            try:
                import subprocess
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=2.0,
                )
            except Exception:
                pass

    async def execute_command_stream(
        self,
        project_id: str,
        command: str,
        timeout_seconds: float = 60.0,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Mengeksekusi perintah shell secara asinkron dan men-stream baris per baris secara real-time."""
        cwd_path = self.get_working_directory(project_id)
        cmd_clean = command.strip()

        if not cmd_clean:
            yield {"type": "exit", "code": 0, "duration_ms": 0}
            return

        if not self.is_command_safe(cmd_clean):
            yield {
                "type": "stderr",
                "data": f"🛡️ SECURITY GUARDRAIL: Perintah [{cmd_clean}] diblokir karena berpotensi merusak OS.\n",
            }
            yield {"type": "exit", "code": 126, "duration_ms": 0}
            return

        yield {
            "type": "start",
            "command": cmd_clean,
            "cwd": str(cwd_path),
            "timestamp": datetime.utcnow().isoformat(),
        }

        start_time = time.time()
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd_clean,
                cwd=str(cwd_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            queue: asyncio.Queue = asyncio.Queue()

            async def stream_reader(stream: asyncio.StreamReader, event_type: str) -> None:
                try:
                    while True:
                        line = await stream.readline()
                        if not line:
                            break
                        decoded = line.decode("utf-8", errors="replace")
                        await queue.put({"type": event_type, "data": decoded})
                except Exception:
                    pass

            out_task = asyncio.create_task(stream_reader(proc.stdout, "stdout"))
            err_task = asyncio.create_task(stream_reader(proc.stderr, "stderr"))

            async def wait_process() -> None:
                await proc.wait()
                await asyncio.gather(out_task, err_task, return_exceptions=True)
                await queue.put(None)

            asyncio.create_task(wait_process())

            deadline = time.time() + timeout_seconds
            while True:
                remaining = deadline - time.time()
                if remaining <= 0:
                    self._terminate_proc(proc)
                    yield {
                        "type": "stderr",
                        "data": f"⏱️ TIMEOUT: Perintah melampaui batas {timeout_seconds} detik dan dihentikan.\n",
                    }
                    yield {"type": "exit", "code": 124, "duration_ms": int((time.time() - start_time) * 1000)}
                    return

                try:
                    item = await asyncio.wait_for(queue.get(), timeout=min(remaining, 0.2))
                    if item is None:
                        break
                    yield item
                except asyncio.TimeoutError:
                    if proc.returncode is not None and queue.empty():
                        break

            duration_ms = int((time.time() - start_time) * 1000)
            yield {
                "type": "exit",
                "code": proc.returncode,
                "duration_ms": duration_ms,
            }
            logger.info(f"Terminal exec [{cmd_clean}] in [{project_id}] exited with {proc.returncode} in {duration_ms}ms")

        except Exception as err:
            logger.error(f"Gagal menjalankan terminal process [{cmd_clean}]: {err}")
            yield {"type": "stderr", "data": f"Terminal Error: {str(err)}\n"}
            yield {"type": "exit", "code": 1, "duration_ms": int((time.time() - start_time) * 1000)}


terminal_manager = TerminalManager()
