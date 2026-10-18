"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Send,
  Sparkles,
  Bot,
  User,
  ShieldCheck,
  AlertTriangle,
  XCircle,
  CheckCircle,
  ExternalLink,
  Cpu,
  Briefcase,
} from "lucide-react";
import { fetchProject, postGateDecision, postSparringChat } from "../../../lib/api";
import { useSSEStream } from "../../../hooks/useSSEStream";
import { VentureStateData } from "../../../lib/types/api";

export default function SparringRoomPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params?.id as string;

  const [project, setProject] = useState<VentureStateData | null>(null);
  const [chatInput, setChatInput] = useState("");
  const [targetAgent, setTargetAgent] = useState<"BROADCAST" | "COS" | "CTO">("BROADCAST");
  const [isSending, setIsSending] = useState(false);

  // Gate feedback input state
  const [gateFeedback, setGateFeedback] = useState("");
  const [isProcessingGate, setIsProcessingGate] = useState(false);

  const {
    messages,
    agentStatus,
    currentStage,
    isConnected,
    addLocalMessage,
    setMessages,
    setCurrentStage,
  } = useSSEStream(projectId);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Load snapshot state awal
  useEffect(() => {
    if (!projectId) return;
    fetchProject(projectId)
      .then((data) => {
        setProject(data);
        setCurrentStage(data.stage);

        // Jika ada event logs awal, populate ke messages
        if (data.event_logs && data.event_logs.length > 0) {
          const initMsgs = data.event_logs.map((log, idx) => {
            const sender = log.includes("[CEO]") || log.startsWith("Founder")
              ? "CEO"
              : log.includes("[COS]")
              ? "COS"
              : log.includes("[CTO]")
              ? "CTO"
              : "SYSTEM";
            return {
              id: `init_${idx}`,
              sender,
              content: log.replace(/^\[(COS|CTO|CEO|SYSTEM)\]\s*/, ""),
              timestamp: "",
              isStreaming: false,
            };
          });
          setMessages(initMsgs);
        }
      })
      .catch((err) => console.error("Gagal load project detail:", err));
  }, [projectId, setCurrentStage, setMessages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || isSending) return;

    const msg = chatInput.trim();
    setChatInput("");
    setIsSending(true);

    // Tambahkan pesan CEO ke UI secara optimistik
    addLocalMessage("CEO", msg);

    try {
      await postSparringChat(projectId, {
        message: msg,
        target_agent: targetAgent === "BROADCAST" ? undefined : targetAgent,
      });
    } catch (err) {
      console.error("Gagal mengirim chat:", err);
    } finally {
      setIsSending(false);
    }
  };

  const handleGateDecision = async (action: "APPROVE" | "REVISE" | "KILL") => {
    try {
      setIsProcessingGate(true);
      const res = await postGateDecision(projectId, "gate_1", {
        action,
        feedback: gateFeedback.trim() || undefined,
      });

      if (action === "APPROVE") {
        router.push(`/preview/${projectId}`);
      } else {
        const updated = await fetchProject(projectId);
        setProject(updated);
        setCurrentStage(updated.stage);
        setGateFeedback("");
      }
    } catch (err) {
      console.error("Gagal mengeksekusi gate decision:", err);
    } finally {
      setIsProcessingGate(false);
    }
  };

  const activeStage = currentStage || project?.stage || "SPARRING_ROOM";
  const isGate1Waiting = activeStage === "GATE_1_WAITING";

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-61px)] overflow-hidden">
      {/* Top Bar */}
      <div className="border-b border-slate-800 bg-slate-950 px-6 py-3 flex items-center justify-between">
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
                {project?.project_name || "Executive Sparring Room"}
              </h2>
              <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-indigo-300">
                {activeStage}
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">{projectId}</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs">
            <span
              className={`w-2 h-2 rounded-full ${
                isConnected ? "bg-emerald-400 animate-pulse" : "bg-slate-600"
              }`}
            />
            <span className="text-slate-400 hidden sm:inline">{agentStatus}</span>
          </div>
          <Link
            href={`/preview/${projectId}`}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-cyan-300 transition-colors"
          >
            <span>Buka Webview</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Main Chat Stream Viewport */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
        {/* Project Foundation Note */}
        {project?.founder_idea && (
          <div className="glass-panel p-4 rounded-2xl border border-indigo-500/20 max-w-3xl mx-auto space-y-1.5">
            <div className="flex items-center space-x-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider">
              <Sparkles className="w-4 h-4" />
              <span>Founder Business Thesis</span>
            </div>
            <p className="text-sm text-slate-200">{project.founder_idea}</p>
          </div>
        )}

        {/* Message Bubbles */}
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.map((msg) => {
            const isCEO = msg.sender === "CEO";
            const isCoS = msg.sender === "COS";
            const isCTO = msg.sender === "CTO";

            return (
              <div
                key={msg.id}
                className={`flex items-start gap-3 ${isCEO ? "flex-row-reverse" : "flex-row"}`}
              >
                {/* Avatar Icon */}
                <div
                  className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-white font-bold text-xs shadow-md ${
                    isCEO
                      ? "bg-indigo-600"
                      : isCoS
                      ? "bg-amber-500 text-slate-950 font-extrabold"
                      : isCTO
                      ? "bg-cyan-500 text-slate-950 font-extrabold"
                      : "bg-slate-700"
                  }`}
                >
                  {isCEO ? <User className="w-4 h-4" /> : isCoS ? <Briefcase className="w-4 h-4" /> : <Cpu className="w-4 h-4" />}
                </div>

                {/* Message Bubble Container */}
                <div
                  className={`max-w-[80%] rounded-2xl p-4 text-sm space-y-1 shadow-lg ${
                    isCEO
                      ? "bg-indigo-600/90 text-white rounded-tr-none"
                      : isCoS
                      ? "bg-slate-900 border border-amber-500/30 text-slate-200 rounded-tl-none"
                      : isCTO
                      ? "bg-slate-900 border border-cyan-500/30 text-slate-200 rounded-tl-none"
                      : "bg-slate-900 border border-slate-800 text-slate-300"
                  }`}
                >
                  <div className="flex items-center justify-between gap-3 text-xs pb-1 border-b border-white/10">
                    <span className="font-bold tracking-wider">
                      {isCEO ? "Founder (CEO)" : isCoS ? "Chief of Staff (CoS)" : isCTO ? "Chief Technology Officer (CTO)" : msg.sender}
                    </span>
                    {msg.timestamp && <span className="opacity-60 text-[10px]">{msg.timestamp}</span>}
                  </div>
                  <div className="whitespace-pre-wrap leading-relaxed text-sm pt-1">
                    {msg.content}
                    {msg.isStreaming && (
                      <span className="inline-block w-1.5 h-4 ml-1 bg-current animate-pulse align-middle" />
                    )}
                  </div>
                </div>
              </div>
            );
          })}
          <div ref={messagesEndRef} />
        </div>

        {/* Stage-Gate 1 Decision Card */}
        {isGate1Waiting && (
          <div className="max-w-3xl mx-auto my-6 p-6 rounded-3xl glass-panel-glow border-2 border-yellow-500/40 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-yellow-500/20 text-yellow-400">
                  <ShieldCheck className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Stage-Gate 1: Executive Alignment Decision</h3>
                  <p className="text-xs text-slate-400">CoS & CTO telah menyelesaikan briefing strategi & spesifikasi arsitektur.</p>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-yellow-500/20 text-yellow-300 border border-yellow-500/40 animate-pulse">
                Action Required
              </span>
            </div>

            {/* Input Feedback jika revisi */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
                Catatan Instruksi Revisi (Opsional untuk REVISE):
              </label>
              <textarea
                rows={2}
                value={gateFeedback}
                onChange={(e) => setGateFeedback(e.target.value)}
                placeholder="Berikan umpan balik spesifik jika Anda memilih REVISE..."
                className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-yellow-500 transition-colors"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => handleGateDecision("KILL")}
                disabled={isProcessingGate}
                className="px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-400 text-xs font-bold transition-all disabled:opacity-50"
              >
                <span className="flex items-center gap-1.5">
                  <XCircle className="w-4 h-4" />
                  <span>KILL (Arsipkan Proyek)</span>
                </span>
              </button>
              <button
                type="button"
                onClick={() => handleGateDecision("REVISE")}
                disabled={isProcessingGate}
                className="px-4 py-2 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 text-xs font-bold transition-all disabled:opacity-50"
              >
                <span className="flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4" />
                  <span>REVISE (Putar Ulang Sparring)</span>
                </span>
              </button>
              <button
                type="button"
                onClick={() => handleGateDecision("APPROVE")}
                disabled={isProcessingGate}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white text-xs font-bold shadow-lg shadow-emerald-500/20 transition-all hover:scale-105 disabled:opacity-50"
              >
                <span className="flex items-center gap-1.5">
                  <CheckCircle className="w-4 h-4" />
                  <span>APPROVE (Kunci Spec & Lanjut ke Mock)</span>
                </span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Chat Input Bar */}
      <div className="border-t border-slate-800 bg-slate-950 p-4">
        <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto space-y-2">
          {/* Target Selector */}
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-400">Target Penerima:</span>
            <button
              type="button"
              onClick={() => setTargetAgent("BROADCAST")}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
                targetAgent === "BROADCAST"
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-900 text-slate-400 hover:bg-slate-800"
              }`}
            >
              Broadcast (CoS + CTO)
            </button>
            <button
              type="button"
              onClick={() => setTargetAgent("COS")}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
                targetAgent === "COS"
                  ? "bg-amber-500 text-slate-950 font-bold"
                  : "bg-slate-900 text-slate-400 hover:bg-slate-800"
              }`}
            >
              CoS Only (Bisnis)
            </button>
            <button
              type="button"
              onClick={() => setTargetAgent("CTO")}
              className={`px-2.5 py-1 rounded-lg font-medium transition-colors ${
                targetAgent === "CTO"
                  ? "bg-cyan-500 text-slate-950 font-bold"
                  : "bg-slate-900 text-slate-400 hover:bg-slate-800"
              }`}
            >
              CTO Only (Teknis)
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Ketik instruksi, tanggapan, atau kritik Founder..."
              className="flex-1 px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
            />
            <button
              type="submit"
              disabled={isSending || !chatInput.trim()}
              className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/25 disabled:opacity-50 transition-all hover:scale-105 active:scale-95"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
