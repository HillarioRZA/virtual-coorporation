/**
 * API & Event Streaming TypeScript Contracts
 * Single Source of Truth diselaraskan dengan backend FastAPI & SQLite Blackboard.
 */

export type StageName =
  | "SPARRING_ROOM"
  | "GATE_1_WAITING"
  | "PRD_AND_SPECS"
  | "MOCK_PROTOTYPING"
  | "GATE_2_WAITING"
  | "PRODUCTION_HARDENING"
  | "GATE_3_WAITING"
  | "DEPLOY_LIVE"
  | "LIVE_OBSERVABILITY"
  | "PROJECT_KILLED";

export type GateDecision = "APPROVE" | "REVISE" | "KILL";

export interface ProjectSummary {
  project_id: string;
  name: string;
  stage: StageName;
  archetype_id: number;
  tokens_cost: number;
  gross_revenue: number;
  net_profit: number;
  status: "ACTIVE" | "ARCHIVED" | "KILLED";
}

export interface GateDecisionPayload {
  action: GateDecision;
  feedback?: string;
}

export interface SSETokenPayload {
  sender_role: string;
  recipient_role?: string;
  token: string;
  is_first?: boolean;
}

export interface SSEStateChangePayload {
  from_stage: StageName;
  to_stage: StageName;
  action?: string;
  gate_id?: string;
  timestamp?: string;
}

export interface SSEPreviewReadyPayload {
  url: string;
  port: number;
}

export interface BusinessBriefData {
  target_user: string;
  core_pain_point: string;
  unique_value_proposition: string;
  monetization_model: string;
  kill_switch_triggers: string[];
  market_feasibility_score: number;
}

export interface SystemArchitectureData {
  stack_selection: {
    frontend: string;
    backend: string;
    database: string;
    auth?: string;
  };
  key_modules: Array<{
    name: string;
    responsibility: string;
    complexity: string;
  }>;
  risk_mitigation: string[];
  simulated_cloud_cost_monthly: number;
}

export interface VentureStateData {
  project_id: string;
  project_name: string;
  stage: StageName;
  founder_idea: string;
  selected_archetype: number;
  business_brief?: BusinessBriefData;
  system_architecture?: SystemArchitectureData;
  prd_spec?: Record<string, any>;
  openapi_spec?: Record<string, any>;
  ui_spec?: Record<string, any>;
  preview_url?: string;
  gate_decision?: string;
  gate_feedback?: string;
  token_usage?: Record<string, number>;
  event_logs?: string[];
}

export interface ApiResponse<T> {
  status: "success" | "error" | "queued";
  data?: T;
  message?: string;
  details?: any;
}

export interface RoleSetting {
  title: string;
  desc: string;
  model: string;
  provider: string;
}

export interface ProviderSetting {
  key: string;
  base_url: string;
  is_set: boolean;
  model?: string;
}

export interface SystemConfig {
  app_env: string;
  backend_host: string;
  backend_port: number;
  frontend_port: number;
  database_url: string;
}

export interface PaaSConfig {
  provider: string;
  api_url: string;
  api_token: string;
  is_token_set: boolean;
}

export interface SandboxConfig {
  domain_suffix: string;
  caddy_admin_api: string;
  frontend_image: string;
  backend_image: string;
}

export interface TelegramConfig {
  auth_gate_enabled: boolean;
  bot_token: string;
  is_token_set: boolean;
  chat_id: string;
  rotation_hours: number;
}

export interface AuthStatusData {
  is_enabled: boolean;
  is_authenticated: boolean;
  expires_at?: string | null;
  rotation_hours: number;
}

export interface SystemSettingsData {
  roles: Record<string, RoleSetting>;
  providers: Record<string, ProviderSetting>;
  system: SystemConfig;
  paas: PaaSConfig;
  sandbox: SandboxConfig;
  telegram?: TelegramConfig;
  available_providers: string[];
  recommended_models: Record<string, string[]>;
}


