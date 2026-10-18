/**
 * Executive Governance & CEO Control Tower API Client.
 * Menyediakan pemanggilan HTTP ke backend FastAPI /api/v1/governance/*.
 */

import {
  CircuitBreakerOverrideRequest,
  CircuitBreakerStatus,
  ExecutiveDecisionRequest,
  ExecutiveEscalationReport,
} from "./types/corporate";
import { getApiV1Base } from "./config";

const API_BASE = getApiV1Base();

function getAuthHeaders(customHeaders: Record<string, string> = {}): Record<string, string> {
  const headers = { ...customHeaders };
  if (typeof window !== "undefined") {
    const token = sessionStorage.getItem("venture_session_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  return headers;
}

/**
 * Mengambil status loop circuit breaker pada tiket tertentu.
 */
export async function fetchCircuitBreakerStatus(
  ticketId: string,
  projectId: string = ""
): Promise<CircuitBreakerStatus> {
  const res = await fetch(
    `${API_BASE}/governance/status/${encodeURIComponent(ticketId)}?project_id=${encodeURIComponent(projectId)}`,
    {
      headers: getAuthHeaders(),
      cache: "no-store",
    }
  );
  if (!res.ok) {
    throw new Error("Gagal mengambil status circuit breaker.");
  }
  return await res.json();
}

/**
 * Mengeksekusi manual override hak veto CEO atas tiket yang terblokir.
 */
export async function executeCeoOverride(payload: {
  ticket_id: string;
  project_id: string;
  branch_id?: string;
  override: CircuitBreakerOverrideRequest;
}): Promise<{ status: string; action: string; ticket: any }> {
  const res = await fetch(`${API_BASE}/governance/override`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      ticket_id: payload.ticket_id,
      project_id: payload.project_id,
      branch_id: payload.branch_id || "branch_main",
      override: payload.override,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal mengeksekusi override CEO.");
  }
  return await res.json();
}

/**
 * Mengirimkan keputusan 1-klik CEO atas opsi eskalasi direksi.
 */
export async function submitCeoDecision(payload: {
  report_id: string;
  project_id: string;
  branch_id?: string;
  decision: ExecutiveDecisionRequest;
}): Promise<{ status: string; report_id: string; selected_option: string }> {
  const res = await fetch(`${API_BASE}/governance/decision`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      report_id: payload.report_id,
      project_id: payload.project_id,
      branch_id: payload.branch_id || "branch_main",
      decision: payload.decision,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal menerapkan keputusan CEO.");
  }
  return await res.json();
}
