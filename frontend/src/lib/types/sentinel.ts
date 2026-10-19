/**
 * Types & Data Contracts for Internal CoV Sentinel Observability Dashboard
 */

export interface SentinelAuditLog {
  id: string;
  project_id: string;
  agent_role: string;
  status: "APPROVED" | "REPAIRED" | "REJECTED";
  tool_name?: string | null;
  tool_parameters?: Record<string, any> | null;
  original_content: string;
  inspected_content: string;
  repair_feedback?: string | null;
  repairs_count: number;
  latency_ms: number;
  created_at?: string;
}

export interface SentinelStats {
  total_inspections: number;
  approved_count: number;
  repaired_count: number;
  rejected_count: number;
  reliability_rate: number;
  avg_latency_ms: number;
}
