"""
OpenAPI Contract Compliance Validator.
Membandingkan endpoint yang baru dibuat agen secara otomatis terhadap berkas openapi.json SSOT.
"""

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from app.core.logger import logger


class ContractValidator:
    """Validator kepatuhan kontrak API antara kode implementasi dan OpenAPI SSOT."""

    def __init__(self, projects_dir: Optional[Path] = None) -> None:
        """Inisialisasi ContractValidator."""
        self.projects_dir = projects_dir or Path("projects_output")

    def _load_openapi_spec(self, project_id: str) -> Dict[str, Any]:
        """Memuat berkas openapi.json dari direktori proyek."""
        spec_path = self.projects_dir / project_id / "openapi.json"
        if not spec_path.exists():
            spec_path = self.projects_dir / project_id / "backend" / "openapi.json"

        if not spec_path.exists():
            return {}

        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as err:
            logger.error(f"Gagal membaca OpenAPI spec [{project_id}]: {err}")
            return {}

    def extract_endpoints_from_code(self, code: str) -> Set[Tuple[str, str]]:
        """Mengekstrak pasangan (METHOD, PATH) dari kode router FastAPI menggunakan regex."""
        endpoints: Set[Tuple[str, str]] = set()
        pattern = re.compile(r'@(?:router|app)\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']', re.IGNORECASE)
        for match in pattern.finditer(code):
            method = match.group(1).upper()
            path = match.group(2).rstrip("/") or "/"
            endpoints.add((method, path))
        return endpoints

    def validate_code_against_spec(
        self,
        project_id: str,
        code_content: str,
        spec_override: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Memvalidasi endpoint pada kode terhadap OpenAPI SSOT.

        Returns:
            Dict berisi status validasi, mismatches, missing endpoints, dan ekstra endpoints.
        """
        spec = spec_override or self._load_openapi_spec(project_id)
        if not spec or "paths" not in spec:
            return {"valid": True, "warning": "OpenAPI spec tidak ditemukan atau kosong, validasi dilewati."}

        spec_endpoints: Set[Tuple[str, str]] = set()
        for path_key, path_item in spec.get("paths", {}).items():
            normalized_path = path_key.rstrip("/") or "/"
            for method in path_item.keys():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    spec_endpoints.add((method.upper(), normalized_path))

        code_endpoints = self.extract_endpoints_from_code(code_content)

        missing_in_code = [
            {"method": m, "path": p}
            for m, p in spec_endpoints
            if (m, p) not in code_endpoints
        ]
        extra_in_code = [
            {"method": m, "path": p}
            for m, p in code_endpoints
            if (m, p) not in spec_endpoints
        ]

        is_valid = len(missing_in_code) == 0
        return {
            "valid": is_valid,
            "project_id": project_id,
            "spec_endpoints_count": len(spec_endpoints),
            "code_endpoints_count": len(code_endpoints),
            "missing_in_code": missing_in_code,
            "extra_in_code": extra_in_code,
            "summary": (
                "Kontrak OpenAPI 100% patuh."
                if is_valid
                else f"Ditemukan {len(missing_in_code)} endpoint SSOT yang belum diimplementasikan."
            ),
        }


contract_validator = ContractValidator()
