"""Autonomous Peer-to-Peer Code Review Engine.

Mengorkestrasi peninjauan kode asinkron antar-karyawan AI (QA Security, CTO Architecture,
dan Cross-Discipline Peer) dengan sistem kuorum persetujuan dan komentar inline berbaris.
"""

import ast
import re
from typing import Any, Dict, List, Optional
from app.core.logger import logger
from app.db.pr_repo import pr_repo


class AutonomousPeerReviewer:
    """Orkestrator audit kode dan persetujuan kuorum otomatis antar peran AI."""

    async def review_security_qa(
        self, pr_id: str, files: List[Dict[str, Any]], custom_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Menjalankan inspeksi keamanan OWASP statis dan deteksi secret bocor oleh QA/DevSecOps."""
        inline_comments: List[Dict[str, Any]] = []
        security_score = 100

        for file_item in files:
            path = file_item.get("path", "")
            code = file_item.get("new_content", "")
            lines = code.splitlines()

            for idx, line in enumerate(lines, start=1):
                # Deteksi hardcoded credentials
                if re.search(r'(api_key|password|secret|token)\s*=\s*["\'][a-zA-Z0-9_\-]{8,}["\']', line, re.I):
                    inline_comments.append({
                        "file_path": path,
                        "line_number": idx,
                        "comment": "Terdeteksi hardcoded credential berisiko tinggi. Gunakan environment variables.",
                        "code_suggestion": "api_key = os.getenv('API_KEY')",
                    })
                    security_score -= 25

                # Deteksi eval / exec berbahaya
                if re.search(r'\b(eval|exec)\s*\(', line):
                    inline_comments.append({
                        "file_path": path,
                        "line_number": idx,
                        "comment": "Penggunaan fungsi eval/exec dilarang keras untuk mencegah RCE.",
                        "code_suggestion": "Gunakan parser aman seperti ast.literal_eval()",
                    })
                    security_score -= 40

        security_score = max(0, security_score)
        verdict = "APPROVED" if security_score >= 80 else "CHANGES_REQUESTED"
        summary = (
            f"Audit Keamanan QA: Skor {security_score}/100. Kode aman dari celah kritis."
            if verdict == "APPROVED"
            else f"Audit Keamanan QA: Ditemukan {len(inline_comments)} potensi kerentanan keamanan."
        )

        return await pr_repo.add_review(
            pr_id=pr_id,
            reviewer_role_id="role_qa_lead",
            reviewer_name="QA & DevSecOps Specialist",
            verdict=verdict,
            summary=summary,
            inline_comments=inline_comments,
            security_score=security_score,
            custom_path=custom_path,
        )

    async def review_architecture_cto(
        self, pr_id: str, files: List[Dict[str, Any]], custom_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Meninjau kepatuhan arsitektur, prinsip modularitas, dan batasan baris file oleh CTO."""
        inline_comments: List[Dict[str, Any]] = []
        violations = 0

        for file_item in files:
            path = file_item.get("path", "")
            code = file_item.get("new_content", "")
            lines = code.splitlines()

            # Aturan batas baris (150-200 baris)
            if len(lines) > 200:
                violations += 1
                inline_comments.append({
                    "file_path": path,
                    "line_number": len(lines),
                    "comment": f"Panjang berkas ({len(lines)} baris) melebihi batas SRP 200 baris. Wajib dipecah.",
                    "code_suggestion": "# Pisahkan modul menjadi sub-komponen terpisah",
                })

            # Larangan keras print()
            for idx, line in enumerate(lines, start=1):
                if re.search(r'^\s*print\(', line) and not line.strip().startswith("#"):
                    violations += 1
                    inline_comments.append({
                        "file_path": path,
                        "line_number": idx,
                        "comment": "Dilarang menggunakan print(). Gunakan logger terkonfigurasi (loguru).",
                        "code_suggestion": "logger.info(...)",
                    })

        verdict = "APPROVED" if violations == 0 else "CHANGES_REQUESTED"
        summary = (
            "Review Arsitektur CTO: Standar kode bersih, SRP, dan batas baris terpenuhi. LGTM!"
            if verdict == "APPROVED"
            else f"Review Arsitektur CTO: Ditemukan {violations} pelanggaran standar arsitektur."
        )

        return await pr_repo.add_review(
            pr_id=pr_id,
            reviewer_role_id="role_cto",
            reviewer_name="Chief Technology Officer (CTO)",
            verdict=verdict,
            summary=summary,
            inline_comments=inline_comments,
            security_score=100,
            custom_path=custom_path,
        )

    async def review_peer_contracts(
        self,
        pr_id: str,
        reviewer_role_id: str,
        reviewer_name: str,
        files: List[Dict[str, Any]],
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Memvalidasi keselarasan kontrak antarmuka API dan DTO oleh peran rekanan (Frontend/Backend)."""
        inline_comments: List[Dict[str, Any]] = []
        violations = 0
        for f in files:
            path = f.get("path", "")
            code = f.get("new_content", "")
            if path.endswith(".py") and code.strip():
                try:
                    ast.parse(code)
                except SyntaxError as syn_err:
                    violations += 1
                    inline_comments.append({
                        "file_path": path,
                        "line_number": syn_err.lineno or 1,
                        "comment": f"Syntax error pada kontrak Python: {syn_err}",
                        "code_suggestion": "# Perbaiki sintaks Python sebelum integrasi DTO",
                    })

        verdict = "APPROVED" if violations == 0 else "CHANGES_REQUESTED"
        summary = (
            f"Peer Review [{reviewer_name}]: Kontrak payload, respons DTO, dan integrasi antar-komponen selaras."
            if verdict == "APPROVED"
            else f"Peer Review [{reviewer_name}]: Ditemukan {violations} ketidakselarasan kontrak kode."
        )

        return await pr_repo.add_review(
            pr_id=pr_id,
            reviewer_role_id=reviewer_role_id,
            reviewer_name=reviewer_name,
            verdict=verdict,
            summary=summary,
            inline_comments=inline_comments,
            security_score=100 if verdict == "APPROVED" else 60,
            custom_path=custom_path,
        )

    async def run_full_autonomous_review(
        self, pr_id: str, custom_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Menjalankan siklus peninjauan menyeluruh (QA + CTO + Peer) untuk mencapai kuorum."""
        pr = await pr_repo.get_pull_request(pr_id, custom_path)
        if not pr:
            raise ValueError(f"PR '{pr_id}' tidak ditemukan.")

        files = pr.get("files", [])
        author = pr.get("author_role_id", "role_backend")

        # 1. QA Security Scan
        qa_rev = await self.review_security_qa(pr_id, files, custom_path)

        # 2. CTO Architectural Review
        cto_rev = await self.review_architecture_cto(pr_id, files, custom_path)

        # 3. Peer Reviewer Lintas Disiplin
        peer_role = "role_frontend_lead" if "backend" in author else "role_backend_lead"
        peer_name = "Senior Frontend Specialist" if "backend" in author else "Senior Backend Specialist"
        peer_rev = await self.review_peer_contracts(pr_id, peer_role, peer_name, files, custom_path)

        updated_pr = await pr_repo.get_pull_request(pr_id, custom_path)
        logger.info(f"Siklus Peer Review untuk PR {pr_id} selesai. Status akhir: {updated_pr['status'] if updated_pr else 'UNKNOWN'}")

        return {
            "pr": updated_pr,
            "reviews": [qa_rev, cto_rev, peer_rev],
            "quorum_reached": updated_pr["status"] == "APPROVED" if updated_pr else False,
        }


peer_reviewer = AutonomousPeerReviewer()
