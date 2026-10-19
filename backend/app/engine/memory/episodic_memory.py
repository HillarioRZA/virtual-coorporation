"""
Cross-Venture Episodic Memory & Reflexion Store.
Mengumpulkan kartu pengalaman institusional dan menginjeksi preseden teknis antar-venture.
"""

from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.core.logger import logger
from app.engine.memory.vector_store import SovereignVectorStore, vector_store


class ReflectiveExperienceCard(BaseModel):
    """Representasi atomik kartu pengalaman pemecahan masalah lintas-venture."""

    card_id: str = Field(default_factory=lambda: f"exp_{uuid.uuid4().hex[:8]}")
    title: str = Field(..., min_length=5)
    problem_pattern: str = Field(..., min_length=10)
    root_cause: str = Field(..., min_length=5)
    proven_solution: str = Field(..., min_length=10)
    tags: List[str] = Field(default_factory=list)
    source_venture: str = Field(default="global")
    embedding: Optional[List[float]] = None


class CrossVentureEpisodicMemory:
    """Penyimpanan memori episodik semantik lintas venture untuk akumulasi kecerdasan sistem."""

    def __init__(self, store: Optional[SovereignVectorStore] = None) -> None:
        """Inisialisasi CrossVentureEpisodicMemory."""
        self.store = store or vector_store
        self._cards: List[ReflectiveExperienceCard] = []

    def record_experience(
        self,
        title: str,
        problem_pattern: str,
        root_cause: str,
        proven_solution: str,
        tags: Optional[List[str]] = None,
        source_venture: str = "global",
    ) -> ReflectiveExperienceCard:
        """Mencatat dan membuat embedding kartu pengalaman baru."""
        combined_text = f"{title} {problem_pattern} {root_cause} {proven_solution} {' '.join(tags or [])}"
        vec = self.store.embed_text(combined_text)

        card = ReflectiveExperienceCard(
            title=title,
            problem_pattern=problem_pattern,
            root_cause=root_cause,
            proven_solution=proven_solution,
            tags=tags or [],
            source_venture=source_venture,
            embedding=vec,
        )
        self._cards.append(card)
        logger.info(f"EpisodicMemory: Kartu pengalaman baru dicatat [{card.card_id}]: {card.title}")
        return card

    def retrieve_relevant_experiences(
        self,
        query: str,
        top_k: int = 2,
        min_similarity: float = 0.20,
    ) -> List[Dict[str, Any]]:
        """Mencari kartu pengalaman relevan berdasarkan kesamaan semantik kosinus."""
        if not self._cards or not query.strip():
            return []

        candidates = [c.model_dump() for c in self._cards]
        results = self.store.search_similar(query, candidates, top_k=top_k, min_similarity=min_similarity)
        return [{"card": r[0], "similarity": r[1]} for r in results]

    def format_prompt_injection(self, query: str, top_k: int = 2) -> Optional[str]:
        """Menghasilkan teks injeksi prompt bimbingan dari pengalaman masa lalu."""
        matched = self.retrieve_relevant_experiences(query, top_k=top_k)
        if not matched:
            return None

        lines = ["[CROSS-VENTURE HISTORICAL LESSONS & PROVEN FIXES]:"]
        for item in matched:
            card = item["card"]
            sim = item["similarity"]
            lines.append(
                f"- [From: {card.get('source_venture', 'global')} | Sim: {sim:.2f}] \"{card.get('title')}\"\n"
                f"  Problem: {card.get('problem_pattern')}\n"
                f"  Root Cause: {card.get('root_cause')}\n"
                f"  Solution Patch: {card.get('proven_solution')}"
            )
        return "\n".join(lines)


episodic_memory = CrossVentureEpisodicMemory()
