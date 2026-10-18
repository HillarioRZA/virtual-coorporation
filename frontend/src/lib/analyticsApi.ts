/**
 * API Client Library untuk Sovereign Model Router & CFO Token Observability.
 * Menghubungkan dashboard ke endpoint FastAPI /api/v1/analytics/*.
 */

import { getApiV1Base } from "./config";
import {
  TokenUsageSummary,
  BurnRateItem,
  RoleCostItem,
  ChannelHealthItem,
  BudgetCapRequest,
} from "./types/analytics";

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

/** Mengambil ringkasan akumulasi token dan biaya LLM */
export async function fetchTokenSummary(projectId?: string): Promise<TokenUsageSummary> {
  const url = new URL(`${API_BASE}/analytics/token-summary`);
  if (projectId) url.searchParams.append("project_id", projectId);

  const res = await fetch(url.toString(), {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal mengambil token summary: HTTP ${res.status}`);
  }
  return res.json();
}

/** Mengambil timeline burn rate token & biaya per jam */
export async function fetchBurnRate(projectId?: string, limitHours: number = 24): Promise<BurnRateItem[]> {
  const url = new URL(`${API_BASE}/analytics/burn-rate`);
  if (projectId) url.searchParams.append("project_id", projectId);
  url.searchParams.append("limit_hours", limitHours.toString());

  const res = await fetch(url.toString(), {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal mengambil burn rate: HTTP ${res.status}`);
  }
  return res.json();
}

/** Mengambil agregasi token & biaya berdasarkan AI role */
export async function fetchRoleCosts(projectId?: string): Promise<RoleCostItem[]> {
  const url = new URL(`${API_BASE}/analytics/role-costs`);
  if (projectId) url.searchParams.append("project_id", projectId);

  const res = await fetch(url.toString(), {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal mengambil role costs: HTTP ${res.status}`);
  }
  return res.json();
}

/** Mengambil status kesehatan & cooldown saluran router */
export async function fetchChannelHealth(): Promise<ChannelHealthItem[]> {
  const res = await fetch(`${API_BASE}/analytics/channel-health`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal mengambil channel health: HTTP ${res.status}`);
  }
  return res.json();
}

/** Menyimpan batas anggaran finansial proyek (Budget Cap) */
export async function saveBudgetCap(capUsd: number): Promise<{ success: boolean; budget_cap_usd: number }> {
  const payload: BudgetCapRequest = { budget_cap_usd: capUsd };
  const res = await fetch(`${API_BASE}/analytics/budget-cap`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Gagal menyimpan budget cap: HTTP ${res.status}`);
  }
  return res.json();
}
