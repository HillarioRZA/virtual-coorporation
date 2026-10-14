/**
 * Modern Clean Campus Control Bar for Virtual Office Simulator.
 * Features Building Switcher, Floor Switcher, and Meeting/Demo/Sound Controls.
 */

"use client";

import { useState } from "react";
import { Volume2, VolumeX, Play, Square, Users } from "lucide-react";
import { officeSound } from "./OfficeSoundManager";

interface OfficeControlBarProps {
  connected: boolean;
  demoMode: boolean;
  setDemoMode: (val: boolean) => void;
  selectedBuilding: string;
  setSelectedBuilding: (bId: string) => void;
  activeFloor: number;
  setActiveFloor: (fl: number) => void;
  callAllHandsMeeting: () => void;
}

export function OfficeControlBar({
  connected,
  demoMode,
  setDemoMode,
  selectedBuilding,
  setSelectedBuilding,
  activeFloor,
  setActiveFloor,
  callAllHandsMeeting,
}: OfficeControlBarProps) {
  const [muted, setMuted] = useState(officeSound.isMuted());

  const handleToggleMute = () => {
    const isMute = officeSound.toggleMute();
    setMuted(isMute);
  };

  const buildings = [
    { id: "all", label: "🌐 All Campus" },
    { id: "penthouse", label: "👑 Founder Penthouse" },
    { id: "ring", label: "🪐 The Grand Ring" },
    { id: "theater", label: "🎭 Steve Jobs Theater" },
    { id: "caffe", label: "☕ Caffè Macs Atrium" },
    { id: "tantau", label: "🛡️ Tantau SecOps" },
  ];

  const floors = [
    { num: 1, label: "Fl 1", desc: "Floor 1: Silicon Lab & Caffè Macs" },
    { num: 2, label: "Fl 2", desc: "Floor 2: Product & Growth Suites" },
    { num: 3, label: "Fl 3", desc: "Floor 3: Leadership & Boardroom" },
    { num: 4, label: "Fl 4", desc: "Floor 4: Founder Apex Penthouse" },
  ];

  return (
    <div className="bg-slate-950 p-2.5 rounded-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-2.5 shadow-xl">
      {/* Left: Live Connection, Building & Floor Switchers */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex items-center space-x-2 px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-800 text-xs">
          <span className={`w-2 h-2 rounded-full ${connected ? "bg-emerald-500 animate-pulse" : "bg-rose-500"}`} />
          <span className="font-semibold text-slate-300 font-mono text-[11px]">
            {connected ? "60 FPS Live" : "Offline"}
          </span>
        </div>

        {/* Building Tabs */}
        <div className="flex items-center space-x-1 bg-slate-900 p-0.5 rounded-xl border border-slate-800 text-xs">
          {buildings.map((b) => (
            <button
              key={b.id}
              onClick={() => setSelectedBuilding(b.id)}
              className={`px-2.5 py-1 rounded-lg font-medium text-xs transition-all ${
                selectedBuilding === b.id
                  ? "bg-indigo-600 text-white font-bold shadow-md shadow-indigo-600/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {b.label}
            </button>
          ))}
        </div>

        {/* Floor Tabs */}
        <div className="flex items-center space-x-1 bg-slate-900 p-0.5 rounded-xl border border-slate-800 text-xs">
          {floors.map((fl) => (
            <button
              key={fl.num}
              title={fl.desc}
              onClick={() => {
                setActiveFloor(fl.num);
                setSelectedBuilding(fl.num === 4 ? "penthouse" : "ring");
              }}
              className={`px-2.5 py-1 rounded-lg font-medium text-xs transition-all ${
                activeFloor === fl.num
                  ? "bg-sky-600 text-white font-bold shadow-md shadow-sky-600/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {fl.label}
            </button>
          ))}
        </div>
      </div>

      {/* Right: Actions (Meeting, Demo & Sound) */}
      <div className="flex items-center space-x-2">
        {/* All-Hands Gathering */}
        <button
          onClick={callAllHandsMeeting}
          className="flex items-center space-x-1 px-3 py-1 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-semibold transition-all active:scale-95"
          title="Panggil seluruh agen berkumpul di Auditorium Apollo Fl 1"
        >
          <Users className="w-3.5 h-3.5" />
          <span>All-Hands</span>
        </button>

        {/* Demo Mode Toggle */}
        <button
          onClick={() => setDemoMode(!demoMode)}
          className={`flex items-center space-x-1 px-3 py-1 rounded-xl text-xs font-semibold transition-all active:scale-95 ${
            demoMode
              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/25"
              : "bg-slate-800 hover:bg-slate-700 text-slate-300"
          }`}
        >
          {demoMode ? <Square className="w-3 h-3 fill-current" /> : <Play className="w-3 h-3" />}
          <span>Demo</span>
        </button>

        {/* Sound FX Toggle */}
        <button
          onClick={handleToggleMute}
          className="p-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-white transition-colors"
          title={muted ? "Nyalakan Audio FX" : "Matikan Audio FX"}
        >
          {muted ? <VolumeX className="w-4 h-4 text-rose-400" /> : <Volume2 className="w-4 h-4 text-emerald-400" />}
        </button>
      </div>
    </div>
  );
}
