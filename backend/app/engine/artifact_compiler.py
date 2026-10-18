"""Multi-Modal Artifact, Media & Ad Packager Engine.

Mengompilasi hasil kerja lintas divisi (Edukasi, Media Kreatif Divisi B, dan Marketing Divisi C)
menjadi berkas produk nyata (Slide Deck HTML, E-Book HTML, Naskah Storyboard, dan Kampanye Iklan).
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.core.logger import logger

PROJECTS_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "projects_output"


def _get_artifacts_dir(project_id: str) -> Path:
    """Mendapatkan dan membuat direktori artefak proyek jika belum ada."""
    art_dir = PROJECTS_OUTPUT_DIR / project_id / "artifacts"
    art_dir.mkdir(parents=True, exist_ok=True)
    return art_dir


def compile_presentation_deck(project_id: str, slides: List[Dict[str, str]], title: str = "Presentation Deck") -> str:
    """Mengompilasi slide presentasi menjadi dek slide HTML interaktif mandiri."""
    art_dir = _get_artifacts_dir(project_id)
    out_file = art_dir / "presentation_deck.html"

    slides_json = json.dumps(slides, indent=2)
    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8"><title>{title}</title>
  <style>
    body {{ margin: 0; background: #090d16; color: #f8fafc; font-family: system-ui, sans-serif; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}
    .header {{ padding: 12px 24px; border-bottom: 1px solid #1e293b; display: flex; justify-content: space-between; align-items: center; background: #0f172a; }}
    .deck {{ flex: 1; display: flex; align-items: center; justify-content: center; padding: 24px; }}
    .slide-card {{ background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 48px; max-width: 800px; width: 100%; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); min-height: 350px; display: flex; flex-direction: column; justify-content: center; }}
    .nav {{ padding: 16px; display: flex; justify-content: center; gap: 16px; background: #0f172a; border-top: 1px solid #1e293b; }}
    button {{ padding: 8px 20px; border-radius: 8px; border: none; background: #3b82f6; color: white; cursor: pointer; font-weight: bold; }}
    button:disabled {{ opacity: 0.4; cursor: not-allowed; }}
  </style>
</head>
<body>
  <div class="header"><h3>{title}</h3><span id="counter">Slide 1 / {max(1, len(slides))}</span></div>
  <div class="deck"><div class="slide-card" id="content"></div></div>
  <div class="nav"><button id="prevBtn" onclick="prevSlide()">← Prev</button><button id="nextBtn" onclick="nextSlide()">Next →</button></div>
  <script>
    const slides = {slides_json};
    let cur = 0;
    function render() {{
      if(!slides.length) return;
      document.getElementById('content').innerHTML = `<h2>${{slides[cur].title || 'Slide'}}</h2><p style="font-size:1.25rem;line-height:1.6;color:#cbd5e1;">${{slides[cur].content || ''}}</p>`;
      document.getElementById('counter').innerText = `Slide ${{cur + 1}} / ${{slides.length}}`;
      document.getElementById('prevBtn').disabled = cur === 0;
      document.getElementById('nextBtn').disabled = cur === slides.length - 1;
    }}
    function nextSlide() {{ if(cur < slides.length - 1) {{ cur++; render(); }} }}
    function prevSlide() {{ if(cur > 0) {{ cur--; render(); }} }}
    render();
  </script>
</body>
</html>"""

    out_file.write_text(html_content, encoding="utf-8")
    logger.info(f"Deck presentasi berhasil dikompilasi ke {out_file.name}")
    return str(out_file)


