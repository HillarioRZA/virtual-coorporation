"use client";

import React, { useEffect, useState } from "react";
import {
  BookOpen,
  Plus,
  Search,
  RefreshCw,
  FolderOpen,
  FileText,
  Tag,
  CheckCircle2,
  X,
  Sparkles,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
}

interface SkillItem {
  id: string;
  name: string;
  description?: string;
  folder_path: string;
  category_name?: string;
  category_slug?: string;
}

export default function SkillsPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [skills, setSkills] = useState<SkillItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  // Install Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [installTab, setInstallTab] = useState<"git" | "manual">("git");
  const [gitUrl, setGitUrl] = useState("");
  const [gitName, setGitName] = useState("");
  const [gitCategory, setGitCategory] = useState("");
  const [formName, setFormName] = useState("");
  const [formCategory, setFormCategory] = useState("");
  const [formDesc, setFormDesc] = useState("");
  const [formContent, setFormContent] = useState("");
  const [installLoading, setInstallLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Reading Modal State
  const [readingSkill, setReadingSkill] = useState<{ name: string; content: string } | null>(null);
  const [readLoading, setReadLoading] = useState(false);

  const fetchCategories = async () => {
    try {
      const res = await fetch(`${API_BASE}/skills/categories`);
      if (res.ok) setCategories(await res.json());
    } catch (e) {
      console.error("Gagal mengambil kategori:", e);
    }
  };

  const fetchSkills = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchQuery.trim()) params.append("q", searchQuery.trim());
      if (selectedCategory !== "all") params.append("category", selectedCategory);
      const res = await fetch(`${API_BASE}/skills?${params.toString()}`);
      if (res.ok) setSkills(await res.json());
    } catch (e) {
      console.error("Gagal mengambil skills:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchSkills();
  }, [selectedCategory]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchSkills();
  };

  const handleInstall = async (e: React.FormEvent) => {
    e.preventDefault();
    setInstallLoading(true);
    setFormError(null);
    try {
      const res = await fetch(`${API_BASE}/skills/install`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formName.trim().toLowerCase(),
          category_name: formCategory.trim(),
          description: formDesc.trim() || undefined,
          skill_md_content: formContent.trim(),
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Gagal menginstal skill.");
      setIsModalOpen(false);
      setFormName("");
      setFormCategory("");
      setFormDesc("");
      setFormContent("");
      fetchCategories();
      fetchSkills();
    } catch (err: any) {
      setFormError(err.message || "Gagal menyimpan skill.");
    } finally {
      setInstallLoading(false);
    }
  };

  const handleGitInstall = async (e: React.FormEvent) => {
    e.preventDefault();
    setInstallLoading(true);
    setFormError(null);
    try {
      const res = await fetch(`${API_BASE}/skills/import-git`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_url: gitUrl.trim(),
          name: gitName.trim() || undefined,
          category_name: gitCategory.trim() || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Gagal mengimpor skill dari Git.");
      setIsModalOpen(false);
      setGitUrl("");
      setGitName("");
      setGitCategory("");
      fetchCategories();
      fetchSkills();
    } catch (err: any) {
      setFormError(err.message || "Gagal mengimpor skill dari Git.");
    } finally {
      setInstallLoading(false);
    }
  };

  const handleReadPlaybook = async (skill: SkillItem) => {
    setReadLoading(true);
    try {
      // Baca file SKILL.md melalui API atau ambil dari folder
      const dummySample = `# ${skill.name.toUpperCase()}\n\n${skill.description || "Panduan teknis domain standar."}\n\n## Petunjuk Implementasi\n- Ikuti arsitektur modular\n- Pastikan seluruh fungsi memiliki unit test\n- Manfaatkan type-checking menyeluruh`;
      setReadingSkill({ name: skill.name, content: dummySample });
    } finally {
      setReadLoading(false);
    }
  };

  return (
    <div className="flex-1 p-6 md:p-10 max-w-7xl mx-auto w-full space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <BookOpen className="w-5 h-5" />
            </div>
            <h1 className="text-xl md:text-2xl font-bold tracking-tight text-white font-mono">
              SKILLS LIBRARY & TAXONOMY
            </h1>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
              Public Commons
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Perpustakaan terbuka playbook, SOP domain, dan pedoman arsitektur yang dapat diakses secara mandiri oleh semua peran agen.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              fetchCategories();
              fetchSkills();
            }}
            className="p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 hover:text-white transition-all"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={() => {
              setIsModalOpen(true);
              setFormError(null);
            }}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium transition-all shadow-lg shadow-cyan-600/20"
          >
            <Plus className="w-4 h-4" />
            <span>Pasang Skill Baru</span>
          </button>
        </div>
      </div>

      {/* Category Tabs & Search Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Horizontal Category Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 scrollbar-none">
          <button
            onClick={() => setSelectedCategory("all")}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all shrink-0 ${
              selectedCategory === "all"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "bg-white/5 text-slate-400 hover:text-white border border-transparent"
            }`}
          >
            Semua ({skills.length})
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.slug)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all shrink-0 ${
                selectedCategory === cat.slug
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                  : "bg-white/5 text-slate-400 hover:text-white border border-transparent"
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <form onSubmit={handleSearch} className="relative min-w-[280px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Cari playbook di perpustakaan..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 rounded-xl bg-white/5 border border-white/10 text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </form>
      </div>

      {/* Skills Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-44 rounded-2xl bg-white/5 border border-white/5 animate-pulse" />
          ))}
        </div>
      ) : skills.length === 0 ? (
        <div className="text-center py-16 rounded-2xl bg-white/[0.02] border border-dashed border-white/10 space-y-3">
          <BookOpen className="w-8 h-8 text-slate-500 mx-auto" />
          <h3 className="text-sm font-medium text-slate-300">Belum Ada Skill di Kategori Ini</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Pasang skill baru (misalnya arsitektur flutter, fastapi best practices) untuk menambah wawasan agen.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {skills.map((skill) => (
            <div
              key={skill.id}
              className="rounded-2xl bg-white/[0.03] border border-white/10 p-5 flex flex-col justify-between hover:border-cyan-500/30 transition-all space-y-4 shadow-xl"
            >
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                    {skill.category_name || "General"}
                  </span>
                  <div className="flex items-center gap-1 text-[11px] text-slate-400">
                    <FileText className="w-3.5 h-3.5 text-slate-500" />
                    <span>SKILL.md</span>
                  </div>
                </div>

                <h3 className="font-bold text-sm text-white">{skill.name}</h3>
                <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                  {skill.description || "Panduan teknis dan standar pengerjaan domain."}
                </p>
              </div>

              <div className="pt-3 border-t border-white/5 flex items-center justify-between">
                <span className="text-[10px] text-slate-500 truncate max-w-[140px]">
                  {skill.folder_path?.split(/[\\/]/).slice(-2).join("/")}
                </span>
                <button
                  onClick={() => handleReadPlaybook(skill)}
                  className="px-3 py-1 rounded-lg text-xs font-medium text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/20 transition-all"
                >
                  Buka Playbook &rarr;
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Install Skill Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
          <div className="w-full max-w-xl rounded-2xl bg-[#0c0d14]/95 border border-white/10 shadow-2xl p-6 relative space-y-4">
            <h3 className="text-base font-semibold text-white">Pasang Skill Baru ke Perpustakaan</h3>
            <p className="text-xs text-slate-400">
              Kategori baru akan dibuat secara otomatis jika belum pernah terdaftar sebelumnya.
            </p>

            {formError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
                {formError}
              </div>
            )}

            {/* Mode Switcher Tabs */}
            <div className="flex border-b border-white/10 gap-2 pt-1">
              <button
                type="button"
                onClick={() => setInstallTab("git")}
                className={`pb-2.5 px-3 text-xs font-medium border-b-2 transition-all ${
                  installTab === "git"
                    ? "border-cyan-400 text-cyan-300"
                    : "border-transparent text-slate-400 hover:text-white"
                }`}
              >
                📦 Impor dari Git / GitHub Repo
              </button>
              <button
                type="button"
                onClick={() => setInstallTab("manual")}
                className={`pb-2.5 px-3 text-xs font-medium border-b-2 transition-all ${
                  installTab === "manual"
                    ? "border-cyan-400 text-cyan-300"
                    : "border-transparent text-slate-400 hover:text-white"
                }`}
              >
                ✏️ Editor Manual (SKILL.md)
              </button>
            </div>

            {/* TAB 1: GIT IMPORTER */}
            {installTab === "git" && (
              <form onSubmit={handleGitInstall} className="space-y-4 pt-1">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    URL Repositori Git Publik (GitHub / GitLab)
                  </label>
                  <input
                    type="url"
                    required
                    placeholder="https://github.com/nextlevelbuilder/ui-ux-pro-max-skill"
                    value={gitUrl}
                    onChange={(e) => setGitUrl(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs font-mono focus:outline-none focus:border-cyan-500"
                  />
                  <p className="text-[11px] text-slate-500 mt-1">
                    Mendukung repositori multi-berkas (folder <code className="text-cyan-400">scripts/</code>, <code className="text-cyan-400">templates/</code>, aset, dan <code className="text-cyan-400">SKILL.md</code>).
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">Nama Skill (Opsional)</label>
                    <input
                      type="text"
                      placeholder="Auto-detect dari repo"
                      value={gitName}
                      onChange={(e) => setGitName(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">Kategori Kustom (Opsional)</label>
                    <input
                      type="text"
                      list="category-suggestions"
                      placeholder="Auto-detect dari metadata"
                      value={gitCategory}
                      onChange={(e) => setGitCategory(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                <div className="pt-2 flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="px-4 py-2 text-xs text-slate-400 hover:text-white"
                  >
                    Batal
                  </button>
                  <button
                    type="submit"
                    disabled={installLoading}
                    className="px-4 py-2 text-xs font-medium text-white bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-xl transition-all disabled:opacity-50 shadow-md"
                  >
                    {installLoading ? "Mengkloning & Memasang..." : "Unduh & Pasang Bundle Skill"}
                  </button>
                </div>
              </form>
            )}

            {/* TAB 2: MANUAL EDITOR */}
            {installTab === "manual" && (
              <form onSubmit={handleInstall} className="space-y-4 pt-1">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">Nama Skill</label>
                    <input
                      type="text"
                      required
                      placeholder="flutter-clean-architecture"
                      value={formName}
                      onChange={(e) => setFormName(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">Kategori (Auto-Create)</label>
                    <input
                      type="text"
                      required
                      list="category-suggestions"
                      placeholder="Mobile Development"
                      value={formCategory}
                      onChange={(e) => setFormCategory(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none focus:border-cyan-500"
                    />
                    <datalist id="category-suggestions">
                      {categories.map((c) => (
                        <option key={c.id} value={c.name} />
                      ))}
                    </datalist>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Deskripsi Ringkas</label>
                  <input
                    type="text"
                    placeholder="Standar implementasi BLoC dan Clean Architecture pada Flutter"
                    value={formDesc}
                    onChange={(e) => setFormDesc(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Konten SKILL.md (Markdown)</label>
                  <textarea
                    rows={8}
                    required
                    placeholder="# PANDUAN TEKNIS FLUTTER&#10;&#10;## Pola State Management&#10;Gunakan flutter_bloc..."
                    value={formContent}
                    onChange={(e) => setFormContent(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs font-mono focus:outline-none focus:border-cyan-500"
                  />
                </div>

                <div className="pt-2 flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="px-4 py-2 text-xs text-slate-400 hover:text-white"
                  >
                    Batal
                  </button>
                  <button
                    type="submit"
                    disabled={installLoading}
                    className="px-4 py-2 text-xs font-medium text-white bg-cyan-600 hover:bg-cyan-500 rounded-xl transition-all disabled:opacity-50"
                  >
                    {installLoading ? "Menyimpan..." : "Simpan Skill"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Reading Playbook Modal */}
      {readingSkill && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md overflow-y-auto">
          <div className="w-full max-w-2xl rounded-2xl bg-[#0c0d14]/95 border border-white/10 shadow-2xl p-6 relative space-y-4 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-cyan-400" />
                {readingSkill.name}
              </h3>
              <button
                onClick={() => setReadingSkill(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto pr-2">
              <pre className="text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed bg-black/40 p-4 rounded-xl border border-white/5">
                {readingSkill.content}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
