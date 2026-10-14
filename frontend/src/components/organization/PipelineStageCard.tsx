"use client";

import React from "react";
import { Crown, GripVertical, ArrowLeft, ArrowRight, Copy, Trash2 } from "lucide-react";
import { PipelineStageItem } from "@/lib/types/corporate";

interface PipelineStageCardProps {
  stage: PipelineStageItem;
  index: number;
  totalStages: number;
  isMain: boolean;
  isDragging: boolean;
  isOver: boolean;
  onDragStart: (e: React.DragEvent, index: number) => void;
  onDragOver: (e: React.DragEvent, index: number) => void;
  onDrop: (e: React.DragEvent, index: number) => void;
  onDragEnd: () => void;
  onMoveStage: (index: number, direction: -1 | 1) => void;
  onDuplicateStage: (index: number) => void;
  onRemoveStage: (index: number) => void;
}

export default function PipelineStageCard({
  stage,
  index,
  totalStages,
  isMain,
  isDragging,
  isOver,
  onDragStart,
  onDragOver,
  onDrop,
  onDragEnd,
  onMoveStage,
  onDuplicateStage,
  onRemoveStage,
}: PipelineStageCardProps) {
  const isCeo = stage.stage_type === "CEO_GATE";

  return (
    <div
      draggable={!isMain}
      onDragStart={(e) => onDragStart(e, index)}
      onDragOver={(e) => onDragOver(e, index)}
      onDrop={(e) => onDrop(e, index)}
      onDragEnd={onDragEnd}
      className={`min-w-[220px] max-w-[250px] flex-shrink-0 p-3.5 rounded-xl transition-all duration-200 flex flex-col justify-between space-y-2.5 select-none ${
        isCeo
          ? "bg-gradient-to-b from-amber-500/15 to-amber-950/30 border-2 border-amber-500/50 shadow-lg shadow-amber-500/10"
          : "bg-white/[0.03] border border-white/10 hover:border-white/20"
      } ${isDragging ? "opacity-40 scale-95" : ""} ${
        isOver ? "border-emerald-400 ring-2 ring-emerald-400/30 scale-105" : ""
      } ${!isMain ? "cursor-grab active:cursor-grabbing" : ""}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          {!isMain && <GripVertical className="w-3.5 h-3.5 text-slate-500" />}
          <span className="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 font-mono text-[10px] text-slate-300">
            #{index + 1}
          </span>
        </div>

        {isCeo ? (
          <span className="px-2 py-0.5 rounded-md text-[9px] font-bold tracking-wider bg-amber-400/20 text-amber-300 border border-amber-400/30 flex items-center gap-1">
            <Crown className="w-2.5 h-2.5 text-amber-400" />
            CEO GATE
          </span>
        ) : (
          <span
            className="px-2 py-0.5 rounded-md text-[9px] font-semibold uppercase tracking-wider"
            style={{
              backgroundColor: `${stage.division_color || "#38bdf8"}22`,
              color: stage.division_color || "#38bdf8",
            }}
          >
            {stage.division_name || "General"}
          </span>
        )}
      </div>

      <div>
        <div className="flex items-center gap-1.5">
          {isCeo && <Crown className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />}
          <p className={`text-xs font-semibold truncate ${isCeo ? "text-amber-200" : "text-white"}`}>
            {stage.custom_label || stage.role_name}
          </p>
        </div>
        <p className="text-[10px] font-mono text-slate-400 truncate mt-0.5">
          {isCeo
            ? `Mode: ${stage.ceo_gate_type || "APPROVAL_GATE"}`
            : stage.model_name?.split("/")[1] || stage.model_name || "AI Agent"}
        </p>
        {stage.custom_instructions && (
          <p className="text-[10px] text-slate-400 line-clamp-1 italic mt-1">
            &quot;{stage.custom_instructions}&quot;
          </p>
        )}
      </div>

      {!isMain && (
        <div className="flex items-center justify-between pt-1.5 border-t border-white/5 text-slate-400">
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => onMoveStage(index, -1)}
              disabled={index === 0}
              className="p-1 rounded-lg border border-white/10 hover:bg-white/5 disabled:opacity-20 text-slate-400 hover:text-white"
              title="Geser Mundur"
            >
              <ArrowLeft className="w-3 h-3" />
            </button>
            <button
              type="button"
              onClick={() => onMoveStage(index, 1)}
              disabled={index === totalStages - 1}
              className="p-1 rounded-lg border border-white/10 hover:bg-white/5 disabled:opacity-20 text-slate-400 hover:text-white"
              title="Geser Maju"
            >
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => onDuplicateStage(index)}
              className="p-1 rounded-lg border border-white/10 hover:bg-indigo-500/20 text-slate-400 hover:text-indigo-300 transition-all"
              title="Gandakan Peran (Buat Loop A ➔ B ➔ A)"
            >
              <Copy className="w-3 h-3" />
            </button>
            <button
              type="button"
              onClick={() => onRemoveStage(index)}
              className="p-1 rounded-lg border border-white/10 hover:bg-red-500/20 text-slate-400 hover:text-red-300 transition-all"
              title="Hapus Tahapan"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
