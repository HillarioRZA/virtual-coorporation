"use client";

import { useState } from "react";
import {
  X,
  Send,
  FileCode,
  Brain,
  ShieldAlert,
  Sparkles,
  Crown,
  Briefcase,
  Terminal,
} from "lucide-react";
import { AgentSpatialData, SpatialTier } from "../../lib/types/office";
import { interveneOfficeAgent } from "../../lib/officeApi";

interface RoleInspectorModalProps {
  agent: AgentSpatialData | null;
  onClose: () => void;
}

export function RoleInspectorModal({ agent, onClose }: RoleInspectorModalProps) {
  const [instruction, setInstruction] = useState("");
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState("");

  if (!agent) return null;

  const handleIntervene = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!instruction.trim()) return;

    try {
      setLoading(true);
      await interveneOfficeAgent(agent.role_id, instruction.trim());
      setFeedback("Instruksi berhasil diteruskan ke agen!");
      setInstruction("");
      setTimeout(() => setFeedback(""), 3500);
    } catch (err: any) {
      setFeedback(err.message || "Gagal mengirim intervensi.");
    } finally {
      setLoading(false);
    }
  };

  const getTierBadge = (tier: SpatialTier) => {
    switch (tier) {
      case "EXECUTIVE":
        return { label: "👑 Tier 1: Executive C-Suite", color: "text-amber-400 bg-amber-500/20 border-amber-500/30" };
      case "LEAD_MANAGEMENT":
        return { label: "👔 Tier 2: Product Lead", color: "text-purple-400 bg-purple-500/20 border-purple-500/30" };
      case "WORKER_SPECIALIST":
        return { label: "💻 Tier 3: Tech Specialist", color: "text-cyan-400 bg-cyan-500/20 border-cyan-500/30" };
      default:
        return { label: "🌿 Tier 4: Commons", color: "text-emerald-400 bg-emerald-500/20 border-emerald-500/30" };
    }
  };

  const tierBadge = getTierBadge(agent.tier);

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-md flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-200">
        {/* Header Modal */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div
              className="w-10 h-10 rounded-2xl flex items-center justify-center font-bold text-white text-sm shadow-lg"
              style={{ backgroundColor: agent.color || "#06b6d4" }}
            >
              {agent.name.slice(0, 2).toUpperCase()}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white">{agent.name}</h3>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${tierBadge.color}`}>
                  {tierBadge.label}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">Role ID: {agent.role_id}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 space-y-4 text-xs">
          {/* Status Aktivitas */}
          <div className="p-3 rounded-2xl bg-slate-950/70 border border-slate-800 flex items-center justify-between">
            <span className="text-slate-400 font-semibold uppercase tracking-wider">Aktivitas Terkini</span>
            <span className="font-bold text-cyan-300 font-mono px-2 py-0.5 rounded-lg bg-cyan-950/60 border border-cyan-500/30">
              {agent.activity_state}
            </span>
          </div>

          {/* Live Scratchpad */}
          <div className="space-y-1.5">
            <div className="flex items-center space-x-1.5 text-slate-300 font-semibold">
              <Brain className="w-4 h-4 text-indigo-400" />
              <span>Live Scratchpad (Pemikiran AI)</span>
            </div>
            <div className="p-3 rounded-xl bg-black/50 border border-slate-800 text-slate-300 font-mono text-[11px] leading-relaxed">
              {agent.scratchpad || "Sedang memproses instruksi..."}
            </div>
          </div>

          {/* Active File */}
          {agent.active_file && (
            <div className="space-y-1.5">
              <div className="flex items-center space-x-1.5 text-slate-300 font-semibold">
                <FileCode className="w-4 h-4 text-emerald-400" />
                <span>Berkas Aktif Sedang Ditulis</span>
              </div>
              <div className="p-2.5 rounded-xl bg-emerald-950/30 border border-emerald-500/20 text-emerald-300 font-mono text-[11px]">
                {agent.active_file}
              </div>
            </div>
          )}

          {/* CEO Direct Intervention Form */}
          <form onSubmit={handleIntervene} className="pt-2 border-t border-slate-800/80 space-y-2">
            <label className="block text-[11px] font-semibold text-slate-300 uppercase tracking-wider">
              Intervensi Langsung CEO / Founder
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={instruction}
                onChange={(e) => setInstruction(e.target.value)}
                placeholder="Ketik arahan prioritas langsung..."
                className="flex-1 px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                disabled={loading || !instruction.trim()}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all flex items-center space-x-1 disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Kirim</span>
              </button>
            </div>
            {feedback && (
              <p className="text-[11px] text-cyan-400 font-medium animate-pulse">{feedback}</p>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
