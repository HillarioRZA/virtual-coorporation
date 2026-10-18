"""GitHub Knowledge & Plugin Ecosystem Bridge.

Menyediakan fungsi terisolasi untuk mengunduh, memvalidasi keamanan,
dan mengimpor markdown blueprint ke wisdom base serta plugin Python ke tool registry.
"""

from pathlib import Path
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import uuid
import httpx

from app.core.logger import logger
from app.db.wisdom_repo import wisdom_repo
from app.engine.tool_synthesizer import tool_synthesizer
from app.engine.vector_store import vector_store


def convert_to_raw_github_url(url: str) -> str:
    """Mengonversi URL blob GitHub standar menjadi URL raw.githubusercontent.com yang valid."""
    cleaned = url.strip()
    parsed = urlparse(cleaned)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL harus menggunakan protokol HTTP atau HTTPS.")

    netloc = parsed.netloc.lower()
    if netloc == "raw.githubusercontent.com":
        return cleaned

    if netloc == "github.com":
        parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(parts) >= 4 and parts[2] == "blob":
            owner, repo, _, branch = parts[0], parts[1], parts[2], parts[3]
            file_path = "/".join(parts[4:])
            return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
        raise ValueError("Format URL github.com tidak valid. Format: https://github.com/:owner/:repo/blob/:branch/:file")

    raise ValueError(f"Domain '{netloc}' tidak diizinkan. Hanya github.com atau raw.githubusercontent.com.")


async def fetch_github_markdown_skill(
    url: str,
    namespace: str = "wisdom:skills",
    tags: Optional[List[str]] = None,
    custom_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Mengunduh berkas Markdown dari GitHub dan menyimpannya ke Corporate Wisdom Base dengan embedding."""
    raw_url = convert_to_raw_github_url(url)
    try:
        async with httpx.AsyncClient(timeout=10.0, headers={"User-Agent": "Universal-Conglomerate-OS/5.2"}) as client:
            res = await client.get(raw_url)
            res.raise_for_status()
            content = res.text
    except (httpx.HTTPError, httpx.TimeoutException) as err:
        logger.error(f"Gagal mengunduh Markdown dari GitHub [{raw_url}]: {err}")
        raise ValueError(f"Gagal mengunduh dari GitHub: {err}")

    # Ekstraksi judul berkas atau heading # pertama
    title = ""
    for line in content.splitlines():
        trimmed = line.strip()
        if trimmed.startswith("# "):
            title = trimmed[2:].strip()
            break
    if not title:
        parsed = urlparse(raw_url)
        title = Path(parsed.path).stem.replace("-", " ").replace("_", " ").title()

    wisdom_id = f"wisdom_gh_{uuid.uuid4().hex[:8]}"
    effective_tags = list(tags or [])
    if "github" not in effective_tags:
        effective_tags.append("github")

    problem_pattern = f"GitHub Skill / Architectural Blueprint ({raw_url})"
    solution_guideline = content
    embedding_text = f"{title}\n{problem_pattern}\n{content[:500]}"
    embedding = vector_store.embed_text(embedding_text)

    saved = await wisdom_repo.save_wisdom(
        wisdom_id=wisdom_id,
        namespace=namespace,
        title=title,
        problem_pattern=problem_pattern,
        solution_guideline=solution_guideline,
        tags=effective_tags,
        embedding=embedding,
        source_venture_id="github_bridge",
        custom_path=custom_path,
    )
    logger.info(f"Skill Markdown dari GitHub berhasil diimpor: [{title}] ({wisdom_id})")
    return {
        "success": True,
        "wisdom_id": wisdom_id,
        "title": title,
        "namespace": namespace,
        "raw_url": raw_url,
        "wisdom": saved,
    }


async def fetch_github_python_plugin(
    project_id: str,
    url: str,
    tool_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Mengunduh skrip Python dari GitHub dan memvalidasinya melalui DynamicToolRegistry."""
    raw_url = convert_to_raw_github_url(url)
    try:
        async with httpx.AsyncClient(timeout=10.0, headers={"User-Agent": "Universal-Conglomerate-OS/5.2"}) as client:
            res = await client.get(raw_url)
            res.raise_for_status()
            code = res.text
    except (httpx.HTTPError, httpx.TimeoutException) as err:
        logger.error(f"Gagal mengunduh skrip Python dari GitHub [{raw_url}]: {err}")
        raise ValueError(f"Gagal mengunduh skrip dari GitHub: {err}")

    script_name = tool_name
    if not script_name:
        parsed = urlparse(raw_url)
        script_name = Path(parsed.path).name or "plugin.py"
    if not script_name.endswith(".py"):
        script_name = f"{script_name}.py"

    logger.info(f"Memverifikasi keamanan plugin GitHub [{script_name}] untuk venture [{project_id}]...")
    return tool_synthesizer.synthesize_tool_script(
        project_id=project_id,
        script_name=script_name,
        python_code=code,
    )
