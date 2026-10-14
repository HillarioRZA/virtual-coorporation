"use client";

import { Layers } from "lucide-react";
import { ServiceMetricsInfo } from "../../lib/types/sandboxNetwork";

interface ComposeServicesGridProps {
  services?: ServiceMetricsInfo[];
}

export function ComposeServicesGrid({ services }: ComposeServicesGridProps) {
  const serviceList = services && services.length > 0
    ? services
    : [
        { name: "frontend", status: "STANDBY", port: 3000 },
        { name: "backend", status: "STANDBY", port: 8000 },
        { name: "database", status: "STANDBY", port: 5432 },
      ];

  return (
    <div className="space-y-3">
      <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
        <Layers className="w-4 h-4 text-indigo-400" />
        <span>Micro-Compose Multi-Service Stack</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {serviceList.map((srv, idx) => (
          <div key={idx} className="p-3.5 rounded-xl bg-slate-900/40 border border-slate-800/80 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white capitalize">{srv.name}</span>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                {srv.status || "RUNNING"}
              </span>
            </div>
            <div className="text-[11px] text-slate-400 font-mono space-y-0.5">
              <div>
                Port: {srv.port || (srv.name.includes("fe") ? 3000 : (srv.name.includes("be") ? 8000 : 5432))}
              </div>
              {srv.cpu_percent !== undefined && (
                <div>CPU: {srv.cpu_percent}% • Mem: {srv.memory_mb}MB</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
