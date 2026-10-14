"use client";

import React, { useState } from "react";
import { X, Sparkles, Plus, Loader2 } from "lucide-react";
import { WisdomCreate, WisdomItem, WisdomNamespace } from "@/lib/types/wisdom";
import { createWisdom } from "@/lib/wisdomApi";

interface WisdomModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: (item: WisdomItem) => void;
}

export function WisdomModal({ isOpen, onClose, onCreated }: WisdomModalProps) {
  const [title, setTitle] = useState("");
  const [namespace, setNamespace] = useState<WisdomNamespace>("wisdom:architecture");
  const [problemPattern, setProblemPattern] = useState("");
  const [solutionGuideline, setSolutionGuideline] = useState("");
  const [tagsInput, setTagsInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !problemPattern.trim() || !solutionGuideline.trim()) {
      setError("Seluruh field wajib diisi.");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const tags = tagsInput
        .split(",")
        .map((t) => t.trim().toLowerCase())
        .filter((t) => t.length > 0);

      const payload: WisdomCreate = {
        title: title.trim(),
        namespace,
        problem_pattern: problemPattern.trim(),
        solution_guideline: solutionGuideline.trim(),
        tags,
        source_venture_id: "global",
      };

      const newItem = await createWisdom(payload);
      onCreated(newItem);
      onClose();
      // Reset form
      setTitle("");
      setProblemPattern("");
      setSolutionGuideline("");
      setTagsInput("");
    } catch (err: any) {
      setError(err.message || "Gagal menyimpan wisdom.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
      <div className="liquid-glass border border-white/10 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
        <div className="flex items-center justify-between p-5 border-b border-white/10 bg-white/[0.02]">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Sparkles className="w-4 h-4" />
            </div>
            <h2 className="text-base font-bold text-white tracking-tight">Tambah Wisdom Institusional Baru</h2>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {error && <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-300 text-xs">{error}</div>}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Judul Guideline / Best Practice</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Single Responsibility Modularization Pattern"
              className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Namespace Kategori</label>
            <select
              value={namespace}
              onChange={(e) => setNamespace(e.target.value as WisdomNamespace)}
              className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-indigo-500"
            >
              <option value="wisdom:architecture">wisdom:architecture (Pola Desain & Rekayasa Sistem)</option>
              <option value="wisdom:bugs_and_fixes">wisdom:bugs_and_fixes (Penanganan Error & Vulnerability)</option>
              <option value="wisdom:growth_copy">wisdom:growth_copy (Pola Copywriting & Growth)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Problem Pattern (Gejala / Kendala)</label>
            <textarea
              value={problemPattern}
              onChange={(e) => setProblemPattern(e.target.value)}
              placeholder="Jelaskan pola masalah yang sering muncul..."
              rows={2}
              className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Solution Guideline (Arahan Preskriptif)</label>
            <textarea
              value={solutionGuideline}
              onChange={(e) => setSolutionGuideline(e.target.value)}
              placeholder="Arahan solusi teknis preskriptif yang harus dipatuhi peran AI..."
              rows={2}
              className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Tags (Pisahkan dengan koma)</label>
            <input
              type="text"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              placeholder="architecture, srp, refactor, security"
              className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="pt-2 flex items-center justify-end space-x-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded-xl text-xs text-slate-400 hover:text-white">Batal</button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="liquid-chrome-btn px-4 py-2 rounded-xl text-xs font-semibold text-black inline-flex items-center space-x-1.5"
            >
              {isSubmitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
              <span>Simpan ke Memory</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
