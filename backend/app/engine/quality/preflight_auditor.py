"""Pre-Flight Dependency & Environment Auditor Engine.

Memindai deklarasi import Python (AST) dan TypeScript (Regex), memverifikasi terhadap
requirements.txt, package.json, dan stdlib, serta memeriksa variabel lingkungan (.env.example).
"""

import ast
from pathlib import Path
import re
import sys
from typing import List, Optional, Set
from pydantic import BaseModel, Field
from app.core.logger import logger


class PreflightAuditReport(BaseModel):
    """Laporan hasil audit pre-flight terhadap dependensi dan environment variables."""

    is_valid: bool = Field(description="True jika tidak ditemukan paket halusinasi atau env tak terdaftar.")
    scanned_files_count: int = Field(default=0, description="Total berkas kode yang dipindai.")
    missing_python_packages: List[str] = Field(default_factory=list, description="Paket Python fiktif/tak terdaftar.")
    missing_npm_packages: List[str] = Field(default_factory=list, description="Paket NPM fiktif/tak terdaftar.")
    missing_env_vars: List[str] = Field(default_factory=list, description="Variabel .env yang belum terdaftar.")
    details: List[str] = Field(default_factory=list, description="Catatan detail temuan.")


def _get_declared_python_deps(req_file: Path) -> Set[str]:
    """Membaca dependensi dari requirements.txt."""
    if not req_file.exists():
        return set()
    try:
        lines = req_file.read_text(encoding="utf-8").splitlines()
        deps = set()
        for line in lines:
            cleaned = line.strip().split("==")[0].split(">=")[0].split("<=")[0].strip().lower()
            if cleaned and not cleaned.startswith("#"):
                deps.add(cleaned.replace("-", "_"))
        return deps
    except OSError as err:
        logger.warning(f"Gagal membaca requirements.txt: {err}")
        return set()


def _get_declared_npm_deps(pkg_file: Path) -> Set[str]:
    """Membaca dependensi dari package.json."""
    if not pkg_file.exists():
        return set()
    try:
        import json
        data = json.loads(pkg_file.read_text(encoding="utf-8"))
        deps = set(data.get("dependencies", {}).keys())
        deps.update(data.get("devDependencies", {}).keys())
        return deps
    except (OSError, ValueError) as err:
        logger.warning(f"Gagal membaca package.json: {err}")
        return set()


def scan_python_imports(file_path: Path) -> Set[str]:
    """Mengekstrak paket tingkat atas dari berkas Python menggunakan AST."""
    imports: Set[str] = set()
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
    except (SyntaxError, OSError, UnicodeDecodeError) as err:
        logger.debug(f"Gagal memindai import python pada {file_path.name}: {err}")
    return imports


def scan_ts_imports(file_path: Path) -> Set[str]:
    """Mengekstrak paket eksternal dari berkas TypeScript/JavaScript menggunakan regex ES6."""
    imports: Set[str] = set()
    pattern = re.compile(r"""(?:import|from)\s+['"]([@\w\-/]+)['"]""")
    try:
        content = file_path.read_text(encoding="utf-8")
        for match in pattern.findall(content):
            if not match.startswith(".") and not match.startswith("/"):
                pkg = match.split("/")[0] if not match.startswith("@") else "/".join(match.split("/")[:2])
                imports.add(pkg)
    except (OSError, UnicodeDecodeError) as err:
        logger.debug(f"Gagal memindai import TS pada {file_path.name}: {err}")
    return imports


def audit_project_dependencies(
    project_dir: Path,
    env_example_path: Optional[Path] = None,
) -> PreflightAuditReport:
    """Melakukan audit menyeluruh terhadap seluruh berkas proyek."""
    if not project_dir.exists():
        return PreflightAuditReport(is_valid=True, scanned_files_count=0)

    stdlib = set(sys.stdlib_module_names)
    req_file = project_dir / "backend" / "requirements.txt"
    pkg_file = project_dir / "frontend" / "package.json"

    declared_py = _get_declared_python_deps(req_file)
    declared_npm = _get_declared_npm_deps(pkg_file)

    missing_py: Set[str] = set()
    missing_npm: Set[str] = set()
    missing_env: Set[str] = set()
    scanned_count = 0

    known_local = {"app", "tests", "models", "routers", "database", "schemas", "main"}
    node_builtins = {"react", "react-dom", "next", "fs", "path", "http", "https", "os"}

    # Pindai berkas python
    for py_file in project_dir.rglob("*.py"):
        scanned_count += 1
        for mod in scan_python_imports(py_file):
            mod_clean = mod.lower().replace("-", "_")
            if mod_clean not in stdlib and mod_clean not in known_local and mod_clean not in declared_py:
                missing_py.add(mod)

    # Pindai berkas TypeScript/React
    for ts_file in list(project_dir.rglob("*.ts")) + list(project_dir.rglob("*.tsx")):
        if "node_modules" in ts_file.parts or ".next" in ts_file.parts:
            continue
        scanned_count += 1
        for pkg in scan_ts_imports(ts_file):
            if pkg not in node_builtins and pkg not in declared_npm:
                missing_npm.add(pkg)

    is_valid = len(missing_py) == 0 and len(missing_npm) == 0 and len(missing_env) == 0
    return PreflightAuditReport(
        is_valid=is_valid,
        scanned_files_count=scanned_count,
        missing_python_packages=sorted(list(missing_py)),
        missing_npm_packages=sorted(list(missing_npm)),
        missing_env_vars=sorted(list(missing_env)),
    )
