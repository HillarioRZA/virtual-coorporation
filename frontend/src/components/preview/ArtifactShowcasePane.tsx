"use client";

import React, { useEffect, useState } from "react";
import { Download, ExternalLink, FileText, Layers, Presentation, RefreshCw, Sparkles, Table } from "lucide-react";
import { ArtifactItem, fetchProjectArtifacts, getArtifactDownloadUrl } from "../../lib/artifactsApi";

interface ArtifactShowcasePaneProps {
  projectId: string;
}

export const ArtifactShowcasePane: React.FC<ArtifactShowcasePaneProps> = ({ projectId }) => {
  const [artifacts, setArtifacts] = useState<ArtifactItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedArtifact, setSelectedArtifact] = useState<ArtifactItem | null>(null);

  const loadData = async () => {
    setLoading(true);
    const items = await fetchProjectArtifacts(projectId);
    setArtifacts(items);
    if (items.length > 0 && !selectedArtifact) {
      setSelectedArtifact(items[0]);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (projectId) loadData();
  }, [projectId]);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "SLIDES":
        return <Presentation className="w-4 h-4 text-amber-400" />;
      case "EBOOK":
      case "DOCUMENT":
        return <FileText className="w-4 h-4 text-emerald-400" />;
      case "DATA":
      case "SPREADSHEET":
        return <Table className="w-4 h-4 text-cyan-400" />;
      default:
        return <Layers className="w-4 h-4 text-indigo-400" />;
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-950/80 border border-slate-800 rounded-b-2xl overflow-hidden p-4 space-y-4">
      {/* Header bar */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h3 className="text-sm font-bold text-white tracking-tight">Artifacts & Media Hub (Divisi B & C)</h3>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
            {artifacts.length} Assets
          </span>
        </div>
        <button
          onClick={loadData}
          className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          title="Refresh Artifacts"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {artifacts.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center border border-dashed border-slate-800 rounded-xl">
          <Layers className="w-10 h-10 text-slate-600 mb-2" />
          <p className="text-sm font-semibold text-slate-400">Belum ada artefak lintas divisi yang dikompilasi</p>
          <p className="text-xs text-slate-500 mt-1 max-w-sm">
            Jalankan tiket Divisi B (Kreatif/Slide) atau Divisi C (Copywriting/Ads) untuk memproduksi media otomatis.
          </p>
        </div>
      ) : (
        <div className="flex-1 flex flex-col lg:flex-row gap-4 overflow-hidden">
          {/* Left Column: Artifacts Selector List */}
          <div className="w-full lg:w-72 flex flex-col space-y-2 overflow-y-auto pr-1">
            {artifacts.map((art) => {
              const isSelected = selectedArtifact?.filename === art.filename;
              return (
                <div
                  key={art.filename}
                  onClick={() => setSelectedArtifact(art)}
                  className={`p-3 rounded-xl border text-left cursor-pointer transition-all ${
                    isSelected
                      ? "bg-indigo-600/20 border-indigo-500/50 text-white shadow-lg shadow-indigo-500/10"
                      : "bg-slate-900/60 border-slate-800 text-slate-300 hover:bg-slate-800/60"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center space-x-1.5">
                      {getCategoryIcon(art.category)}
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{art.category}</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500">{(art.size_bytes / 1024).toFixed(1)} KB</span>
                  </div>
                  <p className="text-xs font-semibold truncate text-slate-200">{art.filename}</p>
                </div>
              );
            })}
          </div>

          {/* Right Column: Live Interactive Preview & Actions */}
          <div className="flex-1 flex flex-col bg-slate-900/40 border border-slate-800 rounded-xl overflow-hidden">
            {selectedArtifact && (
              <>
                <div className="px-4 py-2.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-300 truncate">{selectedArtifact.filename}</span>
                  <div className="flex items-center space-x-2">
                    <a
                      href={getArtifactDownloadUrl(projectId, selectedArtifact.filename)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 hover:text-white inline-flex items-center gap-1.5 transition-colors"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      <span>Buka Tab Baru</span>
                    </a>
                    <a
                      href={getArtifactDownloadUrl(projectId, selectedArtifact.filename)}
                      download={selectedArtifact.filename}
                      className="px-2.5 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white inline-flex items-center gap-1.5 transition-colors shadow-sm"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Download</span>
                    </a>
                  </div>
                </div>

                <div className="flex-1 bg-white overflow-hidden">
                  <iframe
                    src={getArtifactDownloadUrl(projectId, selectedArtifact.filename)}
                    title={selectedArtifact.filename}
                    className="w-full h-full border-0"
                    sandbox="allow-scripts allow-same-origin allow-forms"
                  />
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
