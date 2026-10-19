"""
Security Code Scanner (OWASP Top 10 Static Code Analyzer).
Menjalankan audit keamanan kode statis asli menggunakan AST parsing dan aturan keamanan
terstandarisasi pada direktori keluaran proyek (backend & frontend).
"""

import ast
from pathlib import Path
import re
import shutil
from typing import Any, Dict, List, Optional
import json
import asyncio

from app.core.logger import logger
from app.engine.quality.security_finding import SecurityFinding


class StaticSecurityScanner:
    """Pemindai keamanan kode statis untuk proyek yang dihasilkan oleh Multi-Agent."""

    def __init__(self, output_base_dir: Optional[Path] = None) -> None:
        self.output_base = output_base_dir or Path("projects_output")

    def _scan_python_ast(self, py_file: Path) -> List[SecurityFinding]:
        """Memindai AST Python untuk mendeteksi kerentanan OWASP Top 10."""
        findings: List[SecurityFinding] = []
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except Exception as err:
            logger.warning(f"Gagal mem-parse AST file {py_file}: {err}")
            return findings

        rel_path = str(py_file.as_posix())

        for node in ast.walk(tree):
            # 1. Deteksi eksekusi berbahaya: eval, exec
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec"):
                    findings.append(
                        SecurityFinding(
                            rule_id="OWASP-A03-CODE-INJECTION",
                            title="Penggunaan eval/exec berbahaya",
                            severity="CRITICAL",
                            file_path=rel_path,
                            line_number=node.lineno,
                            description=f"Fungsi dinamis {node.func.id}() dapat memicu eksekusi kode berbahaya arbitrer.",
                            remediation="Gunakan parsing data terstruktur (json.loads atau ast.literal_eval).",
                        )
                    )

            # 2. Deteksi Hardcoded Password/Secret Assignment
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name_lower = target.id.lower()
                        if any(k in name_lower for k in ("secret_key", "password", "api_key", "jwt_secret")):
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                val = node.value.value
                                if len(val) > 4 and not val.startswith(("os.", "get_env", "CHANGE_ME", "mock-")):
                                    findings.append(
                                        SecurityFinding(
                                            rule_id="OWASP-A07-HARDCODED-SECRET",
                                            title="Hardcoded Kredensial / Secret",
                                            severity="HIGH",
                                            file_path=rel_path,
                                            line_number=node.lineno,
                                            description=f"Variabel rahasia '{target.id}' diinisialisasi dengan nilai literal mentah.",
                                            remediation="Ambil nilai rahasia dari environment variable menggunakan os.getenv().",
                                        )
                                    )

        # 3. Regex Scan untuk Permissive CORS & Raw SQL Concatenation
        lines = source.splitlines()
        for i, line in enumerate(lines, 1):
            if 'allow_origins=["*"]' in line and "allow_credentials=True" in source:
                findings.append(
                    SecurityFinding(
                        rule_id="OWASP-A05-PERMISSIVE-CORS",
                        title="Permissive CORS dengan Allow Credentials",
                        severity="MEDIUM",
                        file_path=rel_path,
                        line_number=i,
                        description="Konfigurasi CORS mengizinkan semua origin ('*') bersamaan dengan allow_credentials=True.",
                        remediation="Batasi origin spesifik pada domain terpercaya di environment produksi.",
                    )
                )

            if re.search(r'\.execute\(\s*f["\'].*SELECT.*\{.*\}', line, re.IGNORECASE):
                findings.append(
                    SecurityFinding(
                        rule_id="OWASP-A03-SQL-INJECTION",
                        title="Potensi SQL Injection via f-string",
                        severity="CRITICAL",
                        file_path=rel_path,
                        line_number=i,
                        description="Kueri SQL dibangun dengan interpolasi string mentah tanpa parameterized query.",
                        remediation="Gunakan ORM SQLAlchemy atau parameterized query dengan placeholder :param.",
                    )
                )

        return findings

    def _scan_frontend_code(self, fe_file: Path) -> List[SecurityFinding]:
        """Memindai berkas Next.js / TypeScript untuk mendeteksi kerentanan XSS dan kebocoran kunci."""
        findings: List[SecurityFinding] = []
        try:
            content = fe_file.read_text(encoding="utf-8")
        except Exception:
            return findings

        rel_path = str(fe_file.as_posix())
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            if "dangerouslySetInnerHTML" in line and "DOMPurify" not in content:
                findings.append(
                    SecurityFinding(
                        rule_id="OWASP-A03-REACT-XSS",
                        title="Penggunaan dangerouslySetInnerHTML tanpa sanitasi",
                        severity="HIGH",
                        file_path=rel_path,
                        line_number=i,
                        description="dangerouslySetInnerHTML dapat membuka celah Cross-Site Scripting (XSS).",
                        remediation="Sanitasi HTML menggunakan DOMPurify sebelum di-render.",
                    )
                )

            if re.search(r'(?:api_key|secret_key|private_key)\s*[:=]\s*["\'][a-zA-Z0-9_\-]{20,}["\']', line, re.I):
                findings.append(
                    SecurityFinding(
                        rule_id="OWASP-A07-CLIENT-SECRET-LEAK",
                        title="Kebocoran Secret Key di Client-Side Code",
                        severity="CRITICAL",
                        file_path=rel_path,
                        line_number=i,
                        description="Kunci API rahasia ditemukan di komponen frontend yang dapat diakses publik.",
                        remediation="Pindahkan pemanggilan pihak ketiga ke server-side Next.js route handler.",
                    )
                )

        return findings

    async def scan_project(self, project_id: str) -> Dict[str, Any]:
        """Menjalankan pemindaian keamanan menyeluruh pada seluruh berkas proyek."""
        project_dir = self.output_base / project_id
        if not project_dir.exists():
            return {
                "scanned_files_count": 0,
                "vulnerabilities_count": 0,
                "passed": True,
                "findings": [],
                "tool_used": "native_ast_engine",
            }

        findings: List[SecurityFinding] = []
        scanned_count = 0

        # Scan Backend Python files
        for py_file in project_dir.glob("backend/**/*.py"):
            scanned_count += 1
            findings.extend(self._scan_python_ast(py_file))

        # Scan Frontend TS/TSX files
        fe_src_dir = project_dir / "frontend" / "src"
        if fe_src_dir.exists():
            for fe_file in fe_src_dir.rglob("*"):
                if fe_file.is_file() and fe_file.suffix in (".ts", ".tsx"):
                    scanned_count += 1
                    findings.extend(self._scan_frontend_code(fe_file))

        critical_or_high = [f for f in findings if f.severity in ("CRITICAL", "HIGH")]
        passed = len(critical_or_high) == 0

        logger.info(
            f"Static Security Scanner selesai untuk [{project_id}]: "
            f"{scanned_count} berkas dipindai, {len(findings)} temuan (Lolos: {passed})"
        )

        return {
            "scanned_files_count": scanned_count,
            "vulnerabilities_count": len(findings),
            "critical_count": len(critical_or_high),
            "passed": passed,
            "findings": [f.to_dict() for f in findings],
            "tool_used": "native_ast_engine",
        }


security_scanner = StaticSecurityScanner()
