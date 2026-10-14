"use client";

import React, { useState, useEffect, forwardRef, useImperativeHandle } from "react";
import { GitBranch, Save, RotateCcw, Lock, Sparkles, CheckCircle2 } from "lucide-react";
import { BranchResponse, PipelineResponse, RoleResponse } from "@/lib/types/corporate";
import { fetchPipelines, createPipeline, deletePipeline } from "@/lib/workflowApi";
import PipelineTabBar from "./PipelineTabBar";
import PipelineCeoGatePalette from "./PipelineCeoGatePalette";
import PipelineModal from "./PipelineModal";
import PipelineSequenceList from "./PipelineSequenceList";
import { useWorkflowStages } from "./useWorkflowStages";

export interface WorkflowPipelineBuilderHandle {
  addRoleToPipeline: (role: RoleResponse, divName?: string, divColor?: string) => void;
}

interface Props {
  selectedBranch: BranchResponse | null;
  onOpenForkModal: () => void;
  onPipelineChanged?: () => void;
}

const WorkflowPipelineBuilder = forwardRef<WorkflowPipelineBuilderHandle, Props>(
  ({ selectedBranch, onOpenForkModal, onPipelineChanged }, ref) => {
    const [pipelines, setPipelines] = useState<PipelineResponse[]>([]);
    const [activePipelineId, setActivePipelineId] = useState<string>("");
    const [modalOpen, setModalOpen] = useState(false);

    const isMain = selectedBranch ? selectedBranch.slug === "main" || Boolean(selectedBranch.is_active_main) : true;

    const {
      stages, loading, saving, feedback, isDirty,
      addRoleStage, addCeoGate, moveStage, duplicateStage, removeStage,
      handleStageDrop, handleCanvasEndDrop, handleSave, handleReset,
    } = useWorkflowStages({
      branchId: selectedBranch?.id,
      activePipelineId,
      isMain,
      onPipelineChanged,
    });

    useImperativeHandle(ref, () => ({
      addRoleToPipeline: (role, divName, divColor) => addRoleStage(role, divName, divColor),
    }));

    const loadPipelineList = async (branchId: string) => {
      try {
        const list = await fetchPipelines(branchId);
        setPipelines(list);
        if (list.length > 0 && !list.some((p) => p.id === activePipelineId)) {
          setActivePipelineId(list[0].id);
        }
      } catch {
        setPipelines([]);
      }
    };

    useEffect(() => {
      if (selectedBranch?.id) loadPipelineList(selectedBranch.id);
    }, [selectedBranch?.id]);

    if (!selectedBranch) return null;

    return (
      <div className="rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-white/10 p-5 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <GitBranch className="w-4 h-4" />
              </span>
              <h2 className="text-sm font-semibold text-white">Dynamic Multi-Pipeline & Governance Hub</h2>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-white/5 border border-white/10 text-slate-400">
                {stages.length} Tahapan
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">Pilih lini produk, drag peran atau gerbang keputusan CEO ke dalam alur kerja.</p>
          </div>
          <div className="flex items-center gap-2">
            {!isMain && (
              <>
                <button type="button" onClick={handleReset} disabled={saving} className="px-3 py-1.5 rounded-xl border border-white/10 hover:bg-white/5 text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition-all">
                  <RotateCcw className="w-3.5 h-3.5" /> Reset
                </button>
                {isDirty && (
                  <button type="button" onClick={handleSave} disabled={saving} className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs flex items-center gap-1.5 shadow-lg shadow-emerald-600/20 transition-all">
                    <Save className="w-3.5 h-3.5" /> {saving ? "Menyimpan..." : "Simpan Alur"}
                  </button>
                )}
              </>
            )}
          </div>
        </div>

        <PipelineTabBar
          pipelines={pipelines}
          activePipelineId={activePipelineId}
          onSelectPipeline={setActivePipelineId}
          onCreatePipeline={() => setModalOpen(true)}
          onDeletePipeline={async (id) => {
            await deletePipeline(selectedBranch.id, id);
            await loadPipelineList(selectedBranch.id);
          }}
          isMain={isMain}
        />

        {feedback && (
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>{feedback}</span>
          </div>
        )}

        {isMain ? (
          <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2.5 text-amber-200">
              <Lock className="w-4 h-4 text-amber-400 flex-shrink-0" />
              <span><strong>Branch Main Terkunci (Gold Standard).</strong> Fork alur kerja untuk membuat cabang eksperimen.</span>
            </div>
            <button type="button" onClick={onOpenForkModal} className="px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 font-medium text-xs whitespace-nowrap flex items-center gap-1.5">
              <GitBranch className="w-3.5 h-3.5" /> Fork Workflow
            </button>
          </div>
        ) : (
          <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center gap-2 text-xs text-indigo-300">
            <Sparkles className="w-4 h-4 text-indigo-400 flex-shrink-0" />
            <span><strong>Drag & Drop Aktif:</strong> Drag kartu peran atau Gerbang CEO ke canvas untuk menyusun urutan alur kerja.</span>
          </div>
        )}

        <PipelineSequenceList
          stages={stages}
          isMain={isMain}
          loading={loading}
          onMoveStage={moveStage}
          onDuplicateStage={duplicateStage}
          onRemoveStage={removeStage}
          onStageDrop={handleStageDrop}
          onCanvasEndDrop={handleCanvasEndDrop}
        />

        {!isMain && <PipelineCeoGatePalette onAddCeoGate={addCeoGate} />}
        <PipelineModal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          onSubmit={async (p) => {
            await createPipeline(selectedBranch.id, p);
            await loadPipelineList(selectedBranch.id);
          }}
        />
      </div>
    );
  }
);

WorkflowPipelineBuilder.displayName = "WorkflowPipelineBuilder";
export default WorkflowPipelineBuilder;
