"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  ShieldCheck,
  Activity,
  Wrench,
  Zap,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Code2,
  ChevronDown,
  ChevronUp,
  Terminal,
  Lock,
} from "lucide-react";
import { SentinelAuditLog, SentinelStats } from "../../../lib/types/sentinel";
import { fetchSentinelAuditLogs, fetchSentinelStats } from "../../../lib/sentinelApi";

interface SentinelTelemetryDashboardProps {
  projectId: string;
  lastEvent?: any;
}

export function SentinelTelemetryDashboard({ projectId, lastEvent }: SentinelTelemetryDashboardProps) {
  const [logs, setLogs] = useState<SentinelAuditLog[]>([]);
  const [stats, setStats] = useState<SentinelStats>({
    total_inspections: 0,
    approved_count: 0,
    repaired_count: 0,
    rejected_count: 0,
    reliability_rate: 100.0,
    avg_latency_ms: 0.0,
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [roleFilter, setRoleFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [expandedLogId, setExpandedLogId] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!projectId) return;
    setRefreshing(true);
    try {
      const [fetchedLogs, fetchedStats] = await Promise.all([
        fetchSentinelAuditLogs(projectId, 50, roleFilter, statusFilter),
        fetchSentinelStats(projectId),
      ]);
      setLogs(fetchedLogs);
      setStats(fetchedStats);
    } catch (err) {
      console.warn("Failed loading sentinel telemetry:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [projectId, roleFilter, statusFilter]);

  // Event-Driven Sync: Muat saat dibuka & sinkronkan otomatis saat ada event baru di WebSocket Oasis
  useEffect(() => {
    loadData();
  }, [loadData, lastEvent]);

  const toggleExpand = (id: string) => {
    setExpandedLogId((prev) => (prev === id ? null : id));
  };

  const getRoleBadgeColor = (role: string) => {
    const r = role.toUpperCase();
    if (r.includes("CTO")) return "bg-cyan-500/10 text-cyan-400 border-cyan-500/30";
    if (r.includes("COS") || r.includes("CEO")) return "bg-indigo-500/10 text-indigo-400 border-indigo-500/30";
    if (r.includes("FRONTEND") || r.includes("FE")) return "bg-fuchsia-500/10 text-fuchsia-400 border-fuchsia-500/30";
    if (r.includes("BACKEND") || r.includes("BE")) return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
    if (r.includes("QA")) return "bg-amber-500/10 text-amber-400 border-amber-500/30";
    if (r.includes("DEVSECOPS")) return "bg-rose-500/10 text-rose-400 border-rose-500/30";
    return "bg-slate-800 text-slate-300 border-slate-700";
  };

  return (
    <div className="h-full flex flex-col overflow-hidden bg-slate-950 text-slate-100 rounded-2xl border border-slate-800 shadow-2xl">
      {/* Top Header & Security Lock Indicator */}
      <div className="px-5 py-3.5 border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600/30 to-cyan-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shadow-lg shadow-emerald-500/10">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
              <span>CoV Sentinel Pre-Flight Telemetry</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                ACTIVE GATEKEEPER
              </span>
            </h2>
            <p className="text-[11px] text-slate-400">
              Validasi intensi perkakas, pencegahan crash JSON, dan audit perbaikan otomatis sebelum eksekusi.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2.5">
          <span className="text-[11px] font-mono px-2.5 py-1 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 flex items-center gap-1.5">
            <Lock className="w-3.5 h-3.5 text-amber-400" />
            <span>Config: Server-Side (.env)</span>
          </span>

          <button
            onClick={loadData}
            disabled={refreshing}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 text-xs font-medium transition-all active:scale-95 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin text-cyan-400" : ""}`} />
            <span>Segarkan</span>
          </button>
        </div>
      </div>

      {/* Bento Grid Stats Cards */}
      <div className="p-4 grid grid-cols-2 md:grid-cols-4 gap-3 flex-shrink-0 bg-slate-950/60 border-b border-slate-800/60">
        {/* Card 1: Total Inspections */}
        <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800/80 flex items-center space-x-3 shadow-sm hover:border-slate-700 transition-colors">
          <div className="p-2.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] font-medium text-slate-400">Total Pre-Flight</div>
            <div className="text-lg font-bold text-white tracking-tight">{stats.total_inspections}</div>
          </div>
        </div>

        {/* Card 2: Reliability Rate */}
        <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800/80 flex items-center space-x-3 shadow-sm hover:border-slate-700 transition-colors">
          <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] font-medium text-slate-400">Reliabilitas Sistem</div>
            <div className="text-lg font-bold text-emerald-400 tracking-tight">{stats.reliability_rate}%</div>
          </div>
        </div>

        {/* Card 3: Auto-Repairs */}
        <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800/80 flex items-center space-x-3 shadow-sm hover:border-slate-700 transition-colors">
          <div className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Wrench className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] font-medium text-slate-400">Auto-Repairs (CoV)</div>
            <div className="text-lg font-bold text-amber-300 tracking-tight">{stats.repaired_count}</div>
          </div>
        </div>

        {/* Card 4: Average Latency */}
        <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800/80 flex items-center space-x-3 shadow-sm hover:border-slate-700 transition-colors">
          <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] font-medium text-slate-400">Rerata Latensi CoV</div>
            <div className="text-lg font-bold text-indigo-300 tracking-tight">{stats.avg_latency_ms} ms</div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="px-5 py-2.5 bg-slate-900/40 border-b border-slate-800/60 flex flex-wrap items-center justify-between gap-2.5">
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-slate-400 font-medium">Filter Agen:</span>
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">Semua Agen</option>
            <option value="COS">CoS</option>
            <option value="CTO">CTO</option>
            <option value="PM">PM</option>
            <option value="UI_UX">UI/UX Designer</option>
            <option value="FRONTEND">Frontend Engineer</option>
            <option value="BACKEND">Backend Engineer</option>
            <option value="DEVSECOPS">DevSecOps</option>
            <option value="QA">QA Engineer</option>
            <option value="LEGAL">Legal Specialist</option>
          </select>
        </div>

        <div className="flex items-center space-x-1.5 text-xs">
          {["ALL", "APPROVED", "REPAIRED", "REJECTED"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                statusFilter === st
                  ? "bg-slate-800 text-white border border-slate-600 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Live Audit Log Feed */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2.5">
        {loading && logs.length === 0 ? (
          <div className="h-48 flex items-center justify-center text-slate-500 text-xs">
            <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            <span>Memuat rekaman telemetri CoV Sentinel...</span>
          </div>
        ) : logs.length === 0 ? (
          <div className="h-64 flex flex-col items-center justify-center text-slate-500 text-center p-6 border border-dashed border-slate-800 rounded-xl">
            <ShieldCheck className="w-10 h-10 text-slate-600 mb-2" />
            <p className="text-sm font-semibold text-slate-400">Belum Ada Rekaman Audit CoV</p>
            <p className="text-xs text-slate-500 max-w-sm mt-1">
              Setiap kali Anda mengirim arahan atau mendiskusikan tugas dengan agen di Oasis, inspeksi pre-flight CoV akan tercatat di sini secara transparan.
            </p>
          </div>
        ) : (
          logs.map((log) => {
            const isExpanded = expandedLogId === log.id;
            const isRepaired = log.status === "REPAIRED";
            const isApproved = log.status === "APPROVED";

            return (
              <div
                key={log.id}
                className={`rounded-xl border transition-all ${
                  isRepaired
                    ? "bg-amber-950/20 border-amber-500/30 hover:border-amber-500/50"
                    : isApproved
                    ? "bg-slate-900/60 border-slate-800/80 hover:border-slate-700"
                    : "bg-rose-950/20 border-rose-500/30 hover:border-rose-500/50"
                }`}
              >
                {/* Audit Header Row */}
                <div
                  onClick={() => toggleExpand(log.id)}
                  className="p-3 flex items-center justify-between cursor-pointer select-none gap-3"
                >
                  <div className="flex items-center space-x-2.5 min-w-0">
                    {/* Status Pill */}
                    {isApproved && (
                      <span className="flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>APPROVED</span>
                      </span>
                    )}
                    {isRepaired && (
                      <span className="flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30 animate-pulse">
                        <Wrench className="w-3 h-3" />
                        <span>AUTO-REPAIRED</span>
                      </span>
                    )}
                    {!isApproved && !isRepaired && (
                      <span className="flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30">
                        <XCircle className="w-3 h-3" />
                        <span>REJECTED</span>
                      </span>
                    )}

                    {/* Agent Role Badge */}
                    <span className={`text-[11px] font-mono font-bold px-2 py-0.5 rounded-md border ${getRoleBadgeColor(log.agent_role)}`}>
                      {log.agent_role}
                    </span>

                    {/* Tool Badge or Chat */}
                    {log.tool_name ? (
                      <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700 flex items-center gap-1">
                        <Terminal className="w-3 h-3" />
                        <span>{log.tool_name}</span>
                      </span>
                    ) : (
                      <span className="text-[11px] text-slate-400 font-mono">
                        💬 Percakapan Bebas (No Tool)
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-3 text-[11px] text-slate-400 flex-shrink-0">
                    <span className="font-mono text-indigo-300">⚡ {log.latency_ms}ms</span>
                    <span className="hidden sm:inline font-mono">{log.created_at ? new Date(log.created_at).toLocaleTimeString() : ""}</span>
                    <button className="text-slate-400 hover:text-white">
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Content Snippet when Collapsed */}
                {!isExpanded && (
                  <div className="px-3 pb-2.5 text-xs text-slate-400 truncate font-mono">
                    {log.inspected_content.slice(0, 110)}...
                  </div>
                )}

                {/* Expanded Details Drawer */}
                {isExpanded && (
                  <div className="px-4 pb-4 pt-1 border-t border-slate-800/80 space-y-3">
                    {/* Repair Feedback Note */}
                    {log.repair_feedback && (
                      <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 flex items-start gap-2">
                        <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <span className="font-bold">Umpan Balik Koreksi CoV: </span>
                          <span>{log.repair_feedback}</span>
                        </div>
                      </div>
                    )}

                    {/* Side-by-Side Comparison */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="space-y-1">
                        <div className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
                          <span>Kandidat Respons Asli Agen:</span>
                        </div>
                        <pre className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-300 font-mono overflow-x-auto whitespace-pre-wrap max-h-48">
                          {log.original_content}
                        </pre>
                      </div>

                      <div className="space-y-1">
                        <div className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1">
                          <span>Hasil Inspeksi / Verifikasi CoV:</span>
                        </div>
                        <pre className="p-2.5 rounded-lg bg-slate-950 border border-emerald-950/60 text-[11px] text-emerald-300 font-mono overflow-x-auto whitespace-pre-wrap max-h-48">
                          {log.inspected_content}
                        </pre>
                      </div>
                    </div>

                    {/* Tool Parameters Inspection */}
                    {log.tool_parameters && (
                      <div className="space-y-1 pt-1">
                        <div className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
                          <Code2 className="w-3.5 h-3.5 text-cyan-400" />
                          <span>Parameter Perkakas Disetujui (JSON):</span>
                        </div>
                        <pre className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-cyan-300 font-mono overflow-x-auto max-h-36">
                          {JSON.stringify(log.tool_parameters, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
