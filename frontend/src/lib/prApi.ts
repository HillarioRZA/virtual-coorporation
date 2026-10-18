/**
 * API Client Library untuk Autonomous Pull Requests & Peer Reviews.
 * Terhubung ke endpoint FastAPI /api/v1/pull-requests/*.
 */

import { getApiV1Base } from "./config";
import {
  PullRequestResponse,
  CreatePRRequestPayload,
  ReviewVerdict,
  PRReviewItem,
} from "./types/pullRequest";

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

/** Mengambil daftar Pull Request milik suatu proyek */
export async function fetchProjectPRs(projectId: string, status?: string): Promise<PullRequestResponse[]> {
  const url = new URL(`${API_BASE}/pull-requests/project/${projectId}`);
  if (status) url.searchParams.append("status", status);

  const res = await fetch(url.toString(), {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal mengambil daftar PR: HTTP ${res.status}`);
  }
  return res.json();
}

/** Mengambil detail Pull Request beserta catatan review */
export async function fetchPRDetail(prId: string): Promise<PullRequestResponse> {
  const res = await fetch(`${API_BASE}/pull-requests/${prId}`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal mengambil detail PR: HTTP ${res.status}`);
  }
  return res.json();
}

/** Membuka Pull Request baru */
export async function createPullRequest(payload: CreatePRRequestPayload): Promise<PullRequestResponse> {
  const res = await fetch(`${API_BASE}/pull-requests`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Gagal membuka PR: HTTP ${res.status}`);
  }
  return res.json();
}

/** Memicu siklus peer review otonom (QA + CTO + Peer) */
export async function triggerAutonomousReview(prId: string): Promise<{ pr: PullRequestResponse; reviews: PRReviewItem[]; quorum_reached: boolean }> {
  const res = await fetch(`${API_BASE}/pull-requests/${prId}/auto-review`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error(`Gagal menjalankan peer review: HTTP ${res.status}`);
  }
  return res.json();
}

/** Menggabungkan (merge) Pull Request ke branch target */
export async function mergePullRequest(prId: string, force: boolean = false): Promise<{ status: string; pr: PullRequestResponse }> {
  const res = await fetch(`${API_BASE}/pull-requests/${prId}/merge?force=${force}`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Gagal me-merge PR: HTTP ${res.status}`);
  }
  return res.json();
}
