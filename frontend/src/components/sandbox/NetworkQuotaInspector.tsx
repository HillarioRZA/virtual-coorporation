"use client";

import { useEffect, useState } from "react";
import {
  Network,
  Cpu,
  HardDrive,
  RefreshCw,
  Play,
  Square,
  CheckCircle2,
} from "lucide-react";
import {
  fetchNetworkStatus,
  fetchSandboxMetrics,
  launchMultiService,
  stopMultiService,
} from "../../lib/sandboxNetworkApi";
import { NetworkStatusInfo, SandboxMetricsInfo } from "../../lib/types/sandboxNetwork";
import { ComposeServicesGrid } from "./ComposeServicesGrid";

interface NetworkQuotaInspectorProps {
  projectId: string;
}

export function NetworkQuotaInspector({ projectId }: NetworkQuotaInspectorProps) {
  const [network, setNetwork] = useState<NetworkStatusInfo | null>(null);
  const [metrics, setMetrics] = useState<SandboxMetricsInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [toastMsg, setToastMsg] = useState<string>("");

  const loadData = async () => {
    try {
      setLoading(true);
      const [netData, metricData] = await Promise.all([
        fetchNetworkStatus(projectId),
        fetchSandboxMetrics(projectId),
      ]);
      setNetwork(netData);
      setMetrics(metricData);
    } catch (err: any) {
      console.error("Gagal load sandboxing data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) loadData();
    const interval = setInterval(() => {
      if (projectId) {
        fetchSandboxMetrics(projectId).then(setMetrics).catch(() => {});
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [projectId]);

  const handleLaunch = async () => {
    try {
      setActionLoading(true);
      await launchMultiService(projectId, `./sandbox_workspaces/${projectId}`);
      setToastMsg("Stack Multi-Compose berhasil diluncurkan.");
      await loadData();
    } catch (err: any) {
      setToastMsg(err.message || "Gagal meluncurkan stack.");
    } finally {
      setActionLoading(false);
      setTimeout(() => setToastMsg(""), 4000);
    }
  };

  const handleStop = async () => {
    try {
      setActionLoading(true);
      await stopMultiService(projectId);
      setToastMsg("Stack dan bridge network berhasil dihentikan.");
      await loadData();
    } catch (err: any) {
      setToastMsg(err.message || "Gagal menghentikan stack.");
    } finally {
      setActionLoading(false);
      setTimeout(() => setToastMsg(""), 4000);
    }
  };

  const cpuPercent = metrics?.cpu_used_percent ?? metrics?.cpu_percent ?? 0;
  const memPercent = metrics?.memory_percent ?? 0;

  return (
    <div className="flex-1 bg-slate-950/90 border-x border-b border-slate-800 rounded-b-2xl p-5 overflow-y-auto space-y-5">
      {/* Top Banner & Control */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900/80 p-4 rounded-2xl border border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-cyan-600/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-white">Docker Bridge & Resource Quota</h3>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase border ${
                network?.mode === "docker"
                  ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/30"
                  : "bg-amber-500/20 text-amber-300 border-amber-500/30"
              }`}>
                {network?.mode || "offline"} mode
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Net: {network?.network_name || `bridge_net_${projectId}`} • Subnet: {network?.subnet || "172.28.0.0/16"}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={loadData}
            disabled={loading}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Refresh Metrics"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={handleLaunch}
            disabled={actionLoading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition-all active:scale-95"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Launch Stack</span>
          </button>
          <button
            onClick={handleStop}
            disabled={actionLoading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 border border-rose-500/30 text-rose-300 text-xs font-semibold transition-colors"
          >
            <Square className="w-3.5 h-3.5" />
            <span>Tear Down</span>
          </button>
        </div>
      </div>

      {toastMsg && (
        <div className="p-3 rounded-xl bg-cyan-950/40 border border-cyan-500/30 text-xs text-cyan-300 flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-cyan-400 flex-shrink-0" />
          <span>{toastMsg}</span>
        </div>
      )}

      {/* Quota Progress Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* CPU Hard Quota */}
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2 text-slate-300 font-semibold">
              <Cpu className="w-4 h-4 text-indigo-400" />
              <span>CPU Hard Quota</span>
            </div>
            <span className="font-mono text-indigo-300 font-bold">
              {cpuPercent}% / 1.5 Cores
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div
              className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(cpuPercent, 100)}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-500 font-mono">--cpus=1.5 per venture sandbox</p>
        </div>

        {/* Memory Hard Quota */}
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2 text-slate-300 font-semibold">
              <HardDrive className="w-4 h-4 text-cyan-400" />
              <span>RAM Quota & Swap</span>
            </div>
            <span className="font-mono text-cyan-300 font-bold">
              {metrics?.memory_used_mb ?? 0} MB / 1024 MB ({memPercent}%)
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div
              className="bg-cyan-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(memPercent, 100)}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-500 font-mono">--memory=1024m --memory-swap=1024m</p>
        </div>
      </div>

      {/* Micro-Compose Services Matrix */}
      <ComposeServicesGrid services={metrics?.services} />
    </div>
  );
}
