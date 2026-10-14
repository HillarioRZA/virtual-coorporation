"""
Virtual Kanban Dynamic Ticket Seeder.
Menangani seeding tiket tugas Kanban awal untuk alur Tech Core baseline
maupun alur kerja sekuensial dinamis pada branch kustom/eksperimen.
"""

from typing import Any, Dict, List, Optional
import aiosqlite

from app.core.logger import logger

BASELINE_TECH_CORE_PRESETS = [
    ("pm", "Product Requirement Document (PRD)", "Penajaman spesifikasi fitur, user stories, dan acceptance criteria."),
    ("ux", "UI/UX Wireframe & Design System", "Perancangan arketipe antarmuka, tata letak, dan design tokens."),
    ("frontend", "Next.js Frontend Prototyping", "Membangun komponen UI interaktif dan API client mock."),
    ("backend", "FastAPI Backend Implementation", "Mengimplementasikan endpoint API dan skema database relasional."),
    ("qa", "AST Security & Vulnerability Audit", "Memindai celah keamanan OWASP dan pengujian fungsional."),
]

TASK_ROLE_PRESETS: Dict[str, tuple[str, str]] = {
    "cos": ("Business Brief & Strategic Ideation", "Merumuskan value proposition dan model monetisasi."),
    "cto": ("System Architecture & OpenAPI Spec", "Menentukan stack teknologi dan spesifikasi kontrak API."),
    "pm": ("Product Requirement Document (PRD)", "Penajaman spesifikasi fitur dan user stories."),
    "ux": ("UI/UX Wireframe & Design System", "Perancangan tata letak dan arketipe antarmuka."),
    "frontend": ("Next.js Frontend Prototyping", "Membangun komponen UI interaktif dan API client."),
    "backend": ("FastAPI Backend Implementation", "Mengimplementasikan endpoint API dan skema database."),
    "qa": ("AST Security & Vulnerability Audit", "Memindai celah keamanan OWASP dan validasi kode."),
}


async def seed_branch_tickets(
    repo: Any,
    project_id: str,
    branch_id: str,
    conn: aiosqlite.Connection,
    custom_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Melakukan seeding tiket kanban awal berdasarkan branch_id."""
    if branch_id == "branch_main":
        return await _seed_main_baseline_tickets(repo, project_id, branch_id, conn, custom_path)
    return await _seed_custom_branch_tickets(repo, project_id, branch_id, conn, custom_path)


async def _seed_main_baseline_tickets(
    repo: Any,
    project_id: str,
    branch_id: str,
    conn: aiosqlite.Connection,
    custom_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Menghasilkan 5 tiket standar emas Tech Core pada branch_main."""
    roles_q = "SELECT id, division_id, slug FROM corporate_roles WHERE branch_id = 'branch_main';"
    async with conn.execute(roles_q) as cur:
        roles_map = {r["slug"]: dict(r) for r in await cur.fetchall()}

    div_eng_id = roles_map.get("frontend", {}).get("division_id", "div_eng")
    created: List[Dict[str, Any]] = []
    prev_id: Optional[str] = None

    for idx, (slug, title, desc) in enumerate(BASELINE_TECH_CORE_PRESETS):
        r_info = roles_map.get(slug)
        role_id = r_info["id"] if r_info else None
        div_id = r_info["division_id"] if r_info else div_eng_id

        t = await repo.create_ticket(
            branch_id=branch_id,
            project_id=project_id,
            division_id=div_id,
            title=title,
            description=desc,
            status="TODO" if idx == 0 else "BACKLOG",
            assigned_role_id=role_id,
            dependencies=[prev_id] if prev_id else [],
            custom_path=custom_path,
        )
        created.append(t)
        prev_id = t["id"]

    logger.info(f"Seeded 5 baseline tickets for branch_main in project '{project_id}'.")
    return created


async def _seed_custom_branch_tickets(
    repo: Any,
    project_id: str,
    branch_id: str,
    conn: aiosqlite.Connection,
    custom_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Menghasilkan tiket sesuai tahapan alur kerja kustom terurut."""
    # Ambil pipeline target (default pipeline) jika tersedia
    pipe_q = "SELECT id FROM corporate_pipelines WHERE branch_id = ? AND is_default = 1 LIMIT 1;"
    async with conn.execute(pipe_q, (branch_id,)) as cur:
        p_row = await cur.fetchone()
        target_pipe_id = p_row["id"] if p_row else None

    if target_pipe_id:
        stages_q = """
            SELECT s.id, s.stage_index, s.stage_type, s.role_id, s.ceo_gate_type,
                   s.custom_label, s.custom_instructions, r.slug AS role_slug, r.division_id
            FROM corporate_pipeline_stages s
            LEFT JOIN corporate_roles r ON s.role_id = r.id
            WHERE s.branch_id = ? AND s.pipeline_id = ?
            ORDER BY s.stage_index ASC;
        """
        async with conn.execute(stages_q, (branch_id, target_pipe_id)) as cur:
            stages = await cur.fetchall()
    else:
        stages_q = """
            SELECT s.id, s.stage_index, s.stage_type, s.role_id, s.ceo_gate_type,
                   s.custom_label, s.custom_instructions, r.slug AS role_slug, r.division_id
            FROM corporate_pipeline_stages s
            LEFT JOIN corporate_roles r ON s.role_id = r.id
            WHERE s.branch_id = ?
            ORDER BY s.stage_index ASC;
        """
        async with conn.execute(stages_q, (branch_id,)) as cur:
            stages = await cur.fetchall()

    created: List[Dict[str, Any]] = []
    prev_id: Optional[str] = None

    if stages:
        for idx, stg in enumerate(stages):
            is_ceo = stg["stage_type"] == "CEO_GATE"
            div_id = "div_exec" if is_ceo else (stg["division_id"] or "div_eng")
            role_id = None if is_ceo else stg["role_id"]
            slug = "ceo" if is_ceo else (stg["role_slug"] or "unknown")

            d_title, d_desc = TASK_ROLE_PRESETS.get(slug, (f"Tahap #{idx+1}", "Tugas operasional."))
            title = stg["custom_label"] or d_title
            desc = stg["custom_instructions"] or d_desc

            t = await repo.create_ticket(
                branch_id=branch_id,
                project_id=project_id,
                division_id=div_id,
                title=title,
                description=desc,
                status="TODO" if idx == 0 else "BACKLOG",
                assigned_role_id=role_id,
                dependencies=[prev_id] if prev_id else [],
                custom_path=custom_path,
            )
            created.append(t)
            prev_id = t["id"]
        return created

    # Fallback ke corporate_roles order_index
    fallback_q = (
        "SELECT id, division_id, name, slug FROM corporate_roles "
        "WHERE branch_id = ? AND is_active = 1 "
        "ORDER BY COALESCE(order_index, 0) ASC, created_at ASC;"
    )
    async with conn.execute(fallback_q, (branch_id,)) as cur:
        ordered_roles = await cur.fetchall()

    for idx, role in enumerate(ordered_roles):
        d_title, d_desc = TASK_ROLE_PRESETS.get(role["slug"], (f"Tahap {role['name']}", f"Tugas {role['name']}"))
        t = await repo.create_ticket(
            branch_id=branch_id,
            project_id=project_id,
            division_id=role["division_id"],
            title=d_title,
            description=d_desc,
            status="TODO" if idx == 0 else "BACKLOG",
            assigned_role_id=role["id"],
            dependencies=[prev_id] if prev_id else [],
            custom_path=custom_path,
        )
        created.append(t)
        prev_id = t["id"]
    return created
