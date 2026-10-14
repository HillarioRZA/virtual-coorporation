"use client";

import React, { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { ArrowLeft, Sparkles, Brain, Plus, Search, ShieldAlert, Layers, TrendingUp, RefreshCw } from "lucide-react";
import { WisdomItem, WisdomSummary } from "@/lib/types/wisdom";
import { fetchWisdomList, fetchWisdomSummary, searchWisdom, deleteWisdom } from "@/lib/wisdomApi";
import { WisdomCard } from "@/components/wisdom/WisdomCard";
import { WisdomModal } from "@/components/wisdom/WisdomModal";

export default function WisdomPage() {
  const [wisdomList, setWisdomList] = useState<WisdomItem[]>([]);
  const [summary, setSummary] = useState<WisdomSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedNamespace, setSelectedNamespace] = useState<string>("all");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [list, sum] = await Promise.all([fetchWisdomList(), fetchWisdomSummary()]);
      setWisdomList(list);
      setSummary(sum);
    } catch (err) {
      console.error("Gagal memuat wisdom data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      loadData();
      return;
    }
    setIsSearching(true);
    try {
      const ns = selectedNamespace !== "all" ? selectedNamespace : undefined;
      const results = await searchWisdom({ query: searchQuery.trim(), namespace: ns, top_k: 8 });
      setWisdomList(results);
    } catch (err) {
      console.error("Pencarian semantik gagal:", err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Nonaktifkan memori institusional ini?")) return;
    try {
      await deleteWisdom(id);
      setWisdomList((prev) => prev.filter((w) => w.id !== id));
      if (summary) setSummary({ ...summary, total_count: Math.max(0, summary.total_count - 1) });
    } catch (err) {
      alert("Gagal menghapus wisdom.");
    }
  };

  const filteredList = useMemo(() => {
    if (selectedNamespace === "all" || searchQuery.trim()) return wisdomList;
    return wisdomList.filter((w) => w.namespace === selectedNamespace);
  }, [wisdomList, selectedNamespace, searchQuery]);

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-8 py-8 w-full space-y-8 animate-in fade-in">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Link href="/" className="p-1 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors">
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <span className="p-1 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Brain className="w-4 h-4" />
            </span>
            <span className="text-xs font-mono uppercase tracking-wider text-indigo-400 font-semibold">Institutional Memory</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight mt-1">Corporate Wisdom Base</h1>
          <p className="text-xs md:text-sm text-slate-400 max-w-2xl mt-1 leading-relaxed">
            Koleksi pengalaman berharga dan panduan preskriptif lintas-venture yang disuntikkan secara otonom ke prompt agen AI.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button onClick={loadData} className="liquid-dark-btn p-2.5 rounded-xl text-slate-400 hover:text-white" title="Refresh">
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button onClick={() => setIsModalOpen(true)} className="liquid-chrome-btn px-4 py-2.5 rounded-xl text-xs font-bold text-black flex items-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Tambah Wisdom</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="liquid-glass p-4 rounded-xl border border-white/10">
          <div className="text-[11px] text-slate-400 font-mono uppercase">Total Wisdom</div>
          <div className="text-2xl font-mono font-bold text-white mt-1">{summary?.total_count || wisdomList.length}</div>
        </div>
        <div className="liquid-glass p-4 rounded-xl border border-white/10">
          <div className="text-[11px] text-indigo-400 font-mono uppercase flex items-center gap-1"><Layers className="w-3 h-3" /> Architecture</div>
          <div className="text-2xl font-mono font-bold text-indigo-300 mt-1">{summary?.namespace_breakdown["wisdom:architecture"] || 0}</div>
        </div>
        <div className="liquid-glass p-4 rounded-xl border border-white/10">
          <div className="text-[11px] text-rose-400 font-mono uppercase flex items-center gap-1"><ShieldAlert className="w-3 h-3" /> Bugs & Fixes</div>
          <div className="text-2xl font-mono font-bold text-rose-300 mt-1">{summary?.namespace_breakdown["wisdom:bugs_and_fixes"] || 0}</div>
        </div>
        <div className="liquid-glass p-4 rounded-xl border border-white/10">
          <div className="text-[11px] text-amber-400 font-mono uppercase flex items-center gap-1"><TrendingUp className="w-3 h-3" /> Growth & Copy</div>
          <div className="text-2xl font-mono font-bold text-amber-300 mt-1">{summary?.namespace_breakdown["wisdom:growth_copy"] || 0}</div>
        </div>
      </div>

      {/* Search & Namespace Filters */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <form onSubmit={handleSearch} className="flex-1 max-w-lg relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Cari semantik (e.g. 'CORS 401 error', 'SRP 200 baris')..."
            className="w-full pl-9 pr-20 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-indigo-500"
          />
          <button type="submit" disabled={isSearching} className="absolute right-1.5 top-1.5 px-3 py-1 rounded-lg bg-indigo-500/20 text-indigo-300 text-xs font-semibold hover:bg-indigo-500/30">
            {isSearching ? "Mencari..." : "Cari"}
          </button>
        </form>

        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1">
          {[
            { id: "all", label: "Semua" },
            { id: "wisdom:architecture", label: "Architecture" },
            { id: "wisdom:bugs_and_fixes", label: "Bugs & Fixes" },
            { id: "wisdom:growth_copy", label: "Growth & Copy" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => { setSelectedNamespace(tab.id); setSearchQuery(""); }}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
                selectedNamespace === tab.id ? "bg-white/10 text-white border border-white/20" : "text-slate-400 hover:text-white"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Wisdom Grid */}
      {loading ? (
        <div className="text-center py-12 text-slate-500 text-xs font-mono">Memuat memori institusional...</div>
      ) : filteredList.length === 0 ? (
        <div className="text-center py-12 liquid-glass rounded-2xl border border-white/5 space-y-2">
          <Sparkles className="w-6 h-6 text-slate-500 mx-auto" />
          <p className="text-slate-400 text-xs font-medium">Belum ada memori institusional yang sesuai.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredList.map((item) => (
            <WisdomCard key={item.id} item={item} onDelete={handleDelete} />
          ))}
        </div>
      )}

      {/* Modal Tambah Wisdom */}
      <WisdomModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onCreated={(item) => setWisdomList((prev) => [item, ...prev])} />
    </div>
  );
}
