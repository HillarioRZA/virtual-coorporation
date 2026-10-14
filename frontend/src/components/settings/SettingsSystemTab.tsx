"use client";

import { Dispatch, SetStateAction } from "react";
import { Cpu, Terminal } from "lucide-react";

interface SandboxFormData {
  domain_suffix: string;
  caddy_admin_api: string;
  frontend_image: string;
  backend_image: string;
}

interface SystemMetadata {
  app_env: string;
  backend_host: string;
  backend_port: number;
  frontend_port: number;
  database_url: string;
}

interface SettingsSystemTabProps {
  sandboxForm: SandboxFormData;
  systemMeta?: SystemMetadata;
  setSandboxForm: Dispatch<SetStateAction<SandboxFormData>>;
}

export function SettingsSystemTab({
  sandboxForm,
  systemMeta,
  setSandboxForm,
}: SettingsSystemTabProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="liquid-glass p-5 rounded-2xl border border-white/10 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <span>Sandbox Ephemeral & Dual-Engine Fallback</span>
        </h3>

        <div className="space-y-3">
          <div>
            <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Sandbox Domain Suffix
            </label>
            <input
              type="text"
              value={sandboxForm.domain_suffix}
              onChange={(e) => setSandboxForm((s) => ({ ...s, domain_suffix: e.target.value }))}
              className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2 text-slate-200 font-mono"
            />
          </div>

          <div>
            <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Caddy Admin API
            </label>
            <input
              type="text"
              value={sandboxForm.caddy_admin_api}
              onChange={(e) => setSandboxForm((s) => ({ ...s, caddy_admin_api: e.target.value }))}
              className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2 text-slate-200 font-mono"
            />
          </div>

          <div>
            <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Docker Frontend Base Image
            </label>
            <input
              type="text"
              value={sandboxForm.frontend_image}
              onChange={(e) => setSandboxForm((s) => ({ ...s, frontend_image: e.target.value }))}
              className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2 text-slate-200 font-mono"
            />
          </div>

          <div>
            <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Docker Backend Base Image
            </label>
            <input
              type="text"
              value={sandboxForm.backend_image}
              onChange={(e) => setSandboxForm((s) => ({ ...s, backend_image: e.target.value }))}
              className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2 text-slate-200 font-mono"
            />
          </div>
        </div>
      </div>

      <div className="liquid-glass p-5 rounded-2xl border border-white/10 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Cpu className="w-4 h-4 text-slate-400" />
          <span>Informasi Port & Database (Read-Only)</span>
        </h3>
        <div className="space-y-3 text-xs">
          <div>
            <span className="text-slate-500 block text-[11px] uppercase font-mono font-semibold">Environment Mode</span>
            <span className="text-slate-200 font-mono">{systemMeta?.app_env || "production"}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px] uppercase font-mono font-semibold">Backend Endpoint</span>
            <span className="text-slate-200 font-mono">
              {systemMeta?.backend_host || "127.0.0.1"}:{systemMeta?.backend_port || 8000}
            </span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px] uppercase font-mono font-semibold">Frontend Port</span>
            <span className="text-slate-200 font-mono">{systemMeta?.frontend_port || 3000}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[11px] uppercase font-mono font-semibold">SQLite Database URL</span>
            <span className="text-slate-200 font-mono break-all">{systemMeta?.database_url || "sqlite+aiosqlite:///data/corporate.db"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
