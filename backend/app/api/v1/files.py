"""
File Upload & Attachment Management API Router.
Menangani pengunggahan dokumen, gambar, PDF, dan kode sumber untuk interaksi multimodal.
"""

from pathlib import Path
import re
import time
from typing import Any, Dict
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.core.file_parser import extract_text_from_file
from app.core.logger import logger

router = APIRouter(prefix="/files", tags=["Files & Attachments"])

PROJECTS_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "projects_output"
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB

ALLOWED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".webp",
    ".pdf", ".txt", ".md",
    ".json", ".py", ".ts", ".tsx", ".csv", ".yaml", ".yml", ".sql", ".html", ".css",
}


@router.post("/upload", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    project_id: str = Form(..., min_length=1),
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """Mengunggah berkas lampiran untuk chat Oasis HQ atau Executive Sparring.

    Args:
        project_id: ID proyek tujuan penyimpanan lampiran.
        file: Objek berkas multipart yang diunggah.

    Returns:
        Metadata berkas, URL unduhan, dan ringkasan isi teks.
    """
    clean_name = re.sub(r"[^\w\.-]", "_", file.filename or "attachment")
    suffix = Path(clean_name).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format berkas '{suffix}' tidak didukung. Format yang didukung: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    try:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Ukuran berkas melebihi batas maksimal 15 MB.",
            )

        target_dir = PROJECTS_OUTPUT_DIR / project_id / "attachments"
        target_dir.mkdir(parents=True, exist_ok=True)

        file_id = f"att_{int(time.time() * 1000)}"
        stored_filename = f"{file_id}_{clean_name}"
        dest_path = target_dir / stored_filename

        dest_path.write_bytes(content)
        logger.info(f"Berkas berhasil disimpan: {dest_path} ({len(content)} bytes)")

        # Ekstrak konten teks awal untuk konteks instan LLM
        text_content, is_truncated = extract_text_from_file(dest_path, max_chars=12000)

        return {
            "id": file_id,
            "filename": clean_name,
            "stored_filename": stored_filename,
            "file_type": file.content_type or "application/octet-stream",
            "size_bytes": len(content),
            "download_url": f"/api/v1/files/download/{project_id}/{stored_filename}",
            "content_preview": text_content,
            "is_truncated": is_truncated,
        }
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Gagal memproses upload berkas [{file.filename}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menyimpan berkas di server: {str(err)}",
        )


@router.get("/download/{project_id}/{filename}")
async def download_attachment(project_id: str, filename: str) -> FileResponse:
    """Mengunduh atau menampilkan berkas lampiran yang telah tersimpan.

    Args:
        project_id: ID proyek pemilik berkas.
        filename: Nama berkas tersimpan di disk.

    Returns:
        FileResponse berkas sasaran.
    """
    clean_filename = Path(filename).name
    target_path = (PROJECTS_OUTPUT_DIR / project_id / "attachments" / clean_filename).resolve()

    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Berkas '{clean_filename}' tidak ditemukan.",
        )

    # Validasi path traversal
    base_dir = (PROJECTS_OUTPUT_DIR / project_id / "attachments").resolve()
    if base_dir not in target_path.parents and target_path != base_dir:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses berkas di luar direktori proyek ditolak.",
        )

    return FileResponse(path=str(target_path), filename=clean_filename)
