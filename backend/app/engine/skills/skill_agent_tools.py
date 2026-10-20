"""
Perkakas Interaktif Agen untuk Mengakses Perpustakaan Skills Perusahaan.
Memungkinkan agen mencari playbook dan membaca pedoman teknis domain secara mandiri.
"""

from pathlib import Path
from typing import Any, Dict
from app.engine.skills.skills_hub import skills_hub


async def tool_consult_skill_library(project_id: str, **parameters: Any) -> Dict[str, Any]:
    """Mencari playbook teknis di perpustakaan skills berdasarkan topik dan kategori."""
    query = parameters.get("topic") or parameters.get("query") or ""
    category = parameters.get("category")
    custom_path = parameters.get("custom_path")
    if not query.strip():
        cats = await skills_hub.list_categories(custom_db_path=custom_path)
        return {"status": "SUCCESS", "message": "Daftar kategori tersedia", "categories": cats}

    results = await skills_hub.search_skills(query=query.strip(), category_slug=category, custom_db_path=custom_path)
    return {
        "status": "SUCCESS",
        "query": query,
        "category": category,
        "count": len(results),
        "skills": results,
    }


async def tool_read_skill_detail(project_id: str, **parameters: Any) -> Dict[str, Any]:
    """Membaca isi lengkap SKILL.md atau berkas pendukung pada suatu skill."""
    skill_name = parameters.get("skill_name") or parameters.get("name")
    if not skill_name:
        return {"error": "Parameter 'skill_name' wajib diisi."}

    rel_file = parameters.get("file_path", "SKILL.md")
    custom_path = parameters.get("custom_path")
    search_res = await skills_hub.search_skills(query=skill_name, top_k=1, custom_db_path=custom_path)
    if not search_res:
        return {"error": f"Skill [{skill_name}] tidak ditemukan di perpustakaan."}

    folder = Path(search_res[0]["folder_path"])
    target_file = (folder / rel_file).resolve()
    if not target_file.is_relative_to(folder) or not target_file.exists():
        return {"error": f"Berkas [{rel_file}] tidak ditemukan pada skill [{skill_name}]."}

    try:
        content = target_file.read_text(encoding="utf-8")
        return {
            "status": "SUCCESS",
            "skill": skill_name,
            "file": rel_file,
            "content": content,
        }
    except Exception as err:
        return {"error": f"Gagal membaca berkas: {err}"}
