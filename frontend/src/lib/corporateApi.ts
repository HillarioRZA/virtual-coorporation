/**
 * API Client Library untuk Registri Korporat & Git-Style Workflow Branching.
 * Menyediakan metode komunikasi ke backend FastAPI /api/v1/corporate/*.
 */

import {
  BranchForkRequest,
  BranchResponse,
  DivisionCreate,
  DivisionResponse,
  DivisionUpdate,
  RoleCreate,
  RoleResponse,
  RoleUpdate,
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

// ============================================================================
// 1. BRANCHING APIs
// ============================================================================

export async function fetchBranches(): Promise<BranchResponse[]> {
  const res = await fetch(`${API_BASE}/corporate/branches`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Gagal mengambil branches: ${res.statusText}`);
  return await res.json();
}

export async function fetchActiveBranch(): Promise<BranchResponse> {
  const res = await fetch(`${API_BASE}/corporate/branches/active`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Active branch tidak ditemukan.");
  return await res.json();
}

export async function forkBranch(payload: BranchForkRequest): Promise<BranchResponse> {
  const res = await fetch(`${API_BASE}/corporate/branches/fork`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal melakukan fork workflow.");
  }
  return await res.json();
}

export async function activateBranch(branchId: string): Promise<BranchResponse> {
  const res = await fetch(`${API_BASE}/corporate/branches/${branchId}/activate`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal mengaktifkan branch.");
  }
  return await res.json();
}

export async function deleteBranch(branchId: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/corporate/branches/${branchId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal menghapus branch.");
  }
  return await res.json();
}

// ============================================================================
// 2. DIVISION APIs
// ============================================================================

export async function fetchDivisions(branchId?: string): Promise<DivisionResponse[]> {
  const url = branchId
    ? `${API_BASE}/corporate/divisions?branch_id=${encodeURIComponent(branchId)}`
    : `${API_BASE}/corporate/divisions`;
  const res = await fetch(url, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Gagal mengambil divisi: ${res.statusText}`);
  return await res.json();
}

export async function createDivision(payload: DivisionCreate): Promise<DivisionResponse> {
  const res = await fetch(`${API_BASE}/corporate/divisions`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal membuat divisi baru.");
  }
  return await res.json();
}

export async function updateDivision(divisionId: string, payload: DivisionUpdate): Promise<DivisionResponse> {
  const res = await fetch(`${API_BASE}/corporate/divisions/${divisionId}`, {
    method: "PUT",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal memperbarui divisi.");
  }
  return await res.json();
}

export async function deleteDivision(divisionId: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/corporate/divisions/${divisionId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal menghapus divisi.");
  }
  return await res.json();
}

// ============================================================================
// 3. ROLE APIs
// ============================================================================

export async function fetchRoles(branchId?: string, divisionId?: string): Promise<RoleResponse[]> {
  const params = new URLSearchParams();
  if (branchId) params.append("branch_id", branchId);
  if (divisionId) params.append("division_id", divisionId);
  const url = `${API_BASE}/corporate/roles${params.toString() ? `?${params.toString()}` : ""}`;
  const res = await fetch(url, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Gagal mengambil roles: ${res.statusText}`);
  return await res.json();
}

export async function createRole(payload: RoleCreate): Promise<RoleResponse> {
  const res = await fetch(`${API_BASE}/corporate/roles`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal membuat role agen.");
  }
  return await res.json();
}

export async function updateRole(roleId: string, payload: RoleUpdate): Promise<RoleResponse> {
  const res = await fetch(`${API_BASE}/corporate/roles/${roleId}`, {
    method: "PUT",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal memperbarui role agen.");
  }
  return await res.json();
}

export async function deleteRole(roleId: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/corporate/roles/${roleId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal menghapus role agen.");
  }
  return await res.json();
}
