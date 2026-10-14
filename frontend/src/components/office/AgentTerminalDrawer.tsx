"use client";

import { X, Terminal, Cpu, ShieldCheck, Activity } from "lucide-react";
import { AgentSpatialData } from "../../lib/types/office";

interface AgentTerminalDrawerProps {
  agent: AgentSpatialData | null;
  onClose: () => void;
  onIntervene?: (instruction: string) => void;
}

export function AgentTerminalDrawer({ agent, onClose, onIntervene }: AgentTerminalDrawerProps) {
  if (!agent) return null;

  return (
    <div className="absolute right-3 top-16 bottom-3 w-84 md:w-96 bg-slate-950/95 border border-slate-800 rounded-2xl shadow-2xl backdrop-blur-xl flex flex-col overflow-hidden z-30 transition-all">
      {/* Header */}
      <div className="p-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
        <div className="flex items-center space-x-2.5">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs border"
            style={{ backgroundColor: `${agent.color}20`, borderColor: `${agent.color}80`, color: agent.color }}
          >
            {agent.name[0]}
          </div>
          <div>
            <h3 className="text-xs font-bold text-white">{agent.name}</h3>
            <p className="text-[10px] text-slate-400 font-mono capitalize">{agent.tier.toLowerCase()}</p>
          </div>
        </div>
        <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body: Live State & Tools */}
      <div className="flex-1 p-3.5 space-y-3 overflow-y-auto font-mono text-xs">
        {/* Status Pill */}
        <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-slate-400 flex items-center gap-1.5 text-[11px]">
            <Activity className="w-3.5 h-3.5 text-cyan-400" /> State
          </span>
          <span className="font-bold text-cyan-300 uppercase text-[10px] px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-800">
            {agent.activity_state}
          </span>
        </div>

        {/* Live Scratchpad / Terminal Stream */}
        <div className="space-y-1.5">
          <span className="text-slate-400 flex items-center gap-1 text-[11px]">
            <Terminal className="w-3.5 h-3.5 text-indigo-400" /> Live Terminal & Scratchpad
          </span>
          <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-emerald-400 text-[11px] leading-relaxed break-words shadow-inner min-h-[90px]">
            <span className="text-slate-500 font-bold">$ </span>
            {agent.scratchpad || "Standing by for task delegation..."}
          </div>
        </div>

        {/* Active Tool Harness */}
        <div className="space-y-1.5">
          <span className="text-slate-400 flex items-center gap-1 text-[11px]">
            <Cpu className="w-3.5 h-3.5 text-amber-400" /> Active Tool Harness
          </span>
          <div className="flex flex-wrap gap-1.5">
            <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[10px] text-slate-300 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-emerald-400" /> AST Scan
            </span>
            <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[10px] text-slate-300">
              Docker Sandbox
            </span>
            <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[10px] text-slate-300">
              Pytest v8.3
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
