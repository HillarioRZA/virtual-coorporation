"""
Seeder Struktur Korporat, Pipeline Tahapan & Corporate Wisdom Base.
Mengisi konfigurasi kanonikal bawaan saat basis data pertama kali diinisialisasi.
"""

import json
from typing import List, Tuple
import aiosqlite


async def seed_default_corporate_structure(conn: aiosqlite.Connection) -> None:
    """Melakukan seeding otomatis struktur Tech Core bawaan pada branch 'main' jika belum ada."""
    await conn.execute(
        """
        INSERT OR IGNORE INTO corporate_branches (id, name, slug, description, is_active_main)
        VALUES ('branch_main', 'Production Main', 'main', 'Alur kerja resmi produksi aktif (Tech Core Baseline)', 1);
        """
    )

    divisions = [
        ("div_exec", "branch_main", "Executive Suite", "executive", "Koordinasi strategis & anggaran CFO", "#ffffff", "Briefcase", 1, 0),
        ("div_product", "branch_main", "Product & Design Division", "product", "Penajaman spesifikasi produk, user stories, & UI/UX", "#a855f7", "Layout", 1, 1),
        ("div_eng", "branch_main", "Software & SaaS Division", "engineering", "Rekayasa perangkat lunak, arsitektur, coding, & QA", "#3b82f6", "Code", 1, 2),
    ]
    await conn.executemany(
        """
        INSERT OR IGNORE INTO corporate_divisions 
        (id, branch_id, name, slug, description, accent_color, icon_name, is_system_default, order_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        divisions,
    )

    roles = [
        ("role_cos", "branch_main", "div_exec", "Chief of Staff", "cos", "Orkestrasi ide bisnis, evaluasi strategi, dan sparring founder", "openrouter", "deepseek/deepseek-r1:free", 0.2, '["read_file", "write_file"]', 8000, 1, 1, 0),
        ("role_cto", "branch_main", "div_eng", "Chief Technology Officer", "cto", "Arsitektur sistem, pemilihan arketipe, dan validasi engineering", "openrouter", "qwen/qwen-2.5-coder-32b-instruct:free", 0.2, '["read_file", "write_file", "ast_scan"]', 10000, 1, 1, 1),
        ("role_pm", "branch_main", "div_product", "Product Manager", "pm", "Penajaman spesifikasi produk, user stories, dan PRD freeze", "openrouter", "deepseek/deepseek-r1:free", 0.2, '["read_file", "write_file"]', 8000, 1, 1, 2),
        ("role_ux", "branch_main", "div_product", "UI/UX Architect", "ux", "Desain arketipe visual, wireframe, dan layout antarmuka", "openrouter", "deepseek/deepseek-r1:free", 0.3, '["read_file", "write_file"]', 8000, 1, 1, 3),
        ("role_fe", "branch_main", "div_eng", "Frontend Engineer", "frontend", "Implementasi antarmuka Next.js 14, Tailwind CSS, dan scaffolding client", "openrouter", "qwen/qwen-2.5-coder-32b-instruct:free", 0.2, '["read_file", "write_file"]', 12000, 1, 1, 4),
        ("role_be", "branch_main", "div_eng", "Backend Engineer", "backend", "Implementasi API FastAPI, database SQLite, dan scaffolding server", "openrouter", "qwen/qwen-2.5-coder-32b-instruct:free", 0.2, '["read_file", "write_file"]', 12000, 1, 1, 5),
        ("role_qa", "branch_main", "div_eng", "QA & SecOps Engineer", "qa", "Audit keamanan AST OWASP, verifikasi unit testing, dan evaluasi kelayakan release", "openrouter", "deepseek/deepseek-r1:free", 0.1, '["read_file", "ast_scan"]', 8000, 1, 1, 6),
    ]
    await conn.executemany(
        """
        INSERT OR IGNORE INTO corporate_roles 
        (id, branch_id, division_id, name, slug, system_prompt_template, model_provider, model_name, temperature, tool_permissions, token_budget_per_task, is_active, is_system_default, order_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        roles,
    )


async def migrate_order_index(conn: aiosqlite.Connection) -> None:
    """Migrasi aman kolom order_index dan penegakan urutan kanonikal proposal.md & PRD.md."""
    for tbl in ("corporate_divisions", "corporate_roles"):
        cur = await conn.execute(f"PRAGMA table_info({tbl});")
        cols = [r[1] for r in await cur.fetchall()]
        if "order_index" not in cols:
            await conn.execute(f"ALTER TABLE {tbl} ADD COLUMN order_index INTEGER DEFAULT 0;")

    canonical_roles = [("cos", 0), ("cto", 1), ("pm", 2), ("ux", 3), ("frontend", 4), ("backend", 5), ("qa", 6)]
    for slug, order in canonical_roles:
        await conn.execute(
            "UPDATE corporate_roles SET order_index = ? WHERE branch_id = 'branch_main' AND slug = ?;",
            (order, slug),
        )

    canonical_divs = [("executive", 0), ("product", 1), ("engineering", 2)]
    for slug, order in canonical_divs:
        await conn.execute(
            "UPDATE corporate_divisions SET order_index = ? WHERE branch_id = 'branch_main' AND slug = ?;",
            (order, slug),
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




async def seed_default_pipeline_stages(conn: aiosqlite.Connection) -> None:
    """Melakukan seeding otomatis pipeline lini produk dan tahapan alur kerja kanonikal."""
    cur_col = await conn.execute("PRAGMA table_info(corporate_pipeline_stages);")
    cols = [r[1] for r in await cur_col.fetchall()]
    if "pipeline_id" not in cols:
        await conn.execute("ALTER TABLE corporate_pipeline_stages ADD COLUMN pipeline_id TEXT DEFAULT 'pipe_software_main';")
    await conn.execute(
        "UPDATE corporate_pipeline_stages SET pipeline_id = 'pipe_software_main' WHERE pipeline_id IS NULL OR pipeline_id = '';"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_pipeline_stages_pipe ON corporate_pipeline_stages(pipeline_id, stage_index);"
    )

    default_pipes = [
        ("pipe_software_main", "branch_main", "Software & SaaS (Tech Core)", "software", "SOFTWARE", "Alur rekayasa software kanonikal: PRD, Spec, UI/UX, Frontend, Backend, QA, dan Stage-Gates CEO.", 1),
        ("pipe_education_main", "branch_main", "Education & Course Creation", "education", "EDUCATION", "Alur pembuatan silabus edukasi, materi pembelajaran, e-book, dan kurikulum pelatihan.", 0),
        ("pipe_content_main", "branch_main", "Copywriting & Marketing", "copywriting", "COPYWRITING", "Alur produksi konten artikel SEO, copywriting landing page, materi iklan, dan review editor.", 0),
    ]
    await conn.executemany(
        """
        INSERT OR IGNORE INTO corporate_pipelines
        (id, branch_id, name, slug, product_line, description, is_default)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        default_pipes,
    )

    cur = await conn.execute(
        "SELECT COUNT(*) as count FROM corporate_pipeline_stages WHERE branch_id = 'branch_main' AND pipeline_id = 'pipe_software_main';"
    )
    row = await cur.fetchone()
    if row and row["count"] == 0:
        canonical_stages = [
            ("stg_main_0", "branch_main", "pipe_software_main", 0, "ROLE_EXECUTION", "role_cos", None, "Fase 1: Analisis Pasar & Unit Economics", None),
            ("stg_main_1", "branch_main", "pipe_software_main", 1, "ROLE_EXECUTION", "role_cto", None, "Fase 1: Arsitektur Sistem & Arketipe", None),
            ("stg_main_2", "branch_main", "pipe_software_main", 2, "CEO_GATE", None, "APPROVAL_GATE", "Stage-Gate 1: Founder Concept Approval", "Founder mereview Business Brief dan Arsitektur sebelum koding."),
            ("stg_main_3", "branch_main", "pipe_software_main", 3, "ROLE_EXECUTION", "role_pm", None, "Fase 2: Lean PRD & OpenAPI Spec SSOT", None),
            ("stg_main_4", "branch_main", "pipe_software_main", 4, "ROLE_EXECUTION", "role_ux", None, "Fase 2: Wireframe & Tailwind Design Tokens", None),
            ("stg_main_5", "branch_main", "pipe_software_main", 5, "ROLE_EXECUTION", "role_fe", None, "Fase 2: Next.js Interactive Demo Build", None),
            ("stg_main_6", "branch_main", "pipe_software_main", 6, "CEO_GATE", None, "APPROVAL_GATE", "Stage-Gate 2: CEO Demo Day Sandbox Review", "Founder menguji coba langsung klik di browser sandbox."),
            ("stg_main_7", "branch_main", "pipe_software_main", 7, "ROLE_EXECUTION", "role_be", None, "Fase 3: FastAPI Backend & Real Database", None),
            ("stg_main_8", "branch_main", "pipe_software_main", 8, "ROLE_EXECUTION", "role_qa", None, "Fase 3: AST OWASP Security Audit & Evals", None),
            ("stg_main_9", "branch_main", "pipe_software_main", 9, "CEO_GATE", None, "APPROVAL_GATE", "Stage-Gate 3: Pre-Launch Credential Check", "Founder memasukkan kunci produksi ke Vault."),
        ]
        await conn.executemany(
            """
            INSERT OR IGNORE INTO corporate_pipeline_stages
            (id, branch_id, pipeline_id, stage_index, stage_type, role_id, ceo_gate_type, custom_label, custom_instructions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            canonical_stages,
        )


async def seed_default_corporate_wisdom(conn: aiosqlite.Connection) -> None:
    """Melakukan seeding memori institusional kanonikal bawaan organisasi."""
    default_wisdom = [
        (
            "wis_arch_001", "wisdom:architecture", "Single Responsibility Modularization (150-200 Lines)",
            "File membengkak di atas 200 baris menjadi monolit sulit di-maintain dan memicu context drift.",
            "Pecah modul besar menjadi sub-komponen terpisah dengan batas maksimal 150-200 baris kode per file.",
            json.dumps(["architecture", "srp", "refactoring", "code_quality"]),
            "global",
        ),
        (
            "wis_bug_001", "wisdom:bugs_and_fixes", "CORS Middleware Pipeline Ordering on Custom Security Gates",
            "Respon error 401 Unauthorized dari custom security gate kehilangan header CORS dan memicu 'Failed to fetch' di browser.",
            "Daftarkan CORSMiddleware di layer terluar (paling akhir di add_middleware FastAPI) agar membungkus semua respon error status.",
            json.dumps(["cors", "fastapi", "middleware", "auth", "http401"]),
            "global",
        ),
        (
            "wis_copy_001", "wisdom:growth_copy", "B2B SaaS Pain-Benefit Hero Hook Formulation",
            "Copywriting landing page terlalu teknis dan gagal mengonversi pengunjung menjadi pengguna aktif.",
            "Gunakan pola: [Pain Point Utama] + [Solusi Otonom Berdampak Tinggi] + [CTA Eksplisit dengan Zero-Risk Guarantee].",
            json.dumps(["growth", "copywriting", "landing_page", "conversion"]),
            "global",
        ),
    ]
    for wid, ns, title, prob, sol, tags, src in default_wisdom:
        await conn.execute(
            """
            INSERT OR IGNORE INTO corporate_wisdom
            (id, namespace, title, problem_pattern, solution_guideline, tags, source_venture_id)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (wid, ns, title, prob, sol, tags, src),
        )
