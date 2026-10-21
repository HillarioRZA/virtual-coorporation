"""
Lightweight AST Repository Symbol Mapper for Day-2 Multi-Agent Codebase Maintenance.
Memindai berkas Python dan TypeScript lokal di projects_output/<project_id>
untuk mengekstrak peta simbol (class, method, interface, export) hemat token.
"""

import ast
from pathlib import Path
import re
from typing import Dict, List, Optional, Set
from app.core.logger import logger

_IGNORE_DIRS: Set[str] = {
    "node_modules", ".next", "__pycache__", "venv", ".venv", ".git", "dist", "build", ".pytest_cache"
}
_CODE_EXTENSIONS: Set[str] = {".py", ".ts", ".tsx", ".js", ".jsx"}
_MAX_FILES_TO_SCAN: int = 80
_MAX_SYMBOLS_PER_FILE: int = 12
_DEFAULT_CHAR_BUDGET: int = 3500  # ~875 token budget


class ProjectRepoMapper:
    """Pembuat peta hierarki simbol kode proyek lokal untuk efisiensi Day-2 engineering."""

    @staticmethod
    def _extract_python_symbols(content: str) -> List[str]:
        """Mengekstrak nama class dan fungsi dari kode Python menggunakan AST parser."""
        symbols: List[str] = []
        try:
            tree = ast.parse(content)
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
                    base_str = f"({', '.join(bases)})" if bases else ""
                    symbols.append(f"class {node.name}{base_str}")
                    for item in node.body[:4]:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            prefix = "async " if isinstance(item, ast.AsyncFunctionDef) else ""
                            symbols.append(f"  {prefix}def {item.name}()")
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
                    symbols.append(f"{prefix}def {node.name}()")
        except (SyntaxError, Exception) as err:
            logger.debug(f"AST parse Python diabaikan: {err}")
        return symbols[:_MAX_SYMBOLS_PER_FILE]

    @staticmethod
    def _extract_typescript_symbols(content: str) -> List[str]:
        """Mengekstrak interfaces, types, dan exported functions dari TypeScript/TSX."""
        symbols: List[str] = []
        patterns = [
            r"export\s+interface\s+([A-Za-z0-9_]+)",
            r"export\s+type\s+([A-Za-z0-9_]+)",
            r"export\s+(?:default\s+)?(?:async\s+)?function\s+([A-Za-z0-9_]+)",
            r"export\s+const\s+([A-Za-z0-9_]+)\s*=",
            r"export\s+class\s+([A-Za-z0-9_]+)",
        ]
        try:
            for pat in patterns:
                for match in re.finditer(pat, content):
                    sym_name = match.group(1)
                    if "interface" in pat:
                        symbols.append(f"interface {sym_name}")
                    elif "type" in pat:
                        symbols.append(f"type {sym_name}")
                    elif "function" in pat:
                        symbols.append(f"function {sym_name}()")
                    elif "class" in pat:
                        symbols.append(f"class {sym_name}")
                    else:
                        symbols.append(f"const {sym_name}")
        except Exception as err:
            logger.debug(f"Regex TypeScript diabaikan: {err}")
        return symbols[:_MAX_SYMBOLS_PER_FILE]

    @classmethod
    def generate_symbol_map(cls, project_dir: Path, max_chars: int = _DEFAULT_CHAR_BUDGET) -> Optional[str]:
        """Menghasilkan representasi pohon ringkas simbol kode dengan kontrol anggaran token."""
        if not project_dir.exists() or not project_dir.is_dir():
            return None

        file_symbol_map: Dict[str, List[str]] = {}
        try:
            candidates: List[Path] = [
                p for p in project_dir.rglob("*")
                if p.is_file() and p.suffix in _CODE_EXTENSIONS
                and not any(ignored in p.parts for ignored in _IGNORE_DIRS)
            ]

            def _rank(p: Path) -> int:
                name_l = p.name.lower()
                bonus = -10 if any(k in name_l for k in ["main", "app", "page", "api", "route", "schema"]) else 0
                return len(p.parts) + bonus

            candidates.sort(key=_rank)

            for path in candidates[:_MAX_FILES_TO_SCAN]:
                rel_path = path.relative_to(project_dir).as_posix()
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                except (IOError, OSError):
                    continue

                syms = cls._extract_python_symbols(content) if path.suffix == ".py" else cls._extract_typescript_symbols(content)
                if syms:
                    file_symbol_map[rel_path] = syms
        except Exception as scan_err:
            logger.warning(f"Error memindai repositori proyek [{project_dir}]: {scan_err}")
            return None

        if not file_symbol_map:
            return None

        header = f"[PROJECT REPOSITORY SYMBOL MAP (DAY-2 - {len(file_symbol_map)} files)]:\nRoot: {project_dir.name}/"
        lines: List[str] = [header]
        current_len = len(header)
        omitted = 0

        for rel_file, syms in file_symbol_map.items():
            entry_lines = [f"  {rel_file}:"] + [f"    - {s}" for s in syms]
            entry_str = "\n".join(entry_lines)
            if current_len + len(entry_str) > max_chars:
                omitted += 1
                continue
            lines.append(entry_str)
            current_len += len(entry_str) + 1

        if omitted > 0:
            lines.append(f"  ... (+{omitted} files omitted to fit token budget)")

        return "\n".join(lines)


repo_mapper = ProjectRepoMapper()
