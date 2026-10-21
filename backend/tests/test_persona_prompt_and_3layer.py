"""
Test Suite untuk Fitur 3-Layer Prompting & Persona Prompt (Soul/DNA Agen).
Memvalidasi persistensi database, propagasi API, dan perakitan prompt 3-layer di dynamic_node.
"""

from pathlib import Path
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch
import httpx
import pytest
import pytest_asyncio

from app.core.config import settings
from app.db.init_db import init_database
from app.db.role_repo import role_repo
from app.engine.roles.dynamic_node import execute_dynamic_role_node
from app.engine.runtime.state import VentureState
from main import app


@pytest_asyncio.fixture
async def test_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Menyiapkan basis data SQLite terisolasi dan client API test."""
    db_file = tmp_path / "test_persona.db"
    test_db_url = f"sqlite+aiosqlite:///{db_file}"
    monkeypatch.setattr(settings, "DATABASE_URL", test_db_url)
    await init_database(str(db_file))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_default_roles_have_persona_prompt(test_env: httpx.AsyncClient) -> None:
    """Memverifikasi bahwa seluruh role default memiliki persona_prompt (Layer 1 Soul)."""
    roles = await role_repo.get_roles(branch_id="branch_main")
    assert len(roles) >= 7

    for role in roles:
        assert "persona_prompt" in role
        assert len(role["persona_prompt"]) > 20, f"Role {role['name']} belum memiliki persona_prompt yang kaya."

    cto_role = next(r for r in roles if r["id"] == "role_cto")
    assert "anti-bloatware" in cto_role["persona_prompt"]
    assert "modular" in cto_role["persona_prompt"]


@pytest.mark.asyncio
async def test_create_and_update_role_persona_prompt(test_env: httpx.AsyncClient) -> None:
    """Menguji pembuatan dan pembaruan persona_prompt melalui REST API."""
    payload = {
        "branch_id": "branch_main",
        "division_id": "div_eng",
        "name": "Security Pen-Tester",
        "job_description": "Melakukan penetration testing otomatis.",
        "persona_prompt": "Anda adalah hacker etis yang paranoid dan metodis.",
        "system_prompt_template": "Lakukan audit celah keamanan SQL injection dan XSS pada setiap endpoint.",
        "model_provider": "openrouter",
        "model_name": "deepseek/deepseek-r1:free",
        "temperature": 0.2,
        "tool_permissions": ["read_file"],
        "token_budget_per_task": 8000,
        "is_active": True,
        "thinking_level": "medium",
    }
    create_res = await test_env.post("/api/v1/corporate/roles", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["persona_prompt"] == "Anda adalah hacker etis yang paranoid dan metodis."

    # Update persona_prompt
    role_id = created["id"]
    update_res = await test_env.put(f"/api/v1/corporate/roles/{role_id}", json={
        "persona_prompt": "Anda adalah Lead Pen-Tester legendaris yang selalu menemukan zero-day."
    })
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["persona_prompt"] == "Anda adalah Lead Pen-Tester legendaris yang selalu menemukan zero-day."


@pytest.mark.asyncio
async def test_dynamic_node_3layer_prompt_assembly() -> None:
    """Menguji bahwa execute_dynamic_role_node menyusun sistem prompt 3-layer (Soul -> SOP -> User Context)."""
    captured_system_prompt: str = ""

    mock_llm = AsyncMock()
    async def fake_complete(prompt: str, system_prompt: str, **kwargs) -> str:
        nonlocal captured_system_prompt
        captured_system_prompt = system_prompt
        return '{"analysis": "Unit test verified"}'

    mock_llm.complete = AsyncMock(side_effect=fake_complete)

    state = VentureState(
        project_id="proj_3layer_test",
        project_name="ChurnShield",
        stage="SPARRING_ROOM",
        founder_idea="SaaS otomatisasi multi-agent.",
    )

    with patch("app.engine.runtime.model_router.sovereign_router.execute_routed_completion", side_effect=Exception("Trigger direct complete")):
        await execute_dynamic_role_node(
            role_identifier="role_cto",
            state=state,
            llm_client=mock_llm,
        )

    assert "=== CORE PERSONA & IDENTITY (IMMUTABLE SOUL) ===" in captured_system_prompt
    assert "anti-bloatware" in captured_system_prompt
    assert "=== OPERATIONAL DIRECTIVE & SOP ===" in captured_system_prompt
