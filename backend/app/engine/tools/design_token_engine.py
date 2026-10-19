"""Asset & Design Token Synthesis Engine.

Menghasilkan skema token desain terstruktur (design_tokens.json) yang berisi
palet warna HEX, pasangan tipografi Google Fonts, dan template prompt visual seragam.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from app.core.logger import logger

PROJECTS_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "projects_output"

ARCHETYPE_PALETTES: Dict[int, Dict[str, str]] = {
    1: {"primary": "#3b82f6", "accent": "#06b6d4", "bg": "#0f172a", "surface": "#1e293b", "text": "#f8fafc"},
    2: {"primary": "#8b5cf6", "accent": "#ec4899", "bg": "#09090b", "surface": "#18181b", "text": "#fafafa"},
    3: {"primary": "#10b981", "accent": "#f59e0b", "bg": "#022c22", "surface": "#064e3b", "text": "#ecfdf5"},
    4: {"primary": "#f43f5e", "accent": "#fb923c", "bg": "#18181b", "surface": "#27272a", "text": "#fff1f2"},
}


def generate_design_tokens(
    project_id: str,
    archetype_id: int = 1,
    brand_name: str = "",
    custom_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Menyintesis file konfigurasi design_tokens.json terpadu untuk venture startup."""
    palette = ARCHETYPE_PALETTES.get(archetype_id, ARCHETYPE_PALETTES[1])
    tokens = {
        "project_id": project_id,
        "brand_name": brand_name or f"Venture {project_id}",
        "archetype_id": archetype_id,
        "colors": {
            "primary": palette["primary"],
            "accent": palette["accent"],
            "background": palette["bg"],
            "surface": palette["surface"],
            "text_primary": palette["text"],
            "text_muted": "#94a3b8",
        },
        "typography": {
            "heading": "Plus Jakarta Sans, sans-serif",
            "body": "Inter, sans-serif",
            "mono": "JetBrains Mono, monospace",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Plus+Jakarta+Sans:wght@600;800&display=swap",
        },
        "visual_prompts": {
            "ebook_cover": f"Minimalist professional e-book cover for {brand_name}, modern flat style, {palette['primary']} gradient, sleek typography.",
            "presentation_slide": f"Clean dark mode presentation backdrop, subtle geometric accents in {palette['accent']}, executive tech aesthetic.",
            "social_banner": f"High conversion banner for {brand_name}, hero hook with contrasting {palette['primary']} button.",
            "poster_layout": f"Minimalist Swiss-style poster layout, bold typography, {palette['bg']} background with {palette['accent']} focal point.",
        },
    }

    target_dir = custom_dir or (PROJECTS_OUTPUT_DIR / project_id)
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        token_file = target_dir / "design_tokens.json"
        token_file.write_text(json.dumps(tokens, indent=2), encoding="utf-8")
        logger.info(f"Design tokens berhasil disintesis dan disimpan di {token_file}")
    except OSError as err:
        logger.error(f"Gagal menyimpan design_tokens.json: {err}")

    return tokens


def load_design_tokens(project_id: str, custom_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Membaca file design_tokens.json yang sudah tersimpan."""
    target_dir = custom_dir or (PROJECTS_OUTPUT_DIR / project_id)
    token_file = target_dir / "design_tokens.json"
    if not token_file.exists():
        return None
    try:
        return json.loads(token_file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        logger.warning(f"Gagal memuat design_tokens.json: {err}")
        return None
