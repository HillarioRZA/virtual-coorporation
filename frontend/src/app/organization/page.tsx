"use client";

import React, { useEffect, useState, useRef } from "react";
import { Building2, AlertCircle, CheckCircle2 } from "lucide-react";
import { BranchResponse, DivisionResponse, RoleResponse } from "@/lib/types/corporate";
import {
  fetchBranches, fetchDivisions, fetchRoles,
  activateBranch, deleteBranch, deleteDivision, deleteRole, updateRole,
} from "@/lib/corporateApi";
import BranchBar from "@/components/organization/BranchBar";
import DivisionCard from "@/components/organization/DivisionCard";
import BranchForkModal from "@/components/organization/BranchForkModal";
import BranchMergeModal from "@/components/organization/BranchMergeModal";
import DivisionModal from "@/components/organization/DivisionModal";
import RoleModal from "@/components/organization/RoleModal";
import WorkflowPipelineBuilder, { WorkflowPipelineBuilderHandle } from "@/components/organization/WorkflowPipelineBuilder";

export default function OrganizationPage() {
  const pipelineBuilderRef = useRef<WorkflowPipelineBuilderHandle>(null);
  const [branches, setBranches] = useState<BranchResponse[]>([]);
  const [selectedBranchId, setSelectedBranchId] = useState<string>("");
  const [divisions, setDivisions] = useState<DivisionResponse[]>([]);
  const [roles, setRoles] = useState<RoleResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(null);

  const [forkModalOpen, setForkModalOpen] = useState(false);
  const [mergeModalOpen, setMergeModalOpen] = useState(false);
  const [divisionModalOpen, setDivisionModalOpen] = useState(false);
  const [editingDivision, setEditingDivision] = useState<DivisionResponse | null>(null);
  const [roleModalOpen, setRoleModalOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<RoleResponse | null>(null);
  const [preselectedDivisionId, setPreselectedDivisionId] = useState<string | null>(null);

  const selectedBranch = branches.find((b) => b.id === selectedBranchId) || branches[0] || null;

  const loadBranches = async () => {
    try {
      const list = await fetchBranches();
      setBranches(list);
      if (!selectedBranchId && list.length > 0) {
        setSelectedBranchId((list.find((b) => b.is_active_main) || list[0]).id);
      }
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message || "Gagal memuat branches." });
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

  const handleActivateBranch = async (id: string) => {
    try { await activateBranch(id); setFeedback({ type: "success", message: "Branch dipromosikan sebagai alur utama!" }); await loadBranches(); }
    catch (err: any) { setFeedback({ type: "error", message: err.message }); }
  };
  const handleDeleteBranch = async (id: string) => {
    if (!confirm("Hapus branch ini?")) return;
    try { await deleteBranch(id); setFeedback({ type: "success", message: "Branch dihapus." }); setSelectedBranchId("branch_main"); await loadBranches(); }
    catch (err: any) { setFeedback({ type: "error", message: err.message }); }
  };
  const handleDeleteDivision = async (div: DivisionResponse) => {
    if (!confirm(`Hapus divisi '${div.name}'?`)) return;
    try { await deleteDivision(div.id); setFeedback({ type: "success", message: `Divisi '${div.name}' dihapus.` }); if (selectedBranchId) loadStructure(selectedBranchId); }
    catch (err: any) { setFeedback({ type: "error", message: err.message }); }
  };
  const handleDeleteRole = async (r: RoleResponse) => {
    if (!confirm(`Hapus peran '${r.name}'?`)) return;
    try { await deleteRole(r.id); setFeedback({ type: "success", message: `Peran '${r.name}' dihapus.` }); if (selectedBranchId) loadStructure(selectedBranchId); }
    catch (err: any) { setFeedback({ type: "error", message: err.message }); }
  };
  const handleToggleActiveRole = async (r: RoleResponse) => {
    try { await updateRole(r.id, { is_active: !r.is_active }); if (selectedBranchId) loadStructure(selectedBranchId); }
    catch (err: any) { setFeedback({ type: "error", message: err.message }); }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-8 py-8 w-full space-y-6">
      <div className="flex items-center space-x-2">
        <span className="p-1 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"><Building2 className="w-4 h-4" /></span>
        <span className="text-xs font-mono uppercase tracking-wider text-indigo-400">Virtual Org Studio</span>
      </div>
      <div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white mt-1">Bagan Organisasi & Alur Kerja Korporat</h1>
        <p className="text-xs md:text-sm text-slate-400 mt-0.5">Kelola divisi, karyawan AI, dan alur kerja Git-style secara dinamis tanpa hardcode backend.</p>
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

      <BranchBar
        branches={branches}
        selectedBranch={selectedBranch}
        onSelectBranch={setSelectedBranchId}
        onOpenForkModal={() => setForkModalOpen(true)}
        onOpenMergeModal={() => setMergeModalOpen(true)}
        onOpenDivisionModal={() => { setEditingDivision(null); setDivisionModalOpen(true); }}
        onActivateBranch={handleActivateBranch}
        onDeleteBranch={handleDeleteBranch}
      />

      <WorkflowPipelineBuilder
        ref={pipelineBuilderRef}
        selectedBranch={selectedBranch}
        onOpenForkModal={() => setForkModalOpen(true)}
        onPipelineChanged={() => { if (selectedBranchId) loadStructure(selectedBranchId); }}
      />

      {loading ? (
        <div className="py-20 text-center space-y-3">
          <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin mx-auto" />
          <p className="text-xs text-slate-400">Memuat hierarki divisi & karyawan AI...</p>
        </div>
      ) : divisions.length === 0 ? (
        <div className="py-20 text-center border border-dashed border-white/10 rounded-2xl bg-white/[0.01]">
          <p className="text-sm text-slate-400 mb-3">Belum ada divisi pada branch alur kerja ini.</p>
          <button onClick={() => { setEditingDivision(null); setDivisionModalOpen(true); }} className="px-4 py-2 rounded-xl bg-white/10 text-white text-xs font-medium border border-white/15">
            + Buat Divisi Pertama
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {divisions.map((div) => (
            <DivisionCard
              key={div.id} division={div} roles={roles.filter((r) => r.division_id === div.id)}
              isMainBranch={selectedBranch?.slug === "main"}
              onEditDivision={(d) => { setEditingDivision(d); setDivisionModalOpen(true); }}
              onDeleteDivision={handleDeleteDivision}
              onAddRole={(divId) => { setPreselectedDivisionId(divId); setEditingRole(null); setRoleModalOpen(true); }}
              onEditRole={(r) => { setEditingRole(r); setPreselectedDivisionId(r.division_id); setRoleModalOpen(true); }}
              onDeleteRole={handleDeleteRole} onToggleActiveRole={handleToggleActiveRole}
              onAddToPipeline={(r, n, c) => pipelineBuilderRef.current?.addRoleToPipeline(r, n, c)}
            />
          ))}
        </div>
      )}

      <BranchForkModal
        isOpen={forkModalOpen}
        sourceBranch={selectedBranch}
        onClose={() => setForkModalOpen(false)}
        onSuccess={async (b) => {
          setFeedback({ type: "success", message: `Workflow di-fork ke '${b.name}'!` });
          await loadBranches();
          setSelectedBranchId(b.id);
        }}
      />
      <BranchMergeModal
        isOpen={mergeModalOpen}
        sourceBranch={selectedBranch}
        onClose={() => setMergeModalOpen(false)}
        onMerged={async () => {
          setFeedback({ type: "success", message: `Branch '${selectedBranch?.name}' di-merge ke Main!` });
          await loadBranches();
          if (selectedBranchId) loadStructure(selectedBranchId);
        }}
      />
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
