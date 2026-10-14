"use client";

import React from "react";
import { DollarSign, Cpu, ArrowUpRight, ShieldAlert, Zap } from "lucide-react";
import { TokenUsageSummary } from "@/lib/types/analytics";

interface MetricCardsProps {
  summary: TokenUsageSummary | null;
  budgetCap: number;
  onUpdateCap: (newCap: number) => void;
}

export const AnalyticsMetricCards: React.FC<MetricCardsProps> = ({ summary, budgetCap, onUpdateCap }) => {
  const totalCost = summary?.total_cost_usd || 0;
  const totalTokens = (summary?.total_input_tokens || 0) + (summary?.total_output_tokens || 0);
  const requests = summary?.total_requests || 0;
  const fallbacks = summary?.fallbacks_triggered || 0;
  const budgetPercent = budgetCap > 0 ? Math.min(100, (totalCost / budgetCap) * 100) : 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. Total Cost & Budget Cap */}
      <div className="p-4 rounded-2xl bg-zinc-900/60 border border-zinc-800/80 backdrop-blur-xl relative overflow-hidden">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-zinc-400">Total Burned (USD)</span>
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <DollarSign className="w-4 h-4" />
          </div>
        </div>
        <div className="text-2xl font-bold font-mono text-white mb-2">${totalCost.toFixed(4)}</div>
        <div className="w-full bg-zinc-800 rounded-full h-1.5 overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${
              budgetPercent > 85 ? "bg-rose-500" : budgetPercent > 60 ? "bg-amber-500" : "bg-emerald-500"
            }`}
            style={{ width: `${budgetPercent}%` }}
          />
        </div>
        <div className="flex justify-between text-[10px] text-zinc-400 mt-1 font-mono">
          <span>Cap: ${budgetCap.toFixed(2)}</span>
          <span>{budgetPercent.toFixed(1)}%</span>
        </div>
      </div>

      {/* 2. Total Token Consumption */}
      <div className="p-4 rounded-2xl bg-zinc-900/60 border border-zinc-800/80 backdrop-blur-xl">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-zinc-400">Token Consumption</span>
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Cpu className="w-4 h-4" />
          </div>
        </div>
        <div className="text-2xl font-bold font-mono text-white mb-1">{totalTokens.toLocaleString()}</div>
        <p className="text-[11px] text-zinc-400 font-mono">
          In: {(summary?.total_input_tokens || 0).toLocaleString()} | Out: {(summary?.total_output_tokens || 0).toLocaleString()}
        </p>
      </div>

      {/* 3. Total Requests & Efficiency */}
      <div className="p-4 rounded-2xl bg-zinc-900/60 border border-zinc-800/80 backdrop-blur-xl">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-zinc-400">Autonomous LLM Calls</span>
          <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Zap className="w-4 h-4" />
          </div>
        </div>
        <div className="text-2xl font-bold font-mono text-white mb-1">{requests.toLocaleString()}</div>
        <p className="text-[11px] text-zinc-400 font-mono">
          Avg: {requests > 0 ? Math.round(totalTokens / requests).toLocaleString() : 0} tokens/call
        </p>
      </div>

      {/* 4. Failovers & Router Resilience */}
      <div className="p-4 rounded-2xl bg-zinc-900/60 border border-zinc-800/80 backdrop-blur-xl">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-zinc-400">Router Failovers</span>
          <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <ShieldAlert className="w-4 h-4" />
          </div>
        </div>
        <div className="text-2xl font-bold font-mono text-white mb-1">{fallbacks}</div>
        <p className="text-[11px] text-emerald-400 font-mono flex items-center gap-1">
          <ArrowUpRight className="w-3 h-3" /> Zero disruption rate
        </p>
      </div>
    </div>
  );
};
