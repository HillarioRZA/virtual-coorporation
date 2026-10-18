/**
 * API Client Library untuk Tiket Kanban Korporat.
 * Terhubung ke backend FastAPI /api/v1/corporate/tickets/*.
 */

import { TicketCreate, TicketResponse, TicketStatus } from "./types/tickets";
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

export async function fetchTickets(
  projectId: string,
  branchId?: string,
  status?: string,
  divisionId?: string
): Promise<TicketResponse[]> {
  const params = new URLSearchParams();
  if (branchId) params.append("branch_id", branchId);
  if (status) params.append("status", status);
  if (divisionId) params.append("division_id", divisionId);

  const url = `${API_BASE}/corporate/tickets/${projectId}${params.toString() ? `?${params.toString()}` : ""}`;
  const res = await fetch(url, {
    headers: getAuthHeaders(),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Gagal mengambil tiket: ${res.statusText}`);
  return await res.json();
}

export async function createTicket(payload: TicketCreate): Promise<TicketResponse> {
  const res = await fetch(`${API_BASE}/corporate/tickets`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal membuat tiket baru.");
  }
  return await res.json();
}

export async function transitionTicket(
  ticketId: string,
  targetStatus: TicketStatus
): Promise<TicketResponse> {
  const res = await fetch(
    `${API_BASE}/corporate/tickets/${ticketId}/transition?target_status=${encodeURIComponent(targetStatus)}`,
    {
      method: "POST",
      headers: getAuthHeaders(),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal memindahkan status tiket.");
  }
  return await res.json();
}

export async function deleteTicket(ticketId: string): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/corporate/tickets/${ticketId}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal menghapus tiket.");
  }
  return await res.json();
}

export async function seedInitialTickets(
  projectId: string,
  branchId: string = "branch_main"
): Promise<TicketResponse[]> {
  const res = await fetch(
    `${API_BASE}/corporate/tickets/${projectId}/seed-initial?branch_id=${encodeURIComponent(branchId)}`,
    {
      method: "POST",
      headers: getAuthHeaders(),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Gagal menginisialisasi tiket awal.");
  }
  return await res.json();
}

export async function dispatchConcurrentEngineering(
  projectId: string,
  branchId: string = "branch_main"
): Promise<{ status: string; elapsed_seconds: number; [key: string]: any }> {
  const res = await fetch(
    `${API_BASE}/corporate/dispatch/concurrent/${projectId}?branch_id=${encodeURIComponent(branchId)}`,
    {
      method: "POST",
      headers: getAuthHeaders(),
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || err.message || "Gagal memicu dispatch paralel.");
  }
  return await res.json();
}

