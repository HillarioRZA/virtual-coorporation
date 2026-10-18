/**
 * TypeScript Contracts untuk Autonomous Peer-to-Peer Code Review & Git PR Engine.
 * Diselaraskan dengan pull_requests.py dan pr_repo.py.
 */

export type PRStatus = "OPEN" | "CHANGES_REQUESTED" | "APPROVED" | "MERGED" | "CLOSED";
export type ReviewVerdict = "APPROVED" | "CHANGES_REQUESTED" | "COMMENT";

export interface PRFileItem {
  path: string;
  status: "ADDED" | "MODIFIED" | "DELETED";
  additions: number;
  deletions: number;
}

export interface PRInlineComment {
  file_path: string;
  line_number: number;
  comment: string;
  code_suggestion?: string;
}

export interface PRReviewItem {
  id: string;
  pr_id: string;
  reviewer_role_id: string;
  reviewer_name: string;
  verdict: ReviewVerdict;
  summary: string;
  inline_comments: PRInlineComment[];
  security_score: number;
  created_at: string;
}

export interface PullRequestResponse {
  id: string;
  project_id: string;
  ticket_id?: string | null;
  title: string;
  description: string;
  source_branch: string;
  target_branch: string;
  author_role_id: string;
  status: PRStatus;
  files: PRFileItem[];
  diff_unified: string;
  additions_count: number;
  deletions_count: number;
  quorum_required: number;
  approvals_count: number;
  created_at: string;
  updated_at: string;
  reviews?: PRReviewItem[];
}

export interface CreatePRRequestPayload {
  project_id: string;
  ticket_id?: string;
  title: string;
  description?: string;
  source_branch: string;
  author_role_id: string;
  target_branch?: string;
  files_delta: Array<{ path: string; old_content: string; new_content: string }>;
  quorum_required?: number;
}
