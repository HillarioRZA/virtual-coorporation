"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Rocket,
  TrendingUp,
  Cpu,
  Layers,
  Plus,
  ArrowRight,
  ShieldAlert,
  CheckCircle2,
  ExternalLink,
  MessageSquare,
  MonitorPlay,
  Settings,
  Sparkles,
  Columns3,
  Brain,
} from "lucide-react";
import { fetchProjects, createProject } from "../lib/api";
import { ProjectSummary, StageName } from "../lib/types/api";

const ARCHETYPES = [
  { id: 1, name: "Arketipe 1: Single-Tenant CRUD SaaS", icon: Layers, desc: "Aplikasi multi-halaman dengan otentikasi & relational database" },
  { id: 2, name: "Arketipe 2: Real-Time Event Driven", icon: Rocket, desc: "Aplikasi responsif berbasis WebSocket / SSE & background workers" },
  { id: 3, name: "Arketipe 3: AI Copilot Workflow", icon: Cpu, desc: "Eksekusi LLM streaming, prompt chains & integrasi model AI" },
  { id: 4, name: "Arketipe 4: Data Pipeline & Analytics", icon: TrendingUp, desc: "Pengolahan berkas tabular, data visualization & charting" },
];

function getStageBadge(stage: StageName) {
  switch (stage) {
    case "SPARRING_ROOM":
      return { label: "Sparring Room", style: "bg-amber-500/10 text-amber-300 border-amber-500/25" };
    case "GATE_1_WAITING":
      return { label: "Gate 1 Waiting", style: "bg-yellow-500/20 text-yellow-300 border-yellow-500/40 animate-pulse" };
    case "PRD_AND_SPECS":
      return { label: "PRD & Specs", style: "bg-blue-500/10 text-blue-300 border-blue-500/25" };
    case "MOCK_PROTOTYPING":
      return { label: "Mock Prototyping", style: "bg-cyan-500/10 text-cyan-300 border-cyan-500/25" };
    case "GATE_2_WAITING":
      return { label: "Gate 2 Waiting", style: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40 animate-pulse" };
    case "PRODUCTION_HARDENING":
      return { label: "Hardening & QA", style: "bg-purple-500/10 text-purple-300 border-purple-500/25" };
    case "PROJECT_KILLED":
      return { label: "Terminated", style: "bg-rose-500/10 text-rose-400 border-rose-500/25" };
    default:
      return { label: stage, style: "bg-white/5 text-slate-400 border-white/10" };
  }
}

export default function PortfolioHubPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Form state
  const [name, setName] = useState("");
  const [founderIdea, setFounderIdea] = useState("");
  const [archetypeId, setArchetypeId] = useState(1);
  const [errorMsg, setErrorMsg] = useState("");

  const loadData = async () => {
    try {
      setIsLoading(true);
      const data = await fetchProjects();
      setProjects(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateVenture = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !founderIdea.trim()) return;

    try {
      setIsSubmitting(true);
      setErrorMsg("");
      const result = await createProject({
        name,
        founder_idea: founderIdea,
        archetype_id: archetypeId,
      });
      setIsModalOpen(false);
      setName("");
      setFounderIdea("");
      router.push(`/sparring/${result.project_id}`);
    } catch (err: any) {
      setErrorMsg(err.message || "Gagal membuat proyek");
    } finally {
      setIsSubmitting(false);
    }
  };

  const totalTokensCost = projects.reduce((acc, p) => acc + (p.tokens_cost || 0), 0);
  const activeCount = projects.filter((p) => p.status === "ACTIVE").length;

  return (
    <div className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full space-y-8">
      {/* Hero Header Strip */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[11px] font-mono text-slate-300">
            <Sparkles className="w-3.5 h-3.5 text-slate-300" />
            <span>Autonomous Venture Incubator Hub</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Portfolio Hub & Cockpit
          </h1>
          <p className="text-xs md:text-sm text-slate-400 max-w-2xl leading-relaxed">
            Monitor seluruh ide bisnis otonom, kendalikan konsumsi token per agen, dan kelola gerbang keputusan Founder.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            href="/wisdom"
            className="liquid-dark-btn inline-flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-semibold"
          >
            <Brain className="w-4 h-4 text-indigo-400" />
            <span>Wisdom Base</span>
          </Link>
          <Link
            href="/settings"
            className="liquid-dark-btn inline-flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-semibold"
          >
            <Settings className="w-4 h-4 text-slate-300" />
            <span>Pengaturan</span>
          </Link>
          <button
            onClick={() => setIsModalOpen(true)}
            className="liquid-chrome-btn inline-flex items-center justify-center space-x-2 px-5 py-2.5 rounded-xl text-xs uppercase tracking-wider font-bold transition-all"
          >
            <Plus className="w-4 h-4 text-black" />
            <span>Inisiasi Ide Baru</span>
          </button>
        </div>
      </div>

      {/* Metrics Summary Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="liquid-glass p-5 rounded-2xl relative overflow-hidden group hover:border-white/20 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-mono font-semibold uppercase tracking-wider">Active Ventures</span>
            <div className="w-7 h-7 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
              <Rocket className="w-3.5 h-3.5 text-slate-300" />
            </div>
          </div>
          <div className="text-2xl md:text-3xl font-extrabold text-white mt-3 font-mono">{activeCount} Proyek</div>
          <p className="text-[11px] text-slate-400 mt-1">Siklus inkubasi otonom aktif</p>
        </div>

        <div className="liquid-glass p-5 rounded-2xl relative overflow-hidden group hover:border-white/20 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-mono font-semibold uppercase tracking-wider">Total Token Burn</span>
            <div className="w-7 h-7 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
              <Cpu className="w-3.5 h-3.5 text-amber-400" />
            </div>
          </div>
          <div className="text-2xl md:text-3xl font-extrabold text-white mt-3 font-mono">
            ${totalTokensCost.toFixed(4)}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Biaya inferensi seluruh agen AI</p>
        </div>

        <div className="liquid-glass p-5 rounded-2xl relative overflow-hidden group hover:border-white/20 transition-all">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-[11px] font-mono font-semibold uppercase tracking-wider">P&L Status (Est.)</span>
            <div className="w-7 h-7 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
            </div>
          </div>
          <div className="text-2xl md:text-3xl font-extrabold text-emerald-400 mt-3 font-mono">
            -${totalTokensCost.toFixed(4)}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Net profit pra-monetisasi rilis</p>
        </div>
      </div>

      {/* Portfolio Grid Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <span>Daftar Proyek Inkubasi</span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-white/10 text-slate-300">
              {projects.length}
            </span>
          </h2>
        </div>

        {isLoading ? (
          <div className="p-16 text-center text-slate-400 liquid-glass rounded-2xl animate-pulse font-mono text-xs">
            Memuat daftar portofolio venture...
          </div>
        ) : projects.length === 0 ? (
          <div className="p-12 text-center liquid-glass rounded-3xl space-y-4">
            <p className="text-slate-400 text-sm">Belum ada proyek venture yang diinisialisasi.</p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="liquid-chrome-btn inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl text-xs uppercase font-bold"
            >
              <Plus className="w-4 h-4 text-black" />
              <span>Mulai Proyek Pertama</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {projects.map((proj) => {
              const badge = getStageBadge(proj.stage);
              return (
                <div
                  key={proj.project_id}
                  className="liquid-glass liquid-card p-6 rounded-3xl flex flex-col justify-between space-y-4 border border-white/10 relative overflow-hidden group"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="text-base font-bold text-white group-hover:text-slate-200 transition-colors">
                          {proj.name}
                        </h3>
                        <p className="text-[11px] text-slate-500 font-mono mt-0.5">{proj.project_id}</p>
                      </div>
                      <span className={`text-[10px] font-mono font-semibold px-2.5 py-1 rounded-full border ${badge.style}`}>
                        {badge.label}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-[11px] text-slate-400 font-mono">
                      <span className="px-2 py-0.5 rounded-lg bg-white/5 border border-white/10">
                        Archetype #{proj.archetype_id}
                      </span>
                      <span>•</span>
                      <span>Cost: ${proj.tokens_cost.toFixed(3)}</span>
                    </div>
                  </div>

                  <div className="pt-4 border-t border-white/10 flex items-center justify-between gap-2">
                    <Link
                      href={`/sparring/${proj.project_id}`}
                      className="flex-1 inline-flex items-center justify-center space-x-1.5 px-2.5 py-2 rounded-xl liquid-dark-btn text-xs font-semibold transition-colors"
                    >
                      <MessageSquare className="w-3.5 h-3.5 text-slate-400" />
                      <span>Sparring</span>
                    </Link>
                    <Link
                      href={`/kanban/${proj.project_id}`}
                      className="flex-1 inline-flex items-center justify-center space-x-1.5 px-2.5 py-2 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/20 text-xs font-semibold text-purple-300 transition-colors"
                    >
                      <Columns3 className="w-3.5 h-3.5 text-purple-300" />
                      <span>Kanban</span>
                    </Link>
                    <Link
                      href={`/preview/${proj.project_id}`}
                      className="flex-1 inline-flex items-center justify-center space-x-1.5 px-2.5 py-2 rounded-xl bg-white/10 hover:bg-white/15 border border-white/20 text-xs font-semibold text-white transition-colors"
                    >
                      <MonitorPlay className="w-3.5 h-3.5 text-cyan-300" />
                      <span>Preview</span>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Modal Dialog: Inisiasi Ide Baru */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl animate-in fade-in duration-200">
          <div className="liquid-glass-elevated p-6 md:p-8 rounded-3xl max-w-lg w-full border border-white/15 space-y-6 shadow-2xl relative">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Rocket className="w-5 h-5 text-white" />
                <span>Inisiasi Proyek Venture Baru</span>
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            {errorMsg && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs">
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleCreateVenture} className="space-y-4">
              <div>
                <label className="block text-[11px] font-mono font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
                  Nama Venture
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Contoh: NexaFlow AI"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/60 border border-white/15 text-white placeholder-slate-600 text-xs focus:outline-none focus:border-white/40 transition-colors font-mono"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
                  Deskripsi Ide Bisnis Mentah (Founder)
                </label>
                <textarea
                  required
                  rows={3}
                  value={founderIdea}
                  onChange={(e) => setFounderIdea(e.target.value)}
                  placeholder="Jelaskan masalah, target pengguna, dan proposisi nilai yang ingin diselesaikan..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/60 border border-white/15 text-white placeholder-slate-600 text-xs focus:outline-none focus:border-white/40 transition-colors"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono font-semibold text-slate-300 mb-2 uppercase tracking-wider">
                  Pilih Golden Path Archetype
                </label>
                <div className="space-y-2">
                  {ARCHETYPES.map((arch) => (
                    <label
                      key={arch.id}
                      onClick={() => setArchetypeId(arch.id)}
                      className={`flex items-start space-x-3 p-3 rounded-xl border cursor-pointer transition-all ${
                        archetypeId === arch.id
                          ? "bg-white/10 border-white/30 text-white"
                          : "bg-black/40 border-white/5 text-slate-400 hover:border-white/15"
                      }`}
                    >
                      <input
                        type="radio"
                        name="archetype"
                        checked={archetypeId === arch.id}
                        onChange={() => setArchetypeId(arch.id)}
                        className="mt-1 accent-white"
                      />
                      <div className="flex-1 text-xs">
                        <span className="font-semibold block text-slate-200">{arch.name}</span>
                        <span className="text-slate-400 text-[11px]">{arch.desc}</span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div className="pt-4 border-t border-white/10 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl liquid-dark-btn text-xs text-slate-300"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 rounded-xl liquid-chrome-btn text-xs uppercase font-bold text-black shadow-lg disabled:opacity-50"
                >
                  {isSubmitting ? "Menginisialisasi Agen..." : "Deploy Eksekutif Agen"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
