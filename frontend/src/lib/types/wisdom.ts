/**
 * TypeScript Interfaces untuk Corporate Wisdom Base & Vector Memory (Sprint 3.3).
 */

export type WisdomNamespace =
  | "wisdom:architecture"
  | "wisdom:bugs_and_fixes"
  | "wisdom:growth_copy";

export interface WisdomItem {
  id: string;
  namespace: string;
  title: string;
  problem_pattern: string;
  solution_guideline: string;
  tags: string[];
  source_venture_id: string;
  source_pr_id?: string | null;
  relevance_score?: number;
  usage_count: number;
  created_at: string;
  updated_at?: string;
  similarity_score?: number;
}

export interface WisdomCreate {
  namespace: string;
  title: string;
  problem_pattern: string;
  solution_guideline: string;
  tags: string[];
  source_venture_id?: string;
}

export interface WisdomSearchQuery {
  query: string;
  namespace?: string;
  target_role?: string;
  top_k?: number;
  min_similarity?: number;
}

export interface WisdomSummary {
  total_count: number;
  namespace_breakdown: Record<string, number>;
  top_reused_wisdom: WisdomItem[];
}
