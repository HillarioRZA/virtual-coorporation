"use client";

import React, { useState } from "react";
import { GitFork, X, AlertCircle } from "lucide-react";
import { BranchResponse } from "@/lib/types/corporate";
import { forkBranch } from "@/lib/corporateApi";

interface BranchForkModalProps {
  isOpen: boolean;
  sourceBranch: BranchResponse | null;
  onClose: () => void;
  onSuccess: (newBranch: BranchResponse) => void;
}

export default function BranchForkModal({
  isOpen,
  sourceBranch,
  onClose,
  onSuccess,
}: BranchForkModalProps) {
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !sourceBranch) return null;

  const handleNameChange = (val: string) => {
    setName(val);
    const generatedSlug = val
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "");
    setSlug(generatedSlug);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !slug.trim()) {
      setError("Nama dan slug branch wajib diisi.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const created = await forkBranch({
        name: name.trim(),
        slug: slug.trim(),
        description: description.trim() || undefined,
        source_branch_id: sourceBranch.id,
      });
      setName("");
      setSlug("");
      setDescription("");
      onSuccess(created);
      onClose();
    } catch (err: any) {
      setError(err.message || "Gagal melakukan fork workflow.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-fade-in">
      <div className="w-full max-w-md rounded-2xl bg-[#0c0d14]/95 border border-white/10 shadow-2xl p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <GitFork className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white font-sans">Fork Workflow Branch</h3>
            <p className="text-xs text-slate-400">
              Kloning dari: <span className="font-mono text-purple-300">{sourceBranch.name}</span>
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center gap-2 text-rose-300 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Nama Branch Baru</label>
            <input
              type="text"
              required
              placeholder="e.g. Agile Scrum Experiment"
              value={name}
              onChange={(e) => handleNameChange(e.target.value)}
              className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-purple-500/50"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Slug Identifier</label>
            <input
              type="text"
              required
              placeholder="e.g. agile-scrum-experiment"
              value={slug}
              onChange={(e) => setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9_-]/g, ""))}
              className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-purple-300 font-mono text-xs placeholder:text-slate-500 focus:outline-none focus:border-purple-500/50"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Deskripsi Tujuan (Opsional)</label>
            <textarea
              rows={2}
              placeholder="Tujuan forking workflow alur kerja ini..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-purple-500/50"
            />
          </div>

          <div className="pt-2 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white rounded-xl hover:bg-white/5 transition-colors"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-xs font-medium text-white bg-purple-600 hover:bg-purple-500 rounded-xl transition-all shadow-lg shadow-purple-600/20 disabled:opacity-50"
            >
              {loading ? "Menduplikasi..." : "Fork Branch"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
