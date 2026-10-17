"use client";

import { Eye, EyeOff, Key, Server, Zap } from "lucide-react";

interface SettingsProviderTabProps {
  providers: Record<string, { key: string; base_url: string; is_set: boolean; model?: string }>;
  providerForm: Record<string, { key: string; base_url: string; model?: string }>;
  showKeys: Record<string, boolean>;
  onProviderChange: (prov: string, field: "key" | "base_url" | "model", value: string) => void;
  onToggleKeyVisibility: (keyName: string) => void;
}

export function SettingsProviderTab({
  providers,
  providerForm,
  showKeys,
  onProviderChange,
  onToggleKeyVisibility,
}: SettingsProviderTabProps) {
  const customMeta = providers["openai_compatible"] || { key: "", base_url: "https://api.tokenomixai.com/v1", is_set: false, model: "qwen-2.5-coder-32b-instruct" };
  const customVal = providerForm["openai_compatible"] || { key: customMeta.key, base_url: customMeta.base_url || "https://api.tokenomixai.com/v1", model: customMeta.model || "qwen-2.5-coder-32b-instruct" };
  const isCustomVisible = showKeys["openai_compatible"] || false;

  const handleQuickFillTokenomix = () => {
    onProviderChange("openai_compatible", "base_url", "https://api.tokenomixai.com/v1");
    if (!customVal.model) onProviderChange("openai_compatible", "model", "qwen-2.5-coder-32b-instruct");
  };

  return (
    <div className="space-y-6">
      {/* 1. Custom OpenAI-Compatible Provider Card (TokenomixAI / Any Provider) */}
      <div className="liquid-glass p-5 rounded-2xl border border-cyan-500/30 bg-cyan-950/20 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-cyan-500/20 pb-3">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
              <Server className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-white text-sm tracking-wide font-mono">Custom Provider (Format OpenAI / TokenomixAI)</span>
                <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full border ${customMeta.is_set ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-amber-500/10 text-amber-400 border-amber-500/20"}`}>
                  {customMeta.is_set ? "Kunci Aktif" : "Belum Diatur"}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">Mendukung TokenomixAI, LocalAI, vLLM, DeepSeek, dsb. dengan format OpenAI REST</p>
            </div>
          </div>
          <button type="button" onClick={handleQuickFillTokenomix} className="self-start sm:self-center flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-300 text-xs font-semibold transition-all active:scale-95">
            <Zap className="w-3.5 h-3.5" />
            <span>⚡ Isi Cepat TokenomixAI</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">Base Endpoint URL</label>
            <input type="text" value={customVal.base_url} onChange={(e) => onProviderChange("openai_compatible", "base_url", e.target.value)} placeholder="https://api.tokenomixai.com/v1" className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-400 font-mono" />
            <span className="text-[10px] text-slate-500 font-mono mt-1 block">Contoh: https://api.tokenomixai.com/v1</span>
          </div>

          <div>
            <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">API Key (sk-...)</label>
            <div className="relative">
              <input type={isCustomVisible ? "text" : "password"} value={customVal.key} onChange={(e) => onProviderChange("openai_compatible", "key", e.target.value)} placeholder={customMeta.key || "Masukkan API Key (sk-...)"} className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2 pr-10 text-slate-200 focus:outline-none focus:border-cyan-400 font-mono" />
              <button type="button" onClick={() => onToggleKeyVisibility("openai_compatible")} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white">
                {isCustomVisible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <span className="text-[10px] text-slate-500 font-mono mt-1 block">Terenkripsi di SQLite Secret Vault</span>
          </div>

          <div>
            <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">Default Model Identifier</label>
            <input type="text" value={customVal.model || ""} onChange={(e) => onProviderChange("openai_compatible", "model", e.target.value)} placeholder="qwen-2.5-coder-32b-instruct" className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-400 font-mono" />
            <span className="text-[10px] text-slate-500 font-mono mt-1 block">Model default untuk agen custom</span>
          </div>
        </div>
      </div>

      {/* 2. Standard Built-in Providers */}
      <div className="space-y-2">
        <h3 className="text-xs font-mono font-semibold text-slate-400 uppercase tracking-wider">Penyedia Bawaan Lainnya (Standard BYOK)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(providers || {}).filter(([prov]) => prov !== "openai_compatible").map(([prov, meta]) => {
            const currentVal = providerForm[prov] || { key: meta.key, base_url: meta.base_url };
            const isVisible = showKeys[prov] || false;
            return (
              <div key={prov} className="liquid-glass p-5 rounded-2xl border border-white/10 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-white uppercase text-sm tracking-wide font-mono">{prov}</span>
                    <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full border ${meta.is_set ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-amber-500/10 text-amber-400 border-amber-500/20"}`}>
                      {meta.is_set ? "Kunci Aktif" : "Belum Diatur"}
                    </span>
                  </div>
                  <Key className="w-4 h-4 text-slate-400" />
                </div>

                {prov !== "ollama" ? (
                  <div>
                    <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">API Key</label>
                    <div className="relative">
                      <input type={isVisible ? "text" : "password"} value={currentVal.key} onChange={(e) => onProviderChange(prov, "key", e.target.value)} placeholder={meta.key || "Masukkan API Key..."} className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2 pr-10 text-slate-200 focus:outline-none focus:border-white/40 font-mono" />
                      <button type="button" onClick={() => onToggleKeyVisibility(prov)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white">
                        {isVisible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 italic font-mono">Ollama berjalan secara lokal dan tidak memerlukan API key.</p>
                )}

                <div>
                  <label className="text-[11px] font-mono font-semibold text-slate-400 uppercase tracking-wider block mb-1">Base Endpoint URL</label>
                  <input type="text" value={currentVal.base_url} onChange={(e) => onProviderChange(prov, "base_url", e.target.value)} className="w-full text-xs rounded-xl bg-black/60 border border-white/15 px-3 py-2 text-slate-200 focus:outline-none focus:border-white/40 font-mono" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
