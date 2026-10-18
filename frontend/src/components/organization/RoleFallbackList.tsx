"use client";

import React from "react";
import { FallbackChannelConfig } from "@/lib/types/analytics";

interface RoleFallbackListProps {
  fallbacks: FallbackChannelConfig[];
  onChange: (updated: FallbackChannelConfig[]) => void;
}

const PRESET_MODELS = [
  { label: "DeepSeek R1 Free", model: "deepseek/deepseek-r1:free", provider: "openrouter" },
  { label: "Gemini 2.0 Flash", model: "google/gemini-2.0-flash-001", provider: "openrouter" },
  { label: "Llama 3.3 70B Free", model: "meta-llama/llama-3.3-70b-instruct:free", provider: "openrouter" },
  { label: "Groq Llama 70B", model: "llama-3.3-70b-versatile", provider: "groq" },
];

export const RoleFallbackList: React.FC<RoleFallbackListProps> = ({ fallbacks, onChange }) => {
  const handleAdd = (preset?: { model: string; provider: string }) => {
    const newItem: FallbackChannelConfig = {
      channel_name: preset ? preset.model.split("/").pop() || "channel" : "custom-channel",
      model_name: preset ? preset.model : "deepseek/deepseek-r1:free",
      provider: preset ? preset.provider : "openrouter",
      priority: fallbacks.length + 1,
      rpm_limit: 60,
      tpm_limit: 100000,
      cost_per_million_input: 0.0,
      cost_per_million_output: 0.0,
      is_active: true,
    };
    onChange([...fallbacks, newItem]);
  };

  const handleRemove = (index: number) => {
    const updated = fallbacks.filter((_, i) => i !== index).map((item, idx) => ({ ...item, priority: idx + 1 }));
    onChange(updated);
  };

  const handleMove = (index: number, direction: "up" | "down") => {
    const targetIdx = direction === "up" ? index - 1 : index + 1;
    if (targetIdx < 0 || targetIdx >= fallbacks.length) return;
    const items = [...fallbacks];
    const [moved] = items.splice(index, 1);
    items.splice(targetIdx, 0, moved);
    onChange(items.map((item, idx) => ({ ...item, priority: idx + 1 })));
  };

  const handleUpdate = (index: number, key: keyof FallbackChannelConfig, val: any) => {
    const updated = [...fallbacks];
    updated[index] = { ...updated[index], [key]: val };
    onChange(updated);
  };

  return (
    <div className="space-y-3 p-3 bg-zinc-900/60 rounded-xl border border-zinc-800/80">
      <div className="flex items-center justify-between">
        <div>
          <label className="text-xs font-semibold text-zinc-300 uppercase tracking-wider flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
            Multi-Channel Fallback Chain (9router Style)
          </label>
          <p className="text-[11px] text-zinc-400 mt-0.5">
            Model cadangan otomatis jika model utama habis token / terkena rate limit.
          </p>
        </div>
        <button
          type="button"
          onClick={() => handleAdd()}
          className="text-xs bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 px-2.5 py-1 rounded-md border border-amber-500/30 transition-colors"
        >
          + Tambah Model
        </button>
      </div>

      {/* Preset pills */}
      <div className="flex flex-wrap gap-1.5 pt-1">
        <span className="text-[10px] text-zinc-400 self-center">Preset:</span>
        {PRESET_MODELS.map((p) => (
          <button
            key={p.label}
            type="button"
            onClick={() => handleAdd(p)}
            className="text-[10px] bg-zinc-800 hover:bg-zinc-700 text-zinc-300 px-2 py-0.5 rounded-full border border-zinc-700 transition"
          >
            + {p.label}
          </button>
        ))}
      </div>

      {/* Fallback List */}
      {fallbacks.length === 0 ? (
        <div className="text-center py-4 text-xs text-zinc-400 border border-dashed border-zinc-800 rounded-lg">
          Belum ada model cadangan. Tambahkan model di atas untuk proteksi failover.
        </div>
      ) : (
        <div className="space-y-2">
          {fallbacks.map((fb, idx) => (
            <div key={idx} className="flex items-center gap-2 p-2 bg-zinc-800/60 rounded-lg border border-zinc-700/60 text-xs">
              <span className="w-5 text-center font-mono font-bold text-amber-400">#{fb.priority}</span>
              <div className="flex-1 grid grid-cols-1 sm:grid-cols-3 gap-2">
                <input
                  type="text"
                  value={fb.model_name}
                  onChange={(e) => handleUpdate(idx, "model_name", e.target.value)}
                  placeholder="model_name (e.g. google/gemini-2.0-flash)"
                  className="bg-zinc-900 border border-zinc-700 rounded px-2 py-1 text-zinc-200 text-xs focus:ring-1 focus:ring-amber-500 focus:outline-none col-span-2"
                />
                <select
                  value={fb.provider}
                  onChange={(e) => handleUpdate(idx, "provider", e.target.value)}
                  className="bg-zinc-900 border border-zinc-700 rounded px-2 py-1 text-zinc-200 text-xs focus:outline-none"
                >
                  <option value="openrouter">OpenRouter</option>
                  <option value="groq">Groq</option>
                  <option value="google">Google Gemini</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="openai">OpenAI</option>
                  <option value="ollama">Ollama (Local)</option>
                  <option value="openai_compatible">Custom Provider (Format OpenAI)</option>
                </select>
              </div>

              <div className="flex items-center gap-1">
                <button
                  type="button"
                  disabled={idx === 0}
                  onClick={() => handleMove(idx, "up")}
                  className="p-1 hover:bg-zinc-700 text-zinc-400 disabled:opacity-30 rounded"
                  title="Naikkan Prioritas"
                >
                  ▲
                </button>
                <button
                  type="button"
                  disabled={idx === fallbacks.length - 1}
                  onClick={() => handleMove(idx, "down")}
                  className="p-1 hover:bg-zinc-700 text-zinc-400 disabled:opacity-30 rounded"
                  title="Turunkan Prioritas"
                >
                  ▼
                </button>
                <button
                  type="button"
                  onClick={() => handleRemove(idx)}
                  className="p-1 hover:bg-red-500/20 text-red-400 rounded transition"
                  title="Hapus Model"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
