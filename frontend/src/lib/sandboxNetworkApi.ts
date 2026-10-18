/**
 * HTTP Client for Ephemeral Docker Isolated Bridge Network & Resource Quota Metrics.
 */

import { getApiV1Base } from "./config";
import {
  NetworkStatusInfo,
  SandboxMetricsInfo,
  MultiServiceLaunchResponse,
  MultiServiceStopResponse,
} from "./types/sandboxNetwork";

const API_BASE = getApiV1Base();

export async function fetchNetworkStatus(projectId: string): Promise<NetworkStatusInfo> {
  const res = await fetch(`${API_BASE}/sandbox/network/${projectId}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal memuat status network (${res.status})`);
  }
  return res.json();
}

export async function fetchSandboxMetrics(projectId: string): Promise<SandboxMetricsInfo> {
  const res = await fetch(`${API_BASE}/sandbox/metrics/${projectId}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal memuat metrik sandboxing (${res.status})`);
  }
  return res.json();
}

export async function launchMultiService(
  projectId: string,
  hostCodePath: string,
  services?: string[]
): Promise<MultiServiceLaunchResponse> {
  const res = await fetch(`${API_BASE}/sandbox/multi-service/launch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      project_id: projectId,
      host_code_path: hostCodePath,
      services: services || ["fe", "be", "db"],
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Gagal meluncurkan multi-service (${res.status})`);
  }
  return res.json();
}

export async function stopMultiService(projectId: string): Promise<MultiServiceStopResponse> {
  const res = await fetch(`${API_BASE}/sandbox/multi-service/stop`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_id: projectId }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Gagal menghentikan multi-service (${res.status})`);
  }
  return res.json();
}
