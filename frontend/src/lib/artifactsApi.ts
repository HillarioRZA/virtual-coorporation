/**
 * API Client Library untuk Artefak Lintas Divisi (Pilar 7 & 8).
 */

import { getApiV1Base } from "./config";

const API_BASE = getApiV1Base();

export interface ArtifactItem {
  filename: string;
  category: "SLIDES" | "EBOOK" | "DOCUMENT" | "DATA" | "SPREADSHEET" | "MEDIA" | "OTHER";
  size_bytes: number;
  updated_at: string;
}

export async function fetchProjectArtifacts(projectId: string): Promise<ArtifactItem[]> {
  try {
    const res = await fetch(`${API_BASE}/projects/${projectId}/artifacts`, {
      cache: "no-store",
    });
    if (!res.ok) {
      return [];
    }
    const data = await res.json();
    return data.data || [];
  } catch (err) {
    console.error("Gagal mengambil artefak proyek:", err);
    return [];
  }
}

export function getArtifactDownloadUrl(projectId: string, filename: string): string {
  return `${API_BASE}/projects/${projectId}/artifacts/${encodeURIComponent(filename)}`;
}