def compile_ebook_document(project_id: str, chapters: List[Dict[str, str]], title: str = "E-Book", author: str = "Corporate OS") -> str:
    """Mengompilasi draf bab markdown menjadi dokumen e-book HTML terstruktur lengkap."""
    art_dir = _get_artifacts_dir(project_id)
    out_file = art_dir / "ebook_document.html"

    toc_items = "".join([f"<li><a href='#ch_{i}' style='color:#38bdf8;'>{ch.get('title', f'Bab {i+1}')}</a></li>" for i, ch in enumerate(chapters)])
    chapter_blocks = "".join([f"<section id='ch_{i}' style='margin-bottom:48px;border-bottom:1px solid #e2e8f0;padding-bottom:32px;'><h2>{ch.get('title', f'Bab {i+1}')}</h2><div style='line-height:1.8;color:#334155;'>{ch.get('content', '')}</div></section>" for i, ch in enumerate(chapters)])

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8"><title>{title}</title>
  <style>
    body {{ font-family: Georgia, serif; max-width: 800px; margin: 40px auto; padding: 0 24px; color: #1e293b; background: #ffffff; }}
    h1 {{ font-family: system-ui, sans-serif; font-size: 2.5rem; border-bottom: 2px solid #0f172a; padding-bottom: 12px; }}
    .toc {{ background: #f8fafc; padding: 24px; border-radius: 12px; margin: 32px 0; border: 1px solid #e2e8f0; }}
    @media print {{ body {{ max-width: 100%; margin: 0; }} .toc {{ break-after: page; }} }}
  </style>
</head>
<body>
  <h1>{title}</h1><p><strong>Penulis:</strong> {author}</p>
  <div class="toc"><h3>Daftar Isi</h3><ul>{toc_items}</ul></div>
  <main>{chapter_blocks}</main>
</body>
</html>"""

    out_file.write_text(html_content, encoding="utf-8")
    logger.info(f"E-Book berhasil dikompilasi ke {out_file.name}")
    return str(out_file)


def compile_ad_campaign_bundle(
    project_id: str,
    storyboard: List[Dict[str, Any]],
    email_sequences: List[Dict[str, str]],
    keywords: List[Dict[str, Any]],
) -> Dict[str, str]:
    """Mengemas materi iklan video, email marketing funnel, dan metadata SEO kampanye."""
    art_dir = _get_artifacts_dir(project_id)
    files_created = {}

    # 1. Video Storyboard HTML
    sb_file = art_dir / "video_storyboard.html"
    scenes = "".join([f"<div style='background:#1e293b;padding:16px;border-radius:8px;margin-bottom:12px;border:1px solid #334155;'><h4>Scene {s.get('scene', i+1)}: {s.get('visual', '')}</h4><p style='color:#94a3b8;'>Audio: {s.get('audio', '')}</p></div>" for i, s in enumerate(storyboard)])
    sb_file.write_text(f"<!DOCTYPE html><html><body style='background:#0f172a;color:#f8fafc;font-family:sans-serif;padding:24px;'><h2>Video Ad Storyboard</h2>{scenes}</body></html>", encoding="utf-8")
    files_created["storyboard"] = str(sb_file)

    # 2. SEO & Ad Keywords JSON
    seo_file = art_dir / "seo_ad_campaign.json"
    seo_payload = {"campaign": "Cross-Division Launch", "keywords": keywords, "updated_at": datetime.utcnow().isoformat()}
    seo_file.write_text(json.dumps(seo_payload, indent=2), encoding="utf-8")
    files_created["seo_campaign"] = str(seo_file)

    logger.info(f"Bundle materi iklan & kampanye SEO berhasil dikemas untuk [{project_id}]")
    return files_created


def list_project_artifacts(project_id: str) -> List[Dict[str, Any]]:
    """Mendaftar seluruh artefak hasil kompilasi yang siap disajikan."""
    art_dir = _get_artifacts_dir(project_id)
    artifacts = []
    category_map = {".html": "DOCUMENT", ".json": "DATA", ".csv": "SPREADSHEET", ".svg": "MEDIA"}

    for f in art_dir.glob("*"):
        if f.is_file():
            stat = f.stat()
            cat = "SLIDES" if "deck" in f.name else ("EBOOK" if "ebook" in f.name else category_map.get(f.suffix, "OTHER"))
            artifacts.append({
                "filename": f.name,
                "category": cat,
                "size_bytes": stat.st_size,
                "updated_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

    return sorted(artifacts, key=lambda x: x["filename"])
