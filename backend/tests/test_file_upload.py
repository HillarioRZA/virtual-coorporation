"""
Unit tests for File Upload and Attachment Management API.
Menguji endpoint POST /api/v1/files/upload dan parsing dokumen teks/PDF.
"""

import io
import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_file_upload_text_and_download():
    """Menguji pengunggahan berkas teks markdown dan verifikasi ekstraksi konten."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        file_bytes = b"# My PRD Specification\nFeature 1: User Auth\nFeature 2: Dashboard"
        files = {
            "file": ("spec.md", io.BytesIO(file_bytes), "text/markdown"),
        }
        data = {"project_id": "proj_test_upload"}

        resp = await client.post("/api/v1/files/upload", data=data, files=files)
        assert resp.status_code == 201
        payload = resp.json()

        assert payload["filename"] == "spec.md"
        assert payload["size_bytes"] == len(file_bytes)
        assert "My PRD Specification" in payload["content_preview"]
        assert payload["download_url"].startswith("/api/v1/files/download/proj_test_upload/")

        # Test download
        download_url = payload["download_url"]
        down_resp = await client.get(download_url)
        assert down_resp.status_code == 200
        assert b"Feature 1: User Auth" in down_resp.content


@pytest.mark.asyncio
async def test_file_upload_invalid_extension():
    """Menguji penolakan berkas dengan ekstensi terlarang (e.g. .exe)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {
            "file": ("malware.exe", io.BytesIO(b"MZ\x90\x00"), "application/octet-stream"),
        }
        data = {"project_id": "proj_test_upload"}

        resp = await client.post("/api/v1/files/upload", data=data, files=files)
        assert resp.status_code == 400
        assert "tidak didukung" in resp.json()["detail"]
