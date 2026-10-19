"""
Unit Tests untuk SQLite Blackboard Memory & 3-Tier Context Projection.
Menguji inisialisasi skema DDL, log event, checkpointing state, dan proyeksi konteks memori.
"""

from pathlib import Path
from typing import Any, Dict
import pytest
import pytest_asyncio

from app.db.init_db import init_database
from app.db.session import get_db_connection
from app.engine.memory.memory import MemoryManager
from app.engine.schemas.schemas import BusinessBriefSchema
from app.engine.runtime.state import VentureState
from app.engine.runtime.state_machine import NativeStateMachine


@pytest_asyncio.fixture
async def temp_db_path(tmp_path: Path) -> str:
    """Fixture untuk database SQLite terisolasi pada temporary directory."""
    db_file = tmp_path / "test_memory.db"
    db_path_str = str(db_file)
    await init_database(db_path_str)
    return db_path_str


@pytest.mark.asyncio
async def test_init_database_creates_tables(temp_db_path: str) -> None:
    """Menguji bahwa init_database berhasil membuat 4 tabel kanonikal."""
    expected_tables = {"projects", "agent_event_logs", "state_checkpoints", "vault_secrets"}
    async with get_db_connection(temp_db_path) as conn:
        cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        rows = await cursor.fetchall()
        table_names = {row["name"] for row in rows}

    assert expected_tables.issubset(table_names)


@pytest.mark.asyncio
async def test_memory_log_and_get_events(temp_db_path: str) -> None:
    """TASK-2.2.4: Menguji method log_event dan get_event_logs pada MemoryManager."""
    mem = MemoryManager(db_path=temp_db_path)
    project_id = "proj_test_log"

    # Catat event pertama
    log_id1 = await mem.log_event(
        project_id=project_id,
        stage="SPARRING_ROOM",
        sender_role="CEO",
        recipient_role="COS",
        event_type="CHAT",
        content="Saya ingin membuat AI workflow generator.",
        token_cost=0.0,
    )
    assert log_id1 > 0

    # Catat event kedua
    log_id2 = await mem.log_event(
        project_id=project_id,
        stage="SPARRING_ROOM",
        sender_role="COS",
        recipient_role="CEO",
        event_type="CRITIQUE",
        content="Model bisnis kredit per-eksekusi memiliki margin 85%.",
        token_cost=0.012,
    )
    assert log_id2 > log_id1

    # Ambil seluruh log
    logs = await mem.get_event_logs(project_id=project_id)
    assert len(logs) == 2
    assert logs[0]["sender_role"] == "CEO"
    assert logs[1]["sender_role"] == "COS"
    assert logs[1]["token_cost"] == 0.012

    # Filter berdasarkan stage
    logs_filtered = await mem.get_event_logs(project_id=project_id, stage="GATE_1_WAITING")
    assert len(logs_filtered) == 0


@pytest.mark.asyncio
async def test_checkpointer_save_and_load(temp_db_path: str) -> None:
    """Menguji mekanisme checkpointing state dan pemulihan snapshot."""
    mem = MemoryManager(db_path=temp_db_path)
    state = VentureState(
        project_id="proj_ckpt_test",
        project_name="Checkpoint Project",
        stage="SPARRING_ROOM",
        founder_idea="SaaS Churn Predictor",
        selected_archetype=4,
    )

    # Simpan checkpoint step 1
    ckpt_id1 = await mem.save_checkpoint(state)
    assert ckpt_id1 > 0

    # Mutasi state dan simpan checkpoint step 2
    state.stage = "GATE_1_WAITING"
    state.add_token_cost("COS", 0.045)
    ckpt_id2 = await mem.save_checkpoint(state)
    assert ckpt_id2 > ckpt_id1

    # Load checkpoint terakhir
    loaded_state = await mem.load_latest_checkpoint("proj_ckpt_test")
    assert loaded_state is not None
    assert loaded_state.project_id == "proj_ckpt_test"
    assert loaded_state.stage == "GATE_1_WAITING"
    assert loaded_state.token_usage.get("COS") == 0.045
    assert loaded_state.selected_archetype == 4


@pytest.mark.asyncio
async def test_context_builder_tier_1_pinned_contracts(temp_db_path: str) -> None:
    """TASK-2.2.5 Tier 1: Menguji injeksi pinned contracts yang sesuai dengan role."""
    mem = MemoryManager(db_path=temp_db_path)
    project_id = "proj_pinned_test"

    brief = BusinessBriefSchema(
        problem_statement="High churn",
        proposed_solution="Predictive model",
        target_audience="B2B SaaS",
        monetization_model="usage_credits",
        pricing_tiers=[{"tier_name": "Pro", "price_monthly": 49.0, "features_included": ["Predict"]}],
        projected_margin_percentage=80.0,
        market_feasibility_score=90,
        risks_and_mitigations=["Risk: Data quality -> Mitigation: Validation"],
    )

    state = VentureState(
        project_id=project_id,
        project_name="DataPulse",
        stage="PRD_AND_SPECS",
        founder_idea="Idea",
        business_brief=brief,
        openapi_spec={"openapi": "3.1.0", "info": {"title": "DataPulse API"}},
    )

    # Role FRONTEND: wajib menerima pinned OpenAPI spec
    fe_context = await mem.build_context_for_agent(project_id, "FRONTEND", state)
    pinned_fe = [m for m in fe_context if "PINNED API CONTRACT" in m["content"]]
    assert len(pinned_fe) == 1
    assert "DataPulse API" in pinned_fe[0]["content"]

    # Role PM: wajib menerima pinned Business Brief
    pm_context = await mem.build_context_for_agent(project_id, "PM", state)
    pinned_pm = [m for m in pm_context if "PINNED BUSINESS BRIEF" in m["content"]]
    assert len(pinned_pm) == 1
    assert "usage_credits" in pinned_pm[0]["content"]


