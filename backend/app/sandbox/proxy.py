"""
Dynamic Reverse Proxy Controller for Ephemeral Sandboxes.
Mendaftarkan dan mencabut rute subdomain dinamis ke Caddy via REST Admin API.
"""

from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.logger import logger


class ProxyManager:
    """Pengelola rute subdomain dinamis pada Reverse Proxy Caddy."""

    def __init__(self, caddy_api_url: Optional[str] = None) -> None:
        """Inisialisasi ProxyManager.

        Args:
            caddy_api_url: URL basis Admin API Caddy (default: dari settings).
        """
        self.caddy_api_url = caddy_api_url or settings.CADDY_ADMIN_API
        self.domain_suffix = settings.SANDBOX_DOMAIN_SUFFIX
        self.timeout = httpx.Timeout(3.0, connect=1.0)

    async def is_caddy_alive(self) -> bool:
        """Mengecek apakah Caddy Admin API merespon panggilan HTTP.

        Returns:
            True jika server Caddy online dan dapat diakses.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.get(f"{self.caddy_api_url}/config/")
                return res.status_code == 200
        except (httpx.RequestError, httpx.TimeoutException):
            return False

    async def register_route(self, project_id: str, target_port: int) -> str:
        """Mendaftarkan subdomain dinamis demo-<id>.local.sandbox menuju port kontainer.

        Args:
            project_id: ID proyek sasaran.
            target_port: Port host tempat kontainer berjalan.

        Returns:
            URL preview aktif (subdomain jika Caddy aktif, atau fallback localhost:port).
        """
        subdomain = f"demo-{project_id}.{self.domain_suffix}"
        route_id = f"route_{project_id}"

        caddy_online = await self.is_caddy_alive()
        if not caddy_online:
            fallback_url = f"http://localhost:{target_port}"
            logger.info(f"Caddy Admin API offline. Menggunakan URL preview lokal fallback: {fallback_url}")
            return fallback_url

        payload: Dict[str, Any] = {
            "@id": route_id,
            "match": [{"host": [subdomain]}],
            "handle": [{
                "handler": "reverse_proxy",
                "upstreams": [{"dial": f"127.0.0.1:{target_port}"}],
            }],
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Daftarkan rute baru ke srv0 Caddy
                res = await client.post(
                    f"{self.caddy_api_url}/config/apps/http/servers/srv0/routes",
                    json=payload,
                )
                if res.status_code in [200, 201]:
                    preview_url = f"http://{subdomain}"
                    logger.info(f"Caddy Dynamic Route terdaftar: [{subdomain}] -> port {target_port}")
                    return preview_url
                else:
                    logger.warning(f"Gagal mendaftarkan rute Caddy ({res.status_code}): {res.text}")
                    return f"http://localhost:{target_port}"
        except (httpx.RequestError, httpx.TimeoutException) as err:
            logger.warning(f"Kesalahan komunikasi Caddy Admin API: {err}")
            return f"http://localhost:{target_port}"

    async def remove_route(self, project_id: str) -> bool:
        """Mencabut rute dinamis proyek dari konfigurasi Caddy.

        Args:
            project_id: ID proyek sasaran.

        Returns:
            True jika berhasil dihapus atau Caddy sedang offline.
        """
        route_id = f"route_{project_id}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.delete(f"{self.caddy_api_url}/id/{route_id}")
                return res.status_code in [200, 204]
        except (httpx.RequestError, httpx.TimeoutException):
            return False
