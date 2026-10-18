"""
Unit Test Suite untuk Fase 1 (Next-Gen Toolset, Adversarial TDD, dan Prompt Caching).
"""

from pathlib import Path
import sqlite3
import pytest

from app.engine.tools.db_inspector import DatabaseInspector
from app.engine.tools.contract_validator import ContractValidator
from app.engine.tools.diff_digest import DiffDigestGenerator
from app.gateway.adapters.anthropic_adapter import AnthropicAdapter
from app.engine.nodes.backend import write_backend_files, BackendOutputEnvelope
from app.engine.nodes.frontend import write_frontend_files, FrontendCodeBundle


@pytest.fixture
def temp_venture_db(tmp_path: Path) -> Path:
    """Fixture membuat database SQLite sementara dengan skema uji."""
    db_file = tmp_path / "backend" / "venture.db"
    db_file.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_file) as conn:
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE);")
        conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, FOREIGN KEY(user_id) REFERENCES users(id));")
        conn.execute("INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com'), ('Bob', 'bob@example.com');")
    return tmp_path


def test_database_inspector(temp_venture_db: Path) -> None:
    """Menguji fungsionalitas DatabaseInspector read-only dan blokir mutasi."""
    inspector = DatabaseInspector(projects_dir=temp_venture_db.parent)
    project_id = temp_venture_db.name

    tables = inspector.list_tables(project_id)
    assert "users" in tables
    assert "orders" in tables

    schema = inspector.inspect_table_schema(project_id, "users")
    assert schema["table"] == "users"
    assert len(schema["columns"]) == 3
    col_names = [c["name"] for c in schema["columns"]]
    assert "id" in col_names
    assert "name" in col_names

    res = inspector.execute_safe_query(project_id, "SELECT * FROM users")
    assert res["count"] == 2
    assert res["rows"][0]["name"] == "Alice"

    # Uji penolakan mutasi berbahaya
    mutation_res = inspector.execute_safe_query(project_id, "DROP TABLE users;")
    assert "error" in mutation_res
    assert "Hanya operasi SELECT dan PRAGMA" in mutation_res["error"]


def test_contract_validator() -> None:
    """Menguji validasi OpenAPI contract compliance validator."""
    validator = ContractValidator()
    spec = {
        "paths": {
            "/api/v1/users": {"get": {}, "post": {}},
            "/api/v1/users/{id}": {"get": {}},
        }
    }

    matching_code = """
    @router.get('/api/v1/users')
    def get_users(): pass
    @router.post('/api/v1/users')
    def create_user(): pass
    @router.get('/api/v1/users/{id}')
    def get_user(): pass
    """
    res = validator.validate_code_against_spec("proj_1", matching_code, spec_override=spec)
    assert res["valid"] is True
    assert len(res["missing_in_code"]) == 0

    # Kode tidak lengkap
    incomplete_code = """
    @router.get('/api/v1/users')
    def get_users(): pass
    """
    res_bad = validator.validate_code_against_spec("proj_1", incomplete_code, spec_override=spec)
    assert res_bad["valid"] is False
    assert len(res_bad["missing_in_code"]) == 2


@pytest.mark.asyncio
async def test_diff_digest(tmp_path: Path) -> None:
    """Menguji pembuatan ringkasan diff Git."""
    generator = DiffDigestGenerator(projects_dir=tmp_path)
    res = await generator.get_diff_summary("non_existent_proj")
    assert res["success"] is False


def test_anthropic_prompt_caching() -> None:
    """Menguji kesiapan prompt caching headers dan payload pada AnthropicAdapter."""
    adapter = AnthropicAdapter()
    headers = adapter._build_headers("test_key")
    assert headers["anthropic-beta"] == "prompt-caching-2024-07-31"

    cached_blocks = adapter._build_cached_system("System instructions here")
    assert isinstance(cached_blocks, list)
    assert cached_blocks[0]["cache_control"] == {"type": "ephemeral"}


def test_adversarial_tdd_guardrails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Menguji penolakan modifikasi file tes oleh node Backend dan Frontend."""
    import app.engine.nodes.backend as backend_node
    monkeypatch.setattr(backend_node, "PROJECTS_OUTPUT_DIR", tmp_path)

    envelope = BackendOutputEnvelope(
        main_code="import fastapi\napp = fastapi.FastAPI()\n# Main backend entrypoint",
        models_code="class User:\n    id: int\n    name: str\n    email: str",
        routers_code="from fastapi import APIRouter\nrouter = APIRouter()",
        migration_code="def upgrade():\n    pass\ndef downgrade():\n    pass",
        requirements_content="fastapi>=0.110.0\nuvicorn>=0.28.0\n",
    )
    # Tulis file tes palsu terlebih dahulu
    proj_dir = tmp_path / "proj_test" / "backend"
    proj_dir.mkdir(parents=True, exist_ok=True)
    test_file = proj_dir / "test_api.py"
    test_file.write_text("ORIGINAL_TEST_CODE", encoding="utf-8")

    # Agen developer mencoba menimpa
    write_backend_files("proj_test", envelope, read_only_files=["test_api.py"])
    assert test_file.read_text(encoding="utf-8") == "ORIGINAL_TEST_CODE"
