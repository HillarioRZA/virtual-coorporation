"use client";

import React, { useEffect, useState } from "react";

interface FrontierRadarPaneProps {
  projectId: string;
}

export const FrontierRadarPane: React.FC<FrontierRadarPaneProps> = ({ projectId }) => {
  const [events, setEvents] = useState<any[]>([]);
  const [financial, setFinancial] = useState<any>(null);
  const [scorecard, setScorecard] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchRadarData = async () => {
    try {
      const [resLogs, resFin, resScore] = await Promise.all([
        fetch(`/api/v1/projects/${projectId}/frontier-radar/flight-logs`),
        fetch(`/api/v1/projects/${projectId}/frontier-radar/financial-status`),
        fetch(`/api/v1/projects/${projectId}/frontier-radar/visual-scorecard`),
      ]);

      if (resLogs.ok) {
        const dLogs = await resLogs.json();
        setEvents(dLogs.events || []);
      }
      if (resFin.ok) {
        const dFin = await resFin.json();
        setFinancial(dFin);
      }
      if (resScore.ok) {
        const dScore = await resScore.json();
        setScorecard(dScore.scorecard);
      }
    } catch {
      // Fallback local visual defaults
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRadarData();
    const interval = setInterval(fetchRadarData, 5000);
    return () => clearInterval(interval);
  }, [projectId]);

  const handleTopup = async (ticketId: string) => {
    try {
      await fetch(`/api/v1/projects/${projectId}/frontier-radar/financial-topup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticket_id: ticketId, additional_tokens: 150000, additional_dollars: 0.75 }),
      });
      fetchRadarData();
    } catch {
      // Ignore
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-slate-400">Memuat Frontier Radar Observability Hub...</div>;
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto p-6 space-y-6 text-slate-200">
      {/* 1. Header & Financial Quota Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="text-xs text-slate-400 font-mono">TOKEN BUDGET SPEND</div>
          <div className="text-xl font-bold text-indigo-400 mt-1">
            {financial?.ledger?.total_tokens?.toLocaleString() || "0"} <span className="text-xs text-slate-500">/ 350k</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-indigo-500 h-full rounded-full transition-all"
              style={{ width: `${Math.min(100, ((financial?.ledger?.total_tokens || 0) / 350000) * 100)}%` }}
            />
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="text-xs text-slate-400 font-mono">ESTIMATED DOLLAR SPEND</div>
          <div className="text-xl font-bold text-emerald-400 mt-1">
            ${financial?.ledger?.total_cost_usd?.toFixed(3) || "0.000"} <span className="text-xs text-slate-500">/ $1.50</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all"
              style={{ width: `${Math.min(100, ((financial?.ledger?.total_cost_usd || 0) / 1.5) * 100)}%` }}
            />
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="text-xs text-slate-400 font-mono">VISUAL AESTHETIC SCORE</div>
          <div className="text-xl font-bold text-amber-400 mt-1 flex items-center justify-between">
            <span>{scorecard?.aesthetic_score || 88} / 100</span>
            <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono font-normal">
              {scorecard?.status || "APPROVED"}
            </span>
          </div>
          <div className="text-[11px] text-slate-400 mt-2 font-mono">
            Contrast: {scorecard?.contrast_rating || "EXCELLENT"} • Overlaps: {scorecard?.overlapping_elements_count || 0}
          </div>
        </div>
      </div>

      {/* 2. Frozen Tickets Alerts if any */}
      {financial?.frozen_tickets && financial.frozen_tickets.length > 0 && (
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-500/40 flex items-center justify-between">
          <div>
            <div className="text-xs font-bold text-rose-300">⚠️ Tiket Dibekukan (Financial Circuit Breaker Terpicu)</div>
            <div className="text-xs text-rose-400/80">Tiket: {financial.frozen_tickets.join(", ")}</div>
          </div>
          <button
            onClick={() => handleTopup(financial.frozen_tickets[0])}
            className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold"
          >
            Founder Top-up (+$0.75)
          </button>
        </div>
      )}

      {/* 3. Black Box Flight Recorder Stream */}
      <div className="flex-1 p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col space-y-3">
        <div className="text-xs font-bold text-slate-300 flex items-center justify-between">
          <span>BLACK BOX FLIGHT RECORDER (Time-Travel Stream)</span>
          <span className="text-[11px] text-slate-500 font-mono">{events.length} events logged</span>
        </div>

        <div className="space-y-2 overflow-y-auto max-h-72 pr-2">
          {events.length === 0 ? (
            <div className="text-xs text-slate-500 italic py-6 text-center">Belum ada rekaman peristiwa flight stream.</div>
          ) : (
            events.map((ev, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-black/40 border border-slate-800/80 text-xs flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-lg bg-indigo-900/60 text-indigo-300 flex items-center justify-center font-mono font-bold text-[10px]">
                    {ev.step_index}
                  </span>
                  <div>
                    <span className="font-semibold text-slate-300">[{ev.agent_role}]</span>{" "}
                    <span className="text-indigo-400 font-mono">{ev.event_type}</span>
                  </div>
                </div>
                <span className="text-[10px] text-slate-500 font-mono">{ev.timestamp?.slice(11, 19)}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
