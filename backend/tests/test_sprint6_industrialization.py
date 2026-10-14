"""
Unit & Integration Tests untuk Sprint 6: Industrialization, Secret Vault & PaaS Deploy.
Menguji AES-256 SecretVaultManager, REST Vault API, Backend Node, QA OWASP audit,
Legal bundle generator, DevSecOps packaging, dan validasi siklus penuh end-to-end (TASK-6.2.4).
"""

from pathlib import Path
from typing import AsyncGenerator
import httpx
import pytest
import pytest_asyncio

from app.core.config import settings
from app.core.security import SecretVaultManager
from app.db.init_db import init_database
from app.engine.memory import MemoryManager
from app.engine.nodes.backend import backend_engineering_node
from app.engine.nodes.devsecops import devsecops_packaging_node
from app.engine.nodes.hardening import production_hardening_node
from app.engine.nodes.legal import legal_compliance_node
from app.engine.nodes.qa import qa_eval_node
from app.engine.routers import router_deploy_live, router_gate_3
from app.engine.schemas import BusinessBriefSchema, SystemArchitectureSchema
from app.engine.state import VentureState
from app.engine.state_machine import NativeStateMachine
from app.gateway.client import UnifiedLLMClient
from main import app


@pytest_asyncio.fixture
async def temp_db_path(tmp_path: Path) -> str:
    """Fixture path basis data SQLite terisolasi."""
    db_file = tmp_path / "test_sprint6.db"
    db_str = str(db_file)
    await init_database(db_str)
    return db_str


