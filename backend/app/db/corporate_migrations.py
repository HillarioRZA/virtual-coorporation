"""
Modul Migrasi Skema Basis Data SQLite Korporat.
Menangani evolusi skema tabel corporate_roles, corporate_branches, dan corporate_divisions.
"""

from typing import Dict
import aiosqlite
from app.db.corporate_prompts import DEFAULT_ROLE_PROMPTS


async def migrate_order_index(conn: aiosqlite.Connection) -> None:
    """Migrasi aman kolom order_index dan penegakan urutan kanonikal."""
    for tbl in ("corporate_divisions", "corporate_roles"):
        cur = await conn.execute(f"PRAGMA table_info({tbl});")
        cols = [r[1] for r in await cur.fetchall()]
        if "order_index" not in cols:
            await conn.execute(f"ALTER TABLE {tbl} ADD COLUMN order_index INTEGER DEFAULT 0;")

    canonical_roles = [("role_cos", 0), ("role_cto", 1), ("role_pm", 2), ("role_ux", 3), ("role_fe", 4), ("role_be", 5), ("role_qa", 6)]
    for r_id, order in canonical_roles:
        await conn.execute(
            "UPDATE corporate_roles SET order_index = ? WHERE branch_id = 'branch_main' AND id = ?;",
            (order, r_id),
        )

    canonical_divs = [("div_exec", 0), ("div_product", 1), ("div_eng", 2)]
    for d_id, order in canonical_divs:
        await conn.execute(
            "UPDATE corporate_divisions SET order_index = ? WHERE branch_id = 'branch_main' AND id = ?;",
            (order, d_id),
        )


async def migrate_role_fallback_chain(conn: aiosqlite.Connection) -> None:
    """Migrasi aman kolom fallback_chain pada tabel corporate_roles."""
    cur = await conn.execute("PRAGMA table_info(corporate_roles);")
    cols = [r[1] for r in await cur.fetchall()]
    if "fallback_chain" not in cols:
        await conn.execute("ALTER TABLE corporate_roles ADD COLUMN fallback_chain TEXT DEFAULT '[]';")


async def migrate_branch_parent_column(conn: aiosqlite.Connection) -> None:
    """Migrasi aman kolom parent_branch_id dan roles_snapshot pada corporate_branches."""
    cur = await conn.execute("PRAGMA table_info(corporate_branches);")
    cols = [r[1] for r in await cur.fetchall()]
    if "parent_branch_id" not in cols:
        await conn.execute("ALTER TABLE corporate_branches ADD COLUMN parent_branch_id TEXT DEFAULT 'branch_main';")
    if "roles_snapshot" not in cols:
        await conn.execute("ALTER TABLE corporate_branches ADD COLUMN roles_snapshot TEXT DEFAULT '{}';")


async def migrate_role_thinking_level_column(conn: aiosqlite.Connection) -> None:
    """Migrasi aman kolom thinking_level pada corporate_roles."""
    cur = await conn.execute("PRAGMA table_info(corporate_roles);")
    cols = [r[1] for r in await cur.fetchall()]
    if "thinking_level" not in cols:
        await conn.execute("ALTER TABLE corporate_roles ADD COLUMN thinking_level TEXT DEFAULT 'medium';")


async def migrate_drop_role_slug_column(conn: aiosqlite.Connection) -> None:
    """Migrasi aman menghapus kolom slug dari tabel corporate_roles dengan pola Table Rebuild."""
    cur = await conn.execute("PRAGMA table_info(corporate_roles);")
    cols = [r[1] for r in await cur.fetchall()]
    if "slug" not in cols:
        return

    await conn.execute("DROP INDEX IF EXISTS idx_roles_branch_slug;")
    await conn.execute("DROP INDEX IF EXISTS idx_roles_branch_division;")

    await conn.execute("""
    CREATE TABLE IF NOT EXISTS corporate_roles_new (
        id TEXT PRIMARY KEY,
        branch_id TEXT NOT NULL,
        division_id TEXT NOT NULL,
        name TEXT NOT NULL,
        job_description TEXT DEFAULT '',
        persona_prompt TEXT DEFAULT '',
        system_prompt_template TEXT NOT NULL,
        model_provider TEXT NOT NULL DEFAULT 'openrouter',
        model_name TEXT NOT NULL DEFAULT 'deepseek/deepseek-r1:free',
        temperature REAL DEFAULT 0.2,
        thinking_level TEXT NOT NULL DEFAULT 'medium',
        tool_permissions TEXT NOT NULL DEFAULT '["read_file", "write_file", "ast_scan"]',
        token_budget_per_task INTEGER DEFAULT 8000,
        is_active BOOLEAN DEFAULT 1,
        is_system_default BOOLEAN DEFAULT 0,
        order_index INTEGER DEFAULT 0,
        fallback_chain TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(branch_id) REFERENCES corporate_branches(id) ON DELETE CASCADE,
        FOREIGN KEY(division_id) REFERENCES corporate_divisions(id) ON DELETE CASCADE,
        UNIQUE(branch_id, name)
    );
    """)

    has_fb = "fallback_chain" in cols
    fb_expr = "fallback_chain" if has_fb else "'[]'"
    has_tl = "thinking_level" in cols
    tl_expr = "thinking_level" if has_tl else "'medium'"
    has_jd = "job_description" in cols
    jd_expr = "COALESCE(job_description, '')" if has_jd else "''"
    has_oi = "order_index" in cols
    oi_expr = "COALESCE(order_index, 0)" if has_oi else "0"
    has_pp = "persona_prompt" in cols
    pp_expr = "COALESCE(persona_prompt, '')" if has_pp else "''"

    copy_sql = f"""
    INSERT INTO corporate_roles_new (
        id, branch_id, division_id, name, job_description, persona_prompt, system_prompt_template,
        model_provider, model_name, temperature, thinking_level, tool_permissions,
        token_budget_per_task, is_active, is_system_default, order_index, fallback_chain,
        created_at, updated_at
    )
    SELECT
        id, branch_id, division_id, name, {jd_expr}, {pp_expr}, system_prompt_template,
        model_provider, model_name, temperature, {tl_expr}, tool_permissions,
        token_budget_per_task, is_active, is_system_default, {oi_expr}, {fb_expr},
        created_at, updated_at
    FROM corporate_roles;
    """
    await conn.execute(copy_sql)
    await conn.execute("DROP TABLE corporate_roles;")
    await conn.execute("ALTER TABLE corporate_roles_new RENAME TO corporate_roles;")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_roles_branch_division ON corporate_roles(branch_id, division_id);")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_roles_branch_name ON corporate_roles(branch_id, name);")


