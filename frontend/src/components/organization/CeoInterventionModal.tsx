"use client";

import React, { useState } from "react";
import { Crown, AlertTriangle, CheckCircle, X, ShieldAlert, ArrowRight, Send } from "lucide-react";
import { executeCeoOverride, submitCeoDecision } from "@/lib/governanceApi";
import { ExecutiveEscalationReport } from "@/lib/types/corporate";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  ticketId?: string;
  projectId: string;
  branchId?: string;
  escalationReport?: ExecutiveEscalationReport | null;
  onActionComplete?: () => void;
}

export default function CeoInterventionModal({
  isOpen,
  onClose,
  ticketId,
  projectId,
  branchId = "branch_main",
  escalationReport,
  onActionComplete,
}: Props) {
  const [overrideAction, setOverrideAction] = useState<"FORCE_PROCEED" | "INTERVENE" | "REASSIGN">("FORCE_PROCEED");
  const [directive, setDirective] = useState("");
  const [selectedOption, setSelectedOption] = useState<string>("");
  const [ceoFeedback, setCeoFeedback] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleExecuteOverride = async () => {
    if (!ticketId) return;
    setSubmitting(true);
    try {
      await executeCeoOverride({
        ticket_id: ticketId,
        project_id: projectId,
        branch_id: branchId,
        override: {
          action: overrideAction,
          directive: directive.trim() || undefined,
        },
      });
      alert("Hak Veto CEO Berhasil Diterapkan.");
      if (onActionComplete) onActionComplete();
      onClose();
    } catch (err: any) {
      alert(err.message || "Gagal menerapkan hak veto CEO.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleExecuteDecision = async () => {
    if (!escalationReport?.id || !selectedOption) {
      alert("Pilih salah satu opsi solusi terlebih dahulu.");
      return;
    }
    setSubmitting(true);
    try {
      await submitCeoDecision({
        report_id: escalationReport.id,
        project_id: projectId,
        branch_id: branchId,
        decision: {
          selected_option_id: selectedOption,
          feedback: ceoFeedback.trim() || undefined,
        },
      });
      alert(`Keputusan CEO [OPSI ${selectedOption}] Berhasil Disiarkan ke Direksi.`);
      if (onActionComplete) onActionComplete();
      onClose();
    } catch (err: any) {
      alert(err.message || "Gagal menetapkan keputusan CEO.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in">
      <div className="relative w-full max-w-lg rounded-2xl bg-slate-900 border-2 border-amber-500/50 shadow-2xl shadow-amber-500/20 p-6 space-y-5 text-white">
        {/* Header Modal */}
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-2.5">
            <span className="p-2 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-300">
              <Crown className="w-5 h-5" />
            </span>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                CEO Control Tower & Governance Hub
              </h3>
              <p className="text-xs text-amber-300/80">Hak Veto Pendiri & Pengambilan Keputusan Strategis</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab / Mode: C-Level Escalation vs Circuit Breaker */}
        {escalationReport ? (
          <div className="space-y-4">
            <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs space-y-2">
              <div className="flex items-center gap-1.5 text-amber-400 font-bold uppercase tracking-wider text-[11px]">
                <ShieldAlert className="w-4 h-4" />
                Laporan Eskalasi Direksi [{escalationReport.reporter_role.toUpperCase()}]
              </div>
              <h4 className="font-semibold text-white text-sm">{escalationReport.title}</h4>
              <p className="text-slate-300">{escalationReport.summary}</p>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Pilih Solusi Strategis (1-Click Decision):</label>
              <div className="space-y-2">
                {escalationReport.options.map((opt) => (
                  <div
                    key={opt.option_id}
                    onClick={() => setSelectedOption(opt.option_id)}
                    className={`p-3 rounded-xl border cursor-pointer transition-all ${
                      selectedOption === opt.option_id
                        ? "bg-amber-500/20 border-amber-400 ring-2 ring-amber-400/30 text-white"
                        : "bg-white/[0.02] border-white/10 hover:border-white/20 text-slate-300"
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs font-bold">
                      <span className="flex items-center gap-1.5 text-amber-300">
                        Opsi {opt.option_id}: {opt.label}
                      </span>
                      {selectedOption === opt.option_id && <CheckCircle className="w-4 h-4 text-amber-400" />}
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1">{opt.impact}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300">Arahan Tambahan CEO (Opsional):</label>
              <input
                type="text"
                value={ceoFeedback}
                onChange={(e) => setCeoFeedback(e.target.value)}
                placeholder="Misal: Prioritaskan kecepatan deploy untuk demo investor..."
                className="mt-1 w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-400"
              />
            </div>

            <button
              onClick={handleExecuteDecision}
              disabled={submitting || !selectedOption}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-yellow-600 hover:from-amber-400 hover:to-yellow-500 disabled:opacity-50 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-amber-500/25 transition-all"
            >
              <Send className="w-4 h-4" />
              {submitting ? "Memproses Keputusan..." : `Tetapkan Opsi [${selectedOption || "?"}] & Lanjutkan`}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-xs space-y-1.5">
              <div className="flex items-center gap-1.5 text-red-400 font-bold uppercase tracking-wider text-[11px]">
                <AlertTriangle className="w-4 h-4" />
                Anti-Infinite Loop Circuit Breaker Triggered
              </div>
              <p className="text-slate-300">
                Agen AI telah berdiskusi $\ge 3$ putaran berturut-turut tanpa progres kode baru pada tiket{" "}
                <span className="font-mono text-amber-300">{ticketId}</span>. Sistem telah membekukan tugas untuk
                mencegah pemborosan token.
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Pilih Tindakan Intervensi:</label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { id: "FORCE_PROCEED", label: "Force Proceed", desc: "Bypass & paksa selesai" },
                  { id: "INTERVENE", label: "Intervene", desc: "Beri arahan teks langsung" },
                  { id: "REASSIGN", label: "Reassign", desc: "Kembalikan ke antrean TODO" },
                ].map((act) => (
                  <button
                    key={act.id}
                    onClick={() => setOverrideAction(act.id as any)}
                    className={`p-2.5 rounded-xl border text-left transition-all ${
                      overrideAction === act.id
                        ? "bg-amber-500/20 border-amber-400 text-white"
                        : "bg-white/[0.02] border-white/10 text-slate-400 hover:text-white"
                    }`}
                  >
                    <div className="text-xs font-semibold">{act.label}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{act.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {overrideAction === "INTERVENE" && (
              <div>
                <label className="text-xs font-medium text-slate-300">Instruksi Mandat CEO:</label>
                <textarea
                  rows={2}
                  value={directive}
                  onChange={(e) => setDirective(e.target.value)}
                  placeholder="Instruksikan solusi konkret kepada agen (e.g. Gunakan HttpOnly Cookie)..."
                  className="mt-1 w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-400"
                />
              </div>
            )}

            <button
              onClick={handleExecuteOverride}
              disabled={submitting}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-yellow-600 hover:from-amber-400 hover:to-yellow-500 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-amber-500/25 transition-all"
            >
              <Crown className="w-4 h-4" />
              {submitting ? "Mengeksekusi..." : "Terapkan Hak Veto CEO"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
