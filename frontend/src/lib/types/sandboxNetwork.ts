/**
 * TypeScript types for Hardened Docker Network Sandboxing & Multi-Compose (Sprint 3.5).
 */

export interface NetworkStatusInfo {
  project_id: string;
  network_name: string;
  status: "ACTIVE" | "INACTIVE";
  mode: "docker" | "fallback" | "offline";
  subnet: string;
  isolated: boolean;
  containers_count: number;
}

export interface ServiceMetricsInfo {
  name: string;
  status: string;
  port?: number;
  cpu_percent?: number;
  memory_mb?: number;
}

export interface SandboxMetricsInfo {
  project_id: string;
  mode: "docker" | "fallback";
  cpu_limit_cores: number;
  cpu_used_percent?: number;
  cpu_used_cores?: number;
  cpu_percent?: number;
  memory_limit_mb: number;
  memory_used_mb: number;
  memory_percent: number;
  services: ServiceMetricsInfo[];
}

export interface MultiServiceLaunchResponse {
  project_id: string;
  status: string;
  network: NetworkStatusInfo;
  services: Array<{
    service: string;
    status: string;
    mode?: string;
    port?: number;
    container_name?: string;
  }>;
  quota: {
    cpu_limit: number;
    memory_limit: string;
  };
}

export interface MultiServiceStopResponse {
  project_id: string;
  status: string;
  message: string;
}
