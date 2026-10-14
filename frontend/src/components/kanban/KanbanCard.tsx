"use client";

import React from "react";
import { ArrowLeft, ArrowRight, Trash2, FileCheck, Layers, AlertCircle } from "lucide-react";
import { TicketPriority, TicketResponse, TicketStatus } from "@/lib/types/tickets";

interface KanbanCardProps {
  ticket: TicketResponse;
  onTransition: (ticketId: string, nextStatus: TicketStatus) => void;
  onDelete: (ticketId: string) => void;
}

const STATUS_ORDER: TicketStatus[] = ["BACKLOG", "TODO", "IN_PROGRESS", "REVIEW", "DONE"];

const PRIORITY_STYLES: Record<TicketPriority, string> = {
  CRITICAL: "bg-rose-500/15 border-rose-500/30 text-rose-300",
  HIGH: "bg-amber-500/15 border-amber-500/30 text-amber-300",
  MEDIUM: "bg-blue-500/15 border-blue-500/30 text-blue-300",
  LOW: "bg-slate-500/15 border-slate-500/30 text-slate-400",
};

export default function KanbanCard({ ticket, onTransition, onDelete }: KanbanCardProps) {
  const currentIndex = STATUS_ORDER.indexOf(ticket.status);
  const prevStatus = currentIndex > 0 ? STATUS_ORDER[currentIndex - 1] : null;
  const nextStatus = currentIndex < STATUS_ORDER.length - 1 ? STATUS_ORDER[currentIndex + 1] : null;

  return (
    <div className="rounded-xl bg-white/[0.04] hover:bg-white/[0.06] border border-white/10 p-3.5 transition-all shadow-md flex flex-col justify-between space-y-3">
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-1.5">
          <span
            className={`text-[9px] font-mono font-semibold px-2 py-0.5 rounded-full border ${
              PRIORITY_STYLES[ticket.priority] || PRIORITY_STYLES.MEDIUM
            }`}
          >
            {ticket.priority}
          </span>
          <span className="text-[10px] font-mono text-slate-400 px-1.5 py-0.5 rounded bg-white/5 border border-white/5">
            {ticket.product_line}
          </span>
        </div>

        <div>
          <h5 className="text-xs font-semibold text-white tracking-tight leading-snug">
            {ticket.title}
          </h5>
          <p className="text-[11px] text-slate-400 line-clamp-2 mt-1 leading-relaxed">
            {ticket.description}
          </p>
        </div>

        {ticket.assigned_role_id && (
          <div className="flex items-center space-x-1.5 text-[10px] font-mono text-cyan-300 pt-1">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            <span>Assigned: {ticket.assigned_role_id}</span>
          </div>
        )}

        {ticket.artifact_refs?.length > 0 && (
          <div className="pt-1.5 border-t border-white/5 space-y-1">
            {ticket.artifact_refs.map((ref, idx) => (
              <div key={idx} className="flex items-center gap-1 text-[9px] font-mono text-emerald-400 truncate">
                <FileCheck className="w-2.5 h-2.5 shrink-0" />
                <span className="truncate">{ref}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="pt-2 border-t border-white/5 flex items-center justify-between gap-1 text-slate-400">
        <div className="flex items-center gap-1">
          {prevStatus && (
            <button
              onClick={() => onTransition(ticket.id, prevStatus)}
              className="p-1 rounded hover:bg-white/10 hover:text-white transition-colors"
              title={`Pindahkan ke ${prevStatus}`}
            >
              <ArrowLeft className="w-3 h-3" />
            </button>
          )}
          {nextStatus && (
            <button
              onClick={() => onTransition(ticket.id, nextStatus)}
              className="p-1 rounded hover:bg-white/10 hover:text-white transition-colors"
              title={`Pindahkan ke ${nextStatus}`}
            >
              <ArrowRight className="w-3 h-3" />
            </button>
          )}
        </div>

        <button
          onClick={() => onDelete(ticket.id)}
          className="p-1 rounded hover:bg-rose-500/10 hover:text-rose-400 transition-colors"
          title="Hapus tiket"
        >
          <Trash2 className="w-3 h-3" />
        </button>
      </div>
    </div>
  );
}
