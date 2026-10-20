"""
Skema DDL Basis Data SQLite untuk Tabel MCP Servers, Skills, dan Kategori Dinamis.
Mendukung isolasi MCP, penyimpanan folder bundle Skills, dan pencarian teks penuh (FTS5).
"""

MCP_SKILLS_DDL_SCHEMA = """
CREATE TABLE IF NOT EXISTS corporate_mcp_servers (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    transport TEXT NOT NULL DEFAULT 'stdio',
    command_or_url TEXT NOT NULL,
    env_vars_encrypted TEXT DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    tools_manifest TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mcp_servers_status ON corporate_mcp_servers(status);

CREATE TABLE IF NOT EXISTS corporate_skill_categories (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_skill_cat_slug ON corporate_skill_categories(slug);

CREATE TABLE IF NOT EXISTS corporate_skills (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category_id TEXT NOT NULL REFERENCES corporate_skill_categories(id),
    description TEXT,
    folder_path TEXT NOT NULL,
    manifest_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_skills_category ON corporate_skills(category_id);

CREATE VIRTUAL TABLE IF NOT EXISTS corporate_skills_fts USING fts5(
    skill_id UNINDEXED,
    name,
    description,
    content
);
"""

DEFAULT_SKILL_CATEGORIES = [
    {
        "id": "cat_frontend",
        "name": "Frontend Development",
        "slug": "frontend",
        "description": "UI, Next.js, React, Tailwind, Flutter, Mobile UI patterns",
    },
    {
        "id": "cat_backend",
        "name": "Backend & API",
        "slug": "backend",
        "description": "FastAPI, Node.js, Microservices, REST, GraphQL, and business logic",
    },
    {
        "id": "cat_devops",
        "name": "DevOps & Cloud",
        "slug": "devops",
        "description": "Docker, CI/CD, Kubernetes, Terraform, and Cloud Infrastructure",
    },
    {
        "id": "cat_database",
        "name": "Database & Storage",
        "slug": "database",
        "description": "PostgreSQL, SQLite, Redis, Migrations, ORM, and Data Modeling",
    },
    {
        "id": "cat_security",
        "name": "Security & Auth",
        "slug": "security",
        "description": "JWT, RBAC, OAuth2, Cryptography, AST validation, and Pentesting",
    },
    {
        "id": "cat_architecture",
        "name": "Software Architecture",
        "slug": "architecture",
        "description": "Design Patterns, Clean Architecture, DDD, Event-Driven Systems",
    },
    {
        "id": "cat_business",
        "name": "Business & Management",
        "slug": "business",
        "description": "Product Strategy, OKRs, Requirements, and Startup Operations",
    },
]
