"""Project Artifacts API Router.

Menyajikan daftar metadata dan pengunduhan berkas artefak lintas divisi
(Slide PPT, E-Book, Naskah Video, dan Kampanye Iklan) dengan proteksi Path Traversal.
"""

from pathlib import Path
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from app.core.logger import logger
from app.engine.tools.artifact_compiler import PROJECTS_OUTPUT_DIR, list_project_artifacts

router = APIRouter(prefix="/projects", tags=["Project Artifacts"])


@router.get("/{project_id}/artifacts", status_code=status.HTTP_200_OK)
async def get_project_artifacts(project_id: str) -> Dict[str, Any]:
    """Mengambil daftar seluruh artefak hasil kompilasi divisi B & C yang tersedia."""
    try:
        artifacts = list_project_artifacts(project_id)
        return {"status": "success", "data": artifacts}
    except Exception as err:
        logger.error(f"Gagal mengambil artefak proyek [{project_id}]: {err}")
        raise HTTPException(status_code=500, detail=f"Gagal mengambil artefak: {err}") from err


@router.get("/{project_id}/artifacts/{filename}", status_code=status.HTTP_200_OK)
async def download_project_artifact(project_id: str, filename: str) -> FileResponse:
    """Mengunduh atau melihat berkas artefak fisik dengan verifikasi keamanan OWASP."""
    # Sanitasi nama berkas guna mencegah celah Path Traversal (../)
    safe_name = Path(filename).name
    base_dir = (PROJECTS_OUTPUT_DIR / project_id / "artifacts").resolve()
    target_file = (base_dir / safe_name).resolve()

    # Validasi bahwa target_file berada tepat di bawah base_dir
    try:
        if not target_file.is_relative_to(base_dir):
            logger.warning(f"Percobaan Path Traversal terdeteksi: {filename}")
            raise HTTPException(status_code=403, detail="Akses berkas ditolak (Path Traversal terdeteksi).")
    except ValueError as err:
        raise HTTPException(status_code=403, detail="Akses berkas tidak valid.") from err

    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(status_code=404, detail=f"Berkas '{safe_name}' tidak ditemukan.")

    return FileResponse(path=str(target_file), filename=safe_name)
