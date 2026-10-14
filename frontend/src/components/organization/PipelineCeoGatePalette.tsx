"use client";

import React from "react";
import { Plus, Crown, GripVertical } from "lucide-react";
import { CeoGateType } from "@/lib/types/corporate";

export interface CeoGatePreset {
  type: CeoGateType;
  label: string;
  desc: string;
}

export const CEO_GATE_PRESETS: CeoGatePreset[] = [
  {
    type: "APPROVAL_GATE",
    label: "Stage-Gate Approval",
    desc: "CEO Review & Veto Gate: Menyetujui atau menolak hasil kerja sebelum lanjut.",
  },
  {
    type: "STRATEGIC_MEETING",
    label: "Executive Strategic Meeting",
    desc: "Diskusi Meja Bundar: Founder & Direksi menyelaraskan arah dan arsitektur.",
  },
  {
    type: "DIRECTION_INPUT",
    label: "Founder Direction Input",
    desc: "Instruksi Khusus: Founder memberikan arahan parameter sebelum dieksekusi.",
  },
];

interface PipelineCeoGatePaletteProps {
  onAddCeoGate: (preset: CeoGatePreset) => void;
}

export default function PipelineCeoGatePalette({ onAddCeoGate }: PipelineCeoGatePaletteProps) {
  const handleDragStart = (e: React.DragEvent, preset: CeoGatePreset) => {
    e.dataTransfer.effectAllowed = "copy";
    e.dataTransfer.setData(
      "application/json",
      JSON.stringify({
        type: "CEO_GATE_ITEM",
        preset,
      })
    );
  };

  return (
    <div className="pt-2 border-t border-white/5">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
          <Plus className="w-3.5 h-3.5 text-amber-400" />
          <span>Sisipkan Gerbang Keputusan CEO (Human-in-the-Loop):</span>
        </div>
        <span className="text-[10px] font-mono text-amber-400/80">
          Bisa di-drag langsung ke sela-sela tahapan pipeline
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
        {CEO_GATE_PRESETS.map((preset) => (
          <button
            key={preset.type}
            type="button"
            draggable={true}
            onDragStart={(e) => handleDragStart(e, preset)}
            onClick={() => onAddCeoGate(preset)}
            className="p-2.5 rounded-xl bg-amber-500/5 hover:bg-amber-500/15 border border-amber-500/20 hover:border-amber-500/50 text-left transition-all group cursor-grab active:cursor-grabbing select-none"
            title="Drag kartu ini langsung ke posisi mana pun di pipeline atau klik untuk menambahkan!"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-xs font-medium text-amber-300 group-hover:text-amber-200">
                <Crown className="w-3 h-3 text-amber-400" />
                <span>+ {preset.label}</span>
              </div>
              <GripVertical className="w-3 h-3 text-amber-500/40 group-hover:text-amber-400" />
            </div>
            <p className="text-[10px] text-slate-400 mt-1 line-clamp-1">{preset.desc}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
