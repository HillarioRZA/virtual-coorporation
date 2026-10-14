"use client";

import React from "react";
import { GitBranch, GitFork, GitMerge, CheckCircle2, Trash2, FolderPlus } from "lucide-react";
import { BranchResponse } from "@/lib/types/corporate";

interface BranchBarProps {
  branches: BranchResponse[];
  selectedBranch: BranchResponse | null;
  onSelectBranch: (branchId: string) => void;
  onOpenForkModal: () => void;
  onOpenDivisionModal: () => void;
  onActivateBranch: (branchId: string) => void;
  onDeleteBranch: (branchId: string) => void;
  onOpenMergeModal?: () => void;
}

export default function BranchBar({
  branches,
  selectedBranch,
  onSelectBranch,
  onOpenForkModal,
  onOpenDivisionModal,
  onActivateBranch,
  onDeleteBranch,
  onOpenMergeModal,
}: BranchBarProps) {
  const isMain = selectedBranch ? selectedBranch.slug === "main" : true;
  const isActive = selectedBranch ? Boolean(selectedBranch.is_active_main) : true;

  return (
    <div className="rounded-2xl bg-white/[0.03] border border-white/10 p-4 backdrop-blur-xl flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center space-x-2 bg-white/5 border border-white/10 px-3 py-1.5 rounded-xl">
          <GitBranch className="w-4 h-4 text-purple-400" />
          <span className="text-xs font-medium text-slate-300">Alur Kerja:</span>
          <select
            value={selectedBranch?.id || ""}
            onChange={(e) => onSelectBranch(e.target.value)}
            disabled={branches.length === 0}
            className="bg-transparent text-xs font-mono font-semibold text-white focus:outline-none cursor-pointer"
          >
            {branches.length === 0 ? (
              <option value="" className="bg-[#0c0d14] text-white">
                Memuat branch...
              </option>
            ) : (
              branches.map((b) => (
                <option key={b.id} value={b.id} className="bg-[#0c0d14] text-white">
                  {b.name} {b.is_active_main ? "★ (Active Main)" : ""}
                </option>
              ))
            )}
          </select>
        </div>

        {isActive ? (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Active Main
          </span>
        ) : (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-[11px] font-mono">
            Draft / Experiment
          </span>
        )}

        {selectedBranch?.description && (
          <span className="text-xs text-slate-400 italic hidden lg:inline max-w-xs truncate">
            {selectedBranch.description}
          </span>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <button
          onClick={onOpenForkModal}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-300 text-xs font-medium transition-all"
        >
          <GitFork className="w-3.5 h-3.5" />
          <span>Fork Workflow</span>
        </button>

        {!isMain && selectedBranch && onOpenMergeModal && (
          <button
            onClick={onOpenMergeModal}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/40 text-purple-200 text-xs font-medium transition-all shadow-lg shadow-purple-900/20"
            title="Gabungkan branch ini ke Main (Autonomous 3-Way Merge)"
          >
            <GitMerge className="w-3.5 h-3.5 text-purple-400" />
            <span>Merge ke Main</span>
          </button>
        )}

        {!isActive && selectedBranch && (
          <button
            onClick={() => onActivateBranch(selectedBranch.id)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-medium transition-all"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Aktifkan sebagai Main</span>
          </button>
        )}

        {!isMain && !isActive && selectedBranch && (
          <button
            onClick={() => onDeleteBranch(selectedBranch.id)}
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-xl hover:bg-rose-500/10 border border-transparent hover:border-rose-500/20 text-rose-400 text-xs transition-all"
            title="Hapus branch eksperimen ini"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        )}

        <button
          onClick={onOpenDivisionModal}
          className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/15 border border-white/20 text-white text-xs font-medium transition-all shadow-lg"
        >
          <FolderPlus className="w-3.5 h-3.5 text-slate-300" />
          <span>+ Tambah Divisi</span>
        </button>
      </div>
    </div>
  );
}
