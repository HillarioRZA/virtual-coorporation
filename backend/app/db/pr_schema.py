"""SQLite DDL Schema untuk Autonomous Peer-to-Peer PR Review Engine.

Menyimpan metadata Pull Request internal, status kuorum persetujuan,
rekaman Git-style unified diff, dan tinjauan rekanan antar-karyawan AI.
"""

PR_DDL_SCHEMA = """
-- 1. Tabel Pull Requests Internal
CREATE TABLE IF NOT EXISTS corporate_pull_requests (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    ticket_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    source_branch TEXT NOT NULL,
    target_branch TEXT NOT NULL DEFAULT 'branch_main',
    author_role_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN', -- OPEN, CHANGES_REQUESTED, APPROVED, MERGED, CLOSED
    files_changed_json TEXT NOT NULL DEFAULT '[]',
    diff_unified TEXT NOT NULL DEFAULT '',
    additions_count INTEGER NOT NULL DEFAULT 0,
    deletions_count INTEGER NOT NULL DEFAULT 0,
    quorum_required INTEGER NOT NULL DEFAULT 2,
    approvals_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cpr_project ON corporate_pull_requests(project_id);
CREATE INDEX IF NOT EXISTS idx_cpr_status ON corporate_pull_requests(status);
CREATE INDEX IF NOT EXISTS idx_cpr_ticket ON corporate_pull_requests(ticket_id);

-- 2. Tabel Tinjauan Kode Rekanan (Peer Reviews)
CREATE TABLE IF NOT EXISTS corporate_pr_reviews (
    id TEXT PRIMARY KEY,
    pr_id TEXT NOT NULL,
    reviewer_role_id TEXT NOT NULL,
    reviewer_name TEXT NOT NULL,
    verdict TEXT NOT NULL, -- APPROVED, CHANGES_REQUESTED, COMMENT
    summary TEXT NOT NULL,
    inline_comments_json TEXT NOT NULL DEFAULT '[]',
    security_score INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pr_id) REFERENCES corporate_pull_requests(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cpr_rev_pr ON corporate_pr_reviews(pr_id);
CREATE INDEX IF NOT EXISTS idx_cpr_rev_role ON corporate_pr_reviews(reviewer_role_id);
"""
