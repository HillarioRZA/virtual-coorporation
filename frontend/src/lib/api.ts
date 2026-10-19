/**
 * API Client Library untuk Backend FastAPI.
 */

import {
  ApiResponse,
  GateDecisionPayload,
  ProjectSummary,
  SystemSettingsData,
  VentureStateData,
} from "./types/api";
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

export async function fetchProjects(): Promise<ProjectSummary[]> {
  const res = await fetch(`${API_BASE}/projects`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal mengambil proyek: ${res.statusText}`);
  }
  const body: ApiResponse<ProjectSummary[]> = await res.json();
  return body.data || [];
}

export async function fetchProject(projectId: string): Promise<VentureStateData> {
  const res = await fetch(`${API_BASE}/projects/${projectId}`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal mengambil detail proyek: ${res.statusText}`);
  }
  const body: ApiResponse<VentureStateData> = await res.json();
  if (!body.data) throw new Error("Data proyek kosong");
  return body.data;
}

export async function createProject(payload: {
  name: string;
  founder_idea: string;
  archetype_id?: number;
}): Promise<{ project_id: string; name: string; stage: string }> {
  const res = await fetch(`${API_BASE}/projects`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.message || `Gagal membuat proyek: ${res.status}`);
  }
  const body = await res.json();
  return body.data;
}

export async function deleteProject(projectId: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/projects/${projectId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || errorBody.message || `Gagal menghapus proyek: ${res.status}`);
  }
  return res.json();
}

export async function postSparringChat(
  projectId: string,
  payload: { message: string; target_agent?: string; attachments?: any[] }
): Promise<void> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/sparring/chat`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Gagal mengirim chat sparring: ${res.statusText}`);
  }
}

export async function postGateDecision(
  projectId: string,
  gateId: string,
  payload: GateDecisionPayload
): Promise<any> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/gates/${gateId}/decision`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`Gagal mengirim keputusan gate: ${res.statusText}`);
  }
  return await res.json();
}

export async function fetchPreviewStatus(projectId: string): Promise<{
  is_running: boolean;
  port: number;
  preview_url: string;
  uptime_seconds: number;
}> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/preview/status`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal memeriksa status preview: ${res.statusText}`);
  }
  const body = await res.json();
  return body.data;
}

export async function fetchVaultSecrets(projectId: string): Promise<string[]> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/vault/secrets`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal membaca vault secrets: ${res.statusText}`);
  }
  const body = await res.json();
  return body.data?.keys || [];
}

export async function storeVaultSecrets(
  projectId: string,
  secrets: Record<string, string>
): Promise<void> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/vault/secrets`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ secrets }),
  });
  if (!res.ok) {
    throw new Error(`Gagal menyimpan kredensial ke vault: ${res.statusText}`);
  }
}

export async function fetchSystemSettings(): Promise<SystemSettingsData> {
  const res = await fetch(`${API_BASE}/settings`, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal memuat pengaturan sistem: ${res.statusText}`);
  }
  const body = await res.json();
  return body.data;
}

export async function updateSystemSettings(
  updates: Record<string, any>
): Promise<{ status: string; message: string; data: SystemSettingsData }> {
  const res = await fetch(`${API_BASE}/settings`, {
    method: "PUT",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ updates }),
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Gagal memperbarui pengaturan: ${res.statusText}`);
  }
  return await res.json();
}

export async function resetSystemSettings(): Promise<{ status: string; message: string; data: SystemSettingsData }> {
  const res = await fetch(`${API_BASE}/settings/reset`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Gagal mereset pengaturan: ${res.statusText}`);
  }
  return await res.json();
}

export async function fetchAuthStatus(token?: string | null): Promise<{
  is_enabled: boolean;
  is_authenticated: boolean;
  expires_at?: string | null;
  rotation_hours: number;
}> {
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}/auth/status`, {
    headers,
    cache: "no-store",
  });
  if (!res.ok) {
    return { is_enabled: false, is_authenticated: true, rotation_hours: 6 };
  }
  const body = await res.json();
  return body.data;
}

export async function verifyAuthPassword(password: string): Promise<{ session_token: string; expires_at?: string }> {
  const res = await fetch(`${API_BASE}/auth/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });
  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}));
    throw new Error(errBody.detail || "Kode akses tidak valid atau telah kedaluwarsa.");
  }
  const body = await res.json();
  return body.data;
}

export async function resendAuthPassword(): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/auth/resend`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}));
    throw new Error(errBody.detail || "Gagal mengirim ulang kode.");
  }
  return await res.json();
}

export async function rotateAuthPassword(): Promise<{ status: string; message: string; data?: any }> {
  const res = await fetch(`${API_BASE}/auth/rotate`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}));
    throw new Error(errBody.detail || "Gagal merotasi kode baru.");
  }
  return await res.json();
}
