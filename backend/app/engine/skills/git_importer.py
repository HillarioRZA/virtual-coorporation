"""
Git & Remote Repository Importer Subsystem untuk Skills Hub.
Mengkloning repositori playbook eksternal, mengekstrak berkas, dan mendaftarkannya ke FTS5.
"""

import asyncio
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any, Dict, Optional, Union
import httpx
from app.core.logger import logger
from app.engine.skills.skills_hub import skills_hub

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
IGNORED_PATTERNS = {".git", "__pycache__", ".DS_Store", "node_modules"}


def parse_skill_metadata(skill_md_content: str, default_name: str) -> Dict[str, str]:
    """Mengekstrak judul, deskripsi, dan kategori dari konten SKILL.md markdown."""
    name = ""
    category = "General Playbooks"
    description = ""

    lines = skill_md_content.splitlines()
    for line in lines:
        stripped = line.strip()
        lowered = stripped.lower()
        if stripped.startswith("# ") and not name:
            name = stripped[2:].strip().lower().replace(" ", "-")
        elif lowered.startswith("kategori:") or lowered.startswith("category:"):
            category = stripped.split(":", 1)[1].strip().title()
        elif lowered.startswith("description:") or lowered.startswith("deskripsi:"):
            description = stripped.split(":", 1)[1].strip()

    final_name = re.sub(r"[^a-z0-9_-]", "", name.lower()) if name else default_name
    if not description and lines:
        for line in lines:
            if line.strip() and not line.startswith("#"):
                description = line.strip()[:160]
                break

    return {
        "name": final_name or default_name,
        "category": category,
        "description": description or f"Playbook bundle diimpor dari {default_name}",
    }


async def clone_or_download_repo(repo_url: str, dest_dir: Path) -> bool:
    """Mengkloning repositori Git secara dangkal (depth 1) atau fallback ke zipball."""
    clean_url = repo_url.strip().rstrip("/")
    try:
        proc = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth", "1", clean_url, str(dest_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode == 0:
            return True
        logger.warning(f"Git clone gagal ({clean_url}): {stderr.decode(errors='ignore')}")
    except Exception as err:
        logger.warning(f"Gagal memanggil git CLI untuk [{clean_url}]: {err}")

    # Fallback jika GitHub: Unduh zip archive
    gh_match = re.search(r"github\.com/([^/]+)/([^/]+)", clean_url)
    if gh_match:
        owner, repo = gh_match.group(1), gh_match.group(2).replace(".git", "")
        zip_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/main"
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                res = await client.get(zip_url)
                if res.status_code == 200:
                    import zipfile
                    import io
                    with zipfile.ZipFile(io.BytesIO(res.content)) as zf:
                        zf.extractall(dest_dir)
                    return True
        except Exception as zip_err:
            logger.error(f"Fallback unduhan zipball GitHub gagal: {zip_err}")
    return False


def collect_repo_files(source_dir: Path) -> Dict[str, Union[str, bytes]]:
    """Memindai direktori hasil kloning dan mengumpulkan berkas dalam batas ukuran."""
    files: Dict[str, Union[str, bytes]] = {}
    base_path = source_dir

    # Tangani folder bersarang dari ekstraksi zipball
    subdirs = [p for p in source_dir.iterdir() if p.is_dir() and p.name not in IGNORED_PATTERNS]
    if len(subdirs) == 1 and not (source_dir / "SKILL.md").exists():
        base_path = subdirs[0]

    for item in base_path.rglob("*"):
        if not item.is_file():
            continue
        if any(ign in item.parts for ign in IGNORED_PATTERNS):
            continue
        try:
            if item.stat().st_size > MAX_FILE_SIZE_BYTES:
                continue
            rel_str = str(item.relative_to(base_path)).replace("\\", "/")
            try:
                files[rel_str] = item.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                files[rel_str] = item.read_bytes()
        except OSError as os_err:
            logger.warning(f"Lewati berkas [{item}] karena kesalahan I/O: {os_err}")

    return files


async def import_skill_from_git(
    repo_url: str,
    custom_name: Optional[str] = None,
    custom_category: Optional[str] = None,
    custom_db_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Mengimpor playbook lengkap dari repositori Git eksternal ke Skills Hub."""
    if not (repo_url.startswith("http://") or repo_url.startswith("https://") or repo_url.startswith("git@")):
        raise ValueError("URL repositori Git tidak valid. Gunakan skema https:// atau git@.")

    raw_name = custom_name or repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp_path = Path(tmp_str)
        success = await clone_or_download_repo(repo_url, tmp_path)
        if not success:
            raise RuntimeError(f"Gagal mengkloning atau mengunduh repositori dari {repo_url}")

        files = collect_repo_files(tmp_path)
        if not files:
            raise ValueError(f"Tidak ada berkas valid yang ditemukan pada repositori {repo_url}")

        # Cari SKILL.md atau fallback ke README.md
        skill_content = ""
        for key in ("SKILL.md", "skill.md", "README.md", "readme.md"):
            if key in files and isinstance(files[key], str):
                skill_content = files[key]
                if "SKILL.md" not in files:
                    files["SKILL.md"] = skill_content
                break

        if not skill_content:
            skill_content = f"# {raw_name.upper()}\nPlaybook multi-file diimpor dari {repo_url}."
            files["SKILL.md"] = skill_content

        meta = parse_skill_metadata(skill_content, default_name=raw_name)
        target_name = custom_name or meta["name"]
        target_cat = custom_category or meta["category"]

        result = await skills_hub.install_skill_bundle(
            name=target_name,
            category_name=target_cat,
            files=files,
            description=meta["description"],
            custom_db_path=custom_db_path,
        )
        result["files_count"] = len(files)
        result["source_repo"] = repo_url
        logger.info(f"Skill [{target_name}] ({len(files)} berkas) sukses diimpor dari Git.")
        return result
