"use client";

import React from "react";
import { FolderTree, Plus, Edit2, Trash2, ShieldCheck, Users } from "lucide-react";
import { DivisionResponse, RoleResponse } from "@/lib/types/corporate";
import RoleCard from "./RoleCard";

interface DivisionCardProps {
  division: DivisionResponse;
  roles: RoleResponse[];
  isMainBranch: boolean;
  onEditDivision: (div: DivisionResponse) => void;
  onDeleteDivision: (div: DivisionResponse) => void;
  onAddRole: (divisionId: string) => void;
  onEditRole: (role: RoleResponse) => void;
  onDeleteRole: (role: RoleResponse) => void;
  onToggleActiveRole: (role: RoleResponse) => void;
  onAddToPipeline?: (role: RoleResponse, divName?: string, divColor?: string) => void;
}

export default function DivisionCard({
  division,
  roles,
  isMainBranch,
  onEditDivision,
  onDeleteDivision,
  onAddRole,
  onEditRole,
  onDeleteRole,
  onToggleActiveRole,
  onAddToPipeline,
}: DivisionCardProps) {
  const isProtected = isMainBranch && division.is_system_default;
  const accent = division.accent_color || "#3b82f6";

  return (
    <div
      className="rounded-2xl bg-white/[0.02] border p-5 transition-all shadow-xl"
      style={{ borderColor: `${accent}30` }}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-4 border-b border-white/5">
        <div className="flex items-center space-x-3">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center border"
            style={{ backgroundColor: `${accent}15`, borderColor: `${accent}40`, color: accent }}
          >
            <FolderTree className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-bold text-white tracking-tight">{division.name}</h4>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-slate-400 border border-white/10">
                {division.slug}
              </span>
              {isProtected && (
                <span className="inline-flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-300">
                  <ShieldCheck className="w-3 h-3" />
                  Tech Core Baseline
                </span>
              )}
            </div>
            {division.description && (
              <p className="text-xs text-slate-300/90 mt-1 flex items-baseline gap-1.5">
                <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold font-mono">Tujuan:</span>
                <span>{division.description}</span>
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2 self-end sm:self-auto">
          <div className="flex items-center space-x-1 text-xs text-slate-400 font-mono px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 mr-1">
            <Users className="w-3 h-3 text-slate-400" />
            <span>{roles.length} AI Agents</span>
          </div>

          <button
            type="button"
            onClick={() => onAddRole(division.id)}
            className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/15 text-white text-xs font-medium border border-white/15 transition-all"
          >
            <Plus className="w-3 h-3" />
            <span>Role</span>
          </button>

          <button
            type="button"
            onClick={() => onEditDivision(division)}
            className="p-1.5 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white transition-colors"
            title="Edit divisi"
          >
            <Edit2 className="w-3.5 h-3.5" />
          </button>

          {!isProtected && (
            <button
              type="button"
              onClick={() => onDeleteDivision(division)}
              className="p-1.5 rounded-lg hover:bg-rose-500/10 text-rose-400 transition-colors"
              title="Hapus divisi"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {roles.length === 0 ? (
        <div className="py-8 text-center border border-dashed border-white/10 rounded-xl bg-white/[0.01]">
          <p className="text-xs text-slate-500 mb-2">Belum ada karyawan AI di divisi ini.</p>
          <button
            type="button"
            onClick={() => onAddRole(division.id)}
            className="text-xs font-medium text-cyan-400 hover:text-cyan-300"
          >
            + Tambah Karyawan AI Pertama
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {roles.map((role) => (
            <RoleCard
              key={role.id}
              role={role}
              divisionName={division.name}
              divisionColor={accent}
              isMainBranch={isMainBranch}
              onEdit={onEditRole}
              onDelete={onDeleteRole}
              onToggleActive={onToggleActiveRole}
              onAddToPipeline={onAddToPipeline}
            />
          ))}
        </div>
      )}
    </div>
  );
}
