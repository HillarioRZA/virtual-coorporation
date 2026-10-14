"""
Ephemeral Sandbox Container Runner & Port Manager Facade.
Mengelola alokasi port dinamis dan peluncuran kontainer prototipe frontend di lingkungan lokal.
"""

import asyncio
from contextlib import closing
from pathlib import Path
import socket
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.logger import logger
from app.sandbox.docker_network import docker_network_mgr
from app.sandbox.docker_runner import docker_multi_runner
from app.sandbox.fallback_runner import fallback_runner


def find_free_port(start_port: int = 4000, end_port: int = 4999) -> int:
    """Mencari port TCP kosong di localhost dalam jangkauan yang ditentukan.

    Args:
        start_port: Batas awal nomor port (default: 4000).
        end_port: Batas akhir nomor port (default: 4999).

    Returns:
        Nomor port bebas yang siap digunakan.

    Raises:
        RuntimeError: Jika seluruh port dalam jangkauan sedang digunakan.
    """
    for port in range(start_port, end_port + 1):
        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.settimeout(0.1)
                if sock.connect_ex(("127.0.0.1", port)) != 0:
                    return port
        except socket.error as err:
            logger.warning(f"Pengecekan port {port} gagal: {err}")
            continue

    raise RuntimeError(f"Seluruh port sandbox ({start_port}-{end_port}) sedang digunakan.")


def normalize_windows_path(path_str: str) -> str:
    """Mengonversi path Windows ke format mount yang kompatibel dengan Docker Desktop POSIX.

    Args:
        path_str: String path lokal (misal: 'D:\\my project\\...').

    Returns:
        Format path yang dinormalisasi dengan forward slash.
    """
    clean_path = Path(path_str).resolve().as_posix()
    return clean_path


class SandboxManager:
    """Manajer siklus hidup kontainer sandbox frontend ephemeral dengan dual-engine fallback."""

    def __init__(self) -> None:
        """Inisialisasi registry kontainer aktif."""
        self.active_containers: Dict[str, Dict[str, Any]] = {}

    @property
    def fallback_servers(self) -> Dict[str, Any]:
        """Akses registry fallback server yang aktif."""
        return fallback_runner.fallback_servers

    async def is_docker_available(self) -> bool:
        """Memeriksa apakah Docker Engine aktif dan siap menerima perintah.

        Returns:
            True jika Docker daemon merespon dengan sukses.
        """
        return await docker_network_mgr.is_docker_available()

    async def is_image_available(self, image_name: str) -> bool:
        """Memeriksa apakah Docker image lokal tersedia tanpa menunggu pull remote.

        Args:
            image_name: Nama image (e.g. 'venture-frontend-base:latest').

        Returns:
            True jika image lokal telah di-build dan siap digunakan.
        """
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker", "image", "inspect", image_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=2.0)
            return proc.returncode == 0
        except (OSError, asyncio.TimeoutError):
            return False

    async def _start_fallback_http_server(
        self, project_id: str, host_code_path: str, port: int
    ) -> None:
        """Memulai HTTP server berbasis asyncio lokal saat Docker tidak tersedia."""
        await fallback_runner.start_fallback_http_server(project_id, host_code_path, port)

    async def run_frontend_sandbox(
        self,
        project_id: str,
        host_code_path: str,
        port: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Meluncurkan kontainer sandbox frontend untuk proyek tertentu."""
        target_port = port or find_free_port()
        container_name = f"sandbox_fe_{project_id}"
        normalized_mount = normalize_windows_path(host_code_path)
        docker_ready = await self.is_docker_available()
        image_ready = await self.is_image_available(settings.DOCKER_BASE_FRONTEND_IMAGE) if docker_ready else False

        await self.stop_sandbox(project_id)

        if docker_ready and image_ready:
            logger.info(f"Meluncurkan Docker container [{container_name}] pada port {target_port}...")
            res = await docker_multi_runner.run_service_container(
                project_id=project_id,
                service="fe",
                image_name=settings.DOCKER_BASE_FRONTEND_IMAGE,
                host_port=target_port,
                target_port=3000,
                mount_path=normalized_mount,
                env_vars={"WATCHPACK_POLLING": "true"},
            )
            if res.get("status") == "RUNNING":
                mode = "docker"
            else:
                logger.warning("Docker launch warning: fallback server dipicu.")
                mode = "fallback"
                await self._start_fallback_http_server(project_id, host_code_path, target_port)
        else:
            logger.info(f"Docker offline/image belum ada, fallback server [{project_id}:{target_port}]")
            mode = "fallback"
            await self._start_fallback_http_server(project_id, host_code_path, target_port)

        info = {
            "project_id": project_id,
            "container_name": container_name,
            "port": target_port,
            "mode": mode,
            "is_running": True,
            "mount_path": normalized_mount,
        }
        self.active_containers[project_id] = info
        return info

    async def stop_sandbox(self, project_id: str) -> bool:
        """Menghentikan dan menghapus kontainer sandbox proyek atau server fallback.

        Args:
            project_id: ID proyek sasaran.

        Returns:
            True jika kontainer/server berhasil dihentikan.
        """
        self.active_containers.pop(project_id, None)
        await fallback_runner.stop_fallback_server(project_id)
        await docker_multi_runner.stop_all_services(project_id)
        logger.info(f"Sandbox container/fallback untuk [{project_id}] dihentikan.")
        return True

    def is_sandbox_running(self, project_id: str) -> bool:
        """Mengecek apakah sandbox proyek berstatus aktif di memori runner."""
        return project_id in self.active_containers or project_id in fallback_runner.fallback_servers
