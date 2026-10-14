"use client";

import React from "react";
import { LLM_PROVIDERS, RECOMMENDED_PRESETS } from "@/lib/constants/llmPresets";

interface RoleModelFieldsProps {
  modelProvider: string;
  modelName: string;
  temperature: number;
  tokenBudget: number;
  onProviderChange: (prov: string) => void;
  onModelNameChange: (name: string) => void;
  onTemperatureChange: (temp: number) => void;
  onTokenBudgetChange: (budget: number) => void;
}

export default function RoleModelFields({
  modelProvider,
  modelName,
  temperature,
  tokenBudget,
  onProviderChange,
  onModelNameChange,
  onTemperatureChange,
  onTokenBudgetChange,
}: RoleModelFieldsProps) {
  const activePresets = RECOMMENDED_PRESETS[modelProvider] || [];

  return (
    <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-[11px] font-mono uppercase text-slate-400 mb-1">Provider LLM</label>
          <select
            value={modelProvider}
            onChange={(e) => onProviderChange(e.target.value)}
            className="w-full px-3 py-2 rounded-xl bg-black/60 border border-white/15 text-white text-xs focus:outline-none"
          >
            {LLM_PROVIDERS.map((p) => (
              <option key={p.id} value={p.id} className="bg-[#0c0d14]">{p.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-[11px] font-mono uppercase text-slate-400 mb-1">Model Identifier</label>
          <input
            type="text"
            required
            value={modelName}
            onChange={(e) => onModelNameChange(e.target.value)}
            placeholder="deepseek/deepseek-r1:free"
            className="w-full px-3 py-2 rounded-xl bg-black/60 border border-white/15 text-white font-mono text-xs focus:outline-none"
          />
        </div>
      </div>

      {activePresets.length > 0 && (
        <div>
          <span className="text-[10px] text-slate-500 block mb-1.5 font-mono">Pilih Preset Populer:</span>
          <div className="flex flex-wrap gap-1.5">
            {activePresets.map((m) => {
              const isFree = m.includes(":free");
              const isSelected = modelName === m;
              return (
                <button
                  key={m}
                  type="button"
                  onClick={() => onModelNameChange(m)}
                  className={`text-[10px] px-2 py-0.5 rounded-lg border font-mono transition-all flex items-center gap-1 ${
                    isSelected ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-sm" : "bg-black/40 text-slate-400 border-white/10 hover:text-white"
                  }`}
                >
                  {isFree && <span className="text-emerald-400 font-bold">• FREE</span>}
                  <span>{m}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3 pt-1">
        <div>
          <label className="block text-[11px] font-mono text-slate-400 mb-1">Temperature ({temperature})</label>
          <input
            type="range"
            min="0.0"
            max="1.5"
            step="0.05"
            value={temperature}
            onChange={(e) => onTemperatureChange(parseFloat(e.target.value))}
            className="w-full mt-1.5 accent-cyan-400"
          />
        </div>
        <div>
          <label className="block text-[11px] font-mono text-slate-400 mb-1">Token Budget ({tokenBudget})</label>
          <input
            type="number"
            min={1000}
            max={100000}
            step={1000}
            value={tokenBudget}
            onChange={(e) => onTokenBudgetChange(parseInt(e.target.value, 10))}
            className="w-full px-3 py-1.5 rounded-xl bg-black/60 border border-white/15 text-white text-xs font-mono"
          />
        </div>
      </div>
    </div>
  );
}