@pytest.mark.asyncio
async def test_context_builder_tier_2_role_isolation(temp_db_path: str) -> None:
    """TASK-2.2.5 Tier 2: Menguji isolasi konteks pesan antar peran agen."""
    mem = MemoryManager(db_path=temp_db_path)
    project_id = "proj_iso_test"

    # Diskusi privat CoS dan CEO
    await mem.log_event(project_id, "SPARRING", "CEO", "COS", "CHAT", "TAM market sebesar $2B.")
    await mem.log_event(project_id, "SPARRING", "COS", "CEO", "CHAT", "Harga tier awal $29.")

    # Instruksi langsung ke Frontend
    await mem.log_event(project_id, "MOCK", "CTO", "FRONTEND", "CHAT", "Gunakan Tailwind CSS.")
    # Pesan dari Frontend sendiri
    await mem.log_event(project_id, "MOCK", "FRONTEND", "CTO", "CHAT", "Komponen dashboard selesai.")
    # Pengumuman BROADCAST
    await mem.log_event(project_id, "MOCK", "CEO", "BROADCAST", "CHAT", "Target demo sore ini.")

    state = VentureState(
        project_id=project_id,
        project_name="Iso Test",
        stage="MOCK_PROTOTYPING",
        founder_idea="Idea",
    )

    # Ambil konteks untuk FRONTEND
    fe_context = await mem.build_context_for_agent(project_id, "FRONTEND", state)
    fe_contents = [m["content"] for m in fe_context]

    # Pastikan pesan privat CoS-CEO TIDAK masuk ke konteks FRONTEND
    assert not any("TAM market" in c for c in fe_contents)
    assert not any("Harga tier awal" in c for c in fe_contents)

    # Pastikan pesan relevan MASUK ke konteks FRONTEND
    assert any("Tailwind CSS" in c for c in fe_contents)
    assert any("Komponen dashboard selesai" in c for c in fe_contents)
    assert any("Target demo sore ini" in c for c in fe_contents)


@pytest.mark.asyncio
async def test_context_builder_tier_3_sliding_window_compaction(temp_db_path: str) -> None:
    """TASK-2.2.5 Tier 3: Menguji sliding window N pesan dan pemadatan pesan lama."""
    mem = MemoryManager(db_path=temp_db_path)
    project_id = "proj_compaction_test"

    # Buat 10 pesan berurutan untuk FRONTEND
    for i in range(10):
        await mem.log_event(
            project_id=project_id,
            stage="MOCK_PROTOTYPING",
            sender_role="CTO",
            recipient_role="FRONTEND",
            event_type="CHAT",
            content=f"Instruksi teknis langkah ke-{i+1}",
        )

    state = VentureState(
        project_id=project_id,
        project_name="Compaction Test",
        stage="MOCK_PROTOTYPING",
        founder_idea="Idea",
    )

    # Bangun konteks dengan sliding window 4 pesan terbaru
    context = await mem.build_context_for_agent(project_id, "FRONTEND", state, limit_recent_messages=4)

    # Cek ada pesan ringkasan Tier 3
    compacted = [m for m in context if "EXECUTIVE STATE SUMMARY" in m["content"]]
    assert len(compacted) == 1
    assert "Compacted 6 Earlier Turns" in compacted[0]["content"]

    # Cek 4 pesan terbaru tetap tampil utuh sebagai pesan terpisah
    recent = [m for m in context if m["role"] == "user" and "Instruksi teknis langkah ke-" in m["content"]]
    assert len(recent) == 4
    assert "langkah ke-7" in recent[0]["content"]
    assert "langkah ke-10" in recent[3]["content"]


@pytest.mark.asyncio
async def test_state_machine_with_memory_checkpointing(temp_db_path: str) -> None:
    """Menguji integrasi NativeStateMachine dengan MemoryManager.save_checkpoint."""
    mem = MemoryManager(db_path=temp_db_path)
    fsm = NativeStateMachine(checkpointer=mem.save_checkpoint)

    async def sparring_node(state: VentureState) -> Dict[str, Any]:
        return {"project_name": "Persisted Venture"}

    fsm.register_node("SPARRING_ROOM", sparring_node)
    fsm.register_router("SPARRING_ROOM", lambda s: "GATE_1_WAITING")

    state = VentureState(
        project_id="proj_fsm_persist",
        project_name="Initial Venture",
        stage="SPARRING_ROOM",
        founder_idea="Idea",
    )

    # Eksekusi step
    state = await fsm.step(state)
    assert state.stage == "GATE_1_WAITING"
    assert state.project_name == "Persisted Venture"

    # Verifikasi langsung dari database SQLite
    restored = await mem.load_latest_checkpoint("proj_fsm_persist")
    assert restored is not None
    assert restored.project_name == "Persisted Venture"
    assert restored.stage == "GATE_1_WAITING"
