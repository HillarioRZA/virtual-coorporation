"use client";

import { useState, useEffect } from "react";
import { RoleResponse, PipelineStageItem } from "@/lib/types/corporate";
import { fetchWorkflowPipeline, saveWorkflowPipelineStages, resetWorkflowPipeline } from "@/lib/workflowApi";
import { CeoGatePreset } from "./PipelineCeoGatePalette";

interface UseWorkflowStagesOptions {
  branchId?: string;
  activePipelineId: string;
  isMain: boolean;
  onPipelineChanged?: () => void;
}

export function useWorkflowStages({ branchId, activePipelineId, isMain, onPipelineChanged }: UseWorkflowStagesOptions) {
  const [stages, setStages] = useState<PipelineStageItem[]>([]);
  const [initialSnapshot, setInitialSnapshot] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const loadStages = async (bId: string, pipeId: string) => {
    setLoading(true);
    try {
      const data = await fetchWorkflowPipeline(bId, pipeId);
      setStages(data);
      setInitialSnapshot(JSON.stringify(data));
    } catch {
      setStages([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (branchId && activePipelineId) loadStages(branchId, activePipelineId);
  }, [branchId, activePipelineId]);

  const isDirty = JSON.stringify(stages) !== initialSnapshot;

  const addRoleStage = (role: RoleResponse, divName?: string, divColor?: string, targetIndex?: number) => {
    if (isMain) return alert("Branch Main baseline terkunci. Harap Fork Workflow terlebih dahulu.");
    const newStage: PipelineStageItem = {
      id: `stg_role_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      pipeline_id: activePipelineId,
      stage_index: targetIndex ?? stages.length,
      order_index: targetIndex ?? stages.length,
      stage_type: "ROLE_EXECUTION",
      role_id: role.id,
      role_name: role.name,
      division_id: role.division_id,
      division_name: divName || "Custom",
      division_color: divColor || "#38bdf8",
      model_name: role.model_name,
      custom_label: role.name,
      custom_instructions: role.system_prompt_template?.substring(0, 150),
      is_active: true,
      is_system_default: false,
    };
    const updated = [...stages];
    if (typeof targetIndex === "number" && targetIndex >= 0 && targetIndex <= stages.length) {
      updated.splice(targetIndex, 0, newStage);
    } else {
      updated.push(newStage);
    }
    setStages(updated.map((s, idx) => ({ ...s, stage_index: idx, order_index: idx })));
    setFeedback(`Peran '${role.name}' ditambahkan!`);
    setTimeout(() => setFeedback(null), 3000);
  };

  const addCeoGate = (preset: CeoGatePreset, targetIndex?: number) => {
    const newGate: PipelineStageItem = {
      id: `stg_ceo_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      pipeline_id: activePipelineId,
      stage_index: targetIndex ?? stages.length,
      order_index: targetIndex ?? stages.length,
      stage_type: "CEO_GATE",
      role_id: null,
      role_name: "CEO Human Gate",
      division_id: "div_exec",
      division_name: "Executive Suite",
      division_color: "#eab308",
      model_name: "Human-in-the-Loop",
      ceo_gate_type: preset.type,
      custom_label: preset.label,
      custom_instructions: preset.desc,
      is_active: true,
      is_system_default: false,
    };
    const updated = [...stages];
    if (typeof targetIndex === "number" && targetIndex >= 0 && targetIndex <= stages.length) {
      updated.splice(targetIndex, 0, newGate);
    } else {
      updated.push(newGate);
    }
    setStages(updated.map((s, idx) => ({ ...s, stage_index: idx, order_index: idx })));
    setFeedback(`Gerbang CEO '${preset.label}' ditambahkan!`);
    setTimeout(() => setFeedback(null), 3000);
  };

  const handleStageDrop = (e: React.DragEvent, dropIndex: number, draggedIdx: number | null) => {
    if (isMain) return;
    e.preventDefault();
    try {
      const rawJson = e.dataTransfer.getData("application/json");
      if (rawJson) {
        const p = JSON.parse(rawJson);
        if (p.type === "ROLE_ITEM") return addRoleStage(p.role, p.divisionName, p.divisionColor, dropIndex);
        if (p.type === "CEO_GATE_ITEM") return addCeoGate(p.preset, dropIndex);
      }
    } catch {}
    const srcIdx = draggedIdx ?? parseInt(e.dataTransfer.getData("text/plain"), 10);
    if (!isNaN(srcIdx) && srcIdx !== dropIndex) {
      const updated = [...stages];
      const [moved] = updated.splice(srcIdx, 1);
      updated.splice(dropIndex, 0, moved);
      setStages(updated.map((s, idx) => ({ ...s, stage_index: idx, order_index: idx })));
    }
  };

  const handleCanvasEndDrop = (e: React.DragEvent) => {
    if (isMain) return;
    e.preventDefault();
    try {
      const raw = e.dataTransfer.getData("application/json");
      if (raw) {
        const p = JSON.parse(raw);
        if (p.type === "ROLE_ITEM") addRoleStage(p.role, p.divisionName, p.divisionColor);
        if (p.type === "CEO_GATE_ITEM") addCeoGate(p.preset);
      }
    } catch {}
  };

  const handleSave = async () => {
    if (!branchId || !isDirty) return;
    setSaving(true);
    try {
      const updated = await saveWorkflowPipelineStages(branchId, stages, activePipelineId);
      setStages(updated);
      setInitialSnapshot(JSON.stringify(updated));
      setFeedback("Alur kerja berhasil disimpan!");
      setTimeout(() => setFeedback(null), 4000);
      if (onPipelineChanged) onPipelineChanged();
    } catch (err: any) {
      alert(err.message || "Gagal menyimpan alur kerja.");
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!branchId || !confirm("Reset pipeline kembali ke baseline resmi?")) return;
    setLoading(true);
    try {
      const data = await resetWorkflowPipeline(branchId, activePipelineId);
      setStages(data);
      setInitialSnapshot(JSON.stringify(data));
      setFeedback("Pipeline berhasil direset.");
      setTimeout(() => setFeedback(null), 4000);
      if (onPipelineChanged) onPipelineChanged();
    } catch (err: any) {
      alert(err.message || "Gagal mereset.");
    } finally {
      setLoading(false);
    }
  };

  const moveStage = (idx: number, dir: -1 | 1) => {
    const t = idx + dir;
    if (t >= 0 && t < stages.length) {
      const u = [...stages];
      const [m] = u.splice(idx, 1);
      u.splice(t, 0, m);
      setStages(u.map((s, i) => ({ ...s, stage_index: i, order_index: i })));
    }
  };

  const duplicateStage = (idx: number) => {
    const target = stages[idx];
    const dup = { ...target, id: `stg_dup_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`, custom_label: target.custom_label ? `${target.custom_label} (Loop)` : undefined };
    const u = [...stages];
    u.splice(idx + 1, 0, dup);
    setStages(u.map((s, i) => ({ ...s, stage_index: i, order_index: i })));
  };

  const removeStage = (idx: number) => {
    if (stages.length <= 1) return alert("Minimal 1 tahapan diperlukan.");
    setStages(stages.filter((_, i) => i !== idx).map((s, i) => ({ ...s, stage_index: i, order_index: i })));
  };

  return {
    stages,
    loading,
    saving,
    feedback,
    isDirty,
    addRoleStage,
    addCeoGate,
    moveStage,
    duplicateStage,
    removeStage,
    handleStageDrop,
    handleCanvasEndDrop,
    handleSave,
    handleReset,
  };
}