@pytest_asyncio.fixture
async def test_client(temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Fixture HTTP AsyncClient terkonfigurasi ke database sementara."""
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite+aiosqlite:///{temp_db_path}")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def mock_llm_client() -> UnifiedLLMClient:
    """Mock LLM client yang mengembalikan JSON terformat valid untuk seluruh node industri."""
    client = UnifiedLLMClient()

    async def mock_complete(*args, **kwargs) -> str:
        prompt = kwargs.get("prompt", "")
        system_prompt = kwargs.get("system_prompt", "")
        content = f"{prompt} {system_prompt} {' '.join(str(a) for a in args)}"
        if "Backend Engineer" in content or "alembic_migration.py" in content or "FastAPI" in content:
            return (
                '```json\n{\n'
                '  "main_code": "from fastapi import FastAPI\\napp = FastAPI()\\n@app.get(\'/health\')\\ndef h(): return {\'ok\': True}",\n'
                '  "models_code": "from sqlalchemy.orm import declarative_base\\nBase = declarative_base()",\n'
                '  "routers_code": "from fastapi import APIRouter\\nrouter = APIRouter()",\n'
                '  "migration_code": "def upgrade(): pass\\ndef downgrade(): pass",\n'
                '  "requirements_content": "fastapi>=0.115.0\\nuvicorn>=0.31.0\\nsqlalchemy>=2.0.0"\n'
                '}\n```'
            )
        elif "Security Auditor" in content or "QualityGateScorecard" in content or "OWASP" in content:
            return (
                '```json\n{\n'
                '  "unit_test_passed": true,\n'
                '  "test_coverage_percentage": 94.5,\n'
                '  "owasp_vulnerabilities_count": 0,\n'
                '  "hallucination_rate": 0.0,\n'
                '  "status": "PASSED",\n'
                '  "reasons": ["Parameterization valid", "No credentials exposed"]\n'
                '}\n```'
            )
        elif "Legal Counsel" in content or "Terms of Service" in content:
            return (
                '```json\n{\n'
                '  "terms_of_service": "# Terms of Service\\nSelamat datang di platform SaaS ini...",\n'
                '  "privacy_policy": "# Privacy Policy\\nKami menghormati privasi data Anda sesuai UU PDP...",\n'
                '  "refund_policy": "# Refund Policy\\nGaransi uang kembali 14 hari kerja..."\n'
                '}\n```'
            )
        else:  # DevSecOps
            return (
                '```json\n{\n'
                '  "docker_compose_yaml": "version: \'3.8\'\\nservices:\\n  backend:\\n    build: ./backend\\n    ports: [\'8000:8000\']",\n'
                '  "production_env_sample": "APP_ENV=production\\nPORT=8000",\n'
                '  "deployment_payload": {"provider": "coolify", "status": "ready"}\n'
                '}\n```'
            )

    client.complete = mock_complete  # type: ignore
    return client


def test_aes_gcm_vault_encryption_and_tamper(temp_db_path: str) -> None:
    """TASK-6.1.1: Menguji enkripsi AES-256-GCM dan proteksi tamper data."""
    vault = SecretVaultManager(custom_db_path=temp_db_path)
    secret_text = "sk_live_51Mtest_stripe_secret_key_998877"

    encrypted_b64 = vault.encrypt(secret_text)
    assert encrypted_b64 != secret_text

    decrypted = vault.decrypt(encrypted_b64)
    assert decrypted == secret_text

    # Modifikasi payload base64 secara acak untuk memicu kegagalan autentikasi tag
    tampered_bytes = bytearray(encrypted_b64.encode("utf-8"))
    tampered_bytes[15] = (tampered_bytes[15] + 1) % 256
    with pytest.raises(ValueError):
        vault.decrypt(tampered_bytes.decode("utf-8"))


@pytest.mark.asyncio
async def test_secret_vault_sqlite_lifecycle(temp_db_path: str) -> None:
    """TASK-6.1.1: Menguji siklus hidup simpan, baca, dan daftar kunci vault di SQLite."""
    vault = SecretVaultManager(custom_db_path=temp_db_path)
    p_id = "proj_vault_test"

    await vault.store_secret(p_id, "STRIPE_SECRET_KEY", "sk_live_12345")
    await vault.store_secret(p_id, "DATABASE_URL", "postgresql://user:pass@db:5432/app")

    keys = await vault.list_secret_keys(p_id)
    assert "DATABASE_URL" in keys
    assert "STRIPE_SECRET_KEY" in keys

    val = await vault.get_secret(p_id, "STRIPE_SECRET_KEY")
    assert val == "sk_live_12345"

    all_secrets = await vault.get_all_decrypted(p_id)
    assert all_secrets["STRIPE_SECRET_KEY"] == "sk_live_12345"
    assert all_secrets["DATABASE_URL"] == "postgresql://user:pass@db:5432/app"


@pytest.mark.asyncio
async def test_vault_api_endpoints(test_client: httpx.AsyncClient) -> None:
    """TASK-6.1.2: Menguji endpoint REST API /vault/secrets."""
    # Inisialisasi proyek
    c_res = await test_client.post(
        "/api/v1/projects",
        json={"name": "Vault Venture", "founder_idea": "Platform finance with secrets.", "archetype_id": 1},
    )
    p_id = c_res.json()["data"]["project_id"]

    # Simpan kredensial
    secrets_payload = {
        "secrets": {
            "STRIPE_SECRET_KEY": "sk_live_abcdef123456",
            "MIDTRANS_SERVER_KEY": "Mid-server-998877",
        }
    }
    store_res = await test_client.post(f"/api/v1/projects/{p_id}/vault/secrets", json=secrets_payload)
    assert store_res.status_code == 200
    assert "berhasil dienkripsi" in store_res.json()["message"]

    # Ambil daftar kunci rahasia (tanpa plaintext)
    list_res = await test_client.get(f"/api/v1/projects/{p_id}/vault/secrets")
    assert list_res.status_code == 200
    data = list_res.json()["data"]
    assert "STRIPE_SECRET_KEY" in data["keys"]
    assert "MIDTRANS_SERVER_KEY" in data["keys"]
    assert data["total_stored"] == 2


@pytest.mark.asyncio
async def test_backend_and_qa_nodes(
    temp_db_path: str,
    mock_llm_client: UnifiedLLMClient,
) -> None:
    """TASK-6.1.3 & TASK-6.2.1: Menguji node Backend Engineer dan QA Lead."""
    mem = MemoryManager(db_path=temp_db_path)
    state = VentureState(
        project_id="proj_be_test",
        project_name="Inventory App",
        founder_idea="SaaS retail stock tracking.",
        selected_archetype=1,
        stage="PRODUCTION_HARDENING",
    )
    await mem.save_checkpoint(state)

    # 1. Eksekusi Backend Node
    be_res = await backend_engineering_node(state, llm_client=mock_llm_client, memory_manager=mem)
    assert "BACKEND" in state.token_usage
    be_dir = Path("projects_output") / "proj_be_test" / "backend"
    assert (be_dir / "main.py").exists()
    assert (be_dir / "models.py").exists()

    # 2. Eksekusi QA Node
    qa_res = await qa_eval_node(state, llm_client=mock_llm_client, memory_manager=mem)
    assert state.quality_scorecard is not None
    assert state.quality_scorecard.status == "PASSED"
    assert state.quality_scorecard.owasp_vulnerabilities_count == 0


@pytest.mark.asyncio
async def test_legal_and_devsecops_nodes(
    temp_db_path: str,
    mock_llm_client: UnifiedLLMClient,
) -> None:
    """TASK-6.2.2 & TASK-6.2.3: Menguji node Legal dan DevSecOps packaging."""
    mem = MemoryManager(db_path=temp_db_path)
    vault = SecretVaultManager(custom_db_path=temp_db_path)
    p_id = "proj_ops_test"

    state = VentureState(
        project_id=p_id,
        project_name="Legal Tech SaaS",
        founder_idea="AI contract automation.",
        selected_archetype=1,
        stage="PRODUCTION_HARDENING",
    )
    await mem.save_checkpoint(state)
    await vault.store_secret(p_id, "PROD_DATABASE_URL", "postgresql://cloud:pass@db:5432/app")

    # 1. Eksekusi Legal Node
    await legal_compliance_node(state, llm_client=mock_llm_client, memory_manager=mem)
    legal_dir = Path("projects_output") / p_id / "legal"
    assert (legal_dir / "terms_of_service.md").exists()
    assert (legal_dir / "privacy_policy.md").exists()

    # 2. Eksekusi DevSecOps Node
    await devsecops_packaging_node(
        state,
        llm_client=mock_llm_client,
        memory_manager=mem,
        vault_manager=vault,
    )
    bundle_dir = Path("projects_output") / p_id
    assert (bundle_dir / "docker-compose.yml").exists()
    env_content = (bundle_dir / ".env.production").read_text(encoding="utf-8")
    assert "PROD_DATABASE_URL=postgresql://cloud:pass@db:5432/app" in env_content


def test_router_gate_3_and_deploy_live() -> None:
    """Menguji penentu rute transisi Stage-Gate 3 dan deploy live."""
    state = VentureState(
        project_id="proj_r3",
        project_name="Router Test",
        founder_idea="Idea",
        stage="GATE_3_WAITING",
    )

    state.gate_decision = "APPROVE"
    assert router_gate_3(state) == "DEPLOY_LIVE"

    state.gate_decision = "REVISE"
    assert router_gate_3(state) == "PRODUCTION_HARDENING"

    state.gate_decision = "KILL"
    assert router_gate_3(state) == "PROJECT_KILLED"

    assert router_deploy_live(state) == "LIVE_OBSERVABILITY"


@pytest.mark.asyncio
async def test_full_venture_lifecycle_to_production(
    temp_db_path: str,
    mock_llm_client: UnifiedLLMClient,
) -> None:
    """TASK-6.2.4: Validasi final DoD: Siklus penuh dari Sparring -> Demo Prototype -> Production Deploy."""
    mem = MemoryManager(db_path=temp_db_path)
    vault = SecretVaultManager(custom_db_path=temp_db_path)
    p_id = "proj_e2e_full"

    state = VentureState(
        project_id=p_id,
        project_name="AutoEnterprise Cloud",
        founder_idea="SaaS Enterprise Resource Planning.",
        selected_archetype=1,
        stage="SPARRING_ROOM",
    )
    await mem.save_checkpoint(state)

    fsm = NativeStateMachine(checkpointer=mem.save_checkpoint)

    # 1. Daftarkan composite hardening node & router
    fsm.register_node("PRODUCTION_HARDENING", lambda s: production_hardening_node(s, llm_client=mock_llm_client, memory_manager=mem))
    fsm.register_router("PRODUCTION_HARDENING", lambda s: "GATE_3_WAITING")

    # 2. Jalankan step Production Hardening
    state.stage = "PRODUCTION_HARDENING"
    state = await fsm.step(state)
    assert state.stage == "GATE_3_WAITING"
    assert state.quality_scorecard is not None

    # 3. Founder menginjeksi secret dan menyetujui Gate 3
    await vault.store_secret(p_id, "STRIPE_SECRET_KEY", "sk_live_enterprise_prod")
    state.gate_decision = "APPROVE"
    state.stage = router_gate_3(state)
    assert state.stage == "DEPLOY_LIVE"

    # 4. Daftarkan DevSecOps packaging node & router
    fsm.register_node("DEPLOY_LIVE", lambda s: devsecops_packaging_node(s, llm_client=mock_llm_client, memory_manager=mem, vault_manager=vault))
    fsm.register_router("DEPLOY_LIVE", router_deploy_live)

    # 5. Jalankan step Deploy Live
    state = await fsm.step(state)
    assert state.stage == "LIVE_OBSERVABILITY"

    # Verifikasi berkas final tersimpan
    assert (Path("projects_output") / p_id / "docker-compose.yml").exists()
    assert (Path("projects_output") / p_id / "backend" / "main.py").exists()
    assert (Path("projects_output") / p_id / "legal" / "terms_of_service.md").exists()
