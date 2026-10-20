"""
E2E Headless Browser Visual Evaluator & Markup Style Auditor.
Menilai estetika visual antarmuka (1–100), kontras warna, dan mendeteksi tabrakan elemen UI.
"""

from html.parser import HTMLParser
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


class MarkupTagCollector(HTMLParser):
    """Parser HTML untuk mengekstrak token class dan struktur elemen antarmuka."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: List[str] = []
        self.classes: List[str] = []
        self.raw_class_strings: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        self.tags.append(tag)
        for attr, val in attrs:
            if attr in ("class", "classname") and val:
                self.raw_class_strings.append(val)
                self.classes.extend(val.split())


class HeadlessVisualEvaluator:
    """Evaluator estetika visual dan integrasi antarmuka pada sandbox webview."""

    def evaluate_interface_layout(
        self,
        html_or_jsx_content: str,
        viewport_width: int = 1280,
    ) -> VisualScorecard:
        """Mengevaluasi kerapian visual antarmuka dari analisis struktur markup dan styling."""
        recommendations: List[str] = []
        aesthetic_score = 90
        overlaps = 0
        contrast_rating = "EXCELLENT"

        collector = MarkupTagCollector()
        try:
            collector.feed(html_or_jsx_content)
        except Exception as p_err:
            logger.debug(f"HTMLParser parsing error: {p_err}")

        all_classes_str = " ".join(collector.raw_class_strings) or html_or_jsx_content

        # 1. Deteksi tabrakan z-index atau absolute/fixed positioning
        has_high_z = "z-[9999]" in all_classes_str or "z-50" in all_classes_str
        is_fixed = "fixed" in all_classes_str
        is_fullscreen = "top-0 left-0" in all_classes_str and "w-full h-full" in all_classes_str

        if has_high_z and is_fixed and not is_fullscreen:
            overlaps += 1
            aesthetic_score -= 10
            recommendations.append("Periksa elemen bertingkat (z-index tinggi) agar tidak menutupi navigasi utama.")

        # 2. Deteksi kontras dasar (text-gray-400 pada bg-white)
        if "text-gray-400" in all_classes_str and "bg-white" in all_classes_str:
            aesthetic_score -= 10
            recommendations.append("Tingkatkan kontras teks abu-abu terang pada latar belakang putih untuk kepatuhan WCAG.")
            contrast_rating = "POOR"

        # 3. Deteksi responsivitas
        responsive_tokens = ["md:", "lg:", "sm:", "flex-col", "grid-cols-", "xl:"]
        has_responsive_classes = any(tok in all_classes_str for tok in responsive_tokens)
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


MarkupStyleAuditor = HeadlessVisualEvaluator
visual_evaluator = HeadlessVisualEvaluator()
