"""
In-Sandbox LSP Quality Gatekeeper Subsystem.
Menjalankan verifikasi tipe statis LSP (Pyright & TypeScript) sebelum pull request disetujui.
"""

from typing import Any, Dict, List, Optional
from app.core.logger import logger
from app.db.pr_repo import pr_repo
from app.engine.lsp.lsp_service import lsp_service


class LSPGatekeeper:
    """Penilai kelayakan tipe statis berkas PR menggunakan engine LSP."""

    async def review_pr_type_diagnostics(
        self, pr_id: str, files: List[Dict[str, Any]], custom_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Memeriksa setiap berkas pada PR dari fatal type errors dan menambahkan review."""
        inline_comments: List[Dict[str, Any]] = []
        errors_count = 0

        for file_item in files:
            path = file_item.get("path", "")
            if not path.endswith((".py", ".ts", ".tsx")):
                continue
            diags = await lsp_service.get_diagnostics(project_id="pr_check", file_path=path)
            for d in diags:
                if d.get("severity") == "error":
                    errors_count += 1
                    inline_comments.append({
                        "file_path": path,
                        "line_number": d.get("line", 1),
                        "comment": f"LSP Diagnostic Error [{d.get('code')}]: {d.get('message')}",
                        "code_suggestion": "# Perbaiki kesalahan tipe sebelum penggabungan PR",
                    })

        verdict = "APPROVED" if errors_count == 0 else "CHANGES_REQUESTED"
        summary = (
            "LSP Diagnostics Gate: Seluruh berkas bersih dari fatal type errors."
            if verdict == "APPROVED"
            else f"LSP Diagnostics Gate: Ditemukan {errors_count} fatal type errors yang wajib diperbaiki."
        )
        logger.info(f"PR [{pr_id}] evaluasi LSP selesai: {verdict} ({errors_count} errors).")

        return await pr_repo.add_review(
            pr_id=pr_id,
            reviewer_role_id="role_lsp_gatekeeper",
            reviewer_name="In-Sandbox LSP Gatekeeper",
            verdict=verdict,
            summary=summary,
            inline_comments=inline_comments,
            security_score=100 if verdict == "APPROVED" else 50,
            custom_path=custom_path,
        )


lsp_gatekeeper = LSPGatekeeper()
