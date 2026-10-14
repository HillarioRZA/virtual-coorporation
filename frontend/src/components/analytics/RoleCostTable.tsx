"use client";

import React from "react";
import { Users, BarChart3 } from "lucide-react";
import { RoleCostItem } from "@/lib/types/analytics";

interface RoleCostTableProps {
  roles: RoleCostItem[];
  totalCost: number;
}

export const RoleCostTable: React.FC<RoleCostTableProps> = ({ roles, totalCost }) => {
  return (
    <div className="p-5 rounded-2xl bg-zinc-900/60 border border-zinc-800/80 backdrop-blur-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Users className="w-4 h-4 text-purple-400" />
            Agent Role Cost & Token Attribution
          </h3>
          <p className="text-xs text-zinc-400 mt-0.5">
            Rincian konsumsi token & biaya per peran agen kecerdasan buatan.
          </p>
        </div>
      </div>

      {roles.length === 0 ? (
        <div className="py-8 text-center text-xs text-zinc-400 border border-dashed border-zinc-800 rounded-xl">
          Belum ada riwayat eksekusi agen pada buku kas token korporat.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-zinc-800 text-zinc-400 font-mono text-[11px]">
                <th className="pb-2.5 font-medium">PERAN AGEN</th>
                <th className="pb-2.5 font-medium text-right">TOTAL PANGGILAN</th>
                <th className="pb-2.5 font-medium text-right">TOTAL TOKEN</th>
                <th className="pb-2.5 font-medium text-right">FAILOVERS</th>
                <th className="pb-2.5 font-medium text-right">BIAYA (USD)</th>
                <th className="pb-2.5 font-medium text-right">SHARE %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-850">
              {roles.map((r, idx) => {
                const share = totalCost > 0 ? (r.total_cost_usd / totalCost) * 100 : 0;
                return (
                  <tr key={idx} className="hover:bg-zinc-800/30 transition-colors">
                    <td className="py-2.5 font-medium text-white flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-purple-400" />
                      {r.role_name || r.role_id}
                    </td>
                    <td className="py-2.5 text-right font-mono text-zinc-300">
                      {r.request_count.toLocaleString()}
                    </td>
                    <td className="py-2.5 text-right font-mono text-zinc-300">
                      {r.total_tokens.toLocaleString()}
                    </td>
                    <td className="py-2.5 text-right font-mono">
                      {r.fallbacks_count > 0 ? (
                        <span className="text-amber-400 px-1.5 py-0.5 rounded bg-amber-500/10">
                          {r.fallbacks_count}
                        </span>
                      ) : (
                        <span className="text-zinc-400">0</span>
                      )}
                    </td>
                    <td className="py-2.5 text-right font-mono text-emerald-400 font-semibold">
                      ${r.total_cost_usd.toFixed(4)}
                    </td>
                    <td className="py-2.5 text-right font-mono text-zinc-400">
                      {share.toFixed(1)}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
