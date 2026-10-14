/**
 * Minimalist Transparent Real-Time Corner HUD for First-Person & God-Mode PoV.
 * Displays live player coordinates (X, Y, Z), FPS, mode badge, and quick copy button.
 */

"use client";

import { useState } from "react";
import * as THREE from "three";
import { Copy, Check, Gauge, Footprints, Eye } from "lucide-react";
import { CameraViewMode } from "../core/Office3DTypes";

interface OfficeSpatialCornerHUDProps {
  fps: number;
  playerPos: THREE.Vector3;
  camMode: CameraViewMode;
}

export function OfficeSpatialCornerHUD({ fps, playerPos, camMode }: OfficeSpatialCornerHUDProps) {
  const [copied, setCopied] = useState(false);

  // This HUD is exclusive to First-Person and God-Mode spectator PoV
  if (camMode !== "FIRST_PERSON" && camMode !== "GOD_MODE") return null;

  const copyCoordinates = () => {
    const text = `x: ${playerPos.x.toFixed(2)}, y: ${playerPos.y.toFixed(2)}, z: ${playerPos.z.toFixed(2)}`;
    navigator.clipboard?.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getFpsColor = (val: number): string => {
    if (val >= 50) return "text-emerald-400";
    if (val >= 28) return "text-amber-400";
    return "text-rose-400";
  };

  return (
    <div className="absolute bottom-4 right-4 z-20 pointer-events-auto">
      <div className="px-3.5 py-2.5 rounded-2xl bg-slate-950/40 hover:bg-slate-950/70 border border-slate-700/40 hover:border-slate-600/60 backdrop-blur-md shadow-xl text-xs font-mono text-slate-200 transition-all flex flex-col space-y-1.5">
        {/* Top: Mode Badge, FPS & Copy */}
        <div className="flex items-center justify-between space-x-3 text-[11px]">
          <div className="flex items-center space-x-1.5 font-bold">
            {camMode === "GOD_MODE" ? (
              <span className="flex items-center space-x-1 text-purple-300">
                <Eye className="w-3.5 h-3.5 text-purple-400 animate-pulse" />
                <span>GOD MODE [Spectator]</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1 text-emerald-300">
                <Footprints className="w-3.5 h-3.5 text-emerald-400" />
                <span>FIRST-PERSON PoV</span>
              </span>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <span className={`font-bold flex items-center space-x-1 ${getFpsColor(fps)}`}>
              <Gauge className="w-3 h-3" />
              <span>{fps} FPS</span>
            </span>

            <button
              onClick={copyCoordinates}
              className="p-1 rounded-lg bg-slate-900/60 hover:bg-slate-800 border border-slate-700/50 text-slate-300 hover:text-white"
              title="Copy current standing coordinates (X, Y, Z)"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            </button>
          </div>
        </div>

        {/* Real-Time Player Coordinates Display */}
        <div className="flex items-center space-x-2.5 text-[11px] font-bold">
          <span className="text-sky-300">X: {playerPos.x.toFixed(2)}</span>
          <span className="text-emerald-300">Y: {playerPos.y.toFixed(2)}</span>
          <span className="text-indigo-300">Z: {playerPos.z.toFixed(2)}</span>
        </div>

        {/* Quick Keyboard Hotkey Tips */}
        <div className="text-[10px] text-slate-400 border-t border-slate-800/60 pt-1 flex items-center justify-between space-x-2">
          <span>[Tab] Spectator/Walk</span>
          <span>[Hold Alt] Free Cursor</span>
        </div>
      </div>
    </div>
  );
}
