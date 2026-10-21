"use client";

import React, { useEffect, useState } from "react";
import { AGENT_TOOLS } from "@/lib/constants/llmPresets";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface MCPToolOption {
  id: string;
  label: string;
  description?: string;
  server_name: string;
}

interface CustomToolOption {
  id: string;
  name: string;
  label: string;
  description?: string;
  created_by?: string;
}

interface RoleToolSelectorProps {
  selectedTools: string[];
  onToggleTool: (toolId: string) => void;
}

/**
 * RoleToolSelector - Komponen seleksi izin perkakas (tools) agen dinamis (Built-in + MCP + Custom Secretary Tools).
 */
export default function RoleToolSelector({
  selectedTools,
  onToggleTool,
}: RoleToolSelectorProps) {
  const [mcpTools, setMcpTools] = useState<MCPToolOption[]>([]);
  const [customTools, setCustomTools] = useState<CustomToolOption[]>([]);

  useEffect(() => {
    async function loadDynamicTools() {
      try {
        const res = await fetch(`${API_BASE}/mcp/all-tools`);
        if (res.ok) {
          const data = await res.json();
          if (data.mcp_tools) {
            setMcpTools(data.mcp_tools);
          }
          if (data.custom_tools) {
            setCustomTools(data.custom_tools);
          }
        }
      } catch (err) {
        // Fallback anggap belum ada dynamic tools tambahan
      }
    }
    loadDynamicTools();
  }, []);

  return (
    <div className="space-y-3">
      <div>
        <label className="block text-xs font-medium text-slate-300 mb-1.5">
          Izin Perkakas Bawaan (*Standard Built-in Tools*)
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

      {mcpTools.length > 0 && (
        <div className="pt-2 border-t border-white/5">
          <label className="block text-xs font-medium text-purple-300 mb-1.5">
            Izin Perkakas MCP (*Active External MCP Servers*)
          </label>
          <div className="flex flex-wrap gap-2">
            {mcpTools.map((tool) => {
              const isSelected = selectedTools.includes(tool.id);
              return (
                <button
                  type="button"
                  key={tool.id}
                  onClick={() => onToggleTool(tool.id)}
                  title={tool.description || ""}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-mono border transition-all ${
                    isSelected
                      ? "bg-purple-500/20 border-purple-500/40 text-purple-300 shadow-sm"
                      : "bg-white/5 border-white/10 text-slate-400 hover:text-purple-300"
                  }`}
                >
                  {isSelected ? "✓ " : "+ "}
                  {tool.label}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {customTools.length > 0 && (
        <div className="pt-2 border-t border-white/5">
          <label className="block text-xs font-medium text-amber-300 mb-1.5">
            Izin Perkakas Sintesis Dinamis (*Approved Secretary / Custom Tools*)
          </label>
          <div className="flex flex-wrap gap-2">
            {customTools.map((tool) => {
              const isSelected = selectedTools.includes(tool.id) || selectedTools.includes(tool.name);
              return (
                <button
                  type="button"
                  key={tool.id}
                  onClick={() => onToggleTool(tool.name)}
                  title={tool.description || ""}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-mono border transition-all ${
                    isSelected
                      ? "bg-amber-500/20 border-amber-500/40 text-amber-300 shadow-sm"
                      : "bg-white/5 border-white/10 text-slate-400 hover:text-amber-300"
                  }`}
                >
                  {isSelected ? "✓ " : "+ "}
                  {tool.label}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

