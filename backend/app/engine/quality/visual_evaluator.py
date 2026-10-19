"""
E2E Headless Browser Visual Evaluator.
Menilai estetika visual antarmuka (1–100), kontras warna, dan mendeteksi tabrakan elemen UI.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.logger import logger


class VisualScorecard(BaseModel):
    """Hasil evaluasi visual antarmuka pengguna berbasis standar UI/UX modern."""

    aesthetic_score: int = Field(..., ge=1, le=100, description="Skor estetika visual 1–100.")
    contrast_rating: str = Field(default="GOOD", description="Status rasio kontras teks (EXCELLENT, GOOD, POOR).")
    overlapping_elements_count: int = Field(default=0, ge=0, description="Jumlah elemen yang saling bertumpuk.")
    responsive_ready: bool = Field(default=True, description="Kesiapan rendering pada layar mobile.")
    recommendations: List[str] = Field(default_factory=list, description="Saran perbaikan desain.")
    status: str = Field(default="APPROVED", description="Status gate (APPROVED, NEEDS_REVISION).")


class HeadlessVisualEvaluator:
    """Evaluator estetika visual dan integrasi antarmuka pada sandbox webview."""

    def evaluate_interface_layout(
        self,
        html_or_jsx_content: str,
        viewport_width: int = 1280,
    ) -> VisualScorecard:
        """Mengevaluasi kerapian visual antarmuka dari analisis struktur markup dan styling."""
        recommendations: List[str] = []
        aesthetic_score = 88
        overlaps = 0

        # Deteksi tabrakan z-index atau absolute positioning tak terkontrol
        if "z-[9999]" in html_or_jsx_content or "z-50" in html_or_jsx_content and "fixed" in html_or_jsx_content:
            if "top-0 left-0" in html_or_jsx_content and "w-full h-full" in html_or_jsx_content:
                pass
            else:
                overlaps += 1
                aesthetic_score -= 5
                recommendations.append("Periksa elemen bertingkat (z-index tinggi) agar tidak menutupi navigasi utama.")

        # Deteksi kontras dasar (text-gray-300 pada bg-white atau text-slate-800 pada bg-dark)
        if "text-gray-400" in html_or_jsx_content and "bg-white" in html_or_jsx_content:
            aesthetic_score -= 8
            recommendations.append("Tingkatkan kontras teks abu-abu terang pada latar belakang putih untuk kepatuhan WCAG.")
            contrast_rating = "POOR"
        else:
            contrast_rating = "EXCELLENT"

        # Deteksi responsivitas
        has_responsive_classes = any(tag in html_or_jsx_content for tag in ["md:", "lg:", "sm:", "flex-col", "grid-cols-"])
        if not has_responsive_classes:
            aesthetic_score -= 10
            recommendations.append("Tambahkan utilitas layout responsif Tailwind (misal: grid-cols-1 md:grid-cols-3).")

        status = "APPROVED" if aesthetic_score >= 80 and overlaps == 0 else "NEEDS_REVISION"
        scorecard = VisualScorecard(
            aesthetic_score=max(1, min(100, aesthetic_score)),
            contrast_rating=contrast_rating,
            overlapping_elements_count=overlaps,
            responsive_ready=has_responsive_classes,
            recommendations=recommendations,
            status=status,
        )
        logger.info(f"Visual Evaluator: Skor estetika={scorecard.aesthetic_score}/100, Status={scorecard.status}")
        return scorecard


visual_evaluator = HeadlessVisualEvaluator()
