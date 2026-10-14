"use client";

import React, { useState } from "react";
import { ArrowRight } from "lucide-react";
import { PipelineStageItem } from "@/lib/types/corporate";
import PipelineStageCard from "./PipelineStageCard";
import PipelineDropZones from "./PipelineDropZones";

interface PipelineSequenceListProps {
  stages: PipelineStageItem[];
  isMain: boolean;
  loading: boolean;
  onMoveStage: (index: number, direction: -1 | 1) => void;
  onDuplicateStage: (index: number) => void;
  onRemoveStage: (index: number) => void;
  onStageDrop: (e: React.DragEvent, dropIndex: number, draggedIdx: number | null) => void;
  onCanvasEndDrop: (e: React.DragEvent) => void;
}

export default function PipelineSequenceList({
  stages,
  isMain,
  loading,
  onMoveStage,
  onDuplicateStage,
  onRemoveStage,
  onStageDrop,
  onCanvasEndDrop,
}: PipelineSequenceListProps) {
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);

  if (loading) {
    return (
      <div className="py-8 text-center text-xs text-slate-400">
        Memuat tahapan pipeline...
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2.5 overflow-x-auto pb-3 pt-2 scrollbar-thin scrollbar-thumb-white/10">
      {stages.map((stage, idx) => (
        <React.Fragment key={stage.id || `${stage.role_slug}_${idx}`}>
          <PipelineStageCard
            stage={stage}
            index={idx}
            totalStages={stages.length}
            isMain={isMain}
            isDragging={draggedIndex === idx}
            isOver={dragOverIndex === idx}
            onDragStart={(e) => {
              if (isMain) return;
              setDraggedIndex(idx);
              e.dataTransfer.setData("text/plain", idx.toString());
            }}
            onDragOver={(e) => {
              if (isMain) return;
              e.preventDefault();
              if (dragOverIndex !== idx) setDragOverIndex(idx);
            }}
            onDrop={(e) => {
              onStageDrop(e, idx, draggedIndex);
              setDraggedIndex(null);
              setDragOverIndex(null);
            }}
            onDragEnd={() => {
              setDraggedIndex(null);
              setDragOverIndex(null);
            }}
            onMoveStage={onMoveStage}
            onDuplicateStage={onDuplicateStage}
            onRemoveStage={onRemoveStage}
          />
          {idx < stages.length - 1 && (
            <ArrowRight className="w-4 h-4 text-slate-600 flex-shrink-0" />
          )}
        </React.Fragment>
      ))}

      <PipelineDropZones isMain={isMain} onDropItem={onCanvasEndDrop} />
    </div>
  );
}
