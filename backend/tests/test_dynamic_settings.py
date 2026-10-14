"""
Unit and Integration Tests for Dynamic Settings Subsystem.
Memverifikasi modul SettingsManager, persistensi SQLite, masking kredensial,
dan API endpoints FastAPI untuk pengaturan sistem tanpa restart.
"""

from pathlib import Path
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.core.settings_manager import dynamic_settings_manager
from app.db.init_db import init_database
from main import app


@pytest_asyncio.fixture
async def temp_settings_db(tmp_path: Path) -> str:
    """Fixture basis data sementara untuk pengujian independen."""
    db_file = tmp_path / "test_settings.db"
    db_path_str = str(db_file)
    await init_database(db_path_str)

    orig_db = settings.DATABASE_URL
    orig_cos_model = settings.MODEL_COS
    orig_cos_provider = settings.PROVIDER_COS
    settings.DATABASE_URL = f"sqlite+aiosqlite:///{db_path_str}"

    yield db_path_str

    settings.DATABASE_URL = orig_db
    settings.MODEL_COS = orig_cos_model
    settings.PROVIDER_COS = orig_cos_provider


@pytest.mark.asyncio
async def test_dynamic_settings_get_runtime(temp_settings_db: str) -> None:
    """Memverifikasi struktur dan kategori get_runtime_settings."""
    data = dynamic_settings_manager.get_runtime_settings()
    assert "roles" in data
    assert "providers" in data
    assert "system" in data
    assert "paas" in data
    assert "sandbox" in data
    assert "available_providers" in data
    assert "recommended_models" in data

    assert "COS" in data["roles"]
    assert "CTO" in data["roles"]
    assert data["roles"]["COS"]["title"] == "Chief of Staff (CoS)"


@pytest.mark.asyncio
async def test_dynamic_settings_masking() -> None:
    """Memverifikasi bahwa API key disanitasi dan tidak diekspos plaintext."""
    assert dynamic_settings_manager.mask_secret("") == ""
    assert dynamic_settings_manager.mask_secret("12345") == "********"

    masked = dynamic_settings_manager.mask_secret("sk-openai-super-secret-key-1234")
    assert masked.startswith("sk-...")
    assert masked.endswith("1234")
    assert "super-secret" not in masked


@pytest.mark.asyncio
async def test_dynamic_settings_update_and_persist(temp_settings_db: str) -> None:
    """Memverifikasi mutasi in-memory dan persistensi ke SQLite."""
    updates = {
        "MODEL_COS": "gpt-4o-custom",
        "PROVIDER_COS": "openai",
    }
    count = await dynamic_settings_manager.update_runtime_settings(updates, custom_path=temp_settings_db)
    assert count == 2
    assert settings.MODEL_COS == "gpt-4o-custom"
    assert settings.PROVIDER_COS == "openai"

    model, provider = settings.get_agent_model_and_provider("COS")
    assert model == "gpt-4o-custom"
    assert provider == "openai"

    settings.MODEL_COS = "temporary-override"
    await dynamic_settings_manager.load_overrides(custom_path=temp_settings_db)
    assert settings.MODEL_COS == "gpt-4o-custom"


@pytest.mark.asyncio
async def test_dynamic_settings_reset(temp_settings_db: str) -> None:
    """Memverifikasi fungsi reset settings ke default."""
    await dynamic_settings_manager.update_runtime_settings({"MODEL_COS": "temp-mod"}, custom_path=temp_settings_db)
    assert settings.MODEL_COS == "temp-mod"

    await dynamic_settings_manager.reset_to_defaults(custom_path=temp_settings_db)
    assert settings.MODEL_COS != "temp-mod"


@pytest.mark.asyncio
async def test_settings_api_endpoints(temp_settings_db: str) -> None:
    """Memverifikasi REST API GET, PUT, POST /reset pada FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/settings")
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "success"
        assert "roles" in body["data"]

        put_res = await client.put(
            "/api/v1/settings",
            json={"updates": {"MODEL_PM": "claude-custom-pm", "PROVIDER_PM": "anthropic"}},
        )
        assert put_res.status_code == 200
        put_body = put_res.json()
        assert put_body["status"] == "success"
        assert settings.MODEL_PM == "claude-custom-pm"

        reset_res = await client.post("/api/v1/settings/reset")
        assert reset_res.status_code == 200
        reset_body = reset_res.json()
        assert reset_body["status"] == "success"
