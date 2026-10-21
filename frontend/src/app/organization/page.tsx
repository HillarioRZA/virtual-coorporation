"use client";

import React, { useEffect, useState } from "react";
import { Building2, AlertCircle, CheckCircle2, Plus } from "lucide-react";
import { BranchResponse, DivisionResponse, RoleResponse } from "@/lib/types/corporate";
import {
  fetchBranches, fetchDivisions, fetchRoles,
  deleteDivision, deleteRole, updateRole,
} from "@/lib/corporateApi";
import DivisionCard from "@/components/organization/DivisionCard";
import DivisionModal from "@/components/organization/DivisionModal";
import RoleModal from "@/components/organization/RoleModal";

export default function OrganizationPage() {
  const [selectedBranchId, setSelectedBranchId] = useState<string>("branch_main");
  const [divisions, setDivisions] = useState<DivisionResponse[]>([]);
  const [roles, setRoles] = useState<RoleResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(null);

  const [divisionModalOpen, setDivisionModalOpen] = useState(false);
  const [editingDivision, setEditingDivision] = useState<DivisionResponse | null>(null);
  const [roleModalOpen, setRoleModalOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<RoleResponse | null>(null);
  const [preselectedDivisionId, setPreselectedDivisionId] = useState<string | null>(null);

  const loadBranches = async () => {
    try {
      const list = await fetchBranches();
      if (list.length > 0) {
        const active = list.find((b) => b.is_active_main) || list[0];
        setSelectedBranchId(active.id);
      }
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message || "Gagal memuat status organisasi." });
    }
  };

  const loadStructure = async (branchId: string) => {
    setLoading(true);
    try {
      const [divs, rls] = await Promise.all([fetchDivisions(branchId), fetchRoles(branchId)]);
      setDivisions(divs);
      setRoles(rls);
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message || "Gagal memuat struktur." });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadBranches(); }, []);
  useEffect(() => { if (selectedBranchId) loadStructure(selectedBranchId); }, [selectedBranchId]);

  const handleDeleteDivision = async (div: DivisionResponse) => {
    if (!confirm(`Hapus divisi '${div.name}'?`)) return;
    try {
      await deleteDivision(div.id);
      setFeedback({ type: "success", message: `Divisi '${div.name}' dihapus.` });
      if (selectedBranchId) loadStructure(selectedBranchId);
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message });
    }
  };

  const handleDeleteRole = async (r: RoleResponse) => {
    if (!confirm(`Hapus peran '${r.name}'?`)) return;
    try {
      await deleteRole(r.id);
      setFeedback({ type: "success", message: `Peran '${r.name}' dihapus.` });
      if (selectedBranchId) loadStructure(selectedBranchId);
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message });
    }
  };

  const handleToggleActiveRole = async (r: RoleResponse) => {
    try {
      await updateRole(r.id, { is_active: !r.is_active });
      if (selectedBranchId) loadStructure(selectedBranchId);
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message });
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-8 py-8 w-full space-y-6">
      <div className="flex items-center space-x-2">
        <span className="p-1 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
          <Building2 className="w-4 h-4" />
        </span>
        <span className="text-xs font-mono uppercase tracking-wider text-indigo-400">Virtual Org Studio</span>
      </div>
      <div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white mt-1">Bagan Organisasi & Dewan Direksi AI</h1>
        <p className="text-xs md:text-sm text-slate-400 mt-0.5">
          Kelola divisi, karyawan AI, 3-layer prompt (Soul Persona & SOP), dan konfigurasi model LLM secara terpadu.
        </p>
      </div>

      {feedback && (
        <div className={`p-3.5 rounded-xl border flex items-center justify-between gap-3 text-xs ${feedback.type === "success" ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-300" : "bg-rose-500/10 border-rose-500/20 text-rose-300"}`}>
          <div className="flex items-center gap-2">
            {feedback.type === "success" ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
            <span>{feedback.message}</span>
          </div>
          <button onClick={() => setFeedback(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Action Header */}
      <div className="flex items-center justify-between p-4 rounded-2xl bg-white/[0.02] border border-white/10">
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono text-slate-400">Alur Organisasi Utama:</span>
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            {selectedBranchId}
          </span>
        </div>
        <button
          onClick={() => { setEditingDivision(null); setDivisionModalOpen(true); }}
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition shadow-lg shadow-indigo-500/20"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Tambah Divisi</span>
        </button>
      </div>

      {loading ? (
        <div className="py-20 text-center space-y-3">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin mx-auto" />
          <p className="text-xs text-slate-400">Memuat hierarki divisi & karyawan AI...</p>
        </div>
      ) : divisions.length === 0 ? (
        <div className="py-20 text-center border border-dashed border-white/10 rounded-2xl bg-white/[0.01]">
          <p className="text-sm text-slate-400 mb-3">Belum ada divisi pada struktur organisasi ini.</p>
          <button
            onClick={() => { setEditingDivision(null); setDivisionModalOpen(true); }}
            className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-white text-xs font-medium border border-white/15 transition"
          >
            + Buat Divisi Pertama
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {divisions.map((div) => (
            <DivisionCard
              key={div.id}
              division={div}
              roles={roles.filter((r) => r.division_id === div.id)}
              isMainBranch={true}
              onEditDivision={(d) => { setEditingDivision(d); setDivisionModalOpen(true); }}
              onDeleteDivision={handleDeleteDivision}
              onAddRole={(divId) => { setPreselectedDivisionId(divId); setEditingRole(null); setRoleModalOpen(true); }}
              onEditRole={(r) => { setEditingRole(r); setPreselectedDivisionId(r.division_id); setRoleModalOpen(true); }}
              onDeleteRole={handleDeleteRole}
              onToggleActiveRole={handleToggleActiveRole}
            />
          ))}
        </div>
      )}

      <DivisionModal
        isOpen={divisionModalOpen}
        branchId={selectedBranchId}
        initialData={editingDivision}
        onClose={() => setDivisionModalOpen(false)}
        onSuccess={() => { setFeedback({ type: "success", message: "Divisi disimpan!" }); if (selectedBranchId) loadStructure(selectedBranchId); }}
      />
      <RoleModal
        isOpen={roleModalOpen}
        branchId={selectedBranchId}
        divisions={divisions}
        initialData={editingRole}
        preselectedDivisionId={preselectedDivisionId}
        onClose={() => setRoleModalOpen(false)}
        onSuccess={() => { setFeedback({ type: "success", message: "Karyawan AI disimpan!" }); if (selectedBranchId) loadStructure(selectedBranchId); }}
      />
    </div>
  );
}
