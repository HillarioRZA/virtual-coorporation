"use client";

import React from "react";

interface DiffViewerProps {
  diffText: string;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ diffText }) => {
  if (!diffText || !diffText.trim()) {
    return (
      <div className="py-8 text-center text-xs text-zinc-500 font-mono">
        Tidak ada perbedaan berkas terdeteksi (Clean diff).
      </div>
    );
  }

  const lines = diffText.split("\n");

  return (
    <div className="overflow-x-auto rounded-xl bg-zinc-950 border border-zinc-800/80 font-mono text-xs">
      <div className="p-2 border-b border-zinc-800 bg-zinc-900/40 text-[11px] text-zinc-400 flex items-center justify-between">
        <span>Git Unified Diff View</span>
        <span className="text-[10px] text-zinc-500">{lines.length} lines</span>
      </div>
      <pre className="p-3 leading-relaxed">
        {lines.map((line, idx) => {
          let lineClass = "text-zinc-300";
          let bgClass = "transparent";

          if (line.startsWith("+++") || line.startsWith("---")) {
            lineClass = "text-zinc-400 font-semibold";
            bgClass = "rgba(255, 255, 255, 0.03)";
          } else if (line.startsWith("@@")) {
            lineClass = "text-cyan-400 font-semibold";
            bgClass = "rgba(6, 182, 212, 0.08)";
          } else if (line.startsWith("+")) {
            lineClass = "text-emerald-300";
            bgClass = "rgba(16, 185, 129, 0.12)";
          } else if (line.startsWith("-")) {
            lineClass = "text-rose-300";
            bgClass = "rgba(244, 63, 94, 0.12)";
          }

          return (
            <div
              key={idx}
              className="px-2 py-0.5 rounded transition-colors"
              style={{ backgroundColor: bgClass }}
            >
              <span className="inline-block w-8 text-right select-none text-zinc-600 mr-3 text-[10px]">
                {idx + 1}
              </span>
              <span className={lineClass}>{line}</span>
            </div>
          );
        })}
      </pre>
    </div>
  );
};
