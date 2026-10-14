"""
Unit Tests untuk Modul Sandbox & Dynamic Reverse Proxy.
Menguji pemindaian port dinamis, normalisasi path, lifecycle sandbox, dan Caddy proxy manager.
"""

from pathlib import Path
import pytest

from app.sandbox.proxy import ProxyManager
from app.sandbox.runner import SandboxManager, find_free_port, normalize_windows_path


def test_find_free_port() -> None:
    """Menguji alokasi port bebas dalam range 4000-4999."""
    port = find_free_port(4000, 4050)
    assert isinstance(port, int)
    assert 4000 <= port <= 4050


def test_normalize_windows_path() -> None:
    """Menguji normalisasi path Windows ke format POSIX."""
    win_path = r"D:\my project\VIRTUAL TECH STARTUP\test"
    normalized = normalize_windows_path(win_path)
    assert "\\" not in normalized
    assert normalized.startswith("D:/") or normalized.startswith("d:/")


@pytest.mark.asyncio
async def test_sandbox_manager_lifecycle(tmp_path: Path) -> None:
    """Menguji peluncuran, pengecekan status, dan penghentian kontainer/fallback."""
    sbx = SandboxManager()
    project_id = "proj_sbx_test"
    dummy_code_dir = tmp_path / "mock_fe"
    dummy_code_dir.mkdir(parents=True, exist_ok=True)

    # 1. Jalankan sandbox
    info = await sbx.run_frontend_sandbox(project_id, str(dummy_code_dir))
    assert info["project_id"] == project_id
    assert 4000 <= info["port"] <= 4999
    assert info["is_running"] is True
    assert sbx.is_sandbox_running(project_id) is True

    # 2. Hentikan sandbox
    stopped = await sbx.stop_sandbox(project_id)
    assert stopped is True
    assert sbx.is_sandbox_running(project_id) is False


@pytest.mark.asyncio
async def test_proxy_manager_fallback() -> None:
    """Menguji behavior ProxyManager saat Caddy admin offline (fallback localhost URL)."""
    proxy = ProxyManager(caddy_api_url="http://127.0.0.1:19999")  # Port sengaja offline
    project_id = "proj_proxy_test"
    target_port = 4015

    # Caddy offline
    is_alive = await proxy.is_caddy_alive()
    assert is_alive is False

    # Tetap menghasilkan URL preview fallback yang valid
    url = await proxy.register_route(project_id, target_port)
    assert url == f"http://localhost:{target_port}"

    # Remove route tidak melempar error
    res = await proxy.remove_route(project_id)
    assert res is False


@pytest.mark.asyncio
async def test_sandbox_fallback_server_response(tmp_path: Path) -> None:
    """Menguji bahwa server fallback merespons permintaan HTTP dengan status 200 dan HTML valid."""
    import httpx
    sbx = SandboxManager()
    project_id = "proj_fallback_http_test"
    dummy_code_dir = tmp_path / "mock_fe_http"
    src_app = dummy_code_dir / "src" / "app"
    src_app.mkdir(parents=True, exist_ok=True)
    (src_app / "page.tsx").write_text("export default function Page() { return <div>Demo App</div>; }", encoding="utf-8")

    info = await sbx.run_frontend_sandbox(project_id, str(dummy_code_dir))
    port = info["port"]

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"http://127.0.0.1:{port}/")
            assert resp.status_code == 200
            assert "text/html" in resp.headers.get("content-type", "")
            assert "Live Interactive Sandbox" in resp.text
            assert "Demo App" in resp.text
    finally:
        await sbx.stop_sandbox(project_id)

