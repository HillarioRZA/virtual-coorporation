"""Database Schema Definitions for Token Ledger & Upstream Channels.

Mendefinisikan skema DDL SQLite untuk observabilitas finansial,
ledger transaksi token per peran, dan status kesehatan kanal upstream model router.
"""

LEDGER_DDL_SCHEMA = """
-- 13. Tabel Pencatatan Token Finansial (Corporate Token Ledger)
CREATE TABLE IF NOT EXISTS corporate_token_ledger (
    id TEXT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    project_id TEXT,
    branch_id TEXT,
    pipeline_id TEXT,
    role_id TEXT,
    model_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    upstream_channel TEXT NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    latency_ms INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT 'SUCCESS',
    is_fallback BOOLEAN DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ledger_project ON corporate_token_ledger(project_id);
CREATE INDEX IF NOT EXISTS idx_ledger_branch ON corporate_token_ledger(branch_id);
CREATE INDEX IF NOT EXISTS idx_ledger_role ON corporate_token_ledger(role_id);
CREATE INDEX IF NOT EXISTS idx_ledger_timestamp ON corporate_token_ledger(timestamp DESC);

-- 14. Tabel Kanal Penyedia Hulu & Pelacak Kesehatan Kuota (Upstream Channels)
CREATE TABLE IF NOT EXISTS upstream_channels (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    model_id TEXT NOT NULL,
    display_name TEXT NOT NULL,
    priority INTEGER DEFAULT 1,
    is_enabled BOOLEAN DEFAULT 1,
    status TEXT DEFAULT 'ACTIVE',
    rpm_limit INTEGER DEFAULT 30,
    tpm_limit INTEGER DEFAULT 60000,
    rpd_limit INTEGER DEFAULT 1000,
    cooldown_until TIMESTAMP,
    failure_count INTEGER DEFAULT 0,
    total_requests INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_channels_provider ON upstream_channels(provider, model_id);
"""
