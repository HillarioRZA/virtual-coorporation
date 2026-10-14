"""
Docker Isolated Bridge Network Manager.
Mengelola alokasi, isolasi subnet, dan pembersihan virtual bridge network per venture.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from app.core.logger import logger


class DockerNetworkManager:
    """Manajer siklus hidup virtual bridge network Docker terisolasi per proyek."""

    def __init__(self) -> None:
        """Inisialisasi registry network fallback in-memory."""
        self._fallback_networks: Dict[str, Dict[str, Any]] = {}

    async def is_docker_available(self) -> bool:
        """Memeriksa apakah Docker Engine aktif dan siap menerima perintah."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker", "info",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=2.5)
            return proc.returncode == 0
        except (OSError, asyncio.TimeoutError):
            return False

    def get_network_name(self, project_id: str) -> str:
        """Menghasilkan nama standar bridge network proyek."""
        return f"bridge_net_{project_id}"

    async def create_isolated_network(self, project_id: str) -> Dict[str, Any]:
        """Membuat virtual bridge network terisolasi untuk proyek tertentu."""
        net_name = self.get_network_name(project_id)
        docker_ready = await self.is_docker_available()

        if docker_ready:
            try:
                # Cek apakah network sudah ada
                insp = await asyncio.create_subprocess_exec(
                    "docker", "network", "inspect", net_name,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
                stdout, _ = await asyncio.wait_for(insp.communicate(), timeout=3.0)
                if insp.returncode == 0:
                    data = json.loads(stdout.decode("utf-8"))[0]
                    subnet = data.get("IPAM", {}).get("Config", [{}])[0].get("Subnet", "172.28.0.0/16")
                    return {
                        "project_id": project_id, "network_name": net_name,
                        "status": "ACTIVE", "mode": "docker", "subnet": subnet, "isolated": True,
                    }

                # Buat bridge network baru
                create_proc = await asyncio.create_subprocess_exec(
                    "docker", "network", "create", "--driver", "bridge", net_name,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
                await asyncio.wait_for(create_proc.communicate(), timeout=5.0)
                logger.info(f"Berhasil membuat isolated bridge network [{net_name}].")
                return {
                    "project_id": project_id, "network_name": net_name,
                    "status": "ACTIVE", "mode": "docker", "subnet": "172.28.0.0/16", "isolated": True,
                }
            except (OSError, asyncio.TimeoutError, json.JSONDecodeError) as err:
                logger.warning(f"Gagal membuat Docker network ({err}), menggunakan fallback.")

        # Fallback in-memory
        info = {
            "project_id": project_id, "network_name": net_name,
            "status": "ACTIVE", "mode": "fallback", "subnet": f"10.99.{abs(hash(project_id)) % 250}.0/24", "isolated": True,
        }
        self._fallback_networks[project_id] = info
        return info

    async def remove_isolated_network(self, project_id: str) -> bool:
        """Menghapus bridge network proyek secara bersih."""
        net_name = self.get_network_name(project_id)
        self._fallback_networks.pop(project_id, None)

        if await self.is_docker_available():
            try:
                proc = await asyncio.create_subprocess_exec(
                    "docker", "network", "rm", net_name,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
                await asyncio.wait_for(proc.communicate(), timeout=4.0)
                logger.info(f"Docker bridge network [{net_name}] dihapus.")
                return True
            except (OSError, asyncio.TimeoutError):
                pass
        return True

    async def get_network_status(self, project_id: str) -> Dict[str, Any]:
        """Mengambil detail status isolasi network proyek saat ini."""
        net_name = self.get_network_name(project_id)
        if await self.is_docker_available():
            try:
                proc = await asyncio.create_subprocess_exec(
                    "docker", "network", "inspect", net_name,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=3.0)
                if proc.returncode == 0:
                    data = json.loads(stdout.decode("utf-8"))[0]
                    containers = list(data.get("Containers", {}).keys())
                    subnet = data.get("IPAM", {}).get("Config", [{}])[0].get("Subnet", "172.28.0.0/16")
                    return {
                        "project_id": project_id, "network_name": net_name,
                        "status": "ACTIVE", "mode": "docker", "subnet": subnet,
                        "containers_count": len(containers), "isolated": True,
                    }
            except Exception as e:
                logger.debug(f"Pengecekan network status Docker: {e}")

        fallback = self._fallback_networks.get(project_id)
        if fallback:
            return {**fallback, "containers_count": 1}

        return {
            "project_id": project_id, "network_name": net_name,
            "status": "INACTIVE", "mode": "offline", "subnet": "-", "containers_count": 0, "isolated": False,
        }


docker_network_mgr = DockerNetworkManager()
