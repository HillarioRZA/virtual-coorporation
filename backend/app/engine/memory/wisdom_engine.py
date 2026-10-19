"""
Corporate Wisdom Engine & Cross-Venture Institutional Knowledge Manager.
Mengelola ekstraksi, indeksasi, dan query memori korporat jangka panjang antar-venture.
"""

import uuid
from typing import Any, Dict, List, Optional
from app.core.logger import logger
from app.db.wisdom_repo import wisdom_repo, CorporateWisdomRepo
from app.engine.memory.vector_store import vector_store, SovereignVectorStore


DEFAULT_WISDOM_NAMESPACES: List[str] = [
    "wisdom:architecture",
    "wisdom:bugs_and_fixes",
    "wisdom:growth_copy",
    "wisdom:organization",
]


class CorporateWisdomEngine:
    """Orkestrator utama memori institusional jangka panjang organisasi."""

    def __init__(
        self,
        repo: Optional[CorporateWisdomRepo] = None,
        store: Optional[SovereignVectorStore] = None,
    ) -> None:
        """Inisialisasi engine wisdom."""
        self.repo = repo or wisdom_repo
        self.store = store or vector_store

    async def record_wisdom(
        self,
        title: str,
        problem_pattern: str,
        solution_guideline: str,
        namespace: str = "wisdom:architecture",
        tags: Optional[List[str]] = None,
        source_venture_id: str = "global",
        source_pr_id: Optional[str] = None,
        custom_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Mencatat dan meng-embed memori institusional baru ke dalam repositori."""
        wisdom_id = f"wis_{uuid.uuid4().hex[:10]}"
        tag_list = tags or []
        combined_text = f"{title} {problem_pattern} {solution_guideline} {' '.join(tag_list)}"
        embedding = self.store.embed_text(combined_text)

        saved = await self.repo.save_wisdom(
            wisdom_id=wisdom_id,
            namespace=namespace,
            title=title,
            problem_pattern=problem_pattern,
            solution_guideline=solution_guideline,
            tags=tag_list,
            embedding=embedding,
            source_venture_id=source_venture_id,
            source_pr_id=source_pr_id,
            custom_path=custom_path,
        )
        logger.info(f"Berhasil mengindeks wisdom baru [{wisdom_id}] pada namespace [{namespace}]")
        return saved

    async def query_wisdom(
        self,
        query: str,
        target_role: Optional[str] = None,
        namespace: Optional[str] = None,
        top_k: int = 3,
        min_similarity: float = 0.15,
        custom_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Mencari wisdom institusional paling relevan berdasarkan query semantik."""
        if namespace:
            all_candidates = await self.repo.get_all_embeddings(namespace=namespace, custom_path=custom_path)
        else:
            all_candidates = await self.repo.get_all_embeddings(custom_path=custom_path)

        matched = self.store.search_similar(query, all_candidates, top_k=top_k, min_similarity=min_similarity)
        results: List[Dict[str, Any]] = []
        for item, score in matched:
            item_copy = dict(item)
            item_copy["similarity_score"] = score
            results.append(item_copy)
            await self.repo.increment_usage(item["id"], custom_path=custom_path)

        return results

    async def sync_organization_knowledge(self, custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Menyimpan bagan struktur divisi, tujuan, peran aktif & jobdesk ke wisdom base."""
        try:
            from app.db.corporate_repo import corporate_repo
            divisions = await corporate_repo.get_divisions(custom_path=custom_path)
            roles = await corporate_repo.get_roles(custom_path=custom_path)
            if not divisions and not roles:
                return None
            lines = ["STRUKTUR ORGANISASI & KAPASITAS PERUSAHAAN SAAT INI:"]
            for div in divisions:
                div_desc = div.get("description") or "Operasional Divisi"
                lines.append(f"Divisi: {div['name']} (Tujuan: {div_desc})")
                div_roles = [r for r in roles if r.get("division_id") == div["id"]]
                for r in div_roles:
                    job = r.get("job_description") or "Menjalankan tugas spesialisasi peran"
                    lines.append(f"  - Peran: @{r['name']} | Jobdesk: {job}")
            content = "\n".join(lines)
            return await self.record_wisdom(
                title="Bagan Struktur Organisasi, Divisi, dan Peran Aktif Perusahaan",
                problem_pattern="Mengetahui hierarki perusahaan, divisi, kapasitas peran rekan kerja, dan spesialisasi tugas untuk kolaborasi & delegasi.",
                solution_guideline=content,
                namespace="wisdom:organization",
                tags=["organization", "divisions", "roles", "corporate_structure", "jobdesk"],
                source_venture_id="global",
                custom_path=custom_path,
            )
        except Exception as err:
            logger.warning(f"Gagal mensinkronkan knowledge organisasi ke wisdom: {err}")
            return None

    async def distill_from_pr(
        self,
        pr_data: Dict[str, Any],
        review_comments: List[Dict[str, Any]],
        custom_path: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Mengekstraksi wisdom institusional secara otomatis dari PR yang berhasil di-merge."""
        title = pr_data.get("title", "")
        desc = pr_data.get("description", "")
        tags = ["automated_distill", "pr_review", pr_data.get("branch_name", "main")]
        solution = f"Solusi disepakati dari PR: {title}. {desc}"

        guidelines: List[str] = []
        for rev in review_comments:
            for c in rev.get("comments", []):
                if c.get("suggested_fix"):
                    guidelines.append(f"- {c.get('message')}: {c.get('suggested_fix')}")

        if guidelines:
            solution += "\nCatatan reviewer:\n" + "\n".join(guidelines[:3])

        return await self.record_wisdom(
            title=f"Precedent from PR: {title}",
            problem_pattern=desc or "Iterasi dan refactoring modul engineering.",
            solution_guideline=solution,
            namespace="wisdom:bugs_and_fixes" if "fix" in title.lower() or "bug" in title.lower() else "wisdom:architecture",
            tags=tags,
            source_venture_id=pr_data.get("project_id", "global"),
            source_pr_id=pr_data.get("id"),
            custom_path=custom_path,
        )

    def format_wisdom_for_prompt(self, items: List[Dict[str, Any]]) -> str:
        """Memformat daftar item wisdom menjadi blok teks kompak untuk prompt agen."""
        if not items:
            return ""
        lines = ["[CORPORATE WISDOM & CROSS-VENTURE HISTORICAL PRECEDENTS]:"]
        for it in items:
            ns = it.get("namespace", "wisdom")
            title = it.get("title", "Untitled Guideline")
            prob = it.get("problem_pattern", "")
            sol = it.get("solution_guideline", "")
            lines.append(f"- [{ns} | \"{title}\"]\n  Problem: {prob}\n  Prescriptive Rule: {sol}")
        return "\n".join(lines)


wisdom_engine = CorporateWisdomEngine()
