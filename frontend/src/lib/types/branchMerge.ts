export type MergeStrategy = "auto" | "prefer_theirs" | "prefer_ours";

export interface MergeConflictItem {
  entity: string;
  slug: string;
  ours: {
    model?: string;
    temp?: number;
  };
  theirs: {
    model?: string;
    temp?: number;
  };
}

export interface MergePreviewResponse {
  source_branch_id: string;
  target_branch_id: string;
  lca_branch_id: string;
  can_fast_forward: boolean;
  added_roles: Array<{ slug: string; name: string; model_name: string }>;
  updated_roles: Array<{ slug: string; field: string; from: string; to: string }>;
  new_stages_count: number;
  conflicts: MergeConflictItem[];
  has_conflicts: boolean;
  strategy: MergeStrategy;
}

export interface MergeExecuteResponse {
  status: string;
  source_branch_id: string;
  target_branch_id: string;
  added_roles_count: number;
  updated_roles_count: number;
  strategy: MergeStrategy;
}
