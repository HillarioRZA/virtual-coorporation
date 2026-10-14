"""
Unit & Integration Tests untuk Git-Style Autonomous Three-Way Branch Merge (Sprint 3.4).
Menguji deteksi Lowest Common Ancestor (LCA), Fast-Forward merge, 3-Way merge, dan resolusi konflik.
"""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from app.db.init_db import init_database
from app.db.branch_repo import branch_repo
from app.db.division_repo import division_repo
from app.db.role_repo import role_repo
from app.engine.branch_merge import branch_merge_engine
from app.engine.corporate_schemas import RoleCreate


@pytest.fixture
def clean_db(tmp_path):
    """Menyediakan path SQLite terisolasi untuk pengujian merge."""
    db_file = str(tmp_path / "test_merge.db")
    return db_file


@pytest.mark.asyncio
async def test_find_lowest_common_ancestor(clean_db):
    """Menguji kalkulasi Lowest Common Ancestor (LCA) berbasis traversi graf branch."""
    await init_database(custom_path=clean_db)

    # 1. Fork branch_feat_1 dari branch_main
    b1 = await branch_repo.fork_branch(
        name="Feature ML", slug="feat-ml", source_branch_id="branch_main", custom_path=clean_db
    )
    # 2. Fork branch_feat_2 dari branch_feat_1
    b2 = await branch_repo.fork_branch(
        name="Subfeature NLP", slug="subfeat-nlp", source_branch_id=b1["id"], custom_path=clean_db
    )

    lca_1_main = await branch_merge_engine.find_lca(b1["id"], "branch_main", custom_path=clean_db)
    assert lca_1_main == "branch_main"

    lca_2_1 = await branch_merge_engine.find_lca(b2["id"], b1["id"], custom_path=clean_db)
    assert lca_2_1 == b1["id"]

    lca_2_main = await branch_merge_engine.find_lca(b2["id"], "branch_main", custom_path=clean_db)
    assert lca_2_main == "branch_main"


@pytest.mark.asyncio
async def test_preview_and_fast_forward_merge(clean_db):
    """Menguji penambahan peran baru dan penggabungan Fast-Forward ke branch_main."""
    await init_database(custom_path=clean_db)

    # 1. Fork branch
    feat_b = await branch_repo.fork_branch(
        name="Branch New Roles", slug="feat-roles", source_branch_id="branch_main", custom_path=clean_db
    )

    # 2. Tambah peran baru di feature branch menggunakan divisi milik branch tersebut
    divs = await division_repo.get_divisions(feat_b["id"], custom_path=clean_db)
    div_id = divs[0]["id"]
    await role_repo.create_role(
        branch_id=feat_b["id"],
        division_id=div_id,
        name="ML Engineer",
        slug="ml-engineer",
        system_prompt_template="You are ML Engineer.",
        model_name="deepseek/deepseek-r1:free",
        custom_path=clean_db,
    )

    # 3. Preview merge
    preview = await branch_merge_engine.preview_merge(
        source_id=feat_b["id"], target_id="branch_main", custom_path=clean_db
    )
    assert preview["has_conflicts"] is False
    assert len(preview["added_roles"]) == 1
    assert preview["added_roles"][0]["slug"] == "ml-engineer"

    # 4. Execute merge
    result = await branch_merge_engine.execute_merge(
        source_id=feat_b["id"], target_id="branch_main", custom_path=clean_db
    )
    assert result["status"] == "MERGED"
    assert result["added_roles_count"] == 1

    # 5. Verifikasi role baru telah tersinkron di branch_main
    main_roles = await role_repo.get_roles("branch_main", custom_path=clean_db)
    assert any(r["slug"] == "ml-engineer" for r in main_roles)


@pytest.mark.asyncio
async def test_three_way_merge_conflict_resolution(clean_db):
    """Menguji deteksi konflik saat parameter peran yang sama diubah berlainan pada kedua branch."""
    await init_database(custom_path=clean_db)

    # 1. Fork branch
    feat_b = await branch_repo.fork_branch(
        name="Branch Conflict Test", slug="feat-conflict", source_branch_id="branch_main", custom_path=clean_db
    )

    # 2. Ubah role CTO di feat_b ke temperatur 0.8 dan model X
    main_roles = await role_repo.get_roles("branch_main", custom_path=clean_db)
    feat_roles = await role_repo.get_roles(feat_b["id"], custom_path=clean_db)

    cto_main = next(r for r in main_roles if r["slug"] == "cto")
    cto_feat = next(r for r in feat_roles if r["slug"] == "cto")

    # Modifikasi di main
    await role_repo.update_role(
        role_id=cto_main["id"],
        model_name="qwen/qwen-2.5-coder-32b-instruct:free",
        temperature=0.1,
        custom_path=clean_db,
    )

    # Modifikasi berbeda di feature branch
    await role_repo.update_role(
        role_id=cto_feat["id"],
        model_name="meta-llama/llama-3.3-70b-instruct:free",
        temperature=0.8,
        custom_path=clean_db,
    )

    # 3. Preview mendeteksi konflik model
    preview = await branch_merge_engine.preview_merge(
        source_id=feat_b["id"], target_id="branch_main", custom_path=clean_db
    )
    assert preview["has_conflicts"] is True
    assert len(preview["conflicts"]) == 1

    # 4. Eksekusi dengan auto harus gagal karena konflik
    with pytest.raises(ValueError):
        await branch_merge_engine.execute_merge(
            source_id=feat_b["id"], target_id="branch_main", strategy="auto", custom_path=clean_db
        )

    # 5. Eksekusi dengan prefer_theirs berhasil menimpa model CTO di main
    merged = await branch_merge_engine.execute_merge(
        source_id=feat_b["id"], target_id="branch_main", strategy="prefer_theirs", custom_path=clean_db
    )
    assert merged["status"] == "MERGED"

    updated_main = await role_repo.get_role_by_id(cto_main["id"], custom_path=clean_db)
    assert updated_main["model_name"] == "meta-llama/llama-3.3-70b-instruct:free"


@pytest.mark.asyncio
async def test_branch_merge_api_endpoints():
    """Menguji endpoint REST API /api/v1/corporate/branches/merge-preview dan /merge."""
    await init_database()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Fork branch uji via API dengan slug unik
        feat_slug = f"api-merge-{uuid.uuid4().hex[:6]}"
        res_fork = await ac.post(
            "/api/v1/corporate/branches/fork",
            json={"name": "API Merge Feat", "slug": feat_slug, "source_branch_id": "branch_main"},
        )
        assert res_fork.status_code == 201
        feat_id = res_fork.json()["id"]

        # Preview merge endpoint
        res_prev = await ac.post(
            "/api/v1/corporate/branches/merge-preview",
            json={"source_branch_id": feat_id, "target_branch_id": "branch_main"},
        )
        assert res_prev.status_code == 200
        prev_data = res_prev.json()
        assert "can_fast_forward" in prev_data

        # Execute merge endpoint
        res_merge = await ac.post(
            "/api/v1/corporate/branches/merge",
            json={"source_branch_id": feat_id, "target_branch_id": "branch_main", "strategy": "auto"},
        )
        assert res_merge.status_code == 200
        assert res_merge.json()["status"] == "MERGED"
