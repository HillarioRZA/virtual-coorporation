/**
 * Transparent Glass Elevator Floor Selector HUD.
 * Renders proximity [F] prompt and translucent floor dispatch cards (Fl 1 - Fl 4).
 */

"use client";

import { ArrowUpCircle, X } from "lucide-react";

interface OfficeElevatorModalHUDProps {
  isNearElevator: boolean;
  isMenuOpen: boolean;
  currentFloor: number;
  isMoving: boolean;
  onSelectFloor: (fl: number) => void;
  onToggleMenu: () => void;
}

export function OfficeElevatorModalHUD({
  isNearElevator,
  isMenuOpen,
  currentFloor,
  isMoving,
  onSelectFloor,
  onToggleMenu,
}: OfficeElevatorModalHUDProps) {
  if (!isNearElevator) return null;

  const floors = [
    { fl: 4, name: "Fl 4: Founder Apex Penthouse", badge: "Crown Suite", color: "border-amber-500/50 text-amber-300" },
    { fl: 3, name: "Fl 3: Leadership & Boardroom", badge: "Executive", color: "border-indigo-500/50 text-indigo-300" },
    { fl: 2, name: "Fl 2: Product Strategy & UX", badge: "Design Lab", color: "border-sky-500/50 text-sky-300" },
    { fl: 1, name: "Fl 1: Silicon Lab & Caffè Macs", badge: "Ground", color: "border-emerald-500/50 text-emerald-300" },
  ];

  return (
    <>
      {/* 1. Proximity Floating Prompt */}
      {!isMenuOpen && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 z-20 pointer-events-none animate-bounce">
          <div className="flex items-center space-x-2 px-4 py-2 rounded-2xl bg-slate-950/80 border border-sky-500/50 backdrop-blur-xl shadow-2xl text-xs font-mono text-sky-300">
            <span className="px-1.5 py-0.5 rounded bg-sky-500 text-slate-950 font-bold text-[10px]">F</span>
            <span>Tekan F untuk Memilih Lantai Lift (Fl 1–4)</span>
          </div>
        </div>
      )}

      {/* 2. Transparent Floor Selector Modal */}
      {isMenuOpen && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-80 p-4 rounded-3xl bg-slate-950/85 border border-slate-700/60 backdrop-blur-2xl shadow-2xl font-mono text-slate-200">
          <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-800">
            <div className="flex items-center space-x-2 text-xs font-bold text-sky-400 uppercase">
              <ArrowUpCircle className={`w-4 h-4 ${isMoving ? "animate-spin text-amber-400" : "text-sky-400"}`} />
              <span>Elevator Control Core</span>
            </div>
            <button onClick={onToggleMenu} className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2 mb-3">
            {floors.map((item) => (
              <button
                key={item.fl}
                onClick={() => onSelectFloor(item.fl)}
                className={`w-full flex items-center justify-between p-2.5 rounded-xl border text-xs transition-all active:scale-95 ${
                  currentFloor === item.fl
                    ? "bg-sky-500/20 border-sky-400 text-white shadow-lg shadow-sky-500/20 font-bold"
                    : "bg-slate-900/60 hover:bg-slate-800/80 border-slate-800 text-slate-300"
                }`}
              >
                <div className="flex items-center space-x-2">
                  <span className="w-5 h-5 rounded-lg bg-slate-800 text-sky-300 font-bold flex items-center justify-center text-[11px]">
                    {item.fl}
                  </span>
                  <span>{item.name}</span>
                </div>
                <span className={`text-[10px] px-1.5 py-0.5 rounded border ${item.color}`}>{item.badge}</span>
              </button>
            ))}
          </div>

          <div className="text-[10px] text-center text-slate-500 border-t border-slate-800 pt-2">
            Tekan [1-4] untuk pilih cepat • [Esc / F] untuk tutup
          </div>
        </div>
      )}
    </>
  );
}
