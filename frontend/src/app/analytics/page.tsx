"use client";

import React, { useEffect, useState } from "react";
import { Activity, ShieldCheck, RefreshCw, SlidersHorizontal, AlertCircle } from "lucide-react";
import {
  fetchTokenSummary,
  fetchBurnRate,
  fetchRoleCosts,
  fetchChannelHealth,
  saveBudgetCap,
} from "@/lib/analyticsApi";
import {
  TokenUsageSummary,
  BurnRateItem,
  RoleCostItem,
  ChannelHealthItem,
} from "@/lib/types/analytics";
import { AnalyticsMetricCards } from "@/components/analytics/AnalyticsMetricCards";
import { ChannelHealthRadar } from "@/components/analytics/ChannelHealthRadar";
import { RoleCostTable } from "@/components/analytics/RoleCostTable";

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<TokenUsageSummary | null>(null);
  const [burnRate, setBurnRate] = useState<BurnRateItem[]>([]);
  const [roleCosts, setRoleCosts] = useState<RoleCostItem[]>([]);
  const [channels, setChannels] = useState<ChannelHealthItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [budgetCap, setBudgetCap] = useState<number>(50.0);
  const [editingCap, setEditingCap] = useState<boolean>(false);
  const [newCapInput, setNewCapInput] = useState<string>("50.0");

  const loadData = async () => {
    try {
      setError(null);
      const [sumRes, burnRes, costRes, chanRes] = await Promise.all([
        fetchTokenSummary(),
        fetchBurnRate(),
        fetchRoleCosts(),
        fetchChannelHealth(),
      ]);
      setSummary(sumRes);
      setBurnRate(burnRes);
      setRoleCosts(costRes);
      setChannels(chanRes);
      if (sumRes.active_budget_cap_usd > 0) {
        setBudgetCap(sumRes.active_budget_cap_usd);
        setNewCapInput(sumRes.active_budget_cap_usd.toString());
      }
    } catch (err: any) {
      setError(err.message || "Gagal memuat data observabilitas finansial.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSaveBudgetCap = async (e: React.FormEvent) => {
    e.preventDefault();
    const parsed = parseFloat(newCapInput);
    if (isNaN(parsed) || parsed <= 0) return;
    try {
      await saveBudgetCap(parsed);
      setBudgetCap(parsed);
      setEditingCap(false);
      loadData();
    } catch (err: any) {
      setError(err.message || "Gagal menyimpan batas anggaran.");
    }
  };

  return (
    <main className="flex-1 w-full max-w-7xl mx-auto px-4 md:px-8 py-8 space-y-6 z-10 relative">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-800/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Activity className="w-5 h-5" />
            </span>
            <h1 className="text-xl font-bold tracking-tight text-white font-mono">
              CFO OBSERVABILITY & MODEL ROUTER COCKPIT
            </h1>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Audit pembukuan token, rate-limiter proaktif sliding-window, dan multi-channel failover engine.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setEditingCap(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-xs font-medium text-zinc-300 border border-zinc-700 transition"
          >
            <SlidersHorizontal className="w-3.5 h-3.5 text-amber-400" />
            Set Budget Cap
          </button>
          <button
            onClick={loadData}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 text-xs font-medium transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Modal Budget Cap */}
      {editingCap && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <form onSubmit={handleSaveBudgetCap} className="w-full max-w-sm p-5 rounded-2xl bg-zinc-900 border border-zinc-800 shadow-2xl space-y-4">
            <h3 className="text-sm font-semibold text-white">Konfigurasi Financial Budget Cap</h3>
            <p className="text-xs text-zinc-400">
              Menyetel batas pagu biaya token API. Jika terlampaui, circuit-breaker akan memproteksi venture dari pembengkakan biaya.
            </p>
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">Batas Anggaran (USD)</label>
              <input
                type="number" step="0.5" min="1" required value={newCapInput}
                onChange={(e) => setNewCapInput(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-zinc-800 border border-zinc-700 text-white font-mono text-sm focus:outline-none"
              />
            </div>
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setEditingCap(false)} className="px-3 py-1.5 text-xs text-zinc-400 hover:text-white">Batal</button>
              <button type="submit" className="px-4 py-1.5 text-xs font-medium text-white bg-amber-600 hover:bg-amber-500 rounded-xl">Simpan Cap</button>
            </div>
          </form>
        </div>
      )}

      {/* KPI Cards */}
      <AnalyticsMetricCards summary={summary} budgetCap={budgetCap} onUpdateCap={(cap) => setBudgetCap(cap)} />

      {/* Radar Saluran Upstream 9router */}
      <ChannelHealthRadar channels={channels} onRefresh={loadData} loading={loading} />

      {/* Distribusi Biaya Peran Karyawan AI */}
      <RoleCostTable roles={roleCosts} totalCost={summary?.total_cost_usd || 0} />
    </main>
  );
}
