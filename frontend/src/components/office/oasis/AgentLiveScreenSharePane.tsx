"use client";

import { useState } from "react";
import { X, Code2, Terminal, Globe, ShieldCheck, Activity } from "lucide-react";
import { AgentSpatialData } from "../../../lib/types/office";
import { DiffViewer } from "../../pr/DiffViewer";
import { InteractiveTerminal } from "../../sandbox/InteractiveTerminal";
import { RoleCostTable } from "../../analytics/RoleCostTable";

interface AgentLiveScreenSharePaneProps {
  agent: AgentSpatialData | null;
  projectId: string;
  onClose: () => void;
  onInterrupt: (roleId: string) => void;
}

export function AgentLiveScreenSharePane({
  agent,
  projectId,
  onClose,
  onInterrupt,
}: AgentLiveScreenSharePaneProps) {
  const [activeTab, setActiveTab] = useState<"DIFF" | "TERMINAL" | "PREVIEW" | "METRICS">("DIFF");

  if (!agent) return null;

  const sampleDiff = agent.active_file
    ? `--- a/src/${agent.active_file}\n+++ b/src/${agent.active_file}\n@@ -1,5 +1,7 @@\n+import { useState, useEffect } from "react";\n+// Autonomous synthesis by ${agent.name}\n-const status = "PENDING";\n+const status = "ACTIVE_EXECUTION";`
    : `--- a/src/modules/core.ts\n+++ b/src/modules/core.ts\n@@ -10,3 +10,4 @@\n+// Ready for sprint ticket assignment`;

  return (
    <div className="w-full lg:w-[48%] flex flex-col h-full bg-slate-950/90 rounded-2xl border border-slate-800 overflow-hidden shadow-2xl backdrop-blur-xl animate-in fade-in slide-in-from-right-4 duration-200">
      {/* Pane Header */}
      <div className="p-3 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center space-x-2.5">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs border"
            style={{
              backgroundColor: `${agent.color || "#06b6d4"}20`,
              borderColor: `${agent.color || "#06b6d4"}70`,
              color: agent.color || "#06b6d4",
            }}
          >
            {agent.name[0]}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-xs font-bold text-white">{agent.name}</h3>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                {agent.activity_state}
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono truncate max-w-[220px]">
              {agent.scratchpad || "Standing by..."}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => onInterrupt(agent.role_id)}
            className="px-2 py-1 rounded-lg bg-amber-500/15 text-amber-300 hover:bg-amber-500/25 border border-amber-500/30 text-[10px] font-semibold transition-all active:scale-95"
          >
            ⚡ Interrupt
          </button>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tabs Selector Bar */}
      <div className="px-3 pt-2 border-b border-slate-800 flex items-center space-x-2 bg-slate-900/30 text-xs">
        <button
          onClick={() => setActiveTab("DIFF")}
          className={`flex items-center space-x-1.5 pb-2 px-2 border-b-2 font-medium transition-all ${
            activeTab === "DIFF"
              ? "border-cyan-400 text-cyan-300 font-bold"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Code2 className="w-3.5 h-3.5" />
          <span>Live Code Diff</span>
        </button>

        <button
          onClick={() => setActiveTab("TERMINAL")}
          className={`flex items-center space-x-1.5 pb-2 px-2 border-b-2 font-medium transition-all ${
            activeTab === "TERMINAL"
              ? "border-indigo-400 text-indigo-300 font-bold"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Terminal className="w-3.5 h-3.5" />
          <span>Sandbox Terminal</span>
        </button>

        <button
          onClick={() => setActiveTab("PREVIEW")}
          className={`flex items-center space-x-1.5 pb-2 px-2 border-b-2 font-medium transition-all ${
            activeTab === "PREVIEW"
              ? "border-emerald-400 text-emerald-300 font-bold"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Globe className="w-3.5 h-3.5" />
          <span>App Preview</span>
        </button>

        <button
          onClick={() => setActiveTab("METRICS")}
          className={`flex items-center space-x-1.5 pb-2 px-2 border-b-2 font-medium transition-all ${
            activeTab === "METRICS"
              ? "border-purple-400 text-purple-300 font-bold"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Gate & Metrics</span>
        </button>
      </div>

      {/* Tab Panels Body */}
      <div className="flex-1 p-3 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-800">
        {activeTab === "DIFF" && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 px-1">
              <span>File: <strong className="text-slate-200">{agent.active_file || "runtime/synthesis.ts"}</strong></span>
              <span className="text-emerald-400">Sync with Git Working Tree</span>
            </div>
            <DiffViewer diffText={sampleDiff} />
          </div>
        )}

        {activeTab === "TERMINAL" && (
          <div className="h-full min-h-[320px]">
            <InteractiveTerminal projectId={projectId === "all" ? "default_venture" : projectId} />
          </div>
        )}

        {activeTab === "PREVIEW" && (
          <div className="h-full min-h-[300px] flex flex-col items-center justify-center bg-slate-900/50 rounded-xl border border-slate-800 p-6 text-center space-y-3">
            <Globe className="w-10 h-10 text-cyan-400 animate-pulse" />
            <p className="text-xs font-semibold text-slate-200">Local Sandbox Webview Mounted</p>
            <p className="text-[11px] text-slate-400 max-w-xs">
              Live HTTP preview running on container port 8080.
            </p>
            <a
              href={`/preview/${projectId === "all" ? "default_venture" : projectId}`}
              target="_blank"
              rel="noreferrer"
              className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all"
            >
              Open Fullscreen Preview ↗
            </a>
          </div>
        )}

        {activeTab === "METRICS" && (
          <div className="space-y-3">
            <RoleCostTable
              roles={[
                {
                  role_id: agent.role_id,
                  role_name: agent.name,
                  request_count: 12,
                  total_tokens: 3450,
                  total_cost_usd: 0.042,
                  fallbacks_count: 0,
                },
              ]}
              totalCost={0.042}
            />
          </div>
        )}
      </div>
    </div>
  );
}
