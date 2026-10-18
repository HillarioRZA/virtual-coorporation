/**
 * API Client Library untuk Autonomous Three-Way Branch Merge.
 * Berkomunikasi dengan endpoint /api/v1/corporate/branches/merge-preview dan /merge.
 */

import { getApiV1Base } from "./config";
import {
  MergeStrategy,
  MergePreviewResponse,
  MergeExecuteResponse,
} from "./types/branchMerge";

const API_BASE = getApiV1Base();

function getAuthHeaders(customHeaders: Record<string, string> = {}): Record<string, string> {
  const headers: Record<string, string> = { "Content-Type": "application/json", ...customHeaders };
  if (typeof window !== "undefined") {
    const token = sessionStorage.getItem("venture_session_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  return headers;
}

/**
 * Melakukan simulasi preview 3-way merge untuk mendeteksi Fast-Forward atau konflik konfigurasi.
 */
export async function previewBranchMerge(
  sourceBranchId: string,
  targetBranchId: string = "branch_main",
  strategy: MergeStrategy = "auto"
): Promise<MergePreviewResponse> {
  const res = await fetch(`${API_BASE}/corporate/branches/merge-preview`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      source_branch_id: sourceBranchId,
      target_branch_id: targetBranchId,
      strategy,
    }),
    cache: "no-store",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal melakukan simulasi merge cabang.");
  }
  return await res.json();
}

/**
 * Mengeksekusi penggabungan cabang alur kerja secara atomik.
 */
export async function executeBranchMerge(
  sourceBranchId: string,
  targetBranchId: string = "branch_main",
  strategy: MergeStrategy = "auto"
): Promise<MergeExecuteResponse> {
  const res = await fetch(`${API_BASE}/corporate/branches/merge`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      source_branch_id: sourceBranchId,
      target_branch_id: targetBranchId,
      strategy,
    }),
    cache: "no-store",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal mengeksekusi merge alur kerja.");
  }
  return await res.json();
}
