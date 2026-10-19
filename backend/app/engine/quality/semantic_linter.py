"""Automated Semantic Linter for Non-Software Products.

Menghitung Flesch-Kincaid Readability Index murni Python, memvalidasi struktur
pemasaran AIDA/PAS, dan mendeteksi/membersihkan kata klise AI (AI Cliché Stripper).
"""

import re
from typing import List, Tuple
from pydantic import BaseModel, Field
from app.core.logger import logger

AI_CLICHES = [
    "delve into", "in today's digital era", "testament", "tapestry",
    "game changer", "beacon", "cutting-edge", "unleash", "elevate",
    "seamless", "revolutionize", "pivotal", "embark on",
]


class SemanticLintReport(BaseModel):
    """Hasil evaluasi linter semantik untuk materi non-software."""

    flesch_reading_ease: float = Field(description="Skor keterbacaan (0-100, >60 ideal).")
    flesch_kincaid_grade: float = Field(description="Perkiraan tingkat kelas membaca US.")
    has_aida_structure: bool = Field(description="True jika memenuhi struktur Hook-Agitation-Solution-CTA.")
    cliches_detected: List[str] = Field(default_factory=list, description="Daftar kata klise AI yang ditemukan.")
    is_passed: bool = Field(description="True jika konten lolos batas kelayakan minimum.")
    recommendations: List[str] = Field(default_factory=list, description="Saran perbaikan.")


def count_syllables_word(word: str) -> int:
    """Menghitung perkiraan jumlah suku kata dalam satu kata bahasa Inggris."""
    clean = re.sub(r"[^a-zA-Z]", "", word.lower())
    if not clean or len(clean) <= 2:
        return 1
    # Abaikan silent e di akhir
    if clean.endswith("e") and not clean.endswith("le"):
        clean = clean[:-1]
    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False
    for char in clean:
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    return max(1, count)


def compute_flesch_metrics(text: str) -> Tuple[float, float]:
    """Menghitung Flesch Reading Ease dan Flesch-Kincaid Grade Level."""
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    num_sentences = max(1, len(sentences))

    words = re.findall(r"\b[a-zA-Z0-9_'-]+\b", text)
    num_words = max(1, len(words))

    num_syllables = sum(count_syllables_word(w) for w in words)

    words_per_sent = num_words / num_sentences
    raw_spw = num_syllables / num_words
    # Normalisasi rasio suku kata jika teks multibahasa/Indonesia (suku kata rata-rata > 2.0)
    syllables_per_word = raw_spw if raw_spw <= 2.0 else 1.3 + (raw_spw - 2.0) * 0.35

    ease = 206.835 - (1.015 * words_per_sent) - (84.6 * syllables_per_word)
    grade = (0.39 * words_per_sent) + (11.8 * syllables_per_word) - 15.59

    return round(max(0.0, min(100.0, ease)), 2), round(max(0.0, grade), 2)



def check_aida_structure(text: str) -> bool:
    """Memvalidasi keberadaan struktur Attention/Hook, Problem/Agitation, Solution, dan CTA."""
    lower = text.lower()
    has_cta = bool(re.search(r"\b(click|daftar|hubungi|beli|download|mulai|pelajari|sign up|get started|order)\b", lower))
    has_problem = bool(re.search(r"\b(masalah|tantangan|problem|kendala|kesulitan|sulit|frustrasi|pain point)\b", lower))
    has_solution = bool(re.search(r"\b(solusi|fitur|manfaat|benefit|hadir|memberikan|solves|membantu)\b", lower))
    # AIDA valid jika memiliki setidaknya problem, solution, dan CTA
    return has_problem and has_solution and has_cta


def detect_and_strip_cliches(text: str) -> Tuple[str, List[str]]:
    """Mendeteksi dan membersihkan frasa AI klise dari teks."""
    detected: List[str] = []
    cleaned_text = text
    lower = text.lower()

    for cliché in AI_CLICHES:
        if cliché in lower:
            detected.append(cliché)
            pattern = re.compile(re.escape(cliché), re.IGNORECASE)
            cleaned_text = pattern.sub("", cleaned_text)

    # Rapikan spasi ganda
    cleaned_text = re.sub(r" +", " ", cleaned_text).strip()
    return cleaned_text, detected


def lint_copy_or_educational_content(text: str) -> SemanticLintReport:
    """Menjalankan evaluasi linter semantik lengkap pada naskah konten."""
    ease, grade = compute_flesch_metrics(text)
    has_aida = check_aida_structure(text)
    _, cliches = detect_and_strip_cliches(text)

    recs: List[str] = []
    if ease < 40.0:
        recs.append(f"Keterbacaan rendah ({ease}/100). Persingkat kalimat dan kurangi kata bersuku kata banyak.")
    if not has_aida:
        recs.append("Struktur pemasaran belum lengkap. Pastikan menyertakan Problem, Solution, dan Call To Action (CTA).")
    if cliches:
        recs.append(f"Hindari kata klise AI: {', '.join(cliches)}.")

    is_passed = (ease >= 35.0) and (len(cliches) <= 3)
    logger.info(f"Semantic Linter: Ease={ease}, Grade={grade}, Cliches={len(cliches)}, Passed={is_passed}")

    return SemanticLintReport(
        flesch_reading_ease=ease,
        flesch_kincaid_grade=grade,
        has_aida_structure=has_aida,
        cliches_detected=cliches,
        is_passed=is_passed,
        recommendations=recs,
    )
