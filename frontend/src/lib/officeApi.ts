/**
 * HTTP Client and WebSocket URL Resolver for Global Oasis Live Command HQ.
 * Provides APIs for office state, scoped agent interventions, and ticket controls.
 */

import { getApiV1Base, getWsBase } from "./config";
import { AgentSpatialData, OfficeDirectivePayload } from "./types/office";

const API_BASE = getApiV1Base();

function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (typeof window !== "undefined") {
    const token = sessionStorage.getItem("auth_token") || localStorage.getItem("auth_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  return headers;
}

export async function fetchOfficeState(
  projectId: string
): Promise<{ layout?: Record<string, unknown>; agents: AgentSpatialData[] }> {
  const res = await fetch(`${API_BASE}/corporate/office/state/${projectId}`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal memuat state kantor (${res.status})`);
  }
  return res.json();
}

export async function interveneOfficeAgent(
  roleId: string,
  instruction: string
): Promise<{ status: string; role_id: string; agent: AgentSpatialData }> {
  const res = await fetch(`${API_BASE}/corporate/office/intervene`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ role_id: roleId, instruction }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Gagal intervensi agen (${res.status})`);
  }
  return res.json();
}

export async function dispatchOfficeDirective(
  payload: OfficeDirectivePayload
): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/corporate/office/directive`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal mengirim arahan");
  }
  return res.json();
}

export async function holdOfficeTicket(
  projectId: string,
  ticketId: string
): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/governance/circuit-breaker/trip`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ project_id: projectId, reason: `CEO Manual Hold on ${ticketId}` }),
  }).catch(() => null);

  return { status: res && res.ok ? "SUCCESS" : "LOCAL_HOLD" };
}


export function getOfficeWsUrl(projectId: string): string {
  const wsBase = getWsBase();
  return `${wsBase}/corporate/ws/office/${projectId}`;
}
