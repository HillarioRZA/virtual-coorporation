"use client";

import { useState } from "react";
import { Users, X, ShieldAlert, Sparkles, Send, BrainCircuit } from "lucide-react";

interface OasisAllHandsWarRoomProps {
  isOpen: boolean;
  onClose: () => void;
  onDispatchPlan: (plan: string) => void;
}

export function OasisAllHandsWarRoom({
  isOpen,
  onClose,
  onDispatchPlan,
}: OasisAllHandsWarRoomProps) {
  const [executiveAgenda, setExecutiveAgenda] = useState<string>(
    "Penyelarasan Sprint Q4: Mengamankan arsitektur multi-tenant dan menyelesaikan Stage-Gate 2 tanpa regresi."
  );
  const [isSynthesizing, setIsSynthesizing] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleDispatch = () => {
    setIsSynthesizing(true);
    setTimeout(() => {
      onDispatchPlan(executiveAgenda);
      setIsSynthesizing(false);
      onClose();
    }, 1000);
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Modal Header */}
        <div className="px-5 py-4 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400">
              <Users className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide">
                Executive War Room (@all Moderator Gate)
              </h2>
              <p className="text-[11px] text-slate-400 font-mono">
                Moderated by Chief of Staff (CoS) & Chief Technology Officer (CTO)
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Executive Sparring Consensus Cards */}
        <div className="p-5 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* CoS Perspective */}
            <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-800/40 space-y-1.5">
              <div className="flex items-center space-x-2 text-xs font-bold text-amber-400">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Chief of Staff (CoS)</span>
              </div>
              <p className="text-[11px] text-slate-300 leading-relaxed font-sans">
                &ldquo;Fokuskan alokasi sumber daya pada 2 tiket kritis: Penyelesaian OpenAPI spec dan validasi keamanan Docker.&rdquo;
              </p>
            </div>

            {/* CTO Perspective */}
            <div className="p-3.5 rounded-xl bg-purple-950/20 border border-purple-800/40 space-y-1.5">
              <div className="flex items-center space-x-2 text-xs font-bold text-purple-400">
                <BrainCircuit className="w-3.5 h-3.5" />
                <span>Chief Technology Officer (CTO)</span>
              </div>
              <p className="text-[11px] text-slate-300 leading-relaxed font-sans">
                &ldquo;Lintas dependensi frontend & backend harus dikunci via contract-first. Hindari waking 12 worker agents.&rdquo;
              </p>
            </div>
          </div>

          {/* Formulated Directive Input */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">
              Formulated Action Plan Directive:
            </label>
            <textarea
              rows={3}
              value={executiveAgenda}
              onChange={(e) => setExecutiveAgenda(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-amber-500 transition-colors leading-relaxed"
            />
          </div>

          {/* Token Guard Notice */}
          <div className="flex items-center space-x-2 p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-[11px] text-slate-400">
            <ShieldAlert className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>
              Executive Gate memastikan arahan didistribusikan secara terukur tanpa memicu 12 pemanggilan LLM konkuren.
            </span>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-5 py-3 border-t border-slate-800 bg-slate-950/40 flex items-center justify-end space-x-2">
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            Batal
          </button>
          <button
            onClick={handleDispatch}
            disabled={!executiveAgenda.trim() || isSynthesizing}
            className="flex items-center space-x-1.5 px-4 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-40 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 active:scale-95 transition-all"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{isSynthesizing ? "Menyiarkan..." : "🚀 Dispatch Action Plan"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
