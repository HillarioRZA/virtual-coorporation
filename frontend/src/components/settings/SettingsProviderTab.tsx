"use client";

import { Eye, EyeOff, Key } from "lucide-react";

interface SettingsProviderTabProps {
  providers: Record<string, { key: string; base_url: string; is_set: boolean }>;
  providerForm: Record<string, { key: string; base_url: string }>;
  showKeys: Record<string, boolean>;
  onProviderChange: (prov: string, field: "key" | "base_url", value: string) => void;
  onToggleKeyVisibility: (keyName: string) => void;
}

export function SettingsProviderTab({
  providers,
  providerForm,
  showKeys,
  onProviderChange,
  onToggleKeyVisibility,
}: SettingsProviderTabProps) {
  return (
    <div className="space-y-4">
      <p className="text-xs text-slate-400">
        Kunci API disimpan secara terenkripsi di Secret Vault SQLite dan tidak pernah diekspos plaintext ke client.
        Biarkan kolom kunci kosong atau tidak diubah jika ingin mempertahankan kunci tersimpan.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(providers || {}).map(([prov, meta]) => {
          const currentVal = providerForm[prov] || { key: meta.key, base_url: meta.base_url };
          const isVisible = showKeys[prov] || false;

          return (
            <div key={prov} className="liquid-glass p-5 rounded-2xl border border-white/10 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-white uppercase text-sm tracking-wide font-mono">{prov}</span>
                  <span
                    className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full border ${
                      meta.is_set
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                        : "bg-amber-500/10 text-amber-400 border-amber-500/20"
                    }`}
                  >
                    {meta.is_set ? "Kunci Aktif" : "Belum Diatur"}
                  </span>
                </div>
                <Key className="w-4 h-4 text-slate-400" />
              </div>

              {prov !== "ollama" ? (
                <div>
                  <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    API Key
                  </label>
                  <div className="relative">
                    <input
                      type={isVisible ? "text" : "password"}
                      value={currentVal.key}
                      onChange={(e) => onProviderChange(prov, "key", e.target.value)}
                      placeholder={meta.key || "Masukkan API Key..."}
                      className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2 pr-10 text-slate-200 focus:outline-none focus:border-white/40 font-mono"
                    />
                    <button
                      type="button"
                      onClick={() => onToggleKeyVisibility(prov)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                    >
                      {isVisible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic font-mono">
                  Ollama berjalan secara lokal dan tidak memerlukan API key.
                </p>
              )}

              <div>
                <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Base Endpoint URL
                </label>
                <input
                  type="text"
                  value={currentVal.base_url}
                  onChange={(e) => onProviderChange(prov, "base_url", e.target.value)}
                  className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2 text-slate-200 focus:outline-none focus:border-white/40 font-mono"
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
