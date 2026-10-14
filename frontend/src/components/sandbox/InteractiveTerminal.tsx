"use client";

import { useEffect, useRef, useState } from "react";
import { Terminal, Play, Trash2, RefreshCw, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { useTerminalWebSocket } from "../../hooks/useTerminalWebSocket";

interface InteractiveTerminalProps {
  projectId: string;
}

export function InteractiveTerminal({ projectId }: InteractiveTerminalProps) {
  const { status, lines, sendCommand, clearOutput, reconnect } = useTerminalWebSocket(projectId);
  const [inputCmd, setInputCmd] = useState("");
  const [history, setHistory] = useState<string[]>([]);
  const [historyIdx, setHistoryIdx] = useState<number>(-1);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [lines]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputCmd.trim()) return;
    sendCommand(inputCmd);
    setHistory((prev) => [inputCmd, ...prev]);
    setHistoryIdx(-1);
    setInputCmd("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowUp") {
      e.preventDefault();
      if (historyIdx + 1 < history.length) {
        const nextIdx = historyIdx + 1;
        setHistoryIdx(nextIdx);
        setInputCmd(history[nextIdx]);
      }
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (historyIdx - 1 >= 0) {
        const nextIdx = historyIdx - 1;
        setHistoryIdx(nextIdx);
        setInputCmd(history[nextIdx]);
      } else {
        setHistoryIdx(-1);
        setInputCmd("");
      }
    }
  };

  const presets = [
    { label: "dir / ls", cmd: process.platform === "win32" ? "dir" : "ls -la" },
    { label: "python -m pytest", cmd: "pytest backend/tests/test_sandbox_snapshots_and_terminal.py -v" },
    { label: "git status", cmd: "git status" },
    { label: "node & python -v", cmd: "node -v && python --version" },
  ];

  return (
    <div className="flex-1 flex flex-col bg-slate-950 rounded-2xl border border-slate-800 overflow-hidden shadow-2xl font-mono text-xs">
      {/* Terminal Top Bar */}
      <div className="bg-slate-900/90 px-4 py-2.5 border-b border-slate-800 flex items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <span className="font-bold text-white text-xs">Interactive PTY Terminal</span>
          <span className="text-[10px] text-slate-400 hidden sm:inline">projects_output/{projectId}</span>
        </div>

        <div className="flex items-center space-x-2">
          {status === "connected" && (
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px]">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              ONLINE
            </span>
          )}
          {status === "running" && (
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-[10px]">
              <Loader2 className="w-3 h-3 animate-spin" />
              RUNNING
            </span>
          )}
          {status === "disconnected" && (
            <button
              onClick={reconnect}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-[10px] hover:bg-rose-500/20"
            >
              <RefreshCw className="w-2.5 h-2.5" /> RECONNECT
            </button>
          )}
          <button
            onClick={clearOutput}
            title="Bersihkan Terminal"
            className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Quick Action Preset Pills */}
      <div className="bg-slate-950/80 px-4 py-1.5 border-b border-slate-800/80 flex items-center gap-2 overflow-x-auto text-[11px]">
        <span className="text-slate-500 uppercase text-[9px] font-semibold tracking-wider">Presets:</span>
        {presets.map((p, i) => (
          <button
            key={i}
            onClick={() => sendCommand(p.cmd)}
            disabled={status !== "connected"}
            className="px-2.5 py-0.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 transition-colors whitespace-nowrap active:scale-95 disabled:opacity-50"
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Output Console Log Area */}
      <div
        ref={scrollRef}
        className="flex-1 p-4 overflow-y-auto space-y-1.5 bg-[#05070c] text-slate-200 select-text leading-relaxed"
      >
        {lines.length === 0 && (
          <div className="text-slate-500 italic py-6 text-center">
            Terminal siap. Ketik perintah di bawah atau pilih preset aksi cepat di atas.
          </div>
        )}
        {lines.map((l) => (
          <div key={l.id} className="whitespace-pre-wrap break-words">
            {l.type === "prompt" && (
              <span className="text-cyan-400 font-bold">{l.text}</span>
            )}
            {l.type === "system" && (
              <span className="text-emerald-400 font-semibold">{l.text}</span>
            )}
            {l.type === "stdout" && (
              <span className="text-slate-200">{l.text}</span>
            )}
            {l.type === "stderr" && (
              <span className="text-rose-400">{l.text}</span>
            )}
          </div>
        ))}
      </div>

      {/* Bottom Command Input Bar */}
      <form onSubmit={handleSubmit} className="bg-slate-900 p-2.5 border-t border-slate-800 flex items-center gap-2">
        <span className="text-emerald-400 font-bold pl-2 select-none">&gt;</span>
        <input
          type="text"
          value={inputCmd}
          onChange={(e) => setInputCmd(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ketik perintah shell (cth: dir, git status, pytest)..."
          disabled={status !== "connected" && status !== "running"}
          className="flex-1 bg-transparent text-white placeholder-slate-500 focus:outline-none text-xs font-mono"
        />
        <button
          type="submit"
          disabled={!inputCmd.trim() || status !== "connected"}
          className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-500/20 disabled:opacity-40 transition-all active:scale-95 flex items-center gap-1"
        >
          <Play className="w-3 h-3 fill-current" />
          <span>Run</span>
        </button>
      </form>
    </div>
  );
}
