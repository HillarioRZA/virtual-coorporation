/**
 * Unsupported Device Gatekeeper Screen for Office HQ.
 * Displayed when access is attempted from smartphones, tablets, or mobile emulators.
 */

"use client";

import Link from "next/link";
import { Laptop, ArrowLeft, ShieldAlert, Cpu } from "lucide-react";
import { DeviceCapabilities } from "../../hooks/useDeviceCapabilities";

interface UnsupportedDeviceScreenProps {
  capabilities: DeviceCapabilities;
}

export function UnsupportedDeviceScreen({ capabilities }: UnsupportedDeviceScreenProps) {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 text-slate-100">
      <div className="max-w-md w-full bg-slate-900/90 border border-rose-500/30 rounded-3xl p-8 shadow-2xl backdrop-blur-xl flex flex-col items-center text-center relative overflow-hidden">
        {/* Glow ambient background */}
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

        {/* Icon Header */}
        <div className="w-16 h-16 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center mb-6 text-rose-400">
          <Laptop className="w-8 h-8" />
        </div>

        <h1 className="text-xl font-bold text-white tracking-tight mb-2">
          Desktop Workstation Required
        </h1>
        <p className="text-xs text-slate-400 leading-relaxed mb-6">
          Sovereign 3D Cyber-Voxel Campus dirancang secara khusus untuk komputasi grafis presisi tinggi dengan navigasi keyboard & mouse (WASD) pada resolusi layar minimal 1280x720.
        </p>

        {/* Hardware Diagnostic Card */}
        <div className="w-full bg-slate-950/80 border border-slate-800 rounded-2xl p-4 text-left mb-6 space-y-2 font-mono text-[11px]">
          <div className="flex items-center space-x-2 text-rose-400 font-semibold mb-1">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Access Blocked Handshake</span>
          </div>
          <div className="text-slate-400 truncate">
            <span className="text-slate-500">Reason: </span>
            <span className="text-rose-300 font-medium">{capabilities.reason}</span>
          </div>
          <div className="text-slate-400 truncate flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
            <span className="truncate">{capabilities.gpuRenderer}</span>
          </div>
        </div>

        {/* Action Button */}
        <Link
          href="/"
          className="w-full py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-medium text-xs flex items-center justify-center space-x-2 transition-all active:scale-95 border border-slate-700"
        >
          <ArrowLeft className="w-4 h-4 text-slate-400" />
          <span>Kembali ke Command Center Utama</span>
        </Link>
      </div>
    </div>
  );
}
