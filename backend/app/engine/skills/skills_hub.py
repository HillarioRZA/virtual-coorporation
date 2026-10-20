"""
Skills Hub Subsystem - Pengelola Bundle Folder Skills & Kategorisasi Dinamis.
Menyediakan penyimpanan playbook terisolasi, auto-create kategori, dan pencarian teks penuh (FTS5).
"""

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Union
import uuid

import httpx
from app.core.config import BASE_DIR
from app.core.logger import logger
from app.db.session import get_db_connection

SKILLS_ROOT = (BASE_DIR.parent / "skills").resolve()


class SkillsHub:
    """Manajer katalog skills publik mandiri tanpa ketergantungan model RAG/ONNX."""

    def __init__(self, root_dir: Optional[Path] = None) -> None:
        """Inisialisasi direktori penyimpanan root skills."""
        self.root_dir = root_dir or SKILLS_ROOT
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_slug(self, text: str) -> str:
        """Menghasilkan slug bersih hanya alfanumerik, dash, dan underscore."""
        slug = re.sub(r"[^a-z0-9_-]", "", text.strip().lower().replace(" ", "-"))
        return slug or "general"

    async def _resolve_or_create_category(
        self, category_name: str, custom_db_path: Optional[str] = None
    ) -> Dict[str, str]:
        """Memeriksa kategori di SQLite; jika belum ada, otomatis membuat kategori baru."""
        slug = self._sanitize_slug(category_name)
        async with get_db_connection(custom_db_path) as conn:
            async with conn.execute(
                "SELECT id, name, slug FROM corporate_skill_categories WHERE slug = ?;", (slug,)
            ) as cur:
                row = await cur.fetchone()
                if row:
                    return {"id": row["id"], "name": row["name"], "slug": row["slug"]}

            cat_id = f"cat_{slug}_{uuid.uuid4().hex[:4]}"
            formatted_name = category_name.strip().title()
            await conn.execute(
                "INSERT INTO corporate_skill_categories (id, name, slug, description) VALUES (?, ?, ?, ?);",
                (cat_id, formatted_name, slug, f"Kategori dinamis untuk {formatted_name}"),
            )
            await conn.commit()
            logger.info(f"Kategori skill baru dibuat secara otomatis: [{formatted_name}] ({slug}).")
            return {"id": cat_id, "name": formatted_name, "slug": slug}

    async def install_skill_bundle(
        self,
        name: str,
        category_name: str,
        files: Dict[str, Union[str, bytes]],
        description: Optional[str] = None,
        custom_db_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Menginstal bundle skill ke disk dengan validasi path traversal dan mendaftarkannya ke FTS5."""
        cat_info = await self._resolve_or_create_category(category_name, custom_db_path)
        skill_slug = self._sanitize_slug(name)

        dest_dir = (self.root_dir / cat_info["slug"] / skill_slug).resolve()
        if not dest_dir.is_relative_to(self.root_dir):
            raise ValueError("Upaya Path Traversal terdeteksi! Instalasi dibatalkan.")

        dest_dir.mkdir(parents=True, exist_ok=True)
        skill_md_content = ""

        # Tulis seluruh berkas bundle secara aman
        for rel_path, content in files.items():
            clean_rel = Path(rel_path).name if ".." in rel_path else rel_path.lstrip("/\\")
            target_file = (dest_dir / clean_rel).resolve()
            if not target_file.is_relative_to(dest_dir):
                continue
            target_file.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                target_file.write_bytes(content)
            else:
                target_file.write_text(content, encoding="utf-8")
                if clean_rel == "SKILL.md":
                    skill_md_content = content

        desc = description or (skill_md_content.splitlines()[0][:120] if skill_md_content else name)
        skill_id = f"skill_{uuid.uuid4().hex[:8]}"

        async with get_db_connection(custom_db_path) as conn:
            await conn.execute(
                """
                INSERT OR REPLACE INTO corporate_skills
                (id, name, category_id, description, folder_path, manifest_json)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (skill_id, name, cat_info["id"], desc, str(dest_dir), json.dumps({"files": list(files.keys())})),
            )
            # Indeks FTS5 teks penuh
            await conn.execute(
                "INSERT INTO corporate_skills_fts (skill_id, name, description, content) VALUES (?, ?, ?, ?);",
                (skill_id, name, desc, skill_md_content[:4000]),
            )
            await conn.commit()

        logger.info(f"Skill [{name}] berhasil diinstal pada kategori [{cat_info['name']}].")
        return {"id": skill_id, "name": name, "category": cat_info["name"], "folder_path": str(dest_dir)}

    async def search_skills(
        self,
        query: str,
        category_slug: Optional[str] = None,
        top_k: int = 10,
        custom_db_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mencari skills secara cepat menggunakan pencarian teks penuh FTS5 dan filter kategori."""
        sql = """
            SELECT s.id, s.name, s.description, s.folder_path, c.name as category_name, c.slug as category_slug
            FROM corporate_skills s
            JOIN corporate_skill_categories c ON s.category_id = c.id
            JOIN corporate_skills_fts fts ON fts.skill_id = s.id
            WHERE corporate_skills_fts MATCH ?
        """
        params: List[Any] = [f"{query}*"]
        if category_slug:
            sql += " AND c.slug = ?"
            params.append(category_slug)
        sql += " LIMIT ?;"
        params.append(top_k)

        results = []
        try:
            async with get_db_connection(custom_db_path) as conn:
                async with conn.execute(sql, tuple(params)) as cur:
                    rows = await cur.fetchall()
                    results = [dict(r) for r in rows]
        except Exception as err:
            logger.warning(f"Pencarian FTS5 skills gagal, fallback ke LIKE: {err}")
            fallback_sql = """
                SELECT s.id, s.name, s.description, s.folder_path, c.name as category_name, c.slug as category_slug
                FROM corporate_skills s
                JOIN corporate_skill_categories c ON s.category_id = c.id
                WHERE s.name LIKE ? OR s.description LIKE ?
            """
            async with get_db_connection(custom_db_path) as conn:
                async with conn.execute(fallback_sql, (f"%{query}%", f"%{query}%")) as cur:
                    results = [dict(r) for r in await cur.fetchall()]
        return results

    async def list_categories(self, custom_db_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mendapatkan seluruh kategori skills yang tersedia di sistem."""
        async with get_db_connection(custom_db_path) as conn:
            async with conn.execute("SELECT * FROM corporate_skill_categories ORDER BY name ASC;") as cur:
                return [dict(r) for r in await cur.fetchall()]


skills_hub = SkillsHub()
