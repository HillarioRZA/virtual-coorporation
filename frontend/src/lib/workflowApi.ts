/**
 * API Client Library untuk Workflow Multi-Pipeline & Stage Reordering.
 * Menyediakan metode komunikasi ke backend FastAPI /api/v1/corporate/branches/{branch_id}/pipeline(s).
 */

import {
  PipelineCreate,
  PipelineResponse,
  PipelineStageItem,
  PipelineStageResponse,
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
 * Mengambil daftar seluruh pipeline alur kerja (Software, Edukasi, Copywriting, dll) pada branch.
 */
export async function fetchPipelines(branchId: string): Promise<PipelineResponse[]> {
  const res = await fetch(`${API_BASE}/corporate/branches/${encodeURIComponent(branchId)}/pipelines`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal mengambil daftar pipeline.");
  }
  return await res.json();
}

/**
 * Membuat pipeline baru untuk lini produk tertentu.
 */
export async function createPipeline(
  branchId: string,
  payload: PipelineCreate
): Promise<PipelineResponse> {
  const res = await fetch(`${API_BASE}/corporate/branches/${encodeURIComponent(branchId)}/pipelines`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal membuat pipeline baru.");
  }
  return await res.json();
}

/**
 * Menghapus pipeline produk kustom dari branch.
 */
export async function deletePipeline(
  branchId: string,
  pipelineId: string
): Promise<{ status: string; message: string }> {
  const res = await fetch(
    `${API_BASE}/corporate/branches/${encodeURIComponent(branchId)}/pipelines/${encodeURIComponent(pipelineId)}`,
    {
      method: "DELETE",
      headers: getAuthHeaders(),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal menghapus pipeline.");
  }
  return await res.json();
}

/**
 * Mengambil urutan tahapan sekuensial peran & gerbang CEO pada pipeline branch tertentu.
 */
export async function fetchWorkflowPipeline(
  branchId: string,
  pipelineId?: string
): Promise<PipelineStageResponse[]> {
  const query = pipelineId ? `?pipeline_id=${encodeURIComponent(pipelineId)}` : "";
  const res = await fetch(
    `${API_BASE}/corporate/branches/${encodeURIComponent(branchId)}/pipeline${query}`,
    {
      headers: getAuthHeaders(),
      cache: "no-store",
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Gagal mengambil alur kerja: ${res.statusText}`);
  }
  return await res.json();
}

/**
 * Menyimpan seluruh konfigurasi rantai tahapan alur kerja untuk pipeline target.
 */
export async function saveWorkflowPipelineStages(
  branchId: string,
  stages: PipelineStageItem[],
  pipelineId?: string
): Promise<PipelineStageResponse[]> {
  const query = pipelineId ? `?pipeline_id=${encodeURIComponent(pipelineId)}` : "";
  const res = await fetch(
    `${API_BASE}/corporate/branches/${encodeURIComponent(branchId)}/pipeline${query}`,
    {
      method: "PUT",
      headers: getAuthHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ pipeline_id: pipelineId, stages }),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal menyimpan konfigurasi tahapan alur kerja.");
  }
  return await res.json();
}

/**
 * Mereset alur kerja branch eksperimen kembali ke alur kanonikal resmi.
 */
export async function resetWorkflowPipeline(
  branchId: string,
  pipelineId?: string
): Promise<PipelineStageResponse[]> {
  const query = pipelineId ? `?pipeline_id=${encodeURIComponent(pipelineId)}` : "";
  const res = await fetch(
    `${API_BASE}/corporate/branches/${encodeURIComponent(branchId)}/pipeline/reset${query}`,
    {
      method: "POST",
      headers: getAuthHeaders(),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal mereset alur kerja.");
  }
  return await res.json();
}

/**
 * Menyusun ulang urutan divisi dalam branch organisasi.
 */
export async function reorderDivisions(
  branchId: string,
  orderedDivisionIds: string[]
): Promise<{ status: string; message: string }> {
  const res = await fetch(
    `${API_BASE}/corporate/branches/${encodeURIComponent(branchId)}/reorder-divisions`,
    {
      method: "PUT",
      headers: getAuthHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ ordered_division_ids: orderedDivisionIds }),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal memperbarui urutan divisi.");
  }
  return await res.json();
}
