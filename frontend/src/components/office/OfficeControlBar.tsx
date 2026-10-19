"use client";

import { Users, Zap, ShieldAlert, Coffee, Layers, ShieldCheck } from "lucide-react";
import { ProjectSummary } from "../../lib/types/api";
import { OasisStreamCategory } from "../../lib/types/office";

interface OfficeControlBarProps {
  connected: boolean;
  projects: ProjectSummary[];
  selectedProjectId: string;
  onSelectProject: (pId: string) => void;
  categoryFilter: OasisStreamCategory;
  onSelectCategory: (cat: OasisStreamCategory) => void;
  onOpenAllHands: () => void;
}

export function OfficeControlBar({
  connected,
  projects,
  selectedProjectId,
  onSelectProject,
  categoryFilter,
  onSelectCategory,
  onOpenAllHands,
}: OfficeControlBarProps) {
  const categories: Array<{ id: OasisStreamCategory; label: string; icon: any }> = [
    { id: "ALL", label: "All Streams", icon: Layers },
    { id: "EXECUTION", label: "Execution & Handoffs", icon: Zap },
    { id: "GATES", label: "CEO Gates", icon: ShieldAlert },
    { id: "LOUNGE", label: "Oasis Lounge", icon: Coffee },
    { id: "SENTINEL", label: "🛡️ CoV Sentinel", icon: ShieldCheck },
  ];

  return (
    <div className="bg-slate-950 p-2.5 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-2.5 shadow-xl select-none">
      {/* Left: Project Selector Pills */}
      <div className="flex flex-wrap items-center gap-1.5 overflow-x-auto max-w-xl">
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          <span className={`w-2 h-2 rounded-full ${connected ? "bg-emerald-500 animate-pulse" : "bg-amber-500"}`} />
          <span className="font-semibold text-slate-300 font-mono text-[11px]">
            {connected ? "LIVE" : "SYNCING"}
          </span>
        </div>

        <button
          onClick={() => onSelectProject("all")}
          className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all ${
            selectedProjectId === "all"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30 font-bold"
              : "text-slate-400 hover:text-white bg-slate-900/80 border border-slate-800/80"
          }`}
        >
          🌐 All Active Projects
        </button>

        {projects.map((proj) => (
          <button
            key={proj.project_id}
            onClick={() => onSelectProject(proj.project_id)}
            className={`px-2.5 py-1 rounded-lg text-xs transition-all truncate max-w-[150px] ${
              selectedProjectId === proj.project_id
                ? "bg-sky-600 text-white font-bold shadow-md shadow-sky-600/30"
                : "text-slate-400 hover:text-white bg-slate-900/60 border border-slate-800/60"
            }`}
          >
            {proj.name}
          </button>
        ))}
      </div>

      {/* Center: Stream Category Filters */}
      <div className="flex items-center space-x-1 bg-slate-900/90 p-0.5 rounded-xl border border-slate-800 text-xs">
        {categories.map((c) => {
          const Icon = c.icon;
          const isActive = categoryFilter === c.id;
          return (
            <button
              key={c.id}
              onClick={() => onSelectCategory(c.id)}
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-lg font-medium text-xs transition-all ${
                isActive
                  ? "bg-slate-800 text-cyan-300 font-semibold border border-slate-700 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{c.label}</span>
            </button>
          );
        })}
      </div>

      {/* Right: Actions (Token Saver Badge & All-Hands) */}
      <div className="flex items-center space-x-2">
        <span className="hidden lg:flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          ⚡ 0-Token Watch
        </span>

        <button
          onClick={onOpenAllHands}
          className="flex items-center space-x-1.5 px-3.5 py-1 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-semibold transition-all active:scale-95"
          title="Buka Executive War Room (@all moderator session)"
        >
          <Users className="w-3.5 h-3.5" />
          <span>All Hands</span>
        </button>
      </div>
    </div>
  );
}
