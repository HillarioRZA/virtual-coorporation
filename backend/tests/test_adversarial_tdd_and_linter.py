"""Unit tests for Pillar 2 (Preflight & Adversarial TDD), Pillar 3 (Semantic Linter & Editorial), and Pillar 5 (Citation & Design Tokens)."""

import json
from pathlib import Path
from typing import Any, Dict
import httpx
import pytest

from app.engine.citation_auditor import audit_text_citations, extract_citation_urls
from app.engine.design_token_engine import generate_design_tokens, load_design_tokens
from app.engine.editorial_reviewer import editorial_reviewer
from app.engine.nodes.backend import BackendOutputEnvelope, write_backend_files
from app.engine.nodes.frontend import FrontendCodeBundle, write_frontend_files
from app.engine.preflight_auditor import audit_project_dependencies
from app.engine.semantic_linter import (
    compute_flesch_metrics,
    detect_and_strip_cliches,
    lint_copy_or_educational_content,
)
from app.engine.state import VentureState


def test_preflight_auditor_detects_hallucinations(tmp_path: Path) -> None:
    """Memastikan paket yang tidak terdaftar di requirements.txt ditandai sebagai missing."""
    backend_dir = tmp_path / "backend"
    backend_dir.mkdir(parents=True)
    (backend_dir / "requirements.txt").write_text("fastapi==0.110.0\npydantic>=2.0\n", encoding="utf-8")

    # Tulis kode Python dengan impor fiktif
    (backend_dir / "main.py").write_text(
        "import fastapi\nimport non_existent_hallucinated_lib\nfrom math import sqrt\n",
        encoding="utf-8",
    )

    report = audit_project_dependencies(tmp_path)
    assert report.is_valid is False
    assert "non_existent_hallucinated_lib" in report.missing_python_packages
    assert "fastapi" not in report.missing_python_packages


def test_adversarial_tdd_blocks_read_only_overwrites(tmp_path: Path) -> None:
    """Memastikan agen developer tidak dapat menimpa berkas yang terdaftar di read_only_files."""
    state = VentureState(
        project_id="proj_tdd_test",
        project_name="TDD Test Project",
        founder_idea="A project for testing adversarial TDD guardrails.",
        read_only_files=["tests/test_api.py", "main.py"],
    )

    envelope = BackendOutputEnvelope(
        main_code="# New Code Attempting Overwrite exceeding 20 chars",
        models_code="class User(Base):\n    id = 1\n",
        routers_code="# routers FastAPI endpoints exceeding 20 chars",
        migration_code="# alembic migration code exceeding 20 chars",
        requirements_content="fastapi>=0.110.0\n",
    )

    # Jalankan write_backend_files dengan read_only_files
    out_dir = write_backend_files(state.project_id, envelope, state.read_only_files)
    # main.py tidak boleh tertulis karena berstatus read-only
    assert not (out_dir / "main.py").exists()
    # models.py boleh tertulis
    assert (out_dir / "models.py").exists()



def test_semantic_linter_flesch_and_cliches() -> None:
    """Menguji kalkulasi skor keterbacaan dan pembersihan kata klise AI."""
    sample_text = (
        "In today's digital era, we delve into a game changer solution. "
        "Tantangan utama bisnis adalah konversi yang rendah. "
        "Solusi kami membantu melipatgandakan omset dengan cepat. "
        "Daftar sekarang untuk memulai."
    )
    report = lint_copy_or_educational_content(sample_text)
    assert report.flesch_reading_ease > 0
    assert len(report.cliches_detected) >= 2
    assert "delve into" in report.cliches_detected
    assert report.has_aida_structure is True


@pytest.mark.asyncio
async def test_citation_auditor_mock_network() -> None:
    """Menguji audit tautan sitasi dengan mock transport httpx."""
    text_with_links = (
        "Berdasarkan riset pasar [^1], adopsi AI tumbuh pesat. "
        "Tautan referensi: https://example.com/valid dan https://example.com/broken"
    )
    urls = extract_citation_urls(text_with_links)
    assert len(urls) == 2

    def handler(request: httpx.Request) -> httpx.Response:
        if "valid" in str(request.url):
            return httpx.Response(200, json={"status": "ok"})
        return httpx.Response(404, text="Not Found")

    transport = httpx.MockTransport(handler)
    report = await audit_text_citations(text_with_links, custom_transport=transport)
    assert report.total_citations == 2
    assert len(report.verified_urls) == 1
    assert len(report.broken_urls) == 1
    assert report.grounding_score == 50.0


def test_design_token_engine(tmp_path: Path) -> None:
    """Menguji sintesis token desain dan penulisan berkas JSON."""
    tokens = generate_design_tokens("proj_brand_test", archetype_id=2, brand_name="CyberTech", custom_dir=tmp_path)
    assert tokens["archetype_id"] == 2
    assert tokens["colors"]["primary"] == "#8b5cf6"
    assert "visual_prompts" in tokens

    loaded = load_design_tokens("proj_brand_test", custom_dir=tmp_path)
    assert loaded is not None
    assert loaded["brand_name"] == "CyberTech"


@pytest.mark.asyncio
async def test_editorial_reviewer_quorum_gate(tmp_path: Path) -> None:
    """Menguji evaluasi dewan redaksi P2P dan verifikasi kuorum pada PR repo."""
    from app.db.init_db import init_database
    from app.db.pr_repo import pr_repo

    test_db = str(tmp_path / "test_editorial.db")
    await init_database(custom_path=test_db)

    # Buat PR baru untuk konten non-software
    pr = await pr_repo.create_pull_request(
        project_id="proj_content",
        ticket_id="tick_copy_1",
        title="Landing Page Copywriting",
        description="Materi copywriting landing page produk edukasi",
        source_branch="branch_main",
        author_role_id="role_pm",
        files_changed=[{"path": "copy.md"}],
        quorum_required=2,
        custom_path=test_db,
    )

    clean_content = (
        "Finding validated business ideas is hard for many new startup teams. "
        "Our autonomous software helps you research markets quickly and easily. "
        "Sign up today for a free trial to get started."
    )

    eval_res = await editorial_reviewer.evaluate_non_software_submission(
        pr_id=pr["id"],
        content=clean_content,
        project_id="proj_content",
        custom_path=test_db,
    )

    assert eval_res["quorum_met"] is True
    assert eval_res["status"] == "APPROVED"
    assert eval_res["approvals_count"] >= 2

