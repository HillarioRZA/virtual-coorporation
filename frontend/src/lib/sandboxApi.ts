/**
 * Klien HTTP Fetch untuk REST API Sandbox Snapshots & Rollback.
 */

import { SnapshotItem, SnapshotRollbackResponse } from "./types/sandbox";
import { getApiV1Base } from "./config";

const API_BASE = getApiV1Base();

export async function fetchSnapshots(projectId: string): Promise<SnapshotItem[]> {
  const res = await fetch(`${API_BASE}/sandbox/snapshots/${projectId}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Gagal memuat daftar snapshot (${res.status})`);
  }
  return res.json();
}

export async function createSnapshot(
  projectId: string,
  tag: string,
  description?: string
): Promise<SnapshotItem> {
  const res = await fetch(`${API_BASE}/sandbox/snapshots/${projectId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tag, description: description || "" }),
  });
  if (!res.ok) {
    throw new Error(`Gagal membuat snapshot (${res.status})`);
  }
  return res.json();
}

export async function rollbackSnapshot(
  projectId: string,
  snapshotId: string
): Promise<SnapshotRollbackResponse> {
  const res = await fetch(
    `${API_BASE}/sandbox/snapshots/${projectId}/rollback/${snapshotId}`,
    {
      method: "POST",
    }
  );
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Gagal melakukan rollback (${res.status})`);
  }
  return res.json();
}

export async function deleteSnapshot(
  projectId: string,
  snapshotId: string
): Promise<{ status: string; snapshot_id: string }> {
  const res = await fetch(
    `${API_BASE}/sandbox/snapshots/${projectId}/${snapshotId}`,
    {
      method: "DELETE",
    }
  );
  if (!res.ok) {
    throw new Error(`Gagal menghapus snapshot (${res.status})`);
  }
  return res.json();
}
