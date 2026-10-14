"use client";

import React, { useState, useEffect } from "react";
import { GitMerge, X, AlertTriangle, Zap, CheckCircle2, RefreshCw } from "lucide-react";
import { BranchResponse } from "@/lib/types/corporate";
import { MergeStrategy, MergePreviewResponse } from "@/lib/types/branchMerge";
import { previewBranchMerge, executeBranchMerge } from "@/lib/branchMergeApi";

interface BranchMergeModalProps {
  isOpen: boolean;
  sourceBranch: BranchResponse | null;
  onClose: () => void;
  onMerged: () => void;
}

export default function BranchMergeModal({
  isOpen,
  sourceBranch,
  onClose,
  onMerged,
}: BranchMergeModalProps) {
  const [loading, setLoading] = useState(false);
  const [merging, setMerging] = useState(false);
  const [preview, setPreview] = useState<MergePreviewResponse | null>(null);
  const [strategy, setStrategy] = useState<MergeStrategy>("auto");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchPreview = async (branchId: string, strat: MergeStrategy) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const data = await previewBranchMerge(branchId, "branch_main", strat);
      setPreview(data);
      if (data.has_conflicts && strat === "auto") {
        setStrategy("prefer_theirs");
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Gagal memuat preview merge.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && sourceBranch) {
      setStrategy("auto");
      fetchPreview(sourceBranch.id, "auto");
    } else {
      setPreview(null);
      setErrorMsg(null);
    }
  }, [isOpen, sourceBranch]);

  if (!isOpen || !sourceBranch) return null;

  const handleExecute = async () => {
    setMerging(true);
    setErrorMsg(null);
    try {
      await executeBranchMerge(sourceBranch.id, "branch_main", strategy);
      onMerged();
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || "Gagal mengeksekusi merge.");
    } finally {
      setMerging(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-lg rounded-2xl bg-slate-900 border border-white/10 shadow-2xl p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-2.5">
            <span className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <GitMerge className="w-5 h-5" />
            </span>
            <div>
              <h3 className="text-sm font-semibold text-white">Merge Branch ke Main</h3>
              <p className="text-[11px] text-slate-400">
                Menggabungkan <code className="text-purple-300">{sourceBranch.name}</code> ke baseline <code className="text-emerald-300">branch_main</code>
              </p>
            </div>
          </div>
          <button type="button" onClick={onClose} className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5">
            <X className="w-4 h-4" />
          </button>
        </div>

        {errorMsg && (
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
            {errorMsg}
          </div>
        )}

        {loading ? (
          <div className="py-10 text-center space-y-2">
            <RefreshCw className="w-5 h-5 text-indigo-400 animate-spin mx-auto" />
            <p className="text-xs text-slate-400">Menganalisis Lowest Common Ancestor (LCA) & simulasi 3-way diff...</p>
          </div>
        ) : preview ? (
          <div className="space-y-3.5 text-xs">
            {preview.can_fast_forward && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 flex items-center gap-2">
                <Zap className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span><strong>Fast-Forward Clean Merge.</strong> Tidak ada konflik konfigurasi dengan branch main.</span>
              </div>
            )}

            {preview.has_conflicts && (
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 space-y-2">
                <div className="flex items-center gap-2 font-medium">
                  <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                  <span>Ditemukan {preview.conflicts.length} Konflik Konfigurasi Peran</span>
                </div>
                <div className="space-y-1.5">
                  {preview.conflicts.map((c) => (
                    <div key={c.slug} className="p-2 rounded-lg bg-black/40 border border-white/5 space-y-1">
                      <div className="font-semibold text-white">Peran: {c.slug}</div>
                      <div className="grid grid-cols-2 gap-2 text-[10px]">
                        <div className="text-slate-400">Ours (Main): <span className="text-emerald-400 font-mono">{c.ours.model}</span></div>
                        <div className="text-slate-400">Theirs ({sourceBranch.slug}): <span className="text-purple-400 font-mono">{c.theirs.model}</span></div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="pt-2 border-t border-amber-500/20 space-y-1">
                  <label className="text-[11px] font-semibold text-white">Pilih Strategi Resolusi:</label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-1.5 text-slate-300 cursor-pointer">
                      <input type="radio" name="strategy" value="prefer_theirs" checked={strategy === "prefer_theirs"} onChange={() => setStrategy("prefer_theirs")} />
                      <span>Prefer Theirs ({sourceBranch.name})</span>
                    </label>
                    <label className="flex items-center gap-1.5 text-slate-300 cursor-pointer">
                      <input type="radio" name="strategy" value="prefer_ours" checked={strategy === "prefer_ours"} onChange={() => setStrategy("prefer_ours")} />
                      <span>Prefer Ours (Main)</span>
                    </label>
                  </div>
                </div>
              </div>
            )}

            <div className="rounded-xl bg-white/[0.02] border border-white/5 p-3 space-y-1.5">
              <div className="text-slate-400">Ringkasan Perubahan:</div>
              <ul className="list-disc list-inside space-y-0.5 text-slate-300">
                <li>Peran baru ditambahkan: <strong>{preview.added_roles.length}</strong></li>
                <li>Peran diperbarui: <strong>{preview.updated_roles.length}</strong></li>
              </ul>
            </div>
          </div>
        ) : null}

        <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-white/10">
          <button type="button" onClick={onClose} disabled={merging} className="px-4 py-2 rounded-xl border border-white/10 hover:bg-white/5 text-xs text-slate-300">
            Batal
          </button>
          <button
            type="button"
            onClick={handleExecute}
            disabled={loading || merging || !preview}
            className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium text-xs flex items-center gap-1.5 shadow-lg shadow-purple-600/20 disabled:opacity-50"
          >
            <GitMerge className="w-3.5 h-3.5" />
            {merging ? "Menggabungkan..." : "Konfirmasi & Merge"}
          </button>
        </div>
      </div>
    </div>
  );
}
