"""
Unit & Integration Tests untuk Corporate Wisdom Base & Vector Memory (Sprint 3.3).
Menguji Deterministic Semantic Vectorizer, Cosine Similarity, Repository, Engine, dan REST API.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from app.db.init_db import init_database
from app.db.wisdom_repo import CorporateWisdomRepo
from app.engine.memory.vector_store import (
    DeterministicSemanticVectorizer,
    cosine_similarity,
    SovereignVectorStore,
)
from app.engine.memory.wisdom_engine import CorporateWisdomEngine
from app.engine.memory.context_builder import ContextBuilder
from app.engine.runtime.state import VentureState


@pytest.fixture
def clean_db(tmp_path):
    """Menyediakan path SQLite terisolasi untuk pengujian."""
    db_file = str(tmp_path / "test_wisdom.db")
    return db_file


@pytest.mark.asyncio
async def test_deterministic_vectorizer_and_similarity():
    """Menguji bahwa vectorizer 128-dimensi deterministik dan cosine similarity akurat."""
    vectorizer = DeterministicSemanticVectorizer(dimension=128)
    
    text_a = "Fix CORS middleware pipeline ordering on FastAPI 401 Unauthorized"
    text_b = "CORS headers missing on error 401 status in browser fetch"
    text_c = "High-converting B2B SaaS landing page hero section copywriting"

    vec_a = vectorizer.vectorize(text_a)
    vec_b = vectorizer.vectorize(text_b)
    vec_c = vectorizer.vectorize(text_c)

    assert len(vec_a) == 128
    assert len(vec_b) == 128
    assert len(vec_c) == 128

    sim_ab = cosine_similarity(vec_a, vec_b)
    sim_ac = cosine_similarity(vec_a, vec_c)

    # Teks A dan B membahas topik yang sama (CORS & 401), sedangkan C sangat berbeda
    assert sim_ab > 0.25, f"Expected high similarity between related texts, got {sim_ab}"
    assert sim_ac < sim_ab, f"Expected lower similarity for unrelated text, got {sim_ac} vs {sim_ab}"


@pytest.mark.asyncio
async def test_corporate_wisdom_repo_crud(clean_db):
    """Menguji operasi CRUD pada CorporateWisdomRepo."""
    await init_database(custom_path=clean_db)
    repo = CorporateWisdomRepo()

    # 1. Simpan wisdom
    saved = await repo.save_wisdom(
        wisdom_id="wis_test_001",
        namespace="wisdom:architecture",
        title="Test Architecture Pattern",
        problem_pattern="Testing problem pattern",
        solution_guideline="Testing prescriptive solution",
        tags=["arch", "unit_test"],
        embedding=[0.1] * 128,
        source_venture_id="proj_test_1",
        custom_path=clean_db,
    )
    assert saved["id"] == "wis_test_001"
    assert saved["namespace"] == "wisdom:architecture"
    assert "unit_test" in saved["tags"]

    # 2. Ambil by ID
    fetched = await repo.get_wisdom_by_id("wis_test_001", custom_path=clean_db)
    assert fetched is not None
    assert fetched["title"] == "Test Architecture Pattern"

    # 3. List dengan filter namespace
    list_arch = await repo.list_wisdom(namespace="wisdom:architecture", custom_path=clean_db)
    assert any(w["id"] == "wis_test_001" for w in list_arch)

    # 4. Increment usage
    await repo.increment_usage("wis_test_001", custom_path=clean_db)
    updated = await repo.get_wisdom_by_id("wis_test_001", custom_path=clean_db)
    assert updated["usage_count"] == 1

    # 5. Soft delete
    deleted = await repo.delete_wisdom("wis_test_001", custom_path=clean_db)
    assert deleted is True
    assert await repo.get_wisdom_by_id("wis_test_001", custom_path=clean_db) is None


@pytest.mark.asyncio
async def test_wisdom_engine_and_context_injection(clean_db):
    """Menguji CorporateWisdomEngine dan injeksi Tier 0 ke ContextBuilder."""
    await init_database(custom_path=clean_db)
    repo = CorporateWisdomRepo()
    store = SovereignVectorStore()
    engine = CorporateWisdomEngine(repo=repo, store=store)

    # Catat pembelajaran baru
    await engine.record_wisdom(
        title="Pydantic Serialization Rule",
        problem_pattern="Accessing model_fields on instance triggers deprecation warning in v2.11",
        solution_guideline="Use model_fields on model class, not instance.",
        namespace="wisdom:bugs_and_fixes",
        tags=["pydantic", "python", "backend"],
        custom_path=clean_db,
    )

    # Query relevan untuk peran backend
    results = await engine.query_wisdom(
        query="Pydantic model fields deprecation warning",
        target_role="role_be",
        custom_path=clean_db,
    )
    assert len(results) > 0
    assert results[0]["similarity_score"] > 0.20

    # Injeksi ke ContextBuilder
    state = VentureState(project_id="proj_test_ctx", project_name="Test Venture", founder_idea="AI SaaS")
    scoped_events = [{"sender_role": "CEO", "content": "Implement auth models."}]
    context = ContextBuilder.assemble_context(
        target_role="BACKEND",
        state=state,
        scoped_events=scoped_events,
        wisdom_items=results,
    )

    # Pastikan pesan pertama adalah Tier 0 Corporate Wisdom
    assert any("CORPORATE WISDOM" in msg["content"] for msg in context)


@pytest.mark.asyncio
async def test_wisdom_rest_api_endpoints():
    """Menguji endpoint REST API /api/v1/wisdom."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. List wisdom (sudah berisi seeding bawaan)
        res_list = await ac.get("/api/v1/wisdom")
        assert res_list.status_code == 200
        items = res_list.json()
        assert len(items) >= 3

        # 2. Create wisdom
        payload = {
            "namespace": "wisdom:architecture",
            "title": "API Gateway Rate Limit Pattern",
            "problem_pattern": "Cascading failures during upstream model rate limiting",
            "solution_guideline": "Apply sliding-window pre-flight checks and retry-after cooldowns.",
            "tags": ["router", "rate_limit", "gateway"],
            "source_venture_id": "global",
        }
        res_create = await ac.post("/api/v1/wisdom", json=payload)
        assert res_create.status_code == 201
        created_id = res_create.json()["id"]

        # 3. Search wisdom
        res_search = await ac.post(
            "/api/v1/wisdom/search",
            json={"query": "sliding window rate limit upstream", "top_k": 2},
        )
        assert res_search.status_code == 200
        search_results = res_search.json()
        assert len(search_results) > 0
        assert search_results[0]["similarity_score"] > 0.20

        # 4. Summary metrics
        res_summary = await ac.get("/api/v1/wisdom/summary")
        assert res_summary.status_code == 200
        summary = res_summary.json()
        assert summary["total_count"] >= 4
        assert "wisdom:architecture" in summary["namespace_breakdown"]

        # 5. Delete wisdom
        res_del = await ac.delete(f"/api/v1/wisdom/{created_id}")
        assert res_del.status_code == 200
