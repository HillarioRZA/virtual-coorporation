"""
Unit Tests untuk SandboxLogCollector.
Menguji penanganan log runtime kontainer dan perakitan konteks error.
"""

from unittest.mock import AsyncMock, patch
import pytest
from app.sandbox.log_collector import SandboxLogCollector


@pytest.mark.asyncio
async def test_get_container_logs_failure_returns_none() -> None:
    """Menguji bahwa saat docker logs gagal atau offline, mengembalikan None dengan aman."""
    collector = SandboxLogCollector()
    with patch("asyncio.create_subprocess_exec", side_effect=OSError("Docker not running")):
        logs = await collector.get_container_logs("test_proj", "frontend")
        assert logs is None


@pytest.mark.asyncio
async def test_build_runtime_error_context_with_mock_logs() -> None:
    """Menguji penyusunan konteks error saat log kontainer memuat kata kunci error."""
    collector = SandboxLogCollector()
    mock_logs = (
        "ready - started server on 0.0.0.0:3000\n"
        "Error: Hydration failed because the initial UI does not match\n"
        "Warning: Extra attributes from the server: className\n"
    )
    with patch.object(SandboxLogCollector, "get_container_logs", new=AsyncMock(return_value=mock_logs)):
        ctx = await collector.build_runtime_error_context("test_proj", "frontend")
        assert ctx is not None
        assert "SANDBOX RUNTIME CONTAINER LOGS" in ctx
        assert "Hydration failed" in ctx
