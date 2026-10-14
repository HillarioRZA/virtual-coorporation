"use client";

import React, { useState } from "react";
import { GitPullRequest, GitMerge, ShieldCheck, CheckCircle2, AlertTriangle, X, Play, Code2 } from "lucide-react";
import { PullRequestResponse } from "@/lib/types/pullRequest";
import { triggerAutonomousReview, mergePullRequest } from "@/lib/prApi";
import { DiffViewer } from "./DiffViewer";

interface PRReviewModalProps {
  pr: PullRequestResponse | null;
  isOpen: boolean;
  onClose: () => void;
  onRefresh: () => void;
}

export const PRReviewModal: React.FC<PRReviewModalProps> = ({ pr, isOpen, onClose, onRefresh }) => {
  const [activeTab, setActiveTab] = useState<"diff" | "reviews">("reviews");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !pr) return null;

  const handleRunAutoReview = async () => {
    setLoading(true);
    setError(null);
    try {
      await triggerAutonomousReview(pr.id);
      onRefresh();
    } catch (err: any) {
      setError(err.message || "Gagal menjalankan auto-review.");
    } finally {
      setLoading(false);
    }
  };

  const handleMerge = async (force: boolean = false) => {
    setLoading(true);
    setError(null);
    try {
      await mergePullRequest(pr.id, force);
      onRefresh();
      onClose();
    } catch (err: any) {
      setError(err.message || "Gagal me-merge PR.");
    } finally {
      setLoading(false);
    }
  };

  const isApproved = pr.status === "APPROVED";
  const isMerged = pr.status === "MERGED";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
      <div className="w-full max-w-3xl rounded-2xl bg-zinc-900/95 border border-zinc-800 shadow-2xl p-6 relative max-h-[90vh] flex flex-col">
        <button onClick={onClose} className="absolute top-4 right-4 text-zinc-400 hover:text-white"><X className="w-5 h-5" /></button>

        {/* Header */}
        <div className="flex items-center gap-3 pb-4 border-b border-zinc-800">
          <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <GitPullRequest className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-white">{pr.title}</h2>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                isMerged ? "bg-purple-500/10 border-purple-500/30 text-purple-300" :
                isApproved ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300" :
                pr.status === "CHANGES_REQUESTED" ? "bg-rose-500/10 border-rose-500/30 text-rose-300" :
                "bg-amber-500/10 border-amber-500/30 text-amber-300"
              }`}>{pr.status}</span>
            </div>
            <p className="text-xs text-zinc-400 font-mono mt-0.5">
              {pr.source_branch} ➔ {pr.target_branch} • Kuorum: {pr.approvals_count}/{pr.quorum_required} Approval
            </p>
          </div>
        </div>

        {error && (
          <div className="mt-3 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
            {error}
          </div>
        )}

        {/* Tab Selector */}
        <div className="flex items-center gap-2 pt-3 pb-2 text-xs">
          <button
            onClick={() => setActiveTab("reviews")}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === "reviews" ? "bg-zinc-800 text-white font-medium" : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Peer Reviews ({pr.reviews?.length || 0})
          </button>
          <button
            onClick={() => setActiveTab("diff")}
            className={`px-3 py-1.5 rounded-lg transition ${
              activeTab === "diff" ? "bg-zinc-800 text-white font-medium" : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            Files & Diff (+{pr.additions_count}, -{pr.deletions_count})
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto py-2 space-y-3">
          {activeTab === "diff" ? (
            <DiffViewer diffText={pr.diff_unified} />
          ) : (
            <div className="space-y-3">
              {(!pr.reviews || pr.reviews.length === 0) ? (
                <div className="py-8 text-center text-xs text-zinc-500 border border-dashed border-zinc-800 rounded-xl">
                  Belum ada ulasan rekanan. Klik &quot;Jalankan P2P Review&quot; untuk memulai audit otomatis.
                </div>
              ) : (
                pr.reviews.map((rev) => (
                  <div key={rev.id} className="p-3.5 rounded-xl bg-zinc-950/60 border border-zinc-800/80 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-white">{rev.reviewer_name}</span>
                        <span className="text-[10px] text-zinc-500 font-mono">[{rev.reviewer_role_id}]</span>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
                        rev.verdict === "APPROVED" ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" :
                        "bg-rose-500/10 border-rose-500/20 text-rose-400"
                      }`}>{rev.verdict} (Score: {rev.security_score}/100)</span>
                    </div>
                    <p className="text-zinc-300 text-xs">{rev.summary}</p>

                    {/* Inline suggestions */}
                    {rev.inline_comments && rev.inline_comments.length > 0 && (
                      <div className="mt-2 space-y-1.5 pt-2 border-t border-zinc-800/60">
                        {rev.inline_comments.map((c, i) => (
                          <div key={i} className="p-2 rounded bg-zinc-900 border border-zinc-800 text-[11px]">
                            <div className="text-zinc-400 font-mono">{c.file_path}:{c.line_number}</div>
                            <div className="text-zinc-200 mt-0.5">{c.comment}</div>
                            {c.code_suggestion && (
                              <div className="mt-1 font-mono text-emerald-400 bg-emerald-950/20 p-1 rounded">
                                Saran: {c.code_suggestion}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="pt-4 border-t border-zinc-800 flex items-center justify-between">
          <button
            onClick={handleRunAutoReview}
            disabled={loading || isMerged}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 text-xs transition disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5" />
            Jalankan P2P Review
          </button>
          <div className="flex items-center gap-2">
            <button onClick={onClose} className="px-3 py-1.5 text-xs text-zinc-400 hover:text-white">Tutup</button>
            {!isMerged && (
              <button
                onClick={() => handleMerge(false)}
                disabled={loading || !isApproved}
                className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-lg shadow-purple-600/20 transition disabled:opacity-40"
              >
                <GitMerge className="w-3.5 h-3.5" />
                Merge PR (Quorum)
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
