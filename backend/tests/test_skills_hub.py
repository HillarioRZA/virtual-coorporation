"""
Unit Tests untuk SkillsHub, Dynamic Category Auto-Creation, Path Traversal Guards, dan Agent Tools.
"""

from pathlib import Path
import pytest
from app.db.init_db import init_database
from app.engine.skills.skills_hub import SkillsHub
from app.engine.skills.skill_agent_tools import tool_consult_skill_library, tool_read_skill_detail


@pytest.fixture
def skills_test_env(tmp_path):
    """Menyiapkan basis data dan folder root sementara untuk pengujian Skills."""
    db_file = str(tmp_path / "test_skills.db")
    skills_root = tmp_path / "skills_store"
    hub = SkillsHub(root_dir=skills_root)
    return {"db": db_file, "root": skills_root, "hub": hub}


@pytest.mark.asyncio
async def test_skills_hub_bundle_install_and_auto_category(skills_test_env):
    """Memverifikasi ekstraksi bundle skill dan pembuatan kategori otomatis saat kategori baru dimasukkan."""
    db_file = skills_test_env["db"]
    await init_database(custom_path=db_file)
    hub: SkillsHub = skills_test_env["hub"]

    files = {
        "SKILL.md": "# FLUTTER BLOC PLAYBOOK\n\nPanduan arsitektur BLoC pattern untuk Flutter.",
        "scripts/validate.py": "print('validating flutter code')",
    }

    # "Mobile Computing" adalah kategori baru yang belum pernah di-seed
    res = await hub.install_skill_bundle(
        name="flutter-bloc",
        category_name="Mobile Computing",
        files=files,
        custom_db_path=db_file,
    )

    assert res["name"] == "flutter-bloc"
    assert res["category"] == "Mobile Computing"

    # Periksa keberadaan berkas fisik
    dest = Path(res["folder_path"])
    assert (dest / "SKILL.md").exists()
    assert (dest / "scripts" / "validate.py").exists()

    # Periksa bahwa kategori baru tercatat di database
    cats = await hub.list_categories(custom_db_path=db_file)
    assert any(c["slug"] == "mobile-computing" for c in cats)


@pytest.mark.asyncio
async def test_skills_path_traversal_guard(skills_test_env):
    """Memverifikasi penolakan instalasi jika nama kategori atau skill memuat karakter path traversal."""
    db_file = skills_test_env["db"]
    await init_database(custom_path=db_file)
    hub: SkillsHub = skills_test_env["hub"]

    # Nama dengan karakter path traversal ditolak / disanitasi
    res = await hub.install_skill_bundle(
        name="../../../malicious",
        category_name="../../dangerous",
        files={"SKILL.md": "evil payload"},
        custom_db_path=db_file,
    )
    # Sanitasi mereduksi ke slug aman di dalam root
    target = Path(res["folder_path"])
    assert target.is_relative_to(skills_test_env["root"])


@pytest.mark.asyncio
async def test_skills_search_fts5(skills_test_env):
    """Memverifikasi pencarian FTS5 pada nama, deskripsi, dan konten skill."""
    db_file = skills_test_env["db"]
    await init_database(custom_path=db_file)
    hub: SkillsHub = skills_test_env["hub"]

    await hub.install_skill_bundle(
        name="stripe-checkout",
        category_name="Backend & API",
        files={"SKILL.md": "# STRIPE INTEGRATION\nGunakan idempotency key untuk payment gateway webhook."},
        custom_db_path=db_file,
    )

    results = await hub.search_skills("idempotency", custom_db_path=db_file)
    assert len(results) >= 1
    assert results[0]["name"] == "stripe-checkout"


@pytest.mark.asyncio
async def test_agent_tools_consult_and_read(skills_test_env, monkeypatch):
    """Memverifikasi eksekusi perkakas otonom consult_skill_library dan read_skill_detail."""
    db_file = skills_test_env["db"]
    await init_database(custom_path=db_file)
    hub: SkillsHub = skills_test_env["hub"]
    from app.engine.skills import skills_hub as sh_module

    monkeypatch.setattr(sh_module, "skills_hub", hub)

    await hub.install_skill_bundle(
        name="docker-hardening",
        category_name="DevOps & Cloud",
        files={"SKILL.md": "# DOCKER SECURITY\nJalankan non-root user dalam Dockerfile."},
        custom_db_path=db_file,
    )

    # 1. Consult skill library
    consult_res = await tool_consult_skill_library(project_id="proj_1", topic="hardening", custom_path=db_file)
    assert consult_res["status"] == "SUCCESS"
    assert consult_res["count"] >= 1
    assert consult_res["skills"][0]["name"] == "docker-hardening"

    # 2. Read skill detail
    read_res = await tool_read_skill_detail(project_id="proj_1", skill_name="docker-hardening", custom_path=db_file)
    assert read_res["status"] == "SUCCESS"
    assert "DOCKER SECURITY" in read_res["content"]
