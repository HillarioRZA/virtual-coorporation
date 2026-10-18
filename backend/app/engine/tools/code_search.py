"""
Symbol & Text Grep Codebase Search Tool.
Pencarian cepat definisi simbol dan pola teks lintas berkas berbasis Python murni.
"""

from pathlib import Path
import re
from typing import Any, Dict, List, Optional

from app.core.logger import logger

IGNORE_DIRS = {".git", ".snapshots", "node_modules", "__pycache__", ".pytest_cache", ".next", "dist"}


class CodebaseSearcher:
    """Pencari simbol dan grep teks lintas repositori berbasis Python murni."""

    def __init__(self, projects_dir: Optional[Path] = None) -> None:
        """Inisialisasi CodebaseSearcher."""
        self.projects_dir = projects_dir or Path("projects_output")

    def search_codebase(
        self,
        project_id: str,
        query: str,
        is_symbol_only: bool = False,
        file_extension: Optional[str] = None,
        max_results: int = 15,
    ) -> Dict[str, Any]:
        """Mencari simbol fungsi/kelas atau pola teks dalam proyek."""
        base_dir = self.projects_dir / project_id
        if not base_dir.exists():
            return {"success": False, "query": query, "results": [], "total_matches": 0}

        results: List[Dict[str, Any]] = []
        if is_symbol_only:
            pattern = re.compile(rf"^\s*(?:def|class|interface|type|async def)\s+({re.escape(query)})\b", re.IGNORECASE)
        else:
            pattern = re.compile(re.escape(query), re.IGNORECASE)

        try:
            for file_path in base_dir.rglob("*"):
                if file_path.is_file():
                    if any(ignored in file_path.parts for ignored in IGNORE_DIRS):
                        continue
                    if file_extension and not file_path.name.endswith(file_extension):
                        continue
                    try:
                        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                        for idx, line in enumerate(lines, start=1):
                            if pattern.search(line):
                                rel_path = str(file_path.relative_to(base_dir)).replace("\\", "/")
                                results.append({
                                    "file": rel_path,
                                    "line": idx,
                                    "snippet": line.strip()[:150],
                                })
                                if len(results) >= max_results:
                                    break
                    except OSError:
                        continue
                if len(results) >= max_results:
                    break
        except Exception as err:
            logger.error(f"Gagal melakukan pencarian kode [{project_id}]: {err}")
            return {"success": False, "error": str(err), "results": []}

        logger.info(f"CodeSearch: Ditemukan {len(results)} kecocokan untuk '{query}' di [{project_id}]")
        return {
            "success": True,
            "query": query,
            "results": results,
            "total_matches": len(results),
        }


code_searcher = CodebaseSearcher()
