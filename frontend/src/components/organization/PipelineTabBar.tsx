"use client";

import React from "react";
import { Laptop, GraduationCap, Feather, BarChart2, Sparkles, Plus, Trash2 } from "lucide-react";
import { PipelineResponse, ProductLineType } from "@/lib/types/corporate";

interface PipelineTabBarProps {
  pipelines: PipelineResponse[];
  activePipelineId: string;
  onSelectPipeline: (id: string) => void;
  onCreatePipeline: () => void;
  onDeletePipeline?: (id: string) => void;
  isMain: boolean;
}

const getProductLineIcon = (line: ProductLineType) => {
  switch (line) {
    case "SOFTWARE":
      return <Laptop className="w-3.5 h-3.5 text-blue-400" />;
    case "EDUCATION":
      return <GraduationCap className="w-3.5 h-3.5 text-emerald-400" />;
    case "COPYWRITING":
      return <Feather className="w-3.5 h-3.5 text-amber-400" />;
    case "MARKET_RESEARCH":
      return <BarChart2 className="w-3.5 h-3.5 text-purple-400" />;
    default:
      return <Sparkles className="w-3.5 h-3.5 text-indigo-400" />;
  }
};

export default function PipelineTabBar({
  pipelines,
  activePipelineId,
  onSelectPipeline,
  onCreatePipeline,
  onDeletePipeline,
  isMain,
}: PipelineTabBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-1.5 pb-2 border-b border-white/5">
      {pipelines.map((pipe) => {
        const isActive = pipe.id === activePipelineId;
        const canDelete = !isMain && !pipe.is_default && onDeletePipeline;

        return (
          <div
            key={pipe.id}
            onClick={() => onSelectPipeline(pipe.id)}
            className={`group flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs cursor-pointer transition-all ${
              isActive
                ? "bg-indigo-600/20 border-indigo-500/50 text-white font-medium shadow-md shadow-indigo-500/10"
                : "bg-white/[0.03] border-white/5 text-slate-400 hover:text-white hover:border-white/15"
            }`}
          >
            {getProductLineIcon(pipe.product_line)}
            <span className="truncate max-w-[160px] sm:max-w-[220px]">{pipe.name}</span>
            {pipe.is_default && (
              <span className="text-[9px] font-mono px-1 rounded bg-white/5 text-slate-400">
                Default
              </span>
            )}
            {canDelete && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeletePipeline(pipe.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-rose-500/20 text-rose-400 transition-opacity ml-1"
                title="Hapus Pipeline Kustom"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            )}
          </div>
        );
      })}

      {!isMain && (
        <button
          type="button"
          onClick={onCreatePipeline}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl border border-dashed border-white/20 hover:border-indigo-400/50 text-slate-400 hover:text-indigo-300 text-xs transition-all"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Pipeline Baru</span>
        </button>
      )}
    </div>
  );
}
