"use client";

import React, { useState } from "react";
import { X, Layers, Sparkles } from "lucide-react";
import { PipelineCreate, ProductLineType } from "@/lib/types/corporate";

interface PipelineModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: PipelineCreate) => Promise<void>;
}

const PRODUCT_LINES: { value: ProductLineType; label: string; desc: string }[] = [
  { value: "SOFTWARE", label: "Software & SaaS", desc: "Produk rekayasa perangkat lunak, web, mobile, dan API." },
  { value: "EDUCATION", label: "Edukasi & Kursus", desc: "Produk kurikulum, video tutorial, modul pelatihan & sertifikasi." },
  { value: "COPYWRITING", label: "Copywriting & Konten", desc: "Kampanye pemasaran, artikel SEO, sales letter & media sosial." },
  { value: "MARKET_RESEARCH", label: "Riset Pasar", desc: "Laporan analisis kompetitor, survei pasar, dan validasi audiens." },
  { value: "CUSTOM", label: "Kustom / Lainnya", desc: "Alur kerja lintas divisi yang disesuaikan secara bebas." },
];

export default function PipelineModal({ isOpen, onClose, onSubmit }: PipelineModalProps) {
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [productLine, setProductLine] = useState<ProductLineType>("EDUCATION");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleNameChange = (val: string) => {
    setName(val);
    setSlug(val.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !slug.trim()) return;
    setSubmitting(true);
    try {
      await onSubmit({
        name: name.trim(),
        slug: slug.trim(),
        product_line: productLine,
        description: description.trim() || undefined,
      });
      setName("");
      setSlug("");
      setDescription("");
      onClose();
    } catch {
      // Handled by parent
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-md rounded-2xl bg-slate-900 border border-white/10 p-6 shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-white/5 pb-3">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Layers className="w-4 h-4" />
            </span>
            <h3 className="text-sm font-semibold text-white">Buat Pipeline Produk Baru</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3.5">
          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">Nama Pipeline</label>
            <input
              type="text"
              value={name}
              onChange={(e) => handleNameChange(e.target.value)}
              placeholder="Contoh: Pembuatan E-Course Online"
              required
              className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">Slug Pipeline</label>
            <input
              type="text"
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
              placeholder="contoh: ecourse-pipeline"
              required
              className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 font-mono text-white text-xs focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">Lini Produk</label>
            <select
              value={productLine}
              onChange={(e) => setProductLine(e.target.value as ProductLineType)}
              className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-white/10 text-white text-xs focus:outline-none focus:border-indigo-500"
            >
              {PRODUCT_LINES.map((pl) => (
                <option key={pl.value} value={pl.value}>
                  {pl.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-medium text-slate-300 block mb-1">Deskripsi Pipeline</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Tujuan dan target deliverable dari pipeline produk ini..."
              rows={2}
              className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none focus:border-indigo-500 resize-none"
            />
          </div>

          <div className="pt-2 flex items-center justify-end gap-2 border-t border-white/5">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 rounded-xl border border-white/10 hover:bg-white/5 text-xs text-slate-300"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={submitting || !name.trim()}
              className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white font-medium text-xs flex items-center gap-1.5 shadow-lg shadow-indigo-600/20"
            >
              <Sparkles className="w-3.5 h-3.5" />
              {submitting ? "Membuat..." : "Buat Pipeline"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
