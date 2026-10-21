"use client";

import React from "react";
import { Bot, Edit2, Trash2, Shield, Coins, PlusCircle, GripVertical } from "lucide-react";
import { RoleResponse } from "@/lib/types/corporate";

interface RoleCardProps {
  role: RoleResponse;
  divisionName?: string;
  divisionColor?: string;
  isMainBranch: boolean;
  onEdit: (role: RoleResponse) => void;
  onDelete: (role: RoleResponse) => void;
  onToggleActive: (role: RoleResponse) => void;
  onAddToPipeline?: (role: RoleResponse, divName?: string, divColor?: string) => void;
}

export default function RoleCard({
  role,
  divisionName,
  divisionColor,
  isMainBranch,
  onEdit,
  onDelete,
  onToggleActive,
  onAddToPipeline,
}: RoleCardProps) {
  const isProtected = isMainBranch && role.is_system_default;

  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.setData(
      "application/json",
      JSON.stringify({
        type: "ROLE_ITEM",
        role: {
          id: role.id,
          name: role.name,
          division_id: role.division_id,
          model_name: role.model_name,
          token_budget_per_task: role.token_budget_per_task,
          system_prompt_template: role.system_prompt_template,
        },
        divisionName,
        divisionColor,
      })
    );
    e.dataTransfer.effectAllowed = "copy";
  };

  return (
    <div
      draggable={true}
      onDragStart={handleDragStart}
      className={`rounded-xl border p-3.5 transition-all flex flex-col justify-between cursor-grab active:cursor-grabbing select-none ${
        role.is_active
          ? "bg-white/[0.04] border-white/10 hover:border-white/25 shadow-sm"
          : "bg-white/[0.01] border-white/5 opacity-60"
      }`}
      title="Drag kartu ini ke Pipeline di atas untuk memasukkan peran!"
    >
      <div>
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center space-x-2">
            <div
              className={`w-7 h-7 rounded-lg flex items-center justify-center border text-xs font-mono font-bold ${
                role.is_active
                  ? "bg-cyan-500/10 border-cyan-500/30 text-cyan-300"
                  : "bg-white/5 border-white/10 text-slate-500"
              }`}
            >
              <Bot className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h5 className="text-xs font-semibold text-white tracking-tight">{role.name}</h5>
                <GripVertical className="w-3 h-3 text-slate-500 opacity-60" />
              </div>
              <span className="text-[10px] font-mono text-slate-400">{role.model_name.split("/").pop()}</span>
            </div>
          </div>

          <button
            type="button"
            onClick={() => onToggleActive(role)}
            className={`text-[10px] px-2 py-0.5 rounded-full font-mono transition-colors ${
              role.is_active
                ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
                : "bg-slate-500/15 text-slate-400 border border-slate-500/30"
            }`}
            title="Toggle status aktif"
          >
            {role.is_active ? "Active" : "Inactive"}
          </button>
        </div>

        {role.job_description && (
          <div className="mb-2 px-2 py-1 rounded bg-cyan-950/30 border border-cyan-800/40">
            <span className="text-[9px] uppercase tracking-wider text-cyan-400 font-bold block mb-0.5">Jobdesk / Fokus:</span>
            <p className="text-[11px] text-cyan-200/90 font-sans line-clamp-2">
              {role.job_description}
            </p>
          </div>
        )}

        <p className="text-[11px] text-slate-400 line-clamp-2 mb-3 italic font-sans">
          &quot;{role.system_prompt_template}&quot;
        </p>

        <div className="flex flex-wrap items-center gap-1.5 mb-3">
          <span className="px-2 py-0.5 rounded bg-white/5 text-slate-300 border border-white/10 text-[10px] font-mono">
            {role.model_name.includes("free") ? "• FREE: " : ""}
            {role.model_name.split("/").pop()}
          </span>

          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-300 text-[10px] font-mono">
            <Coins className="w-2.5 h-2.5" />
            {(role.token_budget_per_task / 1000).toFixed(0)}k tok
          </span>

          {isProtected && (
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 text-[9px] font-mono">
              <Shield className="w-2.5 h-2.5" />
              Core
            </span>
          )}

          {role.persona_prompt && (
            <span
              className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30 text-[9px] font-mono cursor-help"
              title={`Soul Persona: ${role.persona_prompt}`}
            >
              ✦ Soul
            </span>
          )}
        </div>

        {role.tool_permissions?.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-2">
            {role.tool_permissions.map((tool) => (
              <span
                key={tool}
                className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-white/[0.03] text-slate-400 border border-white/5"
              >
                {tool}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="pt-2 border-t border-white/5 flex items-center justify-between mt-2">
        {onAddToPipeline ? (
          <button
            type="button"
            onClick={() => onAddToPipeline(role, divisionName, divisionColor)}
            className="flex items-center gap-1 px-2 py-0.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/20 text-[10px] font-mono transition-colors"
            title="Tambahkan ke Pipeline yang aktif saat ini"
          >
            <PlusCircle className="w-3 h-3" />
            <span>+ Pipeline</span>
          </button>
        ) : (
          <span />
        )}

        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => onEdit(role)}
            className="p-1 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white transition-colors text-xs"
            title="Edit peran"
          >
            <Edit2 className="w-3.5 h-3.5" />
          </button>

          {!isProtected && (
            <button
              type="button"
              onClick={() => onDelete(role)}
              className="p-1 rounded-lg hover:bg-rose-500/10 text-rose-400 transition-colors text-xs"
              title="Hapus peran"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
