"""
Seeder Struktur Korporat, Pipeline Tahapan & Corporate Wisdom Base.
Mengisi konfigurasi kanonikal bawaan saat basis data pertama kali diinisialisasi.
"""

import json
from typing import List, Tuple
import aiosqlite
from app.db.corporate_prompts import DEFAULT_ROLE_PROMPTS, DEFAULT_PERSONA_PROMPTS
from app.db.corporate_migrations import (
    migrate_order_index,
    migrate_role_fallback_chain,
    migrate_branch_parent_column,
    migrate_role_thinking_level_column,
    migrate_rich_system_prompts,
    migrate_role_job_description_column,
    migrate_drop_role_slug_column,
    migrate_role_persona_prompt,
)


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
        ("role_cos", "branch_main", "div_exec", "Chief of Staff", "Validasi kelayakan pasar, monetisasi, model harga, & mitigasi risiko bisnis.", DEFAULT_PERSONA_PROMPTS["cos"], DEFAULT_ROLE_PROMPTS["cos"], "openrouter", "deepseek/deepseek-r1:free", 0.2, '["read_file", "write_file"]', 8000, 1, 1, 0),
        ("role_cto", "branch_main", "div_eng", "Chief Technology Officer", "Arsitektur sistem, pemilihan stack teknologi, API specs, & batas teknis.", DEFAULT_PERSONA_PROMPTS["cto"], DEFAULT_ROLE_PROMPTS["cto"], "openrouter", "qwen/qwen-2.5-coder-32b-instruct:free", 0.2, '["read_file", "write_file", "ast_scan"]', 10000, 1, 1, 1),
        ("role_pm", "branch_main", "div_product", "Product Manager", "Penyusunan Lean PRD, user stories, acceptance criteria, & pembagian tiket Kanban.", DEFAULT_PERSONA_PROMPTS["pm"], DEFAULT_ROLE_PROMPTS["pm"], "openrouter", "deepseek/deepseek-r1:free", 0.2, '["read_file", "write_file"]', 8000, 1, 1, 2),
        ("role_ux", "branch_main", "div_product", "UI/UX Architect", "Design tokens, tata letak antarmuka, komponen Tailwind CSS, & wireframe visual.", DEFAULT_PERSONA_PROMPTS["ux"], DEFAULT_ROLE_PROMPTS["ux"], "openrouter", "deepseek/deepseek-r1:free", 0.3, '["read_file", "write_file"]', 8000, 1, 1, 3),
        ("role_fe", "branch_main", "div_eng", "Frontend Engineer", "Implementasi UI Next.js 14 App Router, React, & komponen interaktif.", DEFAULT_PERSONA_PROMPTS["frontend"], DEFAULT_ROLE_PROMPTS["frontend"], "openrouter", "qwen/qwen-2.5-coder-32b-instruct:free", 0.2, '["read_file", "write_file"]', 12000, 1, 1, 4),
        ("role_be", "branch_main", "div_eng", "Backend Engineer", "Implementasi REST API FastAPI, skema data Pydantic, & integrasi SQLite.", DEFAULT_PERSONA_PROMPTS["backend"], DEFAULT_ROLE_PROMPTS["backend"], "openrouter", "qwen/qwen-2.5-coder-32b-instruct:free", 0.2, '["read_file", "write_file"]', 12000, 1, 1, 5),
        ("role_qa", "branch_main", "div_eng", "QA & SecOps Engineer", "Adversarial TDD test suite, AST security scan, audit OWASP, & penguncian tes.", DEFAULT_PERSONA_PROMPTS["qa"], DEFAULT_ROLE_PROMPTS["qa"], "openrouter", "deepseek/deepseek-r1:free", 0.1, '["read_file", "ast_scan"]', 8000, 1, 1, 6),
        ("role_secretary", "branch_main", "div_exec", "Sekretaris Eksekutif", "Liaison eksekutif Founder, delegasi tugas Kanban, pemantauan status agen, analisa MCP/Skills, & sintesis perkakas internal via Telegram.", DEFAULT_PERSONA_PROMPTS["secretary"], DEFAULT_ROLE_PROMPTS["secretary"], "openrouter", "deepseek/deepseek-r1:free", 0.4, '["chat_telegram", "runtime_tool_builder", "inspect_db_schema", "read_file"]', 8000, 1, 1, 7),
    ]
    await conn.executemany(
        """
        INSERT OR IGNORE INTO corporate_roles 
        (id, branch_id, division_id, name, job_description, persona_prompt, system_prompt_template, model_provider, model_name, temperature, tool_permissions, token_budget_per_task, is_active, is_system_default, order_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        roles,
    )


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
        (
            "wis_org_001", "wisdom:organization", "Bagan Divisi & Kapasitas Peran Korporat",
            "Mengetahui struktur hierarki, mandat divisi, kapasitas karyawan AI, dan jobdesk rekan kerja untuk kolaborasi.",
            "Setiap peran AI beroperasi di bawah divisi tertentu dan memiliki jobdesk spesifik yang dapat diperbarui di /organization.",
            json.dumps(["organization", "roles", "divisions", "jobdesk", "corporate_structure"]),
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
