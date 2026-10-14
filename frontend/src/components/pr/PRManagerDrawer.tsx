"use client";

import React, { useEffect, useState } from "react";
import { GitPullRequest, GitMerge, CheckCircle2, Clock, Plus, ExternalLink } from "lucide-react";
import { PullRequestResponse } from "@/lib/types/pullRequest";
import { fetchProjectPRs } from "@/lib/prApi";
import { PRReviewModal } from "./PRReviewModal";

interface PRManagerDrawerProps {
  projectId: string;
  isOpen: boolean;
  onClose: () => void;
}

export const PRManagerDrawer: React.FC<PRManagerDrawerProps> = ({ projectId, isOpen, onClose }) => {
  const [prs, setPrs] = useState<PullRequestResponse[]>([]);
  const [selectedPR, setSelectedPR] = useState<PullRequestResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const loadPRs = async () => {
    if (!projectId) return;
    setLoading(true);
    try {
      const data = await fetchProjectPRs(projectId);
      setPrs(data);
    } catch {
      // Ignore initial error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) loadPRs();
  }, [isOpen, projectId]);

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="fixed top-0 right-0 bottom-0 z-50 w-full max-w-md bg-zinc-900 border-l border-zinc-800 shadow-2xl p-6 flex flex-col space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <GitPullRequest className="w-4 h-4" />
            </span>
            <h3 className="text-sm font-bold text-white font-mono">PULL REQUESTS & PEER REVIEWS</h3>
          </div>
          <button onClick={onClose} className="text-xs text-zinc-400 hover:text-white">✕</button>
        </div>

        {prs.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-6 text-xs text-zinc-500 border border-dashed border-zinc-800 rounded-2xl">
            <GitPullRequest className="w-8 h-8 text-zinc-600 mb-2" />
            <p>Belum ada Pull Request internal.</p>
            <p className="text-[11px] text-zinc-600 mt-1">
              PR dibuat otomatis saat karyawan AI menyelesaikan sintesis kode tiket.
            </p>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto space-y-2.5">
            {prs.map((pr) => (
              <div
                key={pr.id}
                onClick={() => setSelectedPR(pr)}
                className="p-3 rounded-xl bg-zinc-950/60 border border-zinc-800/80 hover:border-purple-500/50 cursor-pointer transition-all space-y-1.5"
              >
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-xs font-semibold text-white truncate">{pr.title}</h4>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border shrink-0 ${
                    pr.status === "MERGED" ? "bg-purple-500/10 border-purple-500/20 text-purple-400" :
                    pr.status === "APPROVED" ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" :
                    "bg-amber-500/10 border-amber-500/20 text-amber-400"
                  }`}>
                    {pr.status}
                  </span>
                </div>
                <div className="flex items-center justify-between text-[11px] font-mono text-zinc-400">
                  <span>{pr.source_branch}</span>
                  <span className="text-emerald-400">+{pr.additions_count} <span className="text-rose-400">-{pr.deletions_count}</span></span>
                </div>
                <div className="text-[10px] text-zinc-500 font-mono flex items-center justify-between pt-1 border-t border-zinc-850">
                  <span>Kuorum: {pr.approvals_count}/{pr.quorum_required} Approved</span>
                  <span>Oleh: {pr.author_role_id}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="pt-2 border-t border-zinc-800 flex justify-end">
          <button onClick={onClose} className="px-4 py-1.5 rounded-xl bg-zinc-800 text-xs text-zinc-300 hover:text-white">
            Tutup
          </button>
        </div>
      </div>

      {selectedPR && (
        <PRReviewModal
          pr={selectedPR}
          isOpen={!!selectedPR}
          onClose={() => setSelectedPR(null)}
          onRefresh={() => {
            loadPRs();
            setSelectedPR(null);
          }}
        />
      )}
    </>
  );
};
