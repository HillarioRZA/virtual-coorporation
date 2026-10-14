/**
 * Device Gatekeeper Component.
 * Restricts rendering of the heavy 3D WebGL simulator strictly to verified Desktop/Laptop devices.
 */

"use client";

import { ReactNode } from "react";
import { useDeviceCapabilities } from "../../hooks/useDeviceCapabilities";
import { UnsupportedDeviceScreen } from "./UnsupportedDeviceScreen";
import { ShieldCheck } from "lucide-react";

interface DeviceGatekeeperProps {
  children: ReactNode;
}

export function DeviceGatekeeper({ children }: DeviceGatekeeperProps) {
  const capabilities = useDeviceCapabilities();

  // 1. Initial hardware handshake state
  if (capabilities.isChecking) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center space-y-3 text-slate-400">
        <ShieldCheck className="w-8 h-8 text-indigo-400 animate-pulse" />
        <p className="text-xs font-mono tracking-wider">Verifying Workstation Hardware...</p>
      </div>
    );
  }

  // 2. Block smartphones, tablets, and emulators
  if (!capabilities.isDesktop) {
    return <UnsupportedDeviceScreen capabilities={capabilities} />;
  }

  // 3. Verified Desktop / Laptop: Allow full 3D WebGL bootstrapping
  return <>{children}</>;
}
