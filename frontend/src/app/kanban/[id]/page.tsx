"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  Columns3,
  Sparkles,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  FolderTree,
  GitPullRequest,
} from "lucide-react";
import { PRManagerDrawer } from "@/components/pr/PRManagerDrawer";
import { fetchProject } from "@/lib/api";
import { fetchDivisions, fetchRoles } from "@/lib/corporateApi";
import {
  fetchTickets,
  transitionTicket,
  deleteTicket,
  seedInitialTickets,
  dispatchConcurrentEngineering,
  dispatchKanbanTickets,
} from "@/lib/ticketApi";
import { DivisionResponse, RoleResponse } from "@/lib/types/corporate";
import { TicketResponse, TicketStatus } from "@/lib/types/tickets";
import { VentureStateData } from "@/lib/types/api";
import KanbanBoard from "@/components/kanban/KanbanBoard";
import TicketModal from "@/components/kanban/TicketModal";
import LiveLoungeChat from "@/components/kanban/LiveLoungeChat";

export default function MissionControlKanbanPage() {
  const params = useParams();
  const projectId = params?.id as string;

  const [project, setProject] = useState<VentureStateData | null>(null);
  const [tickets, setTickets] = useState<TicketResponse[]>([]);
  const [divisions, setDivisions] = useState<DivisionResponse[]>([]);
  const [roles, setRoles] = useState<RoleResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isPROpen, setIsPROpen] = useState(false);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const [isDispatching, setIsDispatching] = useState(false);

  const loadData = async () => {
    if (!projectId) return;
    setLoading(true);
    try {
      const [proj, tList, dList, rList] = await Promise.all([
        fetchProject(projectId),
        fetchTickets(projectId),
        fetchDivisions(),
        fetchRoles(),
      ]);
      setProject(proj);
      setTickets(tList);
      setDivisions(dList);
      setRoles(rList);
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message || "Gagal memuat data." });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  const handleTransition = async (ticketId: string, nextStatus: TicketStatus) => {
    try {
      const updated = await transitionTicket(ticketId, nextStatus);
      setTickets((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message });
    }
  };

  const handleDelete = async (ticketId: string) => {
    if (!confirm("Hapus tiket tugas ini?")) return;
    try {
      await deleteTicket(ticketId);
      setTickets((prev) => prev.filter((t) => t.id !== ticketId));
      setFeedback({ type: "success", message: "Tiket berhasil dihapus." });
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message });
    }
  };

  const handleSeed = async () => {
    try {
      const seeded = await seedInitialTickets(projectId);
      setTickets(seeded);
      setFeedback({ type: "success", message: `Berhasil menginisialisasi ${seeded.length} tiket awal!` });
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message });
    }
  };

  const handleDispatchConcurrent = async () => {
    setIsDispatching(true);
    try {
      const data = await dispatchConcurrentEngineering(projectId);
      setFeedback({
        type: "success",
        message: `Sintesis paralel selesai dalam ${data.elapsed_seconds}s!`,
      });
      const updatedTickets = await fetchTickets(projectId);
      setTickets(updatedTickets);
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message || "Gagal memicu dispatch paralel." });
    } finally {
      setIsDispatching(false);
    }
  };

  const handleDispatchAutonomous = async () => {
    setIsDispatching(true);
    try {
      const data = await dispatchKanbanTickets(projectId);
      setFeedback({
        type: "success",
        message: `Autonomous Runner mendispatch ${data.dispatched_count} tiket yang siap dieksekusi!`,
      });
      const updatedTickets = await fetchTickets(projectId);
      setTickets(updatedTickets);
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message || "Gagal memicu Autonomous Runner." });
    } finally {
      setIsDispatching(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-8 py-8 w-full space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Link
              href="/"
              className="p-1 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <span className="p-1 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Columns3 className="w-4 h-4" />
            </span>
            <span className="text-xs font-mono uppercase tracking-wider text-indigo-400">
              Mission Control
            </span>
          </div>

          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white mt-1">
            {project?.project_name || "Venture Kanban"}
          </h1>
          <p className="text-xs md:text-sm text-slate-400 mt-0.5">
            Papan Kanban otonom & live streaming interaksi multi-divisi korporat.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleSeed}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-slate-300 hover:text-white transition-all"
            title="Isi tiket bawaan Tech Core"
          >
            <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
            <span>Seed Default Tickets</span>
          </button>

          <button
            onClick={handleDispatchAutonomous}
            disabled={isDispatching}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/40 text-cyan-300 text-xs font-semibold transition-all disabled:opacity-50"
            title="Memicu Autonomous Runner mengeksekusi tiket TODO yang dependensinya selesai"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isDispatching ? "Runner Berjalan..." : "Jalankan Autonomous Runner"}</span>
          </button>

          <button
            onClick={handleDispatchConcurrent}
            disabled={isDispatching}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/40 text-purple-300 text-xs font-semibold transition-all disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5" />
            <span>{isDispatching ? "Sintesis Paralel..." : "Jalankan Paralel Dispatch"}</span>
          </button>

          <button
            onClick={() => setIsPROpen(true)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-300 text-xs font-medium transition-all"
            title="Lihat Pull Requests & Peer Reviews"
          >
            <GitPullRequest className="w-3.5 h-3.5" />
            <span>Pull Requests</span>
          </button>

          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-all shadow-lg shadow-indigo-600/20"
          >
            <span>+ Buat Tiket</span>
          </button>

          <Link
            href={`/preview/${projectId}`}
            className="px-3.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/15 text-white text-xs font-medium border border-white/20 transition-all"
          >
            Ke Preview
          </Link>
        </div>
      </div>

      {feedback && (
        <div
          className={`p-3.5 rounded-xl border flex items-center justify-between gap-3 text-xs animate-fade-in ${
            feedback.type === "success"
              ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-300"
              : "bg-rose-500/10 border-rose-500/20 text-rose-300"
          }`}
        >
          <div className="flex items-center gap-2">
            {feedback.type === "success" ? (
              <CheckCircle2 className="w-4 h-4 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 shrink-0" />
            )}
            <span>{feedback.message}</span>
          </div>
          <button onClick={() => setFeedback(null)} className="text-slate-400 hover:text-white">
            ✕
          </button>
        </div>
      )}

      {/* Main Grid: Kanban (70%) + Live Lounge (30%) */}
      {loading ? (
        <div className="py-24 text-center space-y-3">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin mx-auto" />
          <p className="text-xs text-slate-400">Memuat Mission Control & Live Lounge...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-8 xl:col-span-9">
            <KanbanBoard
              tickets={tickets}
              onTransition={handleTransition}
              onDelete={handleDelete}
              onOpenCreateModal={() => setIsModalOpen(true)}
            />
          </div>

          <div className="lg:col-span-4 xl:col-span-3">
            <LiveLoungeChat projectId={projectId} />
          </div>
        </div>
      )}

      {/* Create Ticket Modal */}
      <TicketModal
        isOpen={isModalOpen}
        projectId={projectId}
        branchId="branch_main"
        divisions={divisions}
        roles={roles}
        onClose={() => setIsModalOpen(false)}
        onSuccess={(newTicket) => {
          setTickets((prev) => [...prev, newTicket]);
          setFeedback({ type: "success", message: `Tiket '${newTicket.title}' berhasil dibuat!` });
        }}
      />

      {/* Pull Request & Peer Review Drawer */}
      <PRManagerDrawer
        projectId={projectId}
        isOpen={isPROpen}
        onClose={() => setIsPROpen(false)}
      />
    </div>
  );
}
