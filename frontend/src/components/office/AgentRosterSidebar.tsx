"use client";

import { useMemo, useState } from "react";
import { Search, Sparkles, Coffee, Code2, BrainCircuit } from "lucide-react";
import { AgentSpatialData } from "../../lib/types/office";

interface AgentRosterSidebarProps {
  agents: AgentSpatialData[];
  selectedAgent: AgentSpatialData | null;
  onSelectAgent: (agent: AgentSpatialData) => void;
  demoMode: boolean;
}

export function AgentRosterSidebar({
  agents,
  selectedAgent,
  onSelectAgent,
  demoMode,
}: AgentRosterSidebarProps) {
  const [searchQuery, setSearchQuery] = useState<string>("");

  const filteredAgents = useMemo(() => {
    if (!searchQuery.trim()) return agents;
    const q = searchQuery.toLowerCase();
    return agents.filter(
      (a) => a.name.toLowerCase().includes(q) || a.role_id.toLowerCase().includes(q)
    );
  }, [agents, searchQuery]);

  const getStatusBadge = (state: string) => {
    switch (state) {
      case "CODING":
        return { label: "working", color: "text-cyan-400 bg-cyan-950/80 border-cyan-800/60" };
      case "MEETING":
        return { label: "planning", color: "text-amber-400 bg-amber-950/80 border-amber-800/60" };
      case "WALKING":
        return { label: "moving", color: "text-emerald-400 bg-emerald-950/80 border-emerald-800/60" };
      case "BLOCKED":
        return { label: "blocked", color: "text-rose-400 bg-rose-950/80 border-rose-800/60" };
      default:
        return { label: "on a break", color: "text-slate-400 bg-slate-900 border-slate-800" };
    }
  };

  const getRoleIcon = (roleId: string) => {
    if (roleId.includes("founder") || roleId.includes("cos")) return <Sparkles className="w-3.5 h-3.5" />;
    if (roleId.includes("cto") || roleId.includes("pm")) return <BrainCircuit className="w-3.5 h-3.5" />;
    if (roleId.includes("fe") || roleId.includes("be") || roleId.includes("devsecops")) return <Code2 className="w-3.5 h-3.5" />;
    return <Coffee className="w-3.5 h-3.5" />;
  };

  return (
    <aside className="w-72 md:w-80 flex-shrink-0 bg-slate-950/95 border-r border-slate-800 flex flex-col h-full select-none z-10">
      {/* Header bar matching Screenshot 3 */}
      <div className="p-3.5 border-b border-slate-800/80 bg-slate-900/40">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
            </span>
            <h1 className="text-sm font-bold text-white tracking-wide">Agent Office</h1>
            <span className="text-[10px] font-semibold text-emerald-400 uppercase tracking-wider px-1.5 py-0.2 rounded bg-emerald-500/10 border border-emerald-500/20">
              LIVE
            </span>
          </div>
          {demoMode && (
            <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
              DEMO
            </span>
          )}
        </div>
        <p className="text-[11px] text-slate-400 mt-1 font-mono flex items-center gap-1">
          <span className="text-slate-500">•</span>
          <span>working on Mission Control</span>
        </p>

        {/* Search input */}
        <div className="mt-2.5 relative">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search agents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900/90 text-xs text-slate-200 pl-8 pr-3 py-1.5 rounded-lg border border-slate-800 focus:outline-none focus:border-indigo-500 transition-colors placeholder:text-slate-600"
          />
        </div>
      </div>

      {/* Agent Roster List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1 divide-y divide-slate-900/40 scrollbar-thin scrollbar-thumb-slate-800">
        {filteredAgents.map((agent) => {
          const isSelected = selectedAgent?.role_id === agent.role_id;
          const status = getStatusBadge(agent.activity_state);

          return (
            <button
              key={agent.role_id}
              onClick={() => onSelectAgent(agent)}
              className={`w-full pt-1.5 pb-1 px-2.5 rounded-xl flex items-center justify-between text-left transition-all ${
                isSelected
                  ? "bg-indigo-600/20 border border-indigo-500/50 shadow-lg shadow-indigo-950/50"
                  : "hover:bg-slate-900/70 border border-transparent"
              }`}
            >
              <div className="flex items-center space-x-2.5 min-w-0">
                {/* Tactical Avatar Portrait */}
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs shadow-md border flex-shrink-0"
                  style={{
                    backgroundColor: `${agent.color || "#06b6d4"}20`,
                    borderColor: `${agent.color || "#06b6d4"}70`,
                    color: agent.color || "#06b6d4",
                  }}
                >
                  {getRoleIcon(agent.role_id)}
                </div>

                <div className="truncate">
                  <p className="text-xs font-semibold text-slate-200 truncate">
                    {agent.name}
                  </p>
                  <p className="text-[10px] text-slate-500 font-mono capitalize truncate">
                    {agent.tier.toLowerCase().replace("_", " ")}
                  </p>
                </div>
              </div>

              {/* Status pill tag */}
              <div
                className={`text-[10px] font-mono px-2 py-0.5 rounded-full border flex-shrink-0 flex items-center gap-1 ${status.color}`}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
                <span>{status.label}</span>
              </div>
            </button>
          );
        })}
      </div>
    </aside>
  );
}
