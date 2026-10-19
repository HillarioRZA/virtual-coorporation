"""
File Parsing and Content Extraction Engine.
Mengekstrak teks dan konten dari berkas PDF, dokumen teks, dan kode sumber.
"""

from pathlib import Path
from typing import Optional, Tuple
from app.core.logger import logger


def extract_text_from_file(file_path: Path, max_chars: int = 15000) -> Tuple[str, bool]:
    """Mengekstrak teks dari berkas teks, dokumen kode, atau PDF secara aman.

    Args:
        file_path: Objek Path berkas yang akan dibaca.
        max_chars: Batas maksimal karakter yang diekstrak untuk konteks LLM.

    Returns:
        Tuple (teks_hasil_ekstraksi, apakah_terpotong).
    """
    if not file_path.exists() or not file_path.is_file():
        return "", False

    suffix = file_path.suffix.lower()
    is_truncated = False

    # 1. Dokumen PDF
    if suffix == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(str(file_path))
            pages_text = []
            total_len = 0
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages_text.append(f"--- Halaman {idx + 1} ---\n{text}")
                total_len += len(text)
                if total_len >= max_chars:
                    is_truncated = True
                    break
            extracted = "\n\n".join(pages_text)[:max_chars]
            return extracted, is_truncated
        except Exception as pdf_err:
            logger.warning(f"Gagal mengekstrak PDF [{file_path.name}]: {pdf_err}")
            return f"[Gagal membaca konten PDF: {pdf_err}]", False

    # 2. Gambar (Deteksi tipe gambar untuk multimodal)
    if suffix in (".png", ".jpg", ".jpeg", ".webp"):
        size_kb = file_path.stat().st_size / 1024
        return f"[Gambar: {file_path.name} ({suffix.upper()}, {size_kb:.1f} KB)]", False

    # 3. File Teks, Markdown, JSON, dan Kode Sumber
    encodings = ("utf-8", "utf-8-sig", "latin-1")
    raw_content = ""
    for enc in encodings:
        try:
            raw_content = file_path.read_text(encoding=enc)
            break
        except (UnicodeDecodeError, OSError):
            continue

    if not raw_content:
        logger.warning(f"Berkas [{file_path.name}] tidak dapat dibaca sebagai teks.")
        return "[Konten biner atau tidak dapat didekodekan]", False

    if len(raw_content) > max_chars:
        return raw_content[:max_chars], True

    return raw_content, False
