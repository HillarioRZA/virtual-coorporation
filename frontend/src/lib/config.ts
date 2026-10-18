/**
 * Sentralisasi konfigurasi URL API dan WebSocket untuk Cockpit Frontend.
 * Menghindari inkonsistensi path (double /api/v1/api/v1 atau missing /api/v1).
 */

export function getApiBase(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/api\/v1\/?$/, "").replace(/\/$/, "");
  }
  // Otomatis adaptif ke IP laptop saat diakses dari HP di LAN yang sama
  if (typeof window !== "undefined" && window.location.hostname) {
    return `http://${window.location.hostname}:8000`;
  }
  return "http://127.0.0.1:8000";
}

export function getApiV1Base(): string {
  return `${getApiBase()}/api/v1`;
}

export function getWsBase(): string {
  return getApiBase().replace(/^http/, "ws");
}
