"""Unit tests for Pillar 6 (Cross-Division Bridge), Pillar 7 (Artifact Packager), and Pillar 8 (Launchpad Artifact API)."""

import json
from pathlib import Path
from typing import Any, Dict
import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.project_artifacts import router as artifacts_router
from app.engine.tools.artifact_compiler import (
    compile_ad_campaign_bundle,
    compile_ebook_document,
    compile_presentation_deck,
    list_project_artifacts,
)
from app.engine.memory.context_builder import ContextBuilder
from app.engine.runtime.state import VentureState
from app.engine.memory.state_handoff import build_cross_division_manifest
from fastapi import FastAPI


def test_build_cross_division_manifest() -> None:
    """Menguji penyusunan manifest ringkas untuk kolaborasi lintas Divisi A, B, dan C."""
    manifest = build_cross_division_manifest("proj_collab_test")
    assert manifest["manifest_type"] == "CROSS_DIVISION_STRATEGIC_BRIDGE"
    assert "brand_identity" in manifest
    assert "key_api_endpoints" in manifest
    assert "target_audience" in manifest


def test_context_builder_injects_manifest_for_creative_roles() -> None:
    """Memastikan manifest lintas divisi disuntikkan secara otomatis untuk peran Divisi B & C."""
    state = VentureState(
        project_id="proj_ctx_test",
        project_name="Context Test",
        founder_idea="Testing context injection across divisions.",
    )
    # Uji untuk peran COPYWRITER (Divisi C)
    messages = ContextBuilder.assemble_context(
        target_role="COPYWRITER",
        state=state,
        scoped_events=[],
    )
    manifest_msg = [m for m in messages if "[CROSS-DIVISION STRATEGIC MANIFEST]" in m.get("content", "")]
    assert len(manifest_msg) == 1

    # Uji untuk peran BACKEND (Divisi A) -> tidak disuntikkan manifest non-teknis ini
    be_messages = ContextBuilder.assemble_context(
        target_role="BACKEND",
        state=state,
        scoped_events=[],
    )
    be_manifest = [m for m in be_messages if "[CROSS-DIVISION STRATEGIC MANIFEST]" in m.get("content", "")]
    assert len(be_manifest) == 0


def test_artifact_compilers_generate_files(tmp_path: Path) -> None:
    """Menguji kompilasi Slide Deck, E-Book, dan Paket Iklan ke disk."""
    from app.engine import artifact_compiler

    # Redirect direktori proyek ke temporary path
    orig_dir = artifact_compiler.PROJECTS_OUTPUT_DIR
    artifact_compiler.PROJECTS_OUTPUT_DIR = tmp_path

    try:
        p_id = "proj_packager_test"
        # 1. Slide Deck
        slides = [{"title": "Slide 1", "content": "Intro"}, {"title": "Slide 2", "content": "Solution"}]
        deck_path = compile_presentation_deck(p_id, slides, "Deck Title")
        assert Path(deck_path).exists()
        assert "Slide 1" in Path(deck_path).read_text(encoding="utf-8")

        # 2. E-Book
        chapters = [{"title": "Bab 1: Riset", "content": "Isi riset pasar..."}]
        ebook_path = compile_ebook_document(p_id, chapters, "Buku Panduan", "AI Author")
        assert Path(ebook_path).exists()
        assert "Bab 1: Riset" in Path(ebook_path).read_text(encoding="utf-8")

        # 3. Ad Campaign Bundle
        campaign = compile_ad_campaign_bundle(
            p_id,
            storyboard=[{"scene": 1, "visual": "Hero opens app", "audio": "Voiceover"}],
            email_sequences=[{"subject": "Welcome", "body": "Hello founder"}],
            keywords=[{"keyword": "ai startup", "intent": "commercial"}],
        )
        assert Path(campaign["storyboard"]).exists()
        assert Path(campaign["seo_campaign"]).exists()

        # 4. List artifacts
        artifacts = list_project_artifacts(p_id)
        assert len(artifacts) >= 3
        filenames = [a["filename"] for a in artifacts]
        assert "presentation_deck.html" in filenames
        assert "ebook_document.html" in filenames
        assert "seo_ad_campaign.json" in filenames
    finally:
        artifact_compiler.PROJECTS_OUTPUT_DIR = orig_dir


@pytest.mark.asyncio
async def test_project_artifacts_api_and_path_traversal(tmp_path: Path) -> None:
    """Menguji endpoint API artefak dan proteksi keamanan dari serangan path traversal."""
    from app.engine import artifact_compiler
    from app.api.v1 import project_artifacts

    orig_dir = artifact_compiler.PROJECTS_OUTPUT_DIR
    artifact_compiler.PROJECTS_OUTPUT_DIR = tmp_path
    project_artifacts.PROJECTS_OUTPUT_DIR = tmp_path

    try:
        p_id = "proj_api_test"
        compile_presentation_deck(p_id, [{"title": "Deck", "content": "Body"}], "API Deck")

        app = FastAPI()
        app.include_router(artifacts_router)
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Test GET list artifacts
            res_list = await client.get(f"/projects/{p_id}/artifacts")
            assert res_list.status_code == 200
            data = res_list.json()["data"]
            assert len(data) >= 1
            assert data[0]["filename"] == "presentation_deck.html"

            # 2. Test GET valid artifact download
            res_dl = await client.get(f"/projects/{p_id}/artifacts/presentation_deck.html")
            assert res_dl.status_code == 200
            assert "API Deck" in res_dl.text

            # 3. Test Path Traversal Protection
            res_attack = await client.get(f"/projects/{p_id}/artifacts/..%2F..%2Fsecret.txt")
            # Nama disanitasi oleh Path(filename).name menjadi 'secret.txt' yang tidak ada di direktori artefak
            assert res_attack.status_code in (403, 404)
    finally:
        artifact_compiler.PROJECTS_OUTPUT_DIR = orig_dir
        project_artifacts.PROJECTS_OUTPUT_DIR = orig_dir
