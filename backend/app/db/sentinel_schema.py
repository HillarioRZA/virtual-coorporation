"""
Skema Database Sentinel Audit Trail untuk Internal CoV Gatekeeper.
Mencatat seluruh telemetri inspeksi pre-flight, status approval/repair, dan diff parameter.
"""

SENTINEL_DDL_SCHEMA = """
CREATE TABLE IF NOT EXISTS sentinel_audit_logs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    agent_role TEXT NOT NULL,
    status TEXT NOT NULL, -- 'APPROVED', 'REPAIRED', 'REJECTED'
    tool_name TEXT,
    tool_parameters TEXT,
    original_content TEXT,
    inspected_content TEXT,
    repair_feedback TEXT,
    repairs_count INTEGER DEFAULT 0,
    latency_ms REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sentinel_project_created ON sentinel_audit_logs(project_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sentinel_role ON sentinel_audit_logs(agent_role);
"""
