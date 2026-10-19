/**
 * TypeScript Contracts untuk Registri Korporat & Git-Style Workflow Branching.
 * Diselaraskan dengan DTO Pydantic backend (corporate_schemas.py & workflow_schemas.py).
 */
import { FallbackChannelConfig } from "./analytics";

export interface BranchResponse {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  is_active_main: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface BranchCreate {
  name: string;
  slug: string;
  description?: string;
}

export interface BranchForkRequest {
  name: string;
  slug: string;
  description?: string;
  source_branch_id: string;
}

export interface DivisionResponse {
  id: string;
  branch_id: string;
  name: string;
  slug: string;
  description?: string | null;
  accent_color: string;
  icon_name: string;
  is_system_default: boolean;
  order_index?: number;
  roles_count?: number;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface DivisionCreate {
  branch_id: string;
  name: string;
  slug: string;
  description?: string;
  accent_color?: string;
  icon_name?: string;
}

export interface DivisionUpdate {
  name?: string;
  description?: string;
  accent_color?: string;
  icon_name?: string;
}

export type ThinkingLevel = "none" | "low" | "medium" | "high";

export interface RoleResponse {
  id: string;
  branch_id: string;
  division_id: string;
  name: string;
  job_description?: string;
  system_prompt_template: string;
  model_provider: string;
  model_name: string;
  temperature: number;
  tool_permissions: string[];
  token_budget_per_task: number;
  is_active: boolean;
  is_system_default: boolean;
  order_index?: number;
  fallback_chain?: FallbackChannelConfig[];
  thinking_level?: ThinkingLevel;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface RoleCreate {
  branch_id: string;
  division_id: string;
  name: string;
  job_description?: string;
  system_prompt_template: string;
  model_provider?: string;
  model_name?: string;
  temperature?: number;
  tool_permissions?: string[];
  token_budget_per_task?: number;
  is_active?: boolean;
  fallback_chain?: FallbackChannelConfig[];
  thinking_level?: ThinkingLevel;
}

export interface RoleUpdate {
  division_id?: string;
  name?: string;
  job_description?: string;
  system_prompt_template?: string;
  model_provider?: string;
  model_name?: string;
  temperature?: number;
  tool_permissions?: string[];
  token_budget_per_task?: number;
  is_active?: boolean;
  fallback_chain?: FallbackChannelConfig[];
  thinking_level?: ThinkingLevel;
}

export type ProductLineType = "SOFTWARE" | "EDUCATION" | "COPYWRITING" | "MARKET_RESEARCH" | "CUSTOM" | string;

export interface PipelineCreate {
  name: string;
  slug: string;
  product_line?: ProductLineType;
  description?: string;
}

export interface PipelineResponse {
  id: string;
  branch_id: string;
  name: string;
  slug: string;
  product_line: ProductLineType;
  description?: string | null;
  is_default: boolean;
  stages_count: number;
  created_at?: string | null;
  updated_at?: string | null;
}

export type StageType = "ROLE_EXECUTION" | "CEO_GATE";
export type CeoGateType = "APPROVAL_GATE" | "STRATEGIC_MEETING" | "DIRECTION_INPUT";

export interface PipelineStageItem {
  id?: string;
  pipeline_id?: string;
  stage_index: number;
  order_index?: number;
  stage_type: StageType;
  role_id?: string | null;
  role_name?: string | null;
  role_slug?: string | null;
  division_id?: string | null;
  division_name?: string | null;
  division_color?: string | null;
  model_name?: string | null;
  ceo_gate_type?: CeoGateType | null;
  custom_label?: string | null;
  custom_instructions?: string | null;
  is_active?: boolean;
  is_system_default?: boolean;
}

export type PipelineStageResponse = PipelineStageItem;

export interface SavePipelineStagesRequest { pipeline_id?: string; stages: PipelineStageItem[]; }
export interface ReorderPipelineRequest { ordered_role_ids: string[]; }
export interface ReorderDivisionsRequest { ordered_division_ids: string[]; }

export interface CircuitBreakerStatus {
  ticket_id: string;
  project_id: string;
  turn_count: number;
  is_blocked: boolean;
  reason?: string | null;
}

export interface CircuitBreakerOverrideRequest {
  action: "FORCE_PROCEED" | "INTERVENE" | "REASSIGN";
  directive?: string;
  target_role_id?: string;
}

export interface ExecutiveEscalationOption {
  option_id: string;
  label: string;
  impact: string;
}

export interface ExecutiveEscalationReport {
  id?: string;
  project_id: string;
  reporter_role: string;
  title: string;
  summary: string;
  options: ExecutiveEscalationOption[];
  urgency: "NORMAL" | "HIGH" | "CRITICAL";
  selected_option_id?: string | null;
}

export interface ExecutiveDecisionRequest {
  selected_option_id: string;
  feedback?: string;
}
