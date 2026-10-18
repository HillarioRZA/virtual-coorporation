/**
 * TypeScript Contracts untuk Sovereign Model Router & CFO Observability Ledger.
 * Diselaraskan dengan analytics.py dan model_router.py.
 */

export interface FallbackChannelConfig {
  channel_name: string;
  model_name: string;
  provider: string;
  api_key_env?: string;
  priority: number;
  rpm_limit: number;
  tpm_limit: number;
  cost_per_million_input: number;
  cost_per_million_output: number;
  is_active: boolean;
}

export interface TokenUsageSummary {
  total_input_tokens: number;
  total_output_tokens: number;
  total_cost_usd: number;
  total_requests: number;
  fallbacks_triggered: number;
  active_budget_cap_usd: number;
}

export interface BurnRateItem {
  time_bucket: string;
  tokens_used: number;
  cost_usd: number;
  request_count: number;
}

export interface RoleCostItem {
  role_id: string;
  role_name?: string;
  total_tokens: number;
  total_cost_usd?: number;
  cost_usd?: number;
  request_count: number;
  fallbacks_count?: number;
  fallback_count?: number;
}

export interface ChannelHealthItem {
  channel_name: string;
  provider: string;
  model_name: string;
  is_cooling_down: boolean;
  cooldown_seconds_left: number;
  current_rpm: number;
  current_tpm: number;
  rpm_limit: number;
  tpm_limit: number;
  status: "HEALTHY" | "RATE_LIMITED" | "DOWN";
}

export interface BudgetCapRequest {
  budget_cap_usd: number;
}
