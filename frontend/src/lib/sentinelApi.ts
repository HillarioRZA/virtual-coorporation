import { SentinelAuditLog, SentinelStats } from "./types/sentinel";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (typeof window !== "undefined") {
    const token =
      sessionStorage.getItem("venture_session_token") ||
      sessionStorage.getItem("auth_token") ||
      localStorage.getItem("auth_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  return headers;
}

/**
 * Mengambil riwayat log inspeksi pre-flight CoV Sentinel.
 */
export async function fetchSentinelAuditLogs(
  projectId: string,
  limit: number = 50,
  role?: string,
  status?: string
): Promise<SentinelAuditLog[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (role && role !== "ALL") params.append("role", role);
  if (status && status !== "ALL") params.append("status", status);

  try {
    const res = await fetch(`${BASE_URL}/api/v1/sentinel/${projectId}/audit-logs?${params.toString()}`, {
      headers: getAuthHeaders(),
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.warn("fetchSentinelAuditLogs failed:", err);
    return [];
  }
}

/**
 * Mengambil metrik statistik reliabilitas dan latensi CoV Sentinel.
 */
export async function fetchSentinelStats(projectId: string): Promise<SentinelStats> {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/sentinel/${projectId}/stats`, {
      headers: getAuthHeaders(),
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.warn("fetchSentinelStats failed:", err);
    return {
      total_inspections: 0,
      approved_count: 0,
      repaired_count: 0,
      rejected_count: 0,
      reliability_rate: 100.0,
      avg_latency_ms: 0.0,
    };
  }
}
