"use client";

import React, { useState, useEffect } from "react";
import { PlusCircle, X, AlertCircle } from "lucide-react";
import { DivisionResponse, RoleResponse } from "@/lib/types/corporate";
import { ProductLine, TicketPriority, TicketResponse } from "@/lib/types/tickets";
import { createTicket } from "@/lib/ticketApi";

interface TicketModalProps {
  isOpen: boolean;
  projectId: string;
  branchId: string;
  divisions: DivisionResponse[];
  roles: RoleResponse[];
  onClose: () => void;
  onSuccess: (ticket: TicketResponse) => void;
}

export default function TicketModal({
  isOpen,
  projectId,
  branchId,
  divisions,
  roles,
  onClose,
  onSuccess,
}: TicketModalProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [divisionId, setDivisionId] = useState("");
  const [assignedRoleId, setAssignedRoleId] = useState("");
  const [priority, setPriority] = useState<TicketPriority>("MEDIUM");
  const [productLine, setProductLine] = useState<ProductLine>("SOFTWARE");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (divisions.length > 0 && !divisionId) {
      setDivisionId(divisions[0].id);
    }
  }, [divisions, divisionId]);

  const filteredRoles = roles.filter((r) => !divisionId || r.division_id === divisionId);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) {
      setError("Judul dan deskripsi tugas wajib diisi.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await createTicket({
        branch_id: branchId,
        project_id: projectId,
        division_id: divisionId || (divisions[0]?.id ?? "div_eng"),
        assigned_role_id: assignedRoleId || undefined,
        title: title.trim(),
        description: description.trim(),
        priority,
        product_line: productLine,
      });
      setTitle("");
      setDescription("");
      onSuccess(res);
      onClose();
    } catch (err: any) {
      setError(err.message || "Gagal membuat tiket.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md overflow-y-auto">
      <div className="w-full max-w-md rounded-2xl bg-[#0c0d14]/95 border border-white/10 shadow-2xl p-6 relative my-8">
        <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-white">
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <PlusCircle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">Buat Tiket Tugas Baru</h3>
            <p className="text-xs text-slate-400">Papan tugas otonom virtual Kanban</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Judul Tugas</label>
            <input
              type="text"
              required
              placeholder="e.g. Implementasi Autentikasi OAuth2"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Instruksi Deskripsi</label>
            <textarea
              rows={3}
              required
              placeholder="Detail apa yang harus dikerjakan oleh agen..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Divisi Pelaksana</label>
              <select
                value={divisionId}
                onChange={(e) => {
                  setDivisionId(e.target.value);
                  setAssignedRoleId("");
                }}
                className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none"
              >
                {divisions.map((d) => (
                  <option key={d.id} value={d.id} className="bg-[#0c0d14]">
                    {d.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Tugaskan ke Role</label>
              <select
                value={assignedRoleId}
                onChange={(e) => setAssignedRoleId(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none"
              >
                <option value="" className="bg-[#0c0d14]">-- Pilih Role --</option>
                {filteredRoles.map((r) => (
                  <option key={r.id} value={r.id} className="bg-[#0c0d14]">
                    {r.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Prioritas</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as TicketPriority)}
                className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none"
              >
                <option value="LOW" className="bg-[#0c0d14]">LOW</option>
                <option value="MEDIUM" className="bg-[#0c0d14]">MEDIUM</option>
                <option value="HIGH" className="bg-[#0c0d14]">HIGH</option>
                <option value="CRITICAL" className="bg-[#0c0d14]">CRITICAL</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Lini Produk</label>
              <select
                value={productLine}
                onChange={(e) => setProductLine(e.target.value as ProductLine)}
                className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-white text-xs focus:outline-none"
              >
                <option value="SOFTWARE" className="bg-[#0c0d14]">SOFTWARE</option>
                <option value="EDUCATION" className="bg-[#0c0d14]">EDUCATION</option>
                <option value="COPYWRITING" className="bg-[#0c0d14]">COPYWRITING</option>
                <option value="RESEARCH" className="bg-[#0c0d14]">RESEARCH</option>
              </select>
            </div>
          </div>

          <div className="pt-2 flex items-center justify-end gap-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-xs text-slate-400 hover:text-white">
              Batal
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-xs font-medium text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-all disabled:opacity-50"
            >
              {loading ? "Membuat..." : "Buat Tiket"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
