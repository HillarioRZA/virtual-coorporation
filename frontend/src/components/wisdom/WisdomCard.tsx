"use client";

import React from "react";
import { Sparkles, Trash2, Tag, BookOpen, CheckCircle, ShieldAlert } from "lucide-react";
import { WisdomItem } from "@/lib/types/wisdom";

interface WisdomCardProps {
  item: WisdomItem;
  onDelete?: (id: string) => void;
}

export function WisdomCard({ item, onDelete }: WisdomCardProps) {
  const getNamespaceBadge = (ns: string) => {
    switch (ns) {
      case "wisdom:architecture":
        return { label: "Architecture", color: "bg-indigo-500/10 text-indigo-400 border-indigo-500/30" };
      case "wisdom:bugs_and_fixes":
        return { label: "Bugs & Fixes", color: "bg-rose-500/10 text-rose-400 border-rose-500/30" };
      case "wisdom:growth_copy":
        return { label: "Growth & Copy", color: "bg-amber-500/10 text-amber-400 border-amber-500/30" };
      default:
        return { label: ns.replace("wisdom:", ""), color: "bg-slate-500/10 text-slate-400 border-slate-500/30" };
    }
  };

  const badge = getNamespaceBadge(item.namespace);

  return (
    <div className="liquid-glass p-5 rounded-2xl border border-white/10 hover:border-white/20 transition-all flex flex-col justify-between space-y-4 group">
      <div className="space-y-3">
        {/* Header Badges */}
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className={`text-[10px] uppercase font-mono font-semibold px-2.5 py-0.5 rounded-full border ${badge.color}`}>
              {badge.label}
            </span>
            {item.similarity_score !== undefined && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                <Sparkles className="w-2.5 h-2.5" />
                {Math.round(item.similarity_score * 100)}% match
              </span>
            )}
          </div>
          {onDelete && (
            <button
              onClick={() => onDelete(item.id)}
              className="text-slate-500 hover:text-rose-400 p-1 rounded-lg hover:bg-rose-500/10 transition-colors opacity-0 group-hover:opacity-100"
              title="Hapus Wisdom"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Title */}
        <h3 className="text-sm font-bold text-white tracking-tight flex items-start gap-2">
          <BookOpen className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
          <span>{item.title}</span>
        </h3>

        {/* Problem Pattern */}
        <div className="bg-rose-500/5 border border-rose-500/15 rounded-xl p-3 text-xs space-y-1">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold text-rose-400">
            <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
            <span>Problem Pattern</span>
          </div>
          <p className="text-slate-300 leading-relaxed font-sans">{item.problem_pattern}</p>
        </div>

        {/* Solution Guideline */}
        <div className="bg-emerald-500/5 border border-emerald-500/15 rounded-xl p-3 text-xs space-y-1">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-400">
            <CheckCircle className="w-3.5 h-3.5 shrink-0" />
            <span>Solution Guideline</span>
          </div>
          <p className="text-slate-200 leading-relaxed font-sans font-medium">{item.solution_guideline}</p>
        </div>
      </div>

      {/* Footer Tags & Metadata */}
      <div className="pt-2 border-t border-white/5 flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono text-slate-400">
        <div className="flex flex-wrap gap-1">
          {item.tags.map((t, idx) => (
            <span key={idx} className="bg-white/5 px-2 py-0.5 rounded text-[10px] text-slate-400 flex items-center gap-1">
              <Tag className="w-2.5 h-2.5" />
              {t}
            </span>
          ))}
        </div>
        <div className="text-[10px] text-slate-500 font-mono">
          Reused: <span className="text-indigo-400 font-bold">{item.usage_count}x</span>
        </div>
      </div>
    </div>
  );
}
