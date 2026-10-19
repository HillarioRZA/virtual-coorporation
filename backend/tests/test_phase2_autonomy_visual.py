"""
Unit Test Suite untuk Fase 2 (Autonomous Rollback, Speculative Multi-Branch, dan Visual Evaluator).
"""

from typing import List
from unittest.mock import AsyncMock, patch
import pytest

from app.engine.runtime.autonomous_healer import AutonomousHealer
from app.engine.runtime.speculative_branch import SpeculativeBranchEngine, SpeculativeBranchMetric
from app.engine.quality.visual_evaluator import HeadlessVisualEvaluator


@pytest.mark.asyncio
async def test_autonomous_healer_closed_loop() -> None:
    """Menguji auto-rollback saat terjadi 3 kegagalan berturut-turut."""
    healer = AutonomousHealer(failure_threshold=3)
    project_id = "test_healing_proj"

    # Kegagalan 1 dan 2 belum memicu rollback
    res1 = await healer.record_failure(project_id, "Syntax error in main.py")
    assert res1["triggered"] is False
    assert healer.get_failure_count(project_id) == 1

    res2 = await healer.record_failure(project_id, "AssertionError in test_api.py")
    assert res2["triggered"] is False
    assert healer.get_failure_count(project_id) == 2

    # Simulasi keberadaan snapshot GREEN
    mock_snapshots = [
        {"id": "snap_green_001", "tag": "GREEN", "description": "Working release"},
        {"id": "snap_init_000", "tag": "MANUAL", "description": "Initial scaffold"},
    ]

    with patch("app.sandbox.snapshot_manager.snapshot_manager.list_snapshots", return_value=mock_snapshots), \
         patch("app.sandbox.snapshot_manager.snapshot_manager.rollback_snapshot", new_callable=AsyncMock) as mock_rb:
        mock_rb.return_value = {"status": "success", "restored_snapshot_id": "snap_green_001"}

        res3 = await healer.record_failure(project_id, "FastAPI connection refused")
        assert res3["triggered"] is True
        assert res3["restored_snapshot_id"] == "snap_green_001"
        assert "SIKLUS PERBAIKAN ARSITEKTUR OTONOM" in res3["healing_directive"]
        assert healer.get_failure_count(project_id) == 0


def test_speculative_branch_evaluation() -> None:
    """Menguji pemilihan pemenang pada eksplorasi multi-branch spekulatif."""
    engine = SpeculativeBranchEngine()

    metric_a = SpeculativeBranchMetric(
        branch_id="branch_spec_A",
        approach_name="ORM SQLAlchemy",
        test_pass_rate=1.0,
        coverage_rate=0.90,
        ast_complexity=8,
        latency_ms=45.0,
    )
    metric_b = SpeculativeBranchMetric(
        branch_id="branch_spec_B",
        approach_name="Raw aiosqlite",
        test_pass_rate=0.75,
        coverage_rate=0.60,
        ast_complexity=15,
        latency_ms=120.0,
    )

    score_a = engine.calculate_fitness_score(metric_a)
    score_b = engine.calculate_fitness_score(metric_b)
    assert score_a > score_b

    eval_result = engine.evaluate_candidates([metric_a, metric_b])
    assert eval_result["winner_branch_id"] == "branch_spec_A"
    assert eval_result["winner_approach"] == "ORM SQLAlchemy"
    assert "branch_spec_B" in eval_result["discarded_branches"]


def test_visual_evaluator_layout_scoring() -> None:
    """Menguji evaluasi visual antarmuka dan skor estetika WCAG."""
    evaluator = HeadlessVisualEvaluator()

    clean_ui = """
    <div className="flex flex-col md:grid md:grid-cols-3 gap-6 p-8 bg-slate-900 text-white">
        <header className="col-span-3 text-2xl font-bold">Venture Launchpad</header>
        <div className="p-4 bg-slate-800 rounded-xl shadow-lg">Feature A</div>
    </div>
    """
    card = evaluator.evaluate_interface_layout(clean_ui)
    assert card.status == "APPROVED"
    assert card.aesthetic_score >= 80
    assert card.responsive_ready is True
    assert card.overlapping_elements_count == 0

    poor_ui = """
    <div className="bg-white text-gray-400 z-50 fixed p-2">
        <button>Click Me</button>
    </div>
    """
    poor_card = evaluator.evaluate_interface_layout(poor_ui)
    assert poor_card.contrast_rating == "POOR"
    assert len(poor_card.recommendations) > 0
