"""
Unit and Integration Tests for Hardened Docker Network Sandboxing & Multi-Compose.
Menguji isolasi bridge network, penegakan hard quota 1.5 CPU / 1024m RAM, dan endpoint multi-compose.
"""

from pathlib import Path
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import api_v1_router
from app.sandbox.docker_network import docker_network_mgr
from app.sandbox.docker_runner import docker_multi_runner
from app.sandbox.fallback_runner import fallback_runner

_app = FastAPI()
_app.include_router(api_v1_router, prefix="/api/v1")


@pytest.fixture
def client() -> TestClient:
    """Fixture FastAPI TestClient."""
    return TestClient(_app)


@pytest.mark.asyncio
async def test_docker_network_manager_lifecycle() -> None:
    """Menguji alokasi nama bridge network, pembuatan isolasi, status, dan pembersihan."""
    project_id = "proj_net_test_1"
    net_name = docker_network_mgr.get_network_name(project_id)
    assert net_name == f"bridge_net_{project_id}"

    # Buat network (akan menggunakan fallback jika Docker daemon offline)
    res = await docker_network_mgr.create_isolated_network(project_id)
    assert res["project_id"] == project_id
    assert res["network_name"] == net_name
    assert res["status"] == "ACTIVE"
    assert res["isolated"] is True
    assert "subnet" in res

    # Cek status
    status_data = await docker_network_mgr.get_network_status(project_id)
    assert status_data["project_id"] == project_id
    assert status_data["status"] == "ACTIVE"
    assert status_data["isolated"] is True

    # Hapus network
    removed = await docker_network_mgr.remove_isolated_network(project_id)
    assert removed is True


@pytest.mark.asyncio
async def test_fallback_runner_metrics() -> None:
    """Menguji penyediaan metrik simulated saat mode fallback aktif."""
    project_id = "proj_fallback_metrics_test"
    metrics = fallback_runner.get_fallback_metrics(project_id)

    assert metrics["project_id"] == project_id
    assert metrics["mode"] == "fallback"
    assert metrics["cpu_limit_cores"] == 1.5
    assert metrics["memory_limit_mb"] == 1024
    assert isinstance(metrics["services"], list)
    assert len(metrics["services"]) == 3
    service_names = [s["name"] for s in metrics["services"]]
    assert "frontend" in service_names
    assert "backend" in service_names
    assert "database" in service_names


@pytest.mark.asyncio
async def test_docker_multi_runner_stop_all() -> None:
    """Menguji penghentian bersih seluruh layanan dalam multi-service runner."""
    project_id = "proj_runner_stop_test"
    stopped = await docker_multi_runner.stop_all_services(project_id)
    assert stopped is True
    assert project_id not in docker_multi_runner.active_services


def test_api_network_status_endpoint(client: TestClient) -> None:
    """Menguji endpoint GET /api/v1/sandbox/network/{project_id}."""
    project_id = "proj_api_net_test"
    resp = client.get(f"/api/v1/sandbox/network/{project_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_id"] == project_id
    assert "network_name" in data
    assert "status" in data


def test_api_metrics_endpoint(client: TestClient) -> None:
    """Menguji endpoint GET /api/v1/sandbox/metrics/{project_id}."""
    project_id = "proj_api_metrics_test"
    resp = client.get(f"/api/v1/sandbox/metrics/{project_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_id"] == project_id
    assert data["cpu_limit_cores"] == 1.5
    assert data["memory_limit_mb"] == 1024
    assert "services" in data


def test_api_multi_service_launch_and_stop(client: TestClient, tmp_path: Path) -> None:
    """Menguji endpoint POST launch & stop untuk stack multi-service."""
    project_id = "proj_api_compose_test"
    mock_dir = tmp_path / "mock_venture_code"
    mock_dir.mkdir(parents=True, exist_ok=True)

    # Launch stack
    launch_payload = {
        "project_id": project_id,
        "host_code_path": str(mock_dir),
        "services": ["fe", "be", "db"],
    }
    launch_resp = client.post("/api/v1/sandbox/multi-service/launch", json=launch_payload)
    assert launch_resp.status_code == 200
    launch_data = launch_resp.json()
    assert launch_data["project_id"] == project_id
    assert launch_data["status"] == "ACTIVE"
    assert launch_data["quota"]["cpu_limit"] == 1.5
    assert len(launch_data["services"]) == 3

    # Stop stack
    stop_payload = {"project_id": project_id}
    stop_resp = client.post("/api/v1/sandbox/multi-service/stop", json=stop_payload)
    assert stop_resp.status_code == 200
    stop_data = stop_resp.json()
    assert stop_data["project_id"] == project_id
    assert stop_data["status"] == "TERMINATED"
