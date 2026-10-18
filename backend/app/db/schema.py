"""Database Schema Definitions.

Mendefinisikan skema DDL SQLite untuk seluruh tabel basis data Venture Engine:
projek, event logs, state checkpoints, secret vault, system settings, dan corporate hierarchy.
"""

DDL_SCHEMA = """
-- 1. Tabel Proyek Inkubator
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    tagline TEXT,
    stage TEXT NOT NULL DEFAULT 'SPARRING_ROOM',
    archetype_id INTEGER NOT NULL DEFAULT 1,
    founder_idea TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- 2. Tabel Blackboard Event Log (Memory)
CREATE TABLE IF NOT EXISTS agent_event_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    sender_role TEXT NOT NULL,
    recipient_role TEXT NOT NULL,
    event_type TEXT NOT NULL,
    content TEXT NOT NULL,
    artifact_ref TEXT,
    token_cost REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_events_project_stage ON agent_event_logs(project_id, stage);
CREATE INDEX IF NOT EXISTS idx_events_recipient ON agent_event_logs(recipient_role);
-- 3. Tabel Checkpoints (State Serialization)
CREATE TABLE IF NOT EXISTS state_checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    state_blob TEXT NOT NULL,
    step_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
-- 4. Tabel Secret Vault (Kredensial Produksi Terenkripsi)
CREATE TABLE IF NOT EXISTS vault_secrets (
    project_id TEXT NOT NULL,
    secret_key_name TEXT NOT NULL,
    encrypted_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(project_id, secret_key_name),
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
-- 5. Tabel Konfigurasi Sistem Dinamis (Dynamic System Settings)
CREATE TABLE IF NOT EXISTS system_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'general',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- 6. Tabel Branch Organisasi (Git-Style Workflow Branching)
CREATE TABLE IF NOT EXISTS corporate_branches (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active_main BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- 7. Tabel Divisi Korporat Dinamis
CREATE TABLE IF NOT EXISTS corporate_divisions (
    id TEXT PRIMARY KEY,
    branch_id TEXT NOT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    description TEXT,
    accent_color TEXT DEFAULT '#cbd5e1',
    icon_name TEXT DEFAULT 'FolderTree',
    is_system_default BOOLEAN DEFAULT 0,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(branch_id) REFERENCES corporate_branches(id) ON DELETE CASCADE,
    UNIQUE(branch_id, slug)
);

CREATE INDEX IF NOT EXISTS idx_divisions_branch ON corporate_divisions(branch_id);

-- 8. Tabel Role / Agen Dinamis
CREATE TABLE IF NOT EXISTS corporate_roles (
    id TEXT PRIMARY KEY,
    branch_id TEXT NOT NULL,
    division_id TEXT NOT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(branch_id) REFERENCES corporate_branches(id) ON DELETE CASCADE,
    FOREIGN KEY(division_id) REFERENCES corporate_divisions(id) ON DELETE CASCADE,
    UNIQUE(branch_id, slug)
);

CREATE INDEX IF NOT EXISTS idx_roles_branch_division ON corporate_roles(branch_id, division_id);
CREATE INDEX IF NOT EXISTS idx_roles_branch_slug ON corporate_roles(branch_id, slug);

-- 9. Tabel Papan Tiket Otonom (Virtual Kanban)
CREATE TABLE IF NOT EXISTS corporate_tickets (
    id TEXT PRIMARY KEY,
    branch_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    division_id TEXT NOT NULL,
    assigned_role_id TEXT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    product_line TEXT NOT NULL DEFAULT 'SOFTWARE',
    priority TEXT NOT NULL DEFAULT 'MEDIUM',
    status TEXT NOT NULL DEFAULT 'BACKLOG',
    artifact_refs TEXT,
    dependencies TEXT,
    parent_ticket_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(branch_id) REFERENCES corporate_branches(id) ON DELETE CASCADE,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(division_id) REFERENCES corporate_divisions(id) ON DELETE CASCADE,
    FOREIGN KEY(assigned_role_id) REFERENCES corporate_roles(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_tickets_project_status ON corporate_tickets(project_id, status);
CREATE INDEX IF NOT EXISTS idx_tickets_branch ON corporate_tickets(branch_id);

-- 10. Tabel Event Bus Asinkron (Inter-Agent Message Bus)
CREATE TABLE IF NOT EXISTS corporate_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    channel_type TEXT NOT NULL DEFAULT 'LOUNGE',
    sender_role_id TEXT NOT NULL,
    recipient_role_id TEXT,
    ticket_id TEXT,
    event_type TEXT NOT NULL,
    content TEXT NOT NULL,
    token_cost REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(branch_id) REFERENCES corporate_branches(id) ON DELETE CASCADE,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_project_time ON corporate_messages(project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_branch ON corporate_messages(branch_id);

-- 11. Tabel Rantai Sekuensial Tahapan Alur Kerja (Pipeline Stages)
CREATE TABLE IF NOT EXISTS corporate_pipeline_stages (
    id TEXT PRIMARY KEY,
    branch_id TEXT NOT NULL,
    pipeline_id TEXT NOT NULL DEFAULT 'pipe_software_main',
    stage_index INTEGER NOT NULL,
    stage_type TEXT NOT NULL DEFAULT 'ROLE_EXECUTION',
    role_id TEXT,
    ceo_gate_type TEXT,
    custom_label TEXT,
    custom_instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(branch_id) REFERENCES corporate_branches(id) ON DELETE CASCADE,
    FOREIGN KEY(role_id) REFERENCES corporate_roles(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_pipeline_stages_branch ON corporate_pipeline_stages(branch_id, stage_index);

-- 12. Tabel Rantai Alur Kerja Lini Produk (Multi-Pipeline Registry)
CREATE TABLE IF NOT EXISTS corporate_pipelines (
    id TEXT PRIMARY KEY,
    branch_id TEXT NOT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    product_line TEXT NOT NULL DEFAULT 'SOFTWARE',
    description TEXT,
    is_default BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(branch_id) REFERENCES corporate_branches(id) ON DELETE CASCADE,
    UNIQUE(branch_id, slug)
);

CREATE INDEX IF NOT EXISTS idx_pipelines_branch ON corporate_pipelines(branch_id);
"""
