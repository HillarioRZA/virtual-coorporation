"""
Skema DDL Basis Data SQLite untuk Corporate Wisdom Base & Vector Memory.
Mencatat memori institusional jangka panjang lintas-venture dan representasi vektor.
"""

WISDOM_DDL_SCHEMA = """
-- Tabel memori institusional korporat (Corporate Wisdom Base)
CREATE TABLE IF NOT EXISTS corporate_wisdom (
    id TEXT PRIMARY KEY,
    namespace TEXT NOT NULL,
    title TEXT NOT NULL,
    problem_pattern TEXT NOT NULL,
    solution_guideline TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',
    embedding TEXT NOT NULL DEFAULT '[]',
    source_venture_id TEXT NOT NULL DEFAULT 'global',
    source_pr_id TEXT DEFAULT NULL,
    relevance_score REAL NOT NULL DEFAULT 1.0,
    usage_count INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indeks performa pencarian filter dan namespace
CREATE INDEX IF NOT EXISTS idx_wisdom_namespace ON corporate_wisdom(namespace);
CREATE INDEX IF NOT EXISTS idx_wisdom_active ON corporate_wisdom(is_active);
CREATE INDEX IF NOT EXISTS idx_wisdom_source ON corporate_wisdom(source_venture_id);
"""
