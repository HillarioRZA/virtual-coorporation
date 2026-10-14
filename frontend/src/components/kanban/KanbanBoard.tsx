"use client";

import React from "react";
import { Plus, CheckCircle2, Clock, PlayCircle, Eye, Inbox } from "lucide-react";
import { TicketResponse, TicketStatus } from "@/lib/types/tickets";
import KanbanCard from "./KanbanCard";

interface KanbanBoardProps {
  tickets: TicketResponse[];
  onTransition: (ticketId: string, nextStatus: TicketStatus) => void;
  onDelete: (ticketId: string) => void;
  onOpenCreateModal: () => void;
}

interface ColumnConfig {
  id: TicketStatus;
  title: string;
  icon: React.ReactNode;
  accent: string;
}

const COLUMNS: ColumnConfig[] = [
  { id: "BACKLOG", title: "Backlog", icon: <Inbox className="w-3.5 h-3.5" />, accent: "text-slate-400" },
  { id: "TODO", title: "To Do", icon: <Clock className="w-3.5 h-3.5" />, accent: "text-blue-400" },
  { id: "IN_PROGRESS", title: "In Progress", icon: <PlayCircle className="w-3.5 h-3.5" />, accent: "text-amber-400" },
  { id: "REVIEW", title: "Review", icon: <Eye className="w-3.5 h-3.5" />, accent: "text-purple-400" },
  { id: "DONE", title: "Done", icon: <CheckCircle2 className="w-3.5 h-3.5" />, accent: "text-emerald-400" },
];

export default function KanbanBoard({
  tickets,
  onTransition,
  onDelete,
  onOpenCreateModal,
}: KanbanBoardProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-5 gap-3.5 items-start">
      {COLUMNS.map((col) => {
        const colTickets = tickets.filter((t) => t.status === col.id);

        return (
          <div
            key={col.id}
            className="rounded-2xl bg-white/[0.02] border border-white/10 p-3.5 flex flex-col min-h-[500px] shadow-lg backdrop-blur-md"
          >
            {/* Header Kolom */}
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/5">
              <div className="flex items-center space-x-2">
                <span className={col.accent}>{col.icon}</span>
                <h4 className="text-xs font-bold text-white tracking-tight">{col.title}</h4>
                <span className="text-[10px] font-mono font-semibold px-2 py-0.2 rounded-full bg-white/5 text-slate-300 border border-white/10">
                  {colTickets.length}
                </span>
              </div>

              {col.id === "BACKLOG" && (
                <button
                  onClick={onOpenCreateModal}
                  className="p-1 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                  title="Tambah Tiket"
                >
                  <Plus className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* List Kartu */}
            <div className="flex-1 space-y-2.5 overflow-y-auto max-h-[550px] pr-1">
              {colTickets.length === 0 ? (
                <div className="py-12 text-center border border-dashed border-white/5 rounded-xl">
                  <p className="text-[11px] text-slate-600">Kosong</p>
                </div>
              ) : (
                colTickets.map((ticket) => (
                  <KanbanCard
                    key={ticket.id}
                    ticket={ticket}
                    onTransition={onTransition}
                    onDelete={onDelete}
                  />
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
