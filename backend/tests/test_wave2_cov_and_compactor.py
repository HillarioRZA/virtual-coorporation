"""
Unit & Integration Tests untuk Gelombang 2 (Fase 3 & 6):
Two-Tier CoV Gatekeeper, Worker Repair Loop, dan Hermes Context Compactor.
"""

import pytest
from app.engine.sentinel.verifier import cov_gatekeeper
from app.engine.memory.context_compactor import context_compactor, ContextCompactor


@pytest.mark.asyncio
async def test_two_tier_cov_tier1_read_only_fast_pass(tmp_path):
    """Menguji Tier 1 CoV: Tool read-only valid disetujui instan (0 tokens, 0ms)."""
    db_file = tmp_path / "test_cov_w2.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"

    candidate = """Memeriksa skema tabel.
```json
{
  "tool": "inspect_db_schema",
  "parameters": {
    "table_name": "projects"
  }
}
```"""
    res = await cov_gatekeeper.inspect(
        project_id="proj_w2",
        agent_role="CTO",
        candidate_content=candidate,
        stage="architecture",
        custom_path=db_url,
    )
    assert res.approved is True
    assert res.status == "APPROVED"
    assert res.tool_call["tool"] == "inspect_db_schema"
    assert res.tool_call["parameters"]["table_name"] == "projects"


@pytest.mark.asyncio
async def test_two_tier_cov_tier1_parameter_defect_reject(tmp_path):
    """Menguji Tier 1 CoV: Tool read-only dengan parameter cacat ditolak dan minta reparasi."""
    db_file = tmp_path / "test_cov_w2_defect.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"

    # search_codebase memerlukan parameter 'query' non-kosong
    candidate = """Mencari kode.
```json
{
  "tool": "search_codebase",
  "parameters": {}
}
```"""
    res = await cov_gatekeeper.inspect(
        project_id="proj_w2",
        agent_role="BACKEND",
        candidate_content=candidate,
        stage="development",
        custom_path=db_url,
    )
    # Status bug sudah diperbaiki: REPAIR_REQUIRED sekarang wajib approved=False!
    assert res.approved is False
    assert res.status == "REPAIR_REQUIRED"
    assert res.tool_call is None
    assert "query" in res.repair_feedback


@pytest.mark.asyncio
async def test_two_tier_cov_tier2_mutating_tool_schema_guard(tmp_path):
    """Menguji Tier 2 CoV: Tool mutatif dengan parameter kurang ditolak sebelum LLM critic."""
    db_file = tmp_path / "test_cov_w2_mutating.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"

    # write_code_bundle memerlukan 'bundle_type' dan 'code_map'
    candidate = """Menulis kode bundle.
```json
{
  "tool": "write_code_bundle",
  "parameters": {
    "bundle_type": "backend"
  }
}
```"""
    res = await cov_gatekeeper.inspect(
        project_id="proj_w2",
        agent_role="BACKEND",
        candidate_content=candidate,
        stage="development",
        custom_path=db_url,
    )
    assert res.approved is False
    assert res.status == "REPAIR_REQUIRED"
    assert "code_map" in res.repair_feedback


def test_context_compactor_pruning():
    """Menguji pemangkasan tool output masif dengan retensi head dan tail."""
    compactor = ContextCompactor(max_tool_chars=500)
    huge_text = "HEAD_START_" + ("X" * 1000) + "_TAIL_END"

    pruned = compactor.prune_tool_output(huge_text)
    assert len(pruned) < len(huge_text)
    assert "HEAD_START_" in pruned
    assert "_TAIL_END" in pruned
    assert "DIPANGKAS" in pruned


def test_context_compactor_tail_retention():
    """Menguji bahwa compact_context menjaga N percakapan terakhir utuh."""
    compactor = ContextCompactor(tail_count=3)
    events = [
        {"sender_role": "USER", "event_type": "CHAT", "content": f"Turn {i}"}
        for i in range(10)
    ]
    compacted = compactor.compact_context(events)

    # Harus ada 1 summary item + 3 tail items
    assert len(compacted) == 4
    assert compacted[0]["event_type"] == "CONTEXT_COMPACTED_SUMMARY"
    assert compacted[1]["content"] == "Turn 7"
    assert compacted[2]["content"] == "Turn 8"
    assert compacted[3]["content"] == "Turn 9"