async def migrate_rich_system_prompts(conn: aiosqlite.Connection) -> None:
    """Migrasi aman memperbarui prompt sistem kanonikal ke template persona komprehensif."""
    id_map = {"cos": "role_cos", "cto": "role_cto", "pm": "role_pm", "ux": "role_ux", "frontend": "role_fe", "backend": "role_be", "qa": "role_qa"}
    for slug_key, prompt in DEFAULT_ROLE_PROMPTS.items():
        r_id = id_map.get(slug_key, f"role_{slug_key}")
        await conn.execute(
            """
            UPDATE corporate_roles
            SET system_prompt_template = ?
            WHERE branch_id = 'branch_main' AND id = ? AND LENGTH(system_prompt_template) < 120;
            """,
            (prompt, r_id),
        )


async def migrate_role_job_description_column(conn: aiosqlite.Connection) -> None:
    """Migrasi aman kolom job_description pada tabel corporate_roles."""
    cur = await conn.execute("PRAGMA table_info(corporate_roles);")
    cols = [r[1] for r in await cur.fetchall()]
    if "job_description" not in cols:
        await conn.execute("ALTER TABLE corporate_roles ADD COLUMN job_description TEXT DEFAULT '';")

    canonical_jobdesks: Dict[str, str] = {
        "role_cos": "Validasi kelayakan pasar, monetisasi, model harga, & mitigasi risiko bisnis.",
        "role_cto": "Arsitektur sistem, pemilihan stack teknologi, API specs, & batas teknis.",
        "role_pm": "Penyusunan Lean PRD, user stories, acceptance criteria, & pembagian tiket Kanban.",
        "role_ux": "Design tokens, tata letak antarmuka, komponen Tailwind CSS, & wireframe visual.",
        "role_fe": "Implementasi UI Next.js 14 App Router, React, & komponen interaktif.",
        "role_be": "Implementasi REST API FastAPI, skema data Pydantic, & integrasi SQLite.",
        "role_qa": "Adversarial TDD test suite, AST security scan, audit OWASP, & penguncian tes.",
    }
    for r_id, jd in canonical_jobdesks.items():
        await conn.execute(
            """
            UPDATE corporate_roles
            SET job_description = ?
            WHERE branch_id = 'branch_main' AND id = ? AND (job_description IS NULL OR job_description = '');
            """,
            (jd, r_id),
        )


async def migrate_role_persona_prompt(conn: aiosqlite.Connection) -> None:
    """Migrasi aman kolom persona_prompt (Layer 1 Soul/DNA) pada corporate_roles."""
    cur = await conn.execute("PRAGMA table_info(corporate_roles);")
    cols = [r[1] for r in await cur.fetchall()]
    if "persona_prompt" not in cols:
        await conn.execute("ALTER TABLE corporate_roles ADD COLUMN persona_prompt TEXT DEFAULT '';")

    from app.db.corporate_prompts import DEFAULT_PERSONA_PROMPTS
    id_map = {
        "cos": "role_cos", "cto": "role_cto", "pm": "role_pm", "ux": "role_ux",
        "frontend": "role_fe", "backend": "role_be", "qa": "role_qa",
    }
    for slug_key, persona in DEFAULT_PERSONA_PROMPTS.items():
        r_id = id_map.get(slug_key, f"role_{slug_key}")
        await conn.execute(
            """
            UPDATE corporate_roles
            SET persona_prompt = ?
            WHERE branch_id = 'branch_main' AND id = ? AND (persona_prompt IS NULL OR persona_prompt = '');
            """,
            (persona, r_id),
        )
