/**
 * Top HUD Overlay Control Bar for Apple Park 3D Campus.
 * Houses camera mode switcher (First-Person, God-Mode, Orbit) and time presets.
 */

"use client";

import { Eye, Compass, Sun, Moon, Sunrise, Sunset, Footprints } from "lucide-react";
import { CameraViewMode } from "../core/Office3DTypes";

interface OfficeCanvasTopBarProps {
  camMode: CameraViewMode;
  onToggleCamMode: () => void;
  timeDisplay: string;
  onSetPresetHour: (h: number) => void;
}

export function OfficeCanvasTopBar({
  camMode,
  onToggleCamMode,
  timeDisplay,
  onSetPresetHour,
}: OfficeCanvasTopBarProps) {
  const timePresets = [
    { h: 7, l: "Pagi", c: "text-amber-300", Icon: Sunrise },
    { h: 12, l: "Siang", c: "text-sky-300", Icon: Sun },
    { h: 17.5, l: "Sore", c: "text-rose-300", Icon: Sunset },
    { h: 22, l: "Malam", c: "text-indigo-300", Icon: Moon },
  ];

  const getModeBadge = () => {
    if (camMode === "GOD_MODE") {
      return {
        cls: "bg-purple-600/90 border-purple-500/50 text-white shadow-purple-500/25",
        icon: <Eye className="w-3.5 h-3.5 text-white animate-pulse" />,
        text: "God Mode [Spectator Flying]",
      };
    }
    if (camMode === "FIRST_PERSON") {
      return {
        cls: "bg-emerald-600/90 border-emerald-500/50 text-white shadow-emerald-500/25",
        icon: <Footprints className="w-3.5 h-3.5 text-white" />,
        text: "First-Person PoV [Walk • Tab: Fly]",
      };
    }
    return {
      cls: "bg-slate-900/80 border-slate-700/60 text-slate-300 hover:text-white",
      icon: <Compass className="w-3.5 h-3.5 text-indigo-400" />,
      text: "Tactical Orbit [Helper Mode]",
    };
  };

  const badge = getModeBadge();

  return (
    <div className="absolute top-4 left-4 z-10 flex flex-wrap items-center gap-2">
      {/* 1. Camera Mode Switcher Button */}
      <button
        onClick={onToggleCamMode}
        className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-xl border text-xs font-semibold backdrop-blur-md shadow-xl transition-all active:scale-95 ${badge.cls}`}
        title="Beralih Mode Kamera (Atau tekan Tab di keyboard)"
      >
        {badge.icon}
        <span>{badge.text}</span>
      </button>

      {/* 2. Time Badge */}
      <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-900/85 border border-slate-700/60 backdrop-blur-md text-xs font-mono font-bold text-amber-300 shadow-xl">
        <span>{timeDisplay}</span>
      </div>

      {/* 3. Time Presets */}
      <div className="flex items-center space-x-1 bg-slate-900/85 p-0.5 rounded-xl border border-slate-700/60 backdrop-blur-md shadow-xl text-[11px]">
        {timePresets.map(({ h, l, c, Icon }) => (
          <button key={l} onClick={() => onSetPresetHour(h)} className={`px-2 py-1 rounded-lg hover:bg-slate-800 ${c} flex items-center gap-1`}>
            <Icon className="w-3 h-3" /> {l}
          </button>
        ))}
      </div>
    </div>
  );
}
