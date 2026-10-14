"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Columns3, Lock, MessageSquare } from "lucide-react";
import { fetchPreviewStatus, fetchProject, postGateDecision } from "../../../lib/api";
import { useSSEStream } from "../../../hooks/useSSEStream";
import { VentureStateData } from "../../../lib/types/api";
import { SecretVaultModal } from "../../../components/vault/SecretVaultModal";
import {
  PreviewWebviewPane,
  ViewportMode,
  PreviewMode,
} from "../../../components/preview/PreviewWebviewPane";
import { PreviewGateDecisions } from "../../../components/preview/PreviewGateDecisions";
import { PreviewGuildSpecs, SpecTab } from "../../../components/preview/PreviewGuildSpecs";

export default function DemoPreviewPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params?.id as string;

  const [project, setProject] = useState<VentureStateData | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [viewportMode, setViewportMode] = useState<ViewportMode>("desktop");
  const [previewMode, setPreviewMode] = useState<PreviewMode>("webview");
  const [iframeKey, setIframeKey] = useState<number>(0);
  const [activeTab, setActiveTab] = useState<SpecTab>("prd");
  const [isVaultOpen, setIsVaultOpen] = useState<boolean>(false);

  // Gate 2 & 3 decision state
  const [gateFeedback, setGateFeedback] = useState("");
  const [isProcessingGate, setIsProcessingGate] = useState(false);

  const { currentStage, previewUrl: ssePreviewUrl, agentStatus } = useSSEStream(projectId);

  const loadData = async () => {
    try {
      const p = await fetchProject(projectId);
      setProject(p);
      const url = p.preview_url || `http://demo-${projectId}.local.sandbox`;
      setPreviewUrl(url);

      const status = await fetchPreviewStatus(projectId);
      if (status.preview_url) {
        setPreviewUrl(status.preview_url);
      }
    } catch (err) {
      console.error("Gagal load detail preview:", err);
    }
  };

  useEffect(() => {
    if (!projectId) return;
    loadData();
  }, [projectId]);

  useEffect(() => {
    if (ssePreviewUrl) {
      setPreviewUrl(ssePreviewUrl);
    }
  }, [ssePreviewUrl]);

  const handleGateDecision = async (action: "APPROVE" | "REVISE" | "KILL") => {
    try {
      setIsProcessingGate(true);
      const gateId = activeStage === "GATE_3_WAITING" ? "gate_3" : "gate_2";
      await postGateDecision(projectId, gateId, {
        action,
        feedback: gateFeedback.trim() || undefined,
      });

      if (action === "REVISE") {
        router.push(`/sparring/${projectId}`);
      } else {
        await loadData();
        setGateFeedback("");
      }
    } catch (err) {
      console.error("Gagal mengeksekusi gate decision:", err);
    } finally {
      setIsProcessingGate(false);
    }
  };

  const activeStage = currentStage || project?.stage || "MOCK_PROTOTYPING";
  const isGate2Waiting = activeStage === "GATE_2_WAITING";
  const isGate3Waiting = activeStage === "GATE_3_WAITING";

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-61px)] overflow-hidden">
      {/* Top Navbar */}
      <div className="border-b border-slate-800 bg-slate-950 px-6 py-2.5 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link
            href="/"
            className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-white tracking-tight">
                {project?.project_name || "Demo Day Prototype"}
              </h2>
              <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-cyan-300">
                {activeStage}
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">{projectId}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            href={`/kanban/${projectId}`}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 text-xs font-semibold text-purple-300 transition-colors"
          >
            <Columns3 className="w-3.5 h-3.5 text-purple-400" />
            <span>Kanban & Lounge</span>
          </Link>
          <button
            onClick={() => setIsVaultOpen(true)}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-xs font-semibold text-indigo-300 transition-colors"
          >
            <Lock className="w-3.5 h-3.5 text-indigo-400" />
            <span>Secret Vault</span>
          </button>
          <Link
            href={`/sparring/${projectId}`}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-indigo-300 transition-colors"
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Sparring Room</span>
          </Link>
        </div>
      </div>

      {/* Split-Screen Workspace */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Left Pane: Interactive Multi-View Sandbox */}
        <PreviewWebviewPane
          projectId={projectId}
          previewUrl={previewUrl}
          previewMode={previewMode}
          setPreviewMode={setPreviewMode}
          viewportMode={viewportMode}
          setViewportMode={setViewportMode}
          iframeKey={iframeKey}
          onReload={() => setIframeKey((k) => k + 1)}
          onRollbackComplete={() => {
            setIframeKey((k) => k + 1);
            loadData();
          }}
        />

        {/* Right Pane: CEO Control Panel & Specs */}
        <div className="w-full lg:w-[35%] flex flex-col bg-slate-950 overflow-y-auto p-4 space-y-4">
          <PreviewGateDecisions
            isGate2Waiting={isGate2Waiting}
            isGate3Waiting={isGate3Waiting}
            gateFeedback={gateFeedback}
            setGateFeedback={setGateFeedback}
            handleGateDecision={handleGateDecision}
            isProcessingGate={isProcessingGate}
            onOpenVault={() => setIsVaultOpen(true)}
          />

          <PreviewGuildSpecs
            project={project}
            agentStatus={agentStatus}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
          />
        </div>
      </div>

      {/* Secret Vault Modal */}
      <SecretVaultModal
        projectId={projectId}
        isOpen={isVaultOpen}
        onClose={() => setIsVaultOpen(false)}
      />
    </div>
  );
}
