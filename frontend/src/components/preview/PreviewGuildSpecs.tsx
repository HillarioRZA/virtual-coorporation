"use client";

import React from "react";
import { FileCode, Palette, Activity } from "lucide-react";
import { VentureStateData } from "../../lib/types/api";

export type SpecTab = "prd" | "ui" | "telemetry";

interface PreviewGuildSpecsProps {
  project: VentureStateData | null;
  agentStatus: string;
  activeTab: SpecTab;
  setActiveTab: (tab: SpecTab) => void;
}

/**
 * Renders the Guild Specifications tabs (Lean PRD, UI Spec, Telemetry & Tokens).
 */
export const PreviewGuildSpecs: React.FC<PreviewGuildSpecsProps> = ({
  project,
  agentStatus,
  activeTab,
  setActiveTab,
}) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs">
        <button
          onClick={() => setActiveTab("prd")}
          className={`flex-1 py-1.5 rounded-lg font-medium transition-colors flex items-center justify-center gap-1.5 ${
            activeTab === "prd" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
          }`}
        >
          <FileCode className="w-3.5 h-3.5" />
          <span>Lean PRD</span>
        </button>
        <button
          onClick={() => setActiveTab("ui")}
          className={`flex-1 py-1.5 rounded-lg font-medium transition-colors flex items-center justify-center gap-1.5 ${
            activeTab === "ui" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
          }`}
        >
          <Palette className="w-3.5 h-3.5" />
          <span>UI Spec</span>
        </button>
        <button
          onClick={() => setActiveTab("telemetry")}
          className={`flex-1 py-1.5 rounded-lg font-medium transition-colors flex items-center justify-center gap-1.5 ${
            activeTab === "telemetry" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          <span>Telemetry</span>
        </button>
      </div>

      {/* Tab Contents */}
      <div className="glass-panel p-4 rounded-2xl text-xs space-y-3 min-h-[220px]">
        {activeTab === "prd" && (
          <div className="space-y-2">
            <div className="font-bold uppercase text-[11px] tracking-wider text-indigo-400">
              Product Specification (PM Guild)
            </div>
            {project?.prd_spec ? (
              <div className="space-y-2 text-slate-300">
                <div>
                  <span className="font-semibold text-slate-400">Target Persona: </span>
                  <span>{project.prd_spec.target_persona || "N/A"}</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-400">Core User Stories: </span>
                  <ul className="list-disc list-inside mt-1 space-y-0.5 text-slate-400">
                    {project.prd_spec.user_stories?.map((s: string, idx: number) => (
                      <li key={idx}>{s}</li>
                    )) || <li>Belum ada user stories</li>}
                  </ul>
                </div>
              </div>
            ) : (
              <p className="text-slate-400">Spesifikasi PRD akan muncul setelah node PM selesai.</p>
            )}
          </div>
        )}

        {activeTab === "ui" && (
          <div className="space-y-2">
            <div className="font-bold uppercase text-[11px] tracking-wider text-cyan-400">
              Design Tokens & Component Inventory
            </div>
            {project?.ui_spec ? (
              <div className="space-y-2 text-slate-300">
                <div>
                  <span className="font-semibold text-slate-400">Primary Color: </span>
                  <span className="font-mono text-cyan-300">{project.ui_spec.color_palette?.primary || "Indigo"}</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-400">Komponen Visual: </span>
                  <ul className="list-disc list-inside mt-1 space-y-0.5 text-slate-400">
                    {project.ui_spec.components?.map((c: any, idx: number) => (
                      <li key={idx}>{typeof c === "string" ? c : c.name}</li>
                    )) || <li>Daftar komponen mock termount</li>}
                  </ul>
                </div>
              </div>
            ) : (
              <p className="text-slate-400">Skema komponen UI/UX akan muncul setelah node UI/UX selesai.</p>
            )}
          </div>
        )}

        {activeTab === "telemetry" && (
          <div className="space-y-2">
            <div className="font-bold uppercase text-[11px] tracking-wider text-emerald-400">
              Agent Event Logs & Token Costs
            </div>
            <div className="space-y-1 font-mono text-[11px] text-slate-400">
              <div>Status Aktivitas: <span className="text-emerald-300">{agentStatus}</span></div>
              {project?.token_usage && (
                <div className="pt-2 border-t border-slate-800">
                  <span className="font-semibold text-slate-300">Token Cost per Role:</span>
                  {Object.entries(project.token_usage).map(([role, cost]) => (
                    <div key={role} className="flex justify-between text-slate-400">
                      <span>{role}:</span>
                      <span>${cost}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
