"use client";

import React, { useEffect, useState } from "react";
import { FolderPlus, Edit3, X, AlertCircle } from "lucide-react";
import { DivisionResponse } from "@/lib/types/corporate";
import { createDivision, updateDivision } from "@/lib/corporateApi";

interface DivisionModalProps {
  isOpen: boolean;
  branchId: string;
  initialData?: DivisionResponse | null;
  onClose: () => void;
  onSuccess: (division: DivisionResponse) => void;
}

const PRESET_COLORS = ["#3b82f6", "#8b5cf6", "#ec4899", "#10b981", "#f59e0b", "#06b6d4", "#64748b"];
const PRESET_ICONS = ["FolderTree", "Cpu", "Briefcase", "GraduationCap", "Megaphone", "Search", "ShieldCheck"];

export default function DivisionModal({
  isOpen,
  branchId,
  initialData,
  onClose,
  onSuccess,
}: DivisionModalProps) {
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [accentColor, setAccentColor] = useState("#3b82f6");
  const [iconName, setIconName] = useState("FolderTree");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setName(initialData.name);
      setSlug(initialData.slug);
      setDescription(initialData.description || "");
      setAccentColor(initialData.accent_color);
      setIconName(initialData.icon_name);
    } else {
      setName("");
      setSlug("");
      setDescription("");
      setAccentColor("#3b82f6");
      setIconName("FolderTree");
    }
    setError(null);
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleNameChange = (val: string) => {
    setName(val);
    if (!initialData) {
      setSlug(val.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, ""));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return setError("Nama divisi wajib diisi.");
    setLoading(true);
    setError(null);
    try {
      let result: DivisionResponse;
      if (initialData) {
        result = await updateDivision(initialData.id, {
          name: name.trim(),
          description: description.trim() || undefined,
          accent_color: accentColor,
          icon_name: iconName,
        });
      } else {
        result = await createDivision({
          branch_id: branchId,
          name: name.trim(),
          slug: slug.trim(),
          description: description.trim() || undefined,
          accent_color: accentColor,
          icon_name: iconName,
        });
      }
      onSuccess(result);
      onClose();
    } catch (err: any) {
      setError(err.message || "Gagal menyimpan divisi.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-fade-in">
      <div className="w-full max-w-md rounded-2xl bg-[#0c0d14]/95 border border-white/10 shadow-2xl p-6 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-white">
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-5">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center border"
            style={{ backgroundColor: `${accentColor}15`, borderColor: `${accentColor}40`, color: accentColor }}
          >
            {initialData ? <Edit3 className="w-5 h-5" /> : <FolderPlus className="w-5 h-5" />}
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">
              {initialData ? "Edit Divisi" : "Tambah Divisi Baru"}
            </h3>
            <p className="text-xs text-slate-400">Unit operasional mandiri perusahaan</p>
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
            <label className="block text-xs font-medium text-slate-300 mb-1">Nama Divisi</label>
            <input
              type="text"
              required
              placeholder="e.g. Divisi Media & Copywriting"
              value={name}
              onChange={(e) => handleNameChange(e.target.value)}
              className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-white/30"
            />
          </div>

          {!initialData && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Slug</label>
              <input
                type="text"
                required
                placeholder="e.g. copywriting"
                value={slug}
                onChange={(e) => setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9_-]/g, ""))}
                className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-slate-300 font-mono text-xs placeholder:text-slate-500 focus:outline-none focus:border-white/30"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Tujuan / Purpose Divisi</label>
            <textarea
              rows={2}
              placeholder="Tujuan utama dan mandat strategis yang dijalankan divisi ini..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3.5 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-white/30"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Aksen Warna Divisi</label>
            <div className="flex items-center gap-2">
              {PRESET_COLORS.map((color) => (
                <button
                  type="button"
                  key={color}
                  onClick={() => setAccentColor(color)}
                  className={`w-7 h-7 rounded-full border-2 transition-transform ${
                    accentColor === color ? "scale-110 border-white" : "border-transparent"
                  }`}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>

          <div className="pt-2 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white rounded-xl hover:bg-white/5"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-all disabled:opacity-50"
            >
              {loading ? "Menyimpan..." : initialData ? "Perbarui Divisi" : "Simpan Divisi"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
