"""Live Factual Grounding & Citation Auditor Engine.

Mengekstrak referensi URL dan sitasi markdown dari luaran riset pasar/edukasi,
serta melakukan verifikasi keterjangkauan HTTP (status 200) secara asinkron.
"""

import re
from typing import List, Optional
import httpx
from pydantic import BaseModel, Field
from app.core.logger import logger


class CitationAuditReport(BaseModel):
    """Hasil verifikasi sitasi dan keterjangkauan referensi faktual."""

    is_grounded: bool = Field(description="True jika seluruh atau mayoritas URL terverifikasi aktif.")
    total_citations: int = Field(description="Total sitasi URL unik yang terdeteksi.")
    verified_urls: List[str] = Field(default_factory=list, description="Daftar URL yang merespons HTTP 200.")
    broken_urls: List[str] = Field(default_factory=list, description="Daftar URL yang gagal dijangkau atau error.")
    grounding_score: float = Field(description="Persentase URL aktif (0.0 - 100.0).")


def extract_citation_urls(text: str) -> List[str]:
    """Mengekstrak tautan URL dari sitasi markdown [^1]: https://... atau [teks](https://...)."""
    url_pattern = re.compile(r"https?://[^\s)\]\"'>]+")
    matches = url_pattern.findall(text)
    # Bersihkan tanda baca di akhir URL jika terbawa
    cleaned = set()
    for u in matches:
        u_clean = u.rstrip(".,;:")
        if u_clean:
            cleaned.add(u_clean)
    return sorted(list(cleaned))


async def verify_url_live(client: httpx.AsyncClient, url: str) -> bool:
    """Memeriksa apakah URL merespons status sukses (HTTP 200-299)."""
    try:
        # Coba HEAD terlebih dahulu untuk menghemat bandwidth
        resp = await client.head(url, follow_redirects=True)
        if resp.status_code in (405, 403):
            resp = await client.get(url, follow_redirects=True)
        return 200 <= resp.status_code < 300
    except (httpx.RequestError, httpx.HTTPError) as err:
        logger.debug(f"Pengecekan URL [{url}] gagal: {err}")
        return False


async def audit_text_citations(
    text: str,
    custom_transport: Optional[httpx.AsyncBaseTransport] = None,
    timeout_seconds: float = 4.0,
) -> CitationAuditReport:
    """Memverifikasi seluruh sitasi pada naskah secara paralel dan aman."""
    urls = extract_citation_urls(text)
    if not urls:
        # Jika tidak ada klaim ber-URL, dianggap grounded secara default
        return CitationAuditReport(
            is_grounded=True,
            total_citations=0,
            verified_urls=[],
            broken_urls=[],
            grounding_score=100.0,
        )

    verified: List[str] = []
    broken: List[str] = []

    timeout = httpx.Timeout(timeout_seconds, connect=2.0)
    async with httpx.AsyncClient(transport=custom_transport, timeout=timeout) as client:
        for u in urls:
            is_ok = await verify_url_live(client, u)
            if is_ok:
                verified.append(u)
            else:
                broken.append(u)

    score = round((len(verified) / len(urls)) * 100.0, 1)
    is_grounded = score >= 50.0

    logger.info(f"Citation Auditor: {len(verified)}/{len(urls)} URLs aktif (Score: {score}%)")
    return CitationAuditReport(
        is_grounded=is_grounded,
        total_citations=len(urls),
        verified_urls=verified,
        broken_urls=broken,
        grounding_score=score,
    )
