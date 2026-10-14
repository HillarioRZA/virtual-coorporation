"use client";

import React from "react";
import { AGENT_TOOLS } from "@/lib/constants/llmPresets";

interface RoleToolSelectorProps {
  selectedTools: string[];
  onToggleTool: (toolId: string) => void;
}

/**
 * RoleToolSelector - Komponen seleksi izin perkakas (tools) agen
 */
export default function RoleToolSelector({
  selectedTools,
  onToggleTool,
}: RoleToolSelectorProps) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-300 mb-1.5">
        Izin Alat (*Tools*)
      </label>
      <div className="flex flex-wrap gap-2">
        {AGENT_TOOLS.map((tool) => {
          const isSelected = selectedTools.includes(tool.id);
          return (
            <button
              type="button"
              key={tool.id}
              onClick={() => onToggleTool(tool.id)}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-mono border transition-all ${
                isSelected
                  ? "bg-cyan-500/20 border-cyan-500/40 text-cyan-300 shadow-sm"
                  : "bg-white/5 border-white/10 text-slate-400 hover:text-white"
              }`}
            >
              {isSelected ? "✓ " : "+ "}
              {tool.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
