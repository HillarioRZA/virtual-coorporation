"use client";

import { Zap, Pause, Eye, CheckCircle2, ArrowRight, ShieldAlert, Cpu } from "lucide-react";
import { OasisStreamEvent } from "../../../lib/types/office";

interface OasisEventCardProps {
  event: OasisStreamEvent;
  onInterrupt: (roleId: string, ticketId?: string) => void;
  onHold: (ticketId: string) => void;
  onWatchScreen: (roleId: string) => void;
  onApproveGate?: (ticketId: string) => void;
}

export function OasisEventCard({
  event,
  onInterrupt,
  onHold,
  onWatchScreen,
  onApproveGate,
}: OasisEventCardProps) {
  const getBadgeColor = (roleId: string) => {
    if (roleId.includes("founder") || roleId.includes("cos") || roleId.includes("cfo")) {
      return "text-amber-400 bg-amber-950/60 border-amber-800/60";
    }
    if (roleId.includes("cto") || roleId.includes("pm")) {
      return "text-purple-400 bg-purple-950/60 border-purple-800/60";
    }
    if (roleId.includes("growth") || roleId.includes("seo")) {
      return "text-emerald-400 bg-emerald-950/60 border-emerald-800/60";
    }
    return "text-cyan-400 bg-cyan-950/60 border-cyan-800/60";
  };

  const roleName = event.senderRoleId.replace("role_", "").toUpperCase();
  const isThinking = event.eventType === "AGENT_THINKING";
  const isDirectiveResponse = event.eventType === "DIRECTIVE_RESPONSE";

  return (
    <div
      className={`rounded-2xl p-3.5 space-y-2.5 transition-all shadow-lg backdrop-blur-md ${
        isThinking
          ? "bg-amber-950/20 border border-amber-500/40 animate-pulse shadow-amber-500/10"
          : isDirectiveResponse
          ? "bg-gradient-to-br from-slate-900/90 to-emerald-950/30 border border-emerald-500/40 shadow-emerald-500/10"
          : "bg-slate-900/60 hover:bg-slate-900/80 border border-slate-800/80 hover:border-slate-700/80"
      }`}
    >
      {/* Top Header: Role Avatar, Project & Time */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className={`px-2 py-0.5 rounded-lg text-[11px] font-mono font-bold border ${getBadgeColor(event.senderRoleId)}`}>
            {roleName}
          </div>
          {isThinking && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping" />
              Thinking...
            </span>
          )}
          {isDirectiveResponse && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
              Response
            </span>
          )}
          {event.projectName && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              {event.projectName}
            </span>
          )}
          {event.ticketId && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800/60 text-slate-400">
              #{event.ticketId}
            </span>
          )}
        </div>
        <span className="text-[10px] text-slate-500 font-mono">{event.timestamp}</span>
      </div>

      {/* Handoff Ribbon if applicable */}
      {event.handoff && (
        <div className="flex items-center space-x-2 px-2.5 py-1.5 rounded-xl bg-indigo-950/40 border border-indigo-800/40 text-[11px] text-indigo-300 font-mono">
          <span className="font-bold text-white uppercase">{event.handoff.fromRoleId.replace("role_", "")}</span>
          <ArrowRight className="w-3 h-3 text-indigo-400" />
          <span className="font-bold text-white uppercase">{event.handoff.toRoleId.replace("role_", "")}</span>
          <span className="text-slate-400 text-[10px] truncate ml-1">• {event.handoff.summary}</span>
        </div>
      )}

      {/* Main Thought / Content */}
      <div className="text-xs text-slate-200 leading-relaxed font-sans">
        {isThinking ? (
          <div className="flex items-center gap-2 text-amber-300 font-medium py-0.5">
            <span>{event.content}</span>
            <div className="flex items-center gap-1 pl-1">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce [animation-delay:-0.3s]"></span>
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce [animation-delay:-0.15s]"></span>
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce"></span>
            </div>
          </div>
        ) : (
          <p className="whitespace-pre-wrap">{event.content}</p>
        )}
      </div>

      {/* Action Toolbar */}
      <div className="pt-1 flex items-center justify-between border-t border-slate-800/50">
        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => onInterrupt(event.senderRoleId, event.ticketId || undefined)}
            className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 text-[10px] font-semibold transition-all active:scale-95"
            title="Sela agen ini dan kirim arahan perbaikan"
          >
            <Zap className="w-3 h-3" />
            <span>Interrupt</span>
          </button>

          {event.ticketId && (
            <button
              onClick={() => onHold(event.ticketId!)}
              className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-300 text-[10px] font-semibold transition-all active:scale-95"
              title="Tahan tiket ini dari pemakaian token lanjutan"
            >
              <Pause className="w-3 h-3" />
              <span>Hold</span>
            </button>
          )}

          {event.gateStatus === "WAITING_APPROVAL" && onApproveGate && (
            <button
              onClick={() => onApproveGate(event.ticketId || "GATE")}
              className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/40 text-emerald-300 text-[10px] font-semibold transition-all active:scale-95"
            >
              <CheckCircle2 className="w-3 h-3" />
              <span>Approve Gate</span>
            </button>
          )}
        </div>

        <button
          onClick={() => onWatchScreen(event.senderRoleId)}
          className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white text-[10px] font-medium transition-all"
          title="Buka Live Screen Share & Sandbox Terminal agen ini"
        >
          <Eye className="w-3 h-3 text-cyan-400" />
          <span>Watch Screen</span>
        </button>
      </div>
    </div>
  );
}
