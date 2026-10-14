"use client";

import React from "react";
import {
  Laptop,
  Tablet,
  Smartphone,
  Terminal,
  History,
  Network,
  RefreshCw,
} from "lucide-react";
import { InteractiveTerminal } from "../sandbox/InteractiveTerminal";
import { SnapshotManagerView } from "../sandbox/SnapshotManagerModal";
import { NetworkQuotaInspector } from "../sandbox/NetworkQuotaInspector";

export type ViewportMode = "desktop" | "tablet" | "mobile";
export type PreviewMode = "webview" | "terminal" | "snapshots" | "network";

interface PreviewWebviewPaneProps {
  projectId: string;
  previewUrl: string;
  previewMode: PreviewMode;
  setPreviewMode: (mode: PreviewMode) => void;
  viewportMode: ViewportMode;
  setViewportMode: (mode: ViewportMode) => void;
  iframeKey: number;
  onReload: () => void;
  onRollbackComplete: () => void;
}

/**
 * Renders the left pane containing multi-view interactive sandboxes:
 * Webview with device viewport emulation, Terminal CLI, Snapshots, and Network inspector.
 */
export const PreviewWebviewPane: React.FC<PreviewWebviewPaneProps> = ({
  projectId,
  previewUrl,
  previewMode,
  setPreviewMode,
  viewportMode,
  setViewportMode,
  iframeKey,
  onReload,
  onRollbackComplete,
}) => {
  const getViewportWidthClass = (): string => {
    switch (viewportMode) {
      case "mobile":
        return "max-w-[375px]";
      case "tablet":
        return "max-w-[768px]";
      default:
        return "w-full";
    }
  };

  return (
    <div className="flex-1 lg:w-[65%] flex flex-col bg-slate-900/60 p-4 border-r border-slate-800 overflow-hidden">
      {/* Top Multi-View Switcher Bar */}
      <div className="bg-slate-950 p-2 rounded-t-2xl border border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 pl-1">
            <span className="w-3 h-3 rounded-full bg-rose-500/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
          </div>

          {/* View Mode Switcher Pills */}
          <div className="flex items-center space-x-1 bg-slate-900 p-0.5 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => setPreviewMode("webview")}
              className={`px-3 py-1 rounded-lg font-medium transition-colors flex items-center gap-1.5 ${
                previewMode === "webview" ? "bg-indigo-600 text-white font-bold" : "text-slate-400 hover:text-white"
              }`}
            >
              <span>⚡ Webview</span>
            </button>
            <button
              onClick={() => setPreviewMode("terminal")}
              className={`px-3 py-1 rounded-lg font-medium transition-colors flex items-center gap-1.5 ${
                previewMode === "terminal" ? "bg-emerald-600 text-white font-bold" : "text-slate-400 hover:text-white"
              }`}
            >
              <Terminal className="w-3.5 h-3.5 text-emerald-300" />
              <span>Terminal CLI</span>
            </button>
            <button
              onClick={() => setPreviewMode("snapshots")}
              className={`px-3 py-1 rounded-lg font-medium transition-colors flex items-center gap-1.5 ${
                previewMode === "snapshots" ? "bg-purple-600 text-white font-bold" : "text-slate-400 hover:text-white"
              }`}
            >
              <History className="w-3.5 h-3.5 text-purple-300" />
              <span>Snapshots</span>
            </button>
            <button
              onClick={() => setPreviewMode("network")}
              className={`px-3 py-1 rounded-lg font-medium transition-colors flex items-center gap-1.5 ${
                previewMode === "network" ? "bg-cyan-600 text-white font-bold" : "text-slate-400 hover:text-white"
              }`}
            >
              <Network className="w-3.5 h-3.5 text-cyan-300" />
              <span>Network & Quota</span>
            </button>
          </div>
        </div>

        {/* Address Bar & Viewport Switcher */}
        {previewMode === "webview" && (
          <div className="flex items-center gap-2">
            <div className="hidden sm:flex max-w-xs px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 items-center justify-between gap-2">
              <span className="truncate max-w-[180px]">{previewUrl || "http://localhost:4000"}</span>
              <button
                onClick={onReload}
                title="Reload Sandbox"
                className="text-slate-400 hover:text-white p-0.5"
              >
                <RefreshCw className="w-3 h-3" />
              </button>
            </div>

            <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
              <button
                onClick={() => setViewportMode("desktop")}
                className={`p-1 rounded ${viewportMode === "desktop" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"}`}
                title="Desktop View"
              >
                <Laptop className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setViewportMode("tablet")}
                className={`p-1 rounded ${viewportMode === "tablet" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"}`}
                title="Tablet View"
              >
                <Tablet className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setViewportMode("mobile")}
                className={`p-1 rounded ${viewportMode === "mobile" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"}`}
                title="Mobile View"
              >
                <Smartphone className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* View Canvas Body */}
      {previewMode === "webview" && (
        <div className="flex-1 bg-slate-950/90 border-x border-b border-slate-800 rounded-b-2xl overflow-hidden flex items-center justify-center p-2">
          <div className={`h-full transition-all duration-300 shadow-2xl rounded-xl overflow-hidden ${getViewportWidthClass()}`}>
            <iframe
              key={iframeKey}
              src={previewUrl || "about:blank"}
              title="Sandbox Preview"
              className="w-full h-full border-0 bg-white"
              sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
            />
          </div>
        </div>
      )}

      {previewMode === "terminal" && (
        <div className="flex-1 mt-2 flex flex-col overflow-hidden">
          <InteractiveTerminal projectId={projectId} />
        </div>
      )}

      {previewMode === "snapshots" && (
        <div className="flex-1 mt-2 flex flex-col overflow-hidden">
          <SnapshotManagerView
            projectId={projectId}
            onRollbackComplete={onRollbackComplete}
          />
        </div>
      )}

      {previewMode === "network" && (
        <div className="flex-1 mt-2 flex flex-col overflow-hidden">
          <NetworkQuotaInspector projectId={projectId} />
        </div>
      )}
    </div>
  );
};
