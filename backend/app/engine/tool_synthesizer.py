"""
Runtime Tool Synthesizer & Dynamic Tool Registry.
Menyediakan sintesis perkakas sekali pakai dan pendaftaran alat bantu dinamis bagi agen,
dilengkapi audit keamanan OWASP Top 10 dan validasi dependensi pre-flight.
"""

import ast
import asyncio
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

from app.core.logger import logger
from app.engine.preflight_auditor import _get_declared_python_deps
from app.engine.security_scanner import security_scanner


class DynamicToolRegistry:
    """Registry alat bantu runtime yang berevolusi secara organik antar-giliran agen."""

    def __init__(self, projects_dir: Optional[Path] = None) -> None:
        """Inisialisasi DynamicToolRegistry."""
        self.projects_dir = projects_dir or Path("projects_output")
        self._registered_tools: Dict[str, Dict[str, Any]] = {}

    def get_scripts_dir(self, project_id: str) -> Path:
        """Mendapatkan path direktori skrip otomasi proyek."""
        s_dir = self.projects_dir / project_id / "scripts"
        s_dir.mkdir(parents=True, exist_ok=True)
        return s_dir

    def synthesize_tool_script(
        self,
        project_id: str,
        script_name: str,
        python_code: str,
    ) -> Dict[str, Any]:
        """Menyimpan dan memvalidasi sintaks AST serta audit keamanan OWASP skrip perkakas."""
        clean_name = script_name if script_name.endswith(".py") else f"{script_name}.py"
        try:
            tree = ast.parse(python_code)
        except SyntaxError as err:
            logger.error(f"Sintaks skrip perkakas tidak valid [{clean_name}]: {err}")
            return {"success": False, "error": f"SyntaxError: {err}"}

        target_path = self.get_scripts_dir(project_id) / clean_name
        target_path.write_text(python_code, encoding="utf-8")

        # 1. Audit Keamanan AST OWASP Top 10
        findings = security_scanner._scan_python_ast(target_path)
        critical_findings = [f for f in findings if f.severity in ("CRITICAL", "HIGH")]
        if critical_findings:
            target_path.unlink(missing_ok=True)
            logger.warning(f"Skrip [{clean_name}] ditolak karena celah OWASP: {critical_findings[0].title}")
            return {
                "success": False,
                "error": f"Security Violation: [{critical_findings[0].severity}] {critical_findings[0].title}",
            }

        # 2. Audit Dependensi Pre-flight
        declared_req = self.projects_dir / project_id / "backend" / "requirements.txt"
        declared_deps = _get_declared_python_deps(declared_req)

        imported_pkgs = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_pkgs.add(alias.name.split(".")[0].lower())
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_pkgs.add(node.module.split(".")[0].lower())

        unknown_pkgs = [
            pkg for pkg in imported_pkgs
            if pkg not in sys.stdlib_module_names
            and pkg not in declared_deps
            and pkg not in {"app", "fastapi", "pydantic", "sqlite3", "pytest"}
        ]
        if unknown_pkgs:
            target_path.unlink(missing_ok=True)
            logger.warning(f"Skrip [{clean_name}] ditolak karena paket tidak terdaftar: {unknown_pkgs}")
            return {
                "success": False,
                "error": f"Undeclared Dependency: Paket {unknown_pkgs} belum terdaftar di requirements.txt.",
            }

        logger.info(f"Skrip perkakas lolos audit keamanan OWASP & dependensi: {target_path}")
        return {
            "success": True,
            "script_name": clean_name,
            "path": str(target_path),
        }

    async def execute_ephemeral_tool(
        self,
        project_id: str,
        script_name: str,
        args: Optional[List[str]] = None,
        timeout_seconds: float = 10.0,
    ) -> Dict[str, Any]:
        """Mengeksekusi skrip perkakas sekali pakai di lingkungan terisolasi dengan batas waktu."""
        clean_name = script_name if script_name.endswith(".py") else f"{script_name}.py"
        script_path = self.get_scripts_dir(project_id) / clean_name

        if not script_path.exists():
            return {"success": False, "error": f"Berkas skrip {clean_name} tidak ditemukan."}

        cmd = [sys.executable, str(script_path)] + (args or [])
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(self.projects_dir / project_id),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_seconds)
            exit_code = proc.returncode

            out_text = stdout.decode("utf-8", errors="ignore").strip()
            err_text = stderr.decode("utf-8", errors="ignore").strip()

            if exit_code == 0:
                self._registered_tools[f"{project_id}:{clean_name}"] = {
                    "project_id": project_id,
                    "script": clean_name,
                    "status": "VERIFIED_ACTIVE",
                }

            return {
                "success": exit_code == 0,
                "exit_code": exit_code,
                "stdout": out_text,
                "stderr": err_text,
            }
        except asyncio.TimeoutError:
            logger.error(f"Eksekusi perkakas [{clean_name}] melebihi timeout {timeout_seconds}s")
            return {"success": False, "error": f"Execution timed out ({timeout_seconds}s)"}
        except OSError as err:
            logger.error(f"Gagal menjalankan skrip [{clean_name}]: {err}")
            return {"success": False, "error": str(err)}

    def list_active_tools(self, project_id: str) -> List[str]:
        """Mendapatkan daftar perkakas aktif yang terverifikasi untuk proyek tertentu."""
        prefix = f"{project_id}:"
        return [k.replace(prefix, "") for k in self._registered_tools.keys() if k.startswith(prefix)]


tool_synthesizer = DynamicToolRegistry()
