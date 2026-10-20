"""
In-Sandbox Language Server Protocol (LSP) Diagnostics Service.
Menjalankan Pyright (Python) dan TypeScript (tsc project mode) untuk deteksi error tipe real-time.
"""

import ast
import asyncio
import json
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple
from app.core.config import BASE_DIR
from app.core.logger import logger


class LSPService:
    """Layanan diagnostik tipe statis LSP dengan project-wide tsconfig filtering & AST fallback."""

    async def _run_command(self, cmd: List[str], cwd: Path) -> Tuple[int, str, str]:
        """Menjalankan perintah eksternal di direktori kerja tertentu."""
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return proc.returncode or 0, stdout.decode("utf-8", errors="ignore"), stderr.decode("utf-8", errors="ignore")

    async def get_typescript_diagnostics(
        self, root_dir: Path, target_file: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Menjalankan tsc project mode untuk mendiagnosis TypeScript tanpa mengabaikan tsconfig.json."""
        tsconfig = root_dir / "tsconfig.json"
        if not tsconfig.exists():
            return []

        cmd = ["npx", "--no-install", "tsc", "--project", "tsconfig.json", "--noEmit", "--pretty", "false"]
        diagnostics: List[Dict[str, Any]] = []
        try:
            code, out, _ = await self._run_command(cmd, cwd=root_dir)
            # Pola: path/to/file.ts(line,col): error TS1234: Message
            pattern = re.compile(r"^(.+?)\((\d+),(\d+)\):\s*error\s*(TS\d+):\s*(.+)$", re.MULTILINE)
            for match in pattern.finditer(out):
                f_path, line, col, err_code, msg = match.groups()
                clean_norm = Path(f_path).as_posix()
                if target_file and target_file.replace("\\", "/") not in clean_norm:
                    continue
                diagnostics.append({
                    "file": f_path,
                    "line": int(line),
                    "column": int(col),
                    "code": err_code,
                    "message": msg.strip(),
                    "severity": "error",
                })
        except Exception as err:
            logger.debug(f"Eksekusi tsc CLI tidak tersedia atau gagal: {err}")
        return diagnostics

    async def get_python_diagnostics(
        self, root_dir: Path, target_file: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Mendiagnosis kode Python menggunakan Pyright CLI atau fallback AST compilation check."""
        diagnostics: List[Dict[str, Any]] = []
        target_path = (root_dir / target_file) if target_file else None

        # 1. Coba Pyright jika tersedia
        try:
            cmd = ["pyright", "--outputjson"]
            if target_path and target_path.exists():
                cmd.append(str(target_path))
            code, out, _ = await self._run_command(cmd, cwd=root_dir)
            if out.strip().startswith("{"):
                data = json.loads(out)
                for item in data.get("generalDiagnostics", []):
                    if item.get("severity") == "error":
                        # Saring false positive missing imports jika sandbox belum menginstal paket
                        if item.get("rule") == "reportMissingImports":
                            continue
                        rng = item.get("range", {}).get("start", {})
                        diagnostics.append({
                            "file": item.get("file", ""),
                            "line": rng.get("line", 1) + 1,
                            "column": rng.get("character", 1) + 1,
                            "code": item.get("rule", "type_error"),
                            "message": item.get("message", ""),
                            "severity": "error",
                        })
                return diagnostics
        except Exception:
            pass

        # 2. Fallback deterministik: AST Syntax & Name Compilation Check
        if target_path and target_path.exists() and target_path.suffix == ".py":
            try:
                content = target_path.read_text(encoding="utf-8")
                compile(content, str(target_path), "exec", ast.PyCF_ONLY_AST)
            except SyntaxError as syn_err:
                diagnostics.append({
                    "file": str(target_path),
                    "line": syn_err.lineno or 1,
                    "column": syn_err.offset or 1,
                    "code": "SyntaxError",
                    "message": str(syn_err.msg),
                    "severity": "error",
                })
        return diagnostics

    async def get_diagnostics(
        self, project_id: str, file_path: str, custom_root: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Mengevaluasi file target dan mengembalikan daftar kesalahan tipe fatal."""
        root = Path(custom_root) if custom_root else (BASE_DIR.parent / "frontend" if file_path.endswith((".ts", ".tsx")) else BASE_DIR)
        clean_file = file_path.replace("\\", "/")

        if clean_file.endswith((".ts", ".tsx")):
            return await self.get_typescript_diagnostics(root, target_file=clean_file)
        if clean_file.endswith(".py"):
            return await self.get_python_diagnostics(root, target_file=clean_file)
        return []


lsp_service = LSPService()
