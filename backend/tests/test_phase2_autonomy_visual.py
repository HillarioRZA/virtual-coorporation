"""
Unit Test Suite untuk Fase 2 (Autonomous Rollback, Speculative Multi-Branch, dan Visual Evaluator).
"""

from typing import List
from unittest.mock import AsyncMock, patch
import pytest

from app.engine.runtime.autonomous_healer import AutonomousHealer
from app.engine.quality.visual_evaluator import HeadlessVisualEvaluator


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
