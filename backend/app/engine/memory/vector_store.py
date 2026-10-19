"""
Sovereign Embedded Vector Engine & Deterministic Semantic Vectorizer.
Menyediakan kalkulasi representasi vektor semantik 100% lokal dan pencarian kosinus berlatensi rendah.
"""

import math
import re
import zlib
from typing import Any, Dict, List, Optional, Tuple


class DeterministicSemanticVectorizer:
    """Vectorizer semantik deterministik 128-dimensi berbasis n-gram hashing & L2-normalization."""

    def __init__(self, dimension: int = 128) -> None:
        """Inisialisasi vectorizer dengan dimensi vektor tetap (default 128)."""
        self.dimension = dimension

    def tokenize(self, text: str) -> List[str]:
        """Membersihkan dan memecah teks menjadi token kata dan bigram."""
        cleaned = re.sub(r"[^\w\s-]", " ", text.lower())
        words = [w.strip() for w in cleaned.split() if len(w.strip()) > 1]
        tokens = list(words)
        # Tambahkan bigram kata untuk menangkap frasa kontekstual
        for i in range(len(words) - 1):
            tokens.append(f"{words[i]}_{words[i+1]}")
        return tokens

    def vectorize(self, text: str) -> List[float]:
        """Menghasilkan vektor float 128-dimensi yang telah dinormalisasi L2."""
        tokens = self.tokenize(text)
        if not tokens:
            return [0.0] * self.dimension

        counts: Dict[int, float] = {}
        for token in tokens:
            # Gunakan CRC32 deterministik lintas platform OS
            bucket = zlib.crc32(token.encode("utf-8")) % self.dimension
            counts[bucket] = counts.get(bucket, 0.0) + 1.0

        vec = [0.0] * self.dimension
        for idx, cnt in counts.items():
            vec[idx] = 1.0 + math.log(cnt)

        # L2-normalization (unit vector)
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0.0:
            vec = [round(x / norm, 5) for x in vec]
        return vec


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Menghitung cosine similarity antara dua vektor float."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    return max(0.0, min(1.0, float(dot)))


class SovereignVectorStore:
    """Mesin indeks vektor in-memory terpadu untuk Corporate Wisdom Base."""

    def __init__(self, vectorizer: Optional[DeterministicSemanticVectorizer] = None) -> None:
        """Inisialisasi SovereignVectorStore."""
        self.vectorizer = vectorizer or DeterministicSemanticVectorizer()

    def embed_text(self, text: str) -> List[float]:
        """Membentuk embedding teks."""
        return self.vectorizer.vectorize(text)

    def search_similar(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 3,
        min_similarity: float = 0.20,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Mencari kandidat paling mirip secara semantik berdasarkan cosine similarity.

        Args:
            query: Teks pencarian pengguna atau konteks tugas agen.
            candidates: Daftar entri wisdom dengan kolom 'embedding'.
            top_k: Jumlah hasil maksimal yang dikembalikan.
            min_similarity: Ambang batas minimum skor kesamaan kosinus.

        Returns:
            List tuple (item wisdom, skor similarity) terurut dari tertinggi.
        """
        if not candidates or not query.strip():
            return []

        query_vec = self.vectorizer.vectorize(query)
        scored: List[Tuple[Dict[str, Any], float]] = []

        for item in candidates:
            item_vec = item.get("embedding")
            if not item_vec:
                # Fallback: bangun vektor secara on-the-fly jika belum ada
                content = f"{item.get('title', '')} {item.get('problem_pattern', '')} {' '.join(item.get('tags', []))}"
                item_vec = self.vectorizer.vectorize(content)

            score = cosine_similarity(query_vec, item_vec)
            if score >= min_similarity:
                scored.append((item, round(score, 4)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


vector_store = SovereignVectorStore()
