/**
 * Device Capability & Anti-Spoofing Hardware Fingerprinting Hook.
 * Unmasks WebGL GPU, inspects pointer/touch capabilities to restrict Office HQ to Desktop/Laptop.
 */

import { useEffect, useState } from "react";

export interface DeviceCapabilities {
  isDesktop: boolean;
  gpuRenderer: string;
  isTouchDevice: boolean;
  hasFinePointer: boolean;
  reason?: string;
  isChecking: boolean;
}

export function useDeviceCapabilities(): DeviceCapabilities {
  const [capabilities, setCapabilities] = useState<DeviceCapabilities>({
    isDesktop: true,
    gpuRenderer: "Detecting...",
    isTouchDevice: false,
    hasFinePointer: true,
    isChecking: true,
  });

  useEffect(() => {
    if (typeof window === "undefined") return;

    let gpuString = "Generic GPU";
    try {
      const canvas = document.createElement("canvas");
      const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
      if (gl) {
        const debugInfo = (gl as WebGLRenderingContext).getExtension("WEBGL_debug_renderer_info");
        if (debugInfo) {
          gpuString = (gl as WebGLRenderingContext).getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) || "Unknown WebGL";
        }
      }
    } catch {
      gpuString = "Hardware query blocked";
    }

    const hasFinePointer = window.matchMedia("(pointer: fine)").matches;
    const hasHover = window.matchMedia("(hover: hover)").matches;
    const maxTouchPoints = navigator.maxTouchPoints || 0;
    const screenWidth = window.screen.width;
    const isTouchOnly = !hasFinePointer && maxTouchPoints > 1;

    // Mobile GPU detection blacklist
    const mobileGpuKeywords = ["adreno", "mali", "powervr", "apple gpu", "immortalis", "videocore"];
    const isMobileGpu = mobileGpuKeywords.some((kw) => gpuString.toLowerCase().includes(kw));

    // Mobile UA fallback check
    const ua = navigator.userAgent.toLowerCase();
    const isMobileUa = /android|iphone|ipad|ipod|windows phone|mobile/i.test(ua);

    let isDesktop = true;
    let reason = "Workstation verified";

    if (isMobileGpu) {
      isDesktop = false;
      reason = `Mobile chipset detected (${gpuString})`;
    } else if (isTouchOnly) {
      isDesktop = false;
      reason = "Touchscreen mobile interface without precision pointer";
    } else if (screenWidth < 1024 && maxTouchPoints > 1) {
      isDesktop = false;
      reason = `Display width (${screenWidth}px) insufficient for Oasis Live Command HQ workstation`;
    } else if (isMobileUa && maxTouchPoints > 0) {
      isDesktop = false;
      reason = "Mobile platform detected via hardware handshake";
    }

    setCapabilities({
      isDesktop,
      gpuRenderer: gpuString,
      isTouchDevice: maxTouchPoints > 0,
      hasFinePointer,
      reason,
      isChecking: false,
    });
  }, []);

  return capabilities;
}
