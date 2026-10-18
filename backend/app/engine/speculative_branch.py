"""
Speculative Multi-Branch Exploration Engine (A* Pathfinding Arsitektur).
Mengeksekusi cabang spekulatif paralel untuk tiket CRITICAL dan memilih pemenang via evaluasi LCA.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.engine.branch_merge import ThreeWayBranchMergeEngine


class SpeculativeBranchMetric(BaseModel):
    """Metrik performa dan kualitas kode untuk satu branch spekulatif."""

    branch_id: str
    approach_name: str
    test_pass_rate: float = Field(..., ge=0.0, le=1.0)
    coverage_rate: float = Field(..., ge=0.0, le=1.0)
    ast_complexity: int = Field(default=10, ge=1)
    latency_ms: float = Field(default=50.0, ge=0.0)


class SpeculativeBranchEngine:
    """Orkestrator eksplorasi branch paralel untuk mitigasi risiko arsitektur buntu."""

    def __init__(self, merge_engine: Optional[ThreeWayBranchMergeEngine] = None) -> None:
        """Inisialisasi SpeculativeBranchEngine."""
        self.merge_engine = merge_engine or ThreeWayBranchMergeEngine()

    def calculate_fitness_score(self, metric: SpeculativeBranchMetric) -> float:
        """Menghitung skor kelayakan objektif branch spekulatif.

        Formula A*:
            Score = (PassRate * 50) + (Coverage * 30) - (Complexity * 0.5) - (LatencyMs * 0.01)
        """
        score = (
            (metric.test_pass_rate * 50.0)
            + (metric.coverage_rate * 30.0)
            - (metric.ast_complexity * 0.5)
            - (metric.latency_ms * 0.01)
        )
        return round(score, 2)

    def evaluate_candidates(
        self,
        metrics: List[SpeculativeBranchMetric],
    ) -> Dict[str, Any]:
        """Mengevaluasi seluruh metrik branch spekulatif dan menentukan branch pemenang."""
        if not metrics:
            return {"error": "Tidak ada kandidat branch spekulatif."}

        scored: List[Dict[str, Any]] = []
        for m in metrics:
            score = self.calculate_fitness_score(m)
            scored.append({
                "branch_id": m.branch_id,
                "approach": m.approach_name,
                "score": score,
                "pass_rate": m.test_pass_rate,
                "coverage": m.coverage_rate,
                "complexity": m.ast_complexity,
                "latency_ms": m.latency_ms,
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        winner = scored[0]
        losers = scored[1:]

        logger.info(f"Speculative Evaluation: Pemenang [{winner['branch_id']}] (Skor: {winner['score']}) vs {len(losers)} kandidat kalah.")
        return {
            "winner_branch_id": winner["branch_id"],
            "winner_approach": winner["approach"],
            "winning_score": winner["score"],
            "leaderboard": scored,
            "discarded_branches": [l["branch_id"] for l in losers],
        }

    async def execute_lca_merge_decision(
        self,
        winner_branch_id: str,
        target_branch_id: str = "branch_main",
        custom_db_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Menentukan LCA dan memverifikasi kesiapan merge branch pemenang ke target branch."""
        try:
            lca_id = await self.merge_engine.find_lca(winner_branch_id, target_branch_id, custom_db_path)
            preview = await self.merge_engine.preview_merge(winner_branch_id, target_branch_id, custom_path=custom_db_path)
            return {
                "success": True,
                "winner_branch_id": winner_branch_id,
                "target_branch_id": target_branch_id,
                "lca_branch_id": lca_id,
                "merge_preview": preview,
            }
        except Exception as err:
            logger.error(f"Gagal evaluasi LCA merge untuk [{winner_branch_id}]: {err}")
            return {"success": False, "error": str(err)}


speculative_branch_engine = SpeculativeBranchEngine()
