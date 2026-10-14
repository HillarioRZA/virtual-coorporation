"use client";

import React from "react";
import { Server, Clock, Activity, CheckCircle2, AlertTriangle, RefreshCw } from "lucide-react";
import { ChannelHealthItem } from "@/lib/types/analytics";

interface ChannelHealthRadarProps {
  channels: ChannelHealthItem[];
  onRefresh: () => void;
  loading: boolean;
}

export const ChannelHealthRadar: React.FC<ChannelHealthRadarProps> = ({ channels, onRefresh, loading }) => {
  return (
    <div className="p-5 rounded-2xl bg-zinc-900/60 border border-zinc-800/80 backdrop-blur-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            Upstream Router Channels & Rate Limit Radar
          </h3>
          <p className="text-xs text-zinc-400 mt-0.5">
            Sliding-window RPM/TPM tracker & auto-cooldown protection ala 9router.
          </p>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="p-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 transition"
          title="Refresh Radar"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {channels.length === 0 ? (
        <div className="py-6 text-center text-xs text-zinc-400 border border-dashed border-zinc-800 rounded-xl">
          Belum ada aktivitas router tercatat. Saluran akan muncul otomatis saat LLM dieksekusi.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {channels.map((ch, idx) => {
            const isCooling = ch.is_cooling_down || ch.cooldown_seconds_left > 0;
            return (
              <div
                key={idx}
                className={`p-3 rounded-xl border transition-all ${
                  isCooling
                    ? "bg-amber-950/20 border-amber-500/30"
                    : "bg-zinc-850/50 border-zinc-800/80 hover:border-zinc-700"
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-300 border border-zinc-700">
                      {ch.provider}
                    </span>
                    <h4 className="text-xs font-semibold text-white mt-1 truncate max-w-[180px]" title={ch.model_name}>
                      {ch.model_name}
                    </h4>
                  </div>
                  {isCooling ? (
                    <span className="flex items-center gap-1 text-[11px] font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                      <Clock className="w-3 h-3 animate-spin" />
                      {Math.ceil(ch.cooldown_seconds_left)}s
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      <CheckCircle2 className="w-3 h-3" />
                      Ready
                    </span>
                  )}
                </div>

                <div className="space-y-1.5 mt-3 pt-2 border-t border-zinc-800/60 text-[11px] font-mono text-zinc-400">
                  <div className="flex justify-between">
                    <span>RPM Window:</span>
                    <span className="text-zinc-200">
                      {ch.current_rpm} / {ch.rpm_limit}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>TPM Window:</span>
                    <span className="text-zinc-200">
                      {ch.current_tpm.toLocaleString()} / {ch.tpm_limit.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
