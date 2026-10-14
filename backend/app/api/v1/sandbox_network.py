"""
REST API Router untuk Hardened Docker Network Sandboxing & Multi-Compose.
Menyediakan inspeksi isolasi network per-venture, metrik real-time kuota, dan orkestrasi multi-layanan.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.sandbox.docker_network import docker_network_mgr
from app.sandbox.docker_runner import docker_multi_runner
from app.sandbox.fallback_runner import fallback_runner

router = APIRouter(prefix="/sandbox", tags=["Sandbox Network & Compose"])


class LaunchMultiServiceRequest(BaseModel):
    """Payload untuk peluncuran stack multi-service terisolasi."""
    project_id: str = Field(..., description="ID proyek venture")
    host_code_path: str = Field(..., description="Path lokal folder proyek")
    services: Optional[List[str]] = Field(
        default=["fe", "be", "db"],
        description="Daftar layanan yang akan diorkestrasikan (fe, be, db)"
    )


class StopMultiServiceRequest(BaseModel):
    """Payload untuk penghentian stack multi-service."""
    project_id: str = Field(..., description="ID proyek venture")


@router.get("/network/{project_id}", response_model=Dict[str, Any])
async def get_project_network_status(project_id: str) -> Dict[str, Any]:
    """Mengambil status isolasi virtual bridge network untuk venture tertentu."""
    try:
        status_data = await docker_network_mgr.get_network_status(project_id)
        return status_data
    except Exception as err:
        logger.error(f"Gagal mengambil status network proyek [{project_id}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memeriksa status network: {str(err)}",
        )


@router.get("/metrics/{project_id}", response_model=Dict[str, Any])
async def get_sandbox_resource_metrics(project_id: str) -> Dict[str, Any]:
    """Mengambil metrik penggunaan sumber daya real-time dan status penegakan kuota."""
    try:
        docker_ready = await docker_network_mgr.is_docker_available()
        if docker_ready and project_id in docker_multi_runner.active_services:
            metrics = await docker_multi_runner.get_metrics(project_id)
        else:
            metrics = fallback_runner.get_fallback_metrics(project_id)
        return metrics
    except Exception as err:
        logger.error(f"Gagal membaca metrik sumber daya proyek [{project_id}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membaca metrik: {str(err)}",
        )


@router.post("/multi-service/launch", response_model=Dict[str, Any])
async def launch_multi_service_stack(payload: LaunchMultiServiceRequest) -> Dict[str, Any]:
    """Meluncurkan stack multi-service (frontend, backend, db) dengan network terisolasi dan hard quota."""
    try:
        project_id = payload.project_id
        net_info = await docker_network_mgr.create_isolated_network(project_id)
        docker_ready = await docker_network_mgr.is_docker_available()

        launched_services = []
        target_services = payload.services or ["fe", "be", "db"]

        if docker_ready:
            for s in target_services:
                res = await docker_multi_runner.run_service_container(
                    project_id=project_id,
                    service=s,
                    image_name="venture-frontend-base:latest" if s == "fe" else "alpine:latest",
                    host_port=3000 if s == "fe" else (8000 if s == "be" else 5432),
                    target_port=3000 if s == "fe" else (8000 if s == "be" else 5432),
                    mount_path=payload.host_code_path if s == "fe" else None,
                )
                launched_services.append(res)
        else:
            # Fallback HTTP server for FE + mock endpoints
            await fallback_runner.start_fallback_http_server(
                project_id, payload.host_code_path, 4000
            )
            for s in target_services:
                launched_services.append({
                    "service": s,
                    "status": "RUNNING" if s == "fe" else "SIMULATED",
                    "mode": "fallback",
                    "port": 4000 if s == "fe" else (8000 if s == "be" else 5432),
                })

        return {
            "project_id": project_id,
            "status": "ACTIVE",
            "network": net_info,
            "services": launched_services,
            "quota": {"cpu_limit": 1.5, "memory_limit": "1024m"},
        }
    except Exception as err:
        logger.error(f"Gagal meluncurkan multi-service stack [{payload.project_id}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal meluncurkan stack: {str(err)}",
        )


@router.post("/multi-service/stop", response_model=Dict[str, Any])
async def stop_multi_service_stack(payload: StopMultiServiceRequest) -> Dict[str, Any]:
    """Menghentikan seluruh layanan multi-service dan melepas virtual bridge network."""
    try:
        project_id = payload.project_id
        await fallback_runner.stop_fallback_server(project_id)
        await docker_multi_runner.stop_all_services(project_id)
        await docker_network_mgr.remove_isolated_network(project_id)

        return {
            "project_id": project_id,
            "status": "TERMINATED",
            "message": "Semua layanan dan virtual bridge network berhasil dihentikan.",
        }
    except Exception as err:
        logger.error(f"Gagal menghentikan multi-service stack [{payload.project_id}]: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menghentikan stack: {str(err)}",
        )
