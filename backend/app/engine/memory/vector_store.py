"""
Sovereign Embedded Vector Engine & Semantic Vectorizer (FastEmbed ONNX & Local Fallback).
Menyediakan kalkulasi representasi vektor semantik neural 384-dimensi dan deterministik 128-dimensi
dengan inferensi lokal, offload thread non-blocking, dan pencarian kosinus berlatensi rendah.
"""

import asyncio
import math
import re
import zlib
from typing import Any, Dict, List, Optional, Tuple
from app.core.logger import logger


class DeterministicSemanticVectorizer:
    """Vectorizer semantik deterministik berbasis n-gram hashing & L2-normalization."""

    def __init__(self, dimension: int = 128) -> None:
        self.dimension = dimension

    def tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s-]", " ", text.lower())
        words = [w.strip() for w in cleaned.split() if len(w.strip()) > 1]
        tokens = list(words)
        for i in range(len(words) - 1):
            tokens.append(f"{words[i]}_{words[i+1]}")
        return tokens

    def vectorize(self, text: str) -> List[float]:
        tokens = self.tokenize(text)
        if not tokens:
            return [0.0] * self.dimension

        counts: Dict[int, float] = {}
        for token in tokens:
            bucket = zlib.crc32(token.encode("utf-8")) % self.dimension
            counts[bucket] = counts.get(bucket, 0.0) + 1.0

        vec = [0.0] * self.dimension
        for idx, cnt in counts.items():
            vec[idx] = 1.0 + math.log(cnt)

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0.0:
            vec = [round(x / norm, 5) for x in vec]
        return vec


class FastEmbedSemanticVectorizer:
    """Neural embedding vectorizer lokal berbasis FastEmbed ONNX (BGE-small-en-v1.5)."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        self.model_name = model_name
        self._model: Optional[Any] = None
        self._fallback = DeterministicSemanticVectorizer(dimension=128)

    def _ensure_model(self) -> Optional[Any]:
        if self._model is None:
            try:
                from fastembed import TextEmbedding
                self._model = TextEmbedding(model_name=self.model_name)
                logger.info(f"FastEmbed ONNX model [{self.model_name}] berhasil dimuat.")
            except Exception as err:
                logger.warning(f"Gagal memuat FastEmbed ONNX, fallback aktif: {err}")
                self._model = None
        return self._model

    def vectorize(self, text: str) -> List[float]:
        model = self._ensure_model()
        if model is None:
            return self._fallback.vectorize(text)
        try:
            embeddings = list(model.embed([text]))
            return [round(float(x), 5) for x in embeddings[0]]
        except Exception as err:
            logger.warning(f"FastEmbed inference error: {err}, menggunakan fallback.")
            return self._fallback.vectorize(text)

    async def avectorize(self, text: str) -> List[float]:
        """Eksekusi inferensi embedding non-blocking via worker thread."""
        model = self._ensure_model()
        if model is None:
            return self._fallback.vectorize(text)
        try:
            embeddings = await asyncio.to_thread(lambda: list(model.embed([text])))
            return [round(float(x), 5) for x in embeddings[0]]
        except Exception as err:
            logger.warning(f"Async FastEmbed error: {err}, fallback aktif.")
            return self._fallback.vectorize(text)


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Menghitung skor kesamaan kosinus antara dua vektor float."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    return max(0.0, min(1.0, float(dot)))


class SovereignVectorStore:
    """Penyimpan dan pencari vektor semantik memori korporat terpadu."""

    def __init__(self, vectorizer: Optional[Any] = None) -> None:
        self.vectorizer = vectorizer or FastEmbedSemanticVectorizer()

    def embed_text(self, text: str) -> List[float]:
        return self.vectorizer.vectorize(text)

    async def aembed_text(self, text: str) -> List[float]:
        if hasattr(self.vectorizer, "avectorize"):
            return await self.vectorizer.avectorize(text)
        return await asyncio.to_thread(self.vectorizer.vectorize, text)

    def search_similar(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 3,
        min_similarity: float = 0.20,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Mencari entri paling mirip secara kosinus dengan penanganan disparitas dimensi."""
        if not candidates or not query.strip():
            return []

        query_vec = self.vectorizer.vectorize(query)
        scored: List[Tuple[Dict[str, Any], float]] = []

        for item in candidates:
            item_vec = item.get("embedding")
            if not item_vec or len(item_vec) != len(query_vec):
                content = f"{item.get('title', '')} {item.get('problem_pattern', '')} {' '.join(item.get('tags', []))}"
                item_vec = self.vectorizer.vectorize(content)

            score = cosine_similarity(query_vec, item_vec)
            if score >= min_similarity:
                scored.append((item, round(score, 4)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


vector_store = SovereignVectorStore()
