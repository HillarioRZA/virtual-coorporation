"""
Contextual Change & Diff Digest Tool.
Mengambil ringkasan perubahan Git dalam format ramah token (< 100 token) untuk PR dan audit QA.
"""

import asyncio
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional

from app.core.logger import logger


class DiffDigestGenerator:
    """Generator intisari perubahan kode Git berpresisi tinggi dengan footprint token minimal."""

    def __init__(self, projects_dir: Optional[Path] = None) -> None:
        """Inisialisasi DiffDigestGenerator."""
        self.projects_dir = projects_dir or Path("projects_output")

    async def get_diff_summary(
        self,
        project_id: str,
        base_ref: str = "HEAD~1",
        custom_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Menghasilkan ringkasan git diff --stat yang ringkas dan ramah token.

        Args:
            project_id: ID proyek sasaran.
            base_ref: Referensi git pembanding (default HEAD~1 atau branch target).
            custom_dir: Path direktori alternatif jika bukan di projects_output.

        Returns:
            Dict berisi status, ringkasan teks (< 100 token), total berkas, insert, dan delete.
        """
        target_dir = custom_dir or (self.projects_dir / project_id)
        if not target_dir.exists() or not (target_dir / ".git").exists():
            return {
                "success": False,
                "summary": "Bukan repositori Git aktif.",
                "changed_files": 0,
                "insertions": 0,
                "deletions": 0,
            }

        git_bin = shutil.which("git") or "git"
        try:
            proc = await asyncio.create_subprocess_exec(
                git_bin, "diff", "--stat", base_ref,
                cwd=str(target_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                # Fallback: jika base_ref belum ada commit sebelumnya, gunakan git status --short
                proc_status = await asyncio.create_subprocess_exec(
                    git_bin, "status", "--short",
                    cwd=str(target_dir),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                out_stat, _ = await proc_status.communicate()
                lines = [line.strip() for line in out_stat.decode("utf-8", errors="ignore").splitlines() if line.strip()]
                return {
                    "success": True,
                    "summary": f"{len(lines)} files modified/untracked: " + ", ".join(lines[:5]),
                    "changed_files": len(lines),
                    "insertions": 0,
                    "deletions": 0,
                }

            stat_output = stdout.decode("utf-8", errors="ignore").strip()
            lines = [l for l in stat_output.splitlines() if l.strip()]
            summary_line = lines[-1] if lines else "No changes detected."

            # Ekstrak file yang disentuh
            touched = [l.split("|")[0].strip() for l in lines[:-1] if "|" in l][:5]
            compact_summary = f"{summary_line}. Touched: {', '.join(touched)}" if touched else summary_line

            return {
                "success": True,
                "summary": compact_summary[:250],
                "raw_stat": stat_output,
                "changed_files": len(touched),
            }
        except (OSError, asyncio.SubprocessError) as err:
            logger.error(f"Gagal mengekstrak git diff digest [{project_id}]: {err}")
            return {"success": False, "summary": f"Error mengekstrak diff: {err}"}


diff_digest = DiffDigestGenerator()
