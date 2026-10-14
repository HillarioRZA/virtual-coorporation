"use client";

import React from "react";
import { ShieldCheck, Lock } from "lucide-react";

interface PreviewGateDecisionsProps {
  isGate2Waiting: boolean;
  isGate3Waiting: boolean;
  gateFeedback: string;
  setGateFeedback: (val: string) => void;
  handleGateDecision: (action: "APPROVE" | "REVISE" | "KILL") => void;
  isProcessingGate: boolean;
  onOpenVault: () => void;
}

/**
 * Renders the Founder/CEO Stage-Gate 2 and Stage-Gate 3 decision cards.
 */
export const PreviewGateDecisions: React.FC<PreviewGateDecisionsProps> = ({
  isGate2Waiting,
  isGate3Waiting,
  gateFeedback,
  setGateFeedback,
  handleGateDecision,
  isProcessingGate,
  onOpenVault,
}) => {
  return (
    <>
      {/* Stage-Gate 2 Decision Card */}
      <div
        className={`p-5 rounded-2xl border transition-all ${
          isGate2Waiting ? "glass-panel-glow border-emerald-500/40" : "glass-panel border-slate-800"
        }`}
      >
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h3 className="text-sm font-bold text-white">Stage-Gate 2: Demo Day Validation</h3>
          </div>
          {isGate2Waiting && (
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 animate-pulse">
              Ready for Decision
            </span>
          )}
        </div>

        <p className="text-xs text-slate-400 mt-2">
          Uji coba prototipe visual mock di sisi kiri. Putuskan apakah prototipe siap melangkah ke industrialisasi backend produksi.
        </p>

        <div className="mt-3">
          <label className="block text-[11px] font-semibold text-slate-300 mb-1 uppercase tracking-wider">
            Catatan Umpan Balik (Founder Feedback):
          </label>
          <textarea
            rows={2}
            value={gateFeedback}
            onChange={(e) => setGateFeedback(e.target.value)}
            placeholder="Catatan perbaikan jika meminta revisi UI mock..."
            className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        <div className="flex flex-wrap items-center justify-end gap-2 mt-3 pt-3 border-t border-slate-800/80">
          <button
            type="button"
            onClick={() => handleGateDecision("KILL")}
            disabled={isProcessingGate}
            className="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-400 text-xs font-semibold"
          >
            KILL
          </button>
          <button
            type="button"
            onClick={() => handleGateDecision("REVISE")}
            disabled={isProcessingGate}
            className="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-semibold"
          >
            REVISE
          </button>
          <button
            type="button"
            onClick={() => handleGateDecision("APPROVE")}
            disabled={isProcessingGate}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-500/20"
          >
            APPROVE (Stage 3 Production)
          </button>
        </div>
      </div>

      {/* Stage-Gate 3 Decision Card */}
      {isGate3Waiting && (
        <div className="p-5 rounded-2xl border glass-panel-glow border-indigo-500/40 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <Lock className="w-5 h-5 text-indigo-400" />
              <h3 className="text-sm font-bold text-white">Stage-Gate 3: Production Vault & PaaS Deploy</h3>
            </div>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 animate-pulse">
              Ready for Deploy
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Kode backend FastAPI dan audit keamanan OWASP telah selesai. Pastikan kredensial telah disimpan di Secret Vault sebelum deployment.
          </p>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onOpenVault}
              className="w-full py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-200 flex items-center justify-center gap-1.5"
            >
              <Lock className="w-3.5 h-3.5 text-indigo-400" />
              <span>Buka Secret Vault (AES-256)</span>
            </button>
          </div>
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800/80">
            <button
              type="button"
              onClick={() => handleGateDecision("KILL")}
              disabled={isProcessingGate}
              className="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-400 text-xs font-semibold"
            >
              KILL
            </button>
            <button
              type="button"
              onClick={() => handleGateDecision("REVISE")}
              disabled={isProcessingGate}
              className="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-semibold"
            >
              REVISE
            </button>
            <button
              type="button"
              onClick={() => handleGateDecision("APPROVE")}
              disabled={isProcessingGate}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-500/20"
            >
              APPROVE (Deploy to PaaS)
            </button>
          </div>
        </div>
      )}
    </>
  );
};
