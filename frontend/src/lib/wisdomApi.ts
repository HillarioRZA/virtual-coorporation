/**
 * API Client Library untuk Corporate Wisdom Base & Vector Memory.
 * Terhubung ke backend FastAPI /api/v1/wisdom/*.
 */

import { getApiV1Base } from "./config";
import {
  WisdomCreate,
  WisdomItem,
  WisdomSearchQuery,
  WisdomSummary,
} from "./types/wisdom";

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

export async function fetchWisdomList(namespace?: string, tag?: string): Promise<WisdomItem[]> {
  const params = new URLSearchParams();
  if (namespace && namespace !== "all") params.append("namespace", namespace);
  if (tag) params.append("tag", tag);

  const url = `${API_BASE}/wisdom${params.toString() ? `?${params.toString()}` : ""}`;
  const res = await fetch(url, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Gagal memuat wisdom list: ${res.statusText}`);
  return await res.json();
}

export async function searchWisdom(payload: WisdomSearchQuery): Promise<WisdomItem[]> {
  const res = await fetch(`${API_BASE}/wisdom/search`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Pencarian semantik wisdom gagal.");
  }
  return await res.json();
}

export async function fetchWisdomSummary(): Promise<WisdomSummary> {
  const res = await fetch(`${API_BASE}/wisdom/summary`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Gagal mengambil summary wisdom.");
  return await res.json();
}

export async function createWisdom(payload: WisdomCreate): Promise<WisdomItem> {
  const res = await fetch(`${API_BASE}/wisdom`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal mencatat wisdom baru.");
  }
  return await res.json();
}

export async function deleteWisdom(wisdomId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/wisdom/${wisdomId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal menghapus wisdom.");
  }
}

export async function importGitHubSkill(githubUrl: string, namespace: string = "wisdom:skills", tags: string[] = []): Promise<any> {
  const res = await fetch(`${API_BASE}/wisdom/import-github`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ github_url: githubUrl, namespace, tags }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal mengimpor skill dari GitHub.");
  }
  return await res.json();
}

export async function importGitHubPlugin(projectId: string, githubUrl: string, toolName?: string): Promise<any> {
  const res = await fetch(`${API_BASE}/wisdom/import-plugin`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ project_id: projectId, github_url: githubUrl, tool_name: toolName }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal mengimpor plugin dari GitHub.");
  }
  return await res.json();
}
