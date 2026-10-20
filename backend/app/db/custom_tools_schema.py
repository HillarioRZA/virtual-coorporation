"""
Skema DDL Basis Data SQLite untuk Tabel corporate_custom_tools.
Menyimpan perkakas sintesis dinamis yang dibuat agen beserta status approval dan kodenya.
"""

CUSTOM_TOOLS_DDL_SCHEMA = """
CREATE TABLE IF NOT EXISTS corporate_custom_tools (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    parameters_schema TEXT,
    python_code TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING_APPROVAL',
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_custom_tools_status ON corporate_custom_tools(status);
"""
