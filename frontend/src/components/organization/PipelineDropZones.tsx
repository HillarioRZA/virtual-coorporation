"use client";

import React, { useState } from "react";
import { PlusCircle } from "lucide-react";

interface PipelineDropZonesProps {
  isMain: boolean;
  onDropItem: (e: React.DragEvent) => void;
}

export default function PipelineDropZones({ isMain, onDropItem }: PipelineDropZonesProps) {
  const [isOver, setIsOver] = useState(false);

  if (isMain) return null;

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsOver(true);
      }}
      onDragLeave={() => setIsOver(false)}
      onDrop={(e) => {
        setIsOver(false);
        onDropItem(e);
      }}
      className={`min-w-[180px] h-[130px] rounded-xl border-2 border-dashed flex flex-col items-center justify-center text-center p-3 transition-all ${
        isOver
          ? "border-emerald-400 bg-emerald-500/10 text-emerald-300"
          : "border-white/15 bg-white/[0.01] text-slate-400 hover:border-white/30"
      }`}
    >
      <PlusCircle className="w-6 h-6 mb-1 opacity-70" />
      <span className="text-[11px] font-medium">Drop Role / CEO Gate</span>
      <span className="text-[9px] text-slate-500 mt-0.5">atau drag ke sela-sela tahapan</span>
    </div>
  );
}
