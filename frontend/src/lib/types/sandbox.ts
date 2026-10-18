/**
 * Kontrak tipe data TypeScript untuk Sandbox Snapshots & Interactive Terminal (Sprint 2.5).
 */

export interface SnapshotItem {
  id: string;
  project_id: string;
  tag: string;
  description: string;
  file_count: number;
  total_bytes: number;
  created_at: string;
}

export interface SnapshotCreateRequest {
  tag: string;
  description?: string;
}

export interface SnapshotRollbackResponse {
  status: string;
  project_id: string;
  restored_snapshot_id: string;
  tag?: string;
  timestamp: string;
}

export interface TerminalMessage {
  type: "start" | "stdout" | "stderr" | "system" | "exit";
  data?: string;
  command?: string;
  code?: number;
  cwd?: string;
  duration_ms?: number;
  timestamp?: string;
}

export type TerminalStatus = "connecting" | "connected" | "running" | "disconnected";
