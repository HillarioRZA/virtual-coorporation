"use client";

import React, { useState } from "react";
import { X, Sparkles, Plus, Loader2, Github, CheckCircle2, ShieldCheck } from "lucide-react";
import { WisdomCreate, WisdomItem, WisdomNamespace } from "@/lib/types/wisdom";
import { createWisdom, importGitHubSkill, importGitHubPlugin } from "@/lib/wisdomApi";

interface WisdomModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: (item: WisdomItem) => void;
}

export function WisdomModal({ isOpen, onClose, onCreated }: WisdomModalProps) {
  const [tab, setTab] = useState<"manual" | "github">("manual");
  const [title, setTitle] = useState("");
  const [namespace, setNamespace] = useState<WisdomNamespace>("wisdom:architecture");
  const [problemPattern, setProblemPattern] = useState("");
  const [solutionGuideline, setSolutionGuideline] = useState("");
  const [tagsInput, setTagsInput] = useState("");
  const [githubUrl, setGithubUrl] = useState("");
  const [importType, setImportType] = useState<"skill" | "plugin">("skill");
  const [projectId, setProjectId] = useState("prj_gold_master");
  const [toolName, setToolName] = useState("");
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; msg: string } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !problemPattern.trim() || !solutionGuideline.trim()) {
      return setFeedback({ type: "error", msg: "Seluruh field manual wajib diisi." });
    }
    setIsSubmitting(true);
    setFeedback(null);
    try {
      const tags = tagsInput.split(",").map((t) => t.trim().toLowerCase()).filter(Boolean);
      const payload: WisdomCreate = {
        title: title.trim(), namespace, problem_pattern: problemPattern.trim(),
        solution_guideline: solutionGuideline.trim(), tags, source_venture_id: "global",
      };
      const newItem = await createWisdom(payload);
      onCreated(newItem);
      onClose();
    } catch (err: any) {
      setFeedback({ type: "error", msg: err.message || "Gagal menyimpan wisdom." });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGithubSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!githubUrl.trim()) return setFeedback({ type: "error", msg: "URL GitHub wajib diisi." });
    setIsSubmitting(true);
    setFeedback(null);
    try {
      if (importType === "skill") {
        const tags = tagsInput.split(",").map((t) => t.trim().toLowerCase()).filter(Boolean);
        const res = await importGitHubSkill(githubUrl.trim(), namespace, tags);
        setFeedback({ type: "success", msg: `Skill '${res.title}' berhasil diimpor & diindeks ke Corporate Wisdom!` });
        if (res.wisdom) onCreated(res.wisdom);
        setTimeout(() => onClose(), 1500);
      } else {
        const res = await importGitHubPlugin(projectId.trim(), githubUrl.trim(), toolName.trim() || undefined);
        setFeedback({ type: "success", msg: `Plugin [${res.script_name}] lolos audit OWASP AST & aktif di sandbox ${projectId}!` });
        setTimeout(() => onClose(), 1800);
      }
    } catch (err: any) {
      setFeedback({ type: "error", msg: err.message || "Gagal memproses impor GitHub." });
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
            <h2 className="text-base font-bold text-white tracking-tight">Corporate Wisdom & GitHub Bridge</h2>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="grid grid-cols-2 p-1.5 bg-black/40 border-b border-white/10 text-xs font-medium">
          <button
            type="button" onClick={() => { setTab("manual"); setFeedback(null); }}
            className={`py-2 rounded-xl transition-all flex items-center justify-center gap-1.5 ${tab === "manual" ? "bg-white/10 text-white font-semibold" : "text-slate-400 hover:text-white"}`}
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Input Manual Wisdom</span>
          </button>
          <button
            type="button" onClick={() => { setTab("github"); setFeedback(null); }}
            className={`py-2 rounded-xl transition-all flex items-center justify-center gap-1.5 ${tab === "github" ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-semibold" : "text-slate-400 hover:text-white"}`}
          >
            <Github className="w-3.5 h-3.5 text-cyan-400" />
            <span>GitHub 1-Click Import</span>
          </button>
        </div>

        {feedback && (
          <div className={`m-5 mb-0 p-3 rounded-xl border text-xs flex items-center gap-2 ${feedback.type === "success" ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300" : "bg-rose-500/10 border-rose-500/25 text-rose-300"}`}>
            {feedback.type === "success" ? <CheckCircle2 className="w-4 h-4 shrink-0" /> : <ShieldCheck className="w-4 h-4 shrink-0" />}
            <span>{feedback.msg}</span>
          </div>
        )}

        {tab === "manual" ? (
          <form onSubmit={handleManualSubmit} className="p-5 space-y-3.5">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Judul Guideline / Best Practice</label>
              <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required placeholder="Single Responsibility Modularization" className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Namespace</label>
              <select value={namespace} onChange={(e) => setNamespace(e.target.value as WisdomNamespace)} className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none">
                <option value="wisdom:architecture">wisdom:architecture (Pola Desain Sistem)</option>
                <option value="wisdom:bugs_and_fixes">wisdom:bugs_and_fixes (Error & Security)</option>
                <option value="wisdom:growth_copy">wisdom:growth_copy (Growth Copy)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Problem Pattern</label>
              <textarea value={problemPattern} onChange={(e) => setProblemPattern(e.target.value)} required rows={2} placeholder="Pola kendala yang muncul..." className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Solution Guideline</label>
              <textarea value={solutionGuideline} onChange={(e) => setSolutionGuideline(e.target.value)} required rows={2} placeholder="Solusi preskriptif untuk agen AI..." className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none" />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Tags (Koma terpisah)</label>
              <input type="text" value={tagsInput} onChange={(e) => setTagsInput(e.target.value)} placeholder="architecture, srp, security" className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none" />
            </div>
            <div className="pt-2 flex justify-end gap-2">
              <button type="button" onClick={onClose} className="px-4 py-2 text-xs text-slate-400 hover:text-white">Batal</button>
              <button type="submit" disabled={isSubmitting} className="liquid-chrome-btn px-4 py-2 rounded-xl text-xs font-semibold text-black inline-flex items-center gap-1.5">
                {isSubmitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
                <span>Simpan ke Memory</span>
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleGithubSubmit} className="p-5 space-y-3.5">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">GitHub File URL</label>
              <input type="url" value={githubUrl} onChange={(e) => setGithubUrl(e.target.value)} required placeholder="https://github.com/owner/repo/blob/main/skill.md" className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white font-mono text-xs focus:outline-none focus:border-cyan-500" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Tipe Impor</label>
                <select value={importType} onChange={(e) => setImportType(e.target.value as any)} className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none">
                  <option value="skill">Skill Blueprint (.md)</option>
                  <option value="plugin">CLI / Tool Plugin (.py)</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">{importType === "skill" ? "Namespace" : "Target Project ID"}</label>
                {importType === "skill" ? (
                  <select value={namespace} onChange={(e) => setNamespace(e.target.value as WisdomNamespace)} className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none">
                    <option value="wisdom:skills">wisdom:skills</option>
                    <option value="wisdom:architecture">wisdom:architecture</option>
                  </select>
                ) : (
                  <input type="text" value={projectId} onChange={(e) => setProjectId(e.target.value)} placeholder="prj_demo" className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs font-mono focus:outline-none" />
                )}
              </div>
            </div>
            {importType === "plugin" && (
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Tool Script Name (Opsional)</label>
                <input type="text" value={toolName} onChange={(e) => setToolName(e.target.value)} placeholder="custom_scanner.py" className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white font-mono text-xs focus:outline-none" />
              </div>
            )}
            <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-[11px] leading-relaxed">
              {importType === "skill" ? "Skill .md akan diunduh, disarikan, dan divektorisasi 128-D ke Corporate Wisdom." : "Plugin .py wajib lolos audit AST OWASP dan validasi requirements.txt."}
            </div>
            <div className="pt-2 flex justify-end gap-2">
              <button type="button" onClick={onClose} className="px-4 py-2 text-xs text-slate-400 hover:text-white">Batal</button>
              <button type="submit" disabled={isSubmitting} className="liquid-chrome-btn px-4 py-2 rounded-xl text-xs font-semibold text-black inline-flex items-center gap-1.5">
                {isSubmitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Github className="w-3.5 h-3.5" />}
                <span>Impor & Audit GitHub</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
