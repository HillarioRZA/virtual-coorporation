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
  Paperclip,
  FileText,
  Image as ImageIcon,
  Loader2,
  X,
} from "lucide-react";
import { fetchProject, postGateDecision, postSparringChat } from "../../../lib/api";
import { fetchRoles } from "../../../lib/corporateApi";
import { useSSEStream } from "../../../hooks/useSSEStream";
import { VentureStateData } from "../../../lib/types/api";
import { RoleResponse } from "../../../lib/types/corporate";
import { uploadChatAttachment } from "../../../lib/officeApi";
import { AttachmentItem } from "../../../lib/types/office";

export default function SparringRoomPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params?.id as string;

  const [project, setProject] = useState<VentureStateData | null>(null);
  const [chatInput, setChatInput] = useState("");
  const [availableRoles, setAvailableRoles] = useState<RoleResponse[]>([]);
  const [mentionQuery, setMentionQuery] = useState<string | null>(null);
  const [mentionIndex, setMentionIndex] = useState<number>(-1);
  const [isSending, setIsSending] = useState(false);
  const [isWaitingResponse, setIsWaitingResponse] = useState(false);
  const [attachments, setAttachments] = useState<AttachmentItem[]>([]);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const chatInputRef = useRef<HTMLInputElement | null>(null);

  const [isDragging, setIsDragging] = useState<boolean>(false);

  const processUploadedFiles = async (files: FileList | File[]) => {
    if (!files || files.length === 0 || !projectId) return;
    setIsUploading(true);
    try {
      for (let i = 0; i < files.length; i++) {
        const uploaded = await uploadChatAttachment(projectId, files[i]);
        setAttachments((prev) => [...prev, uploaded]);
      }
    } catch (err) {
      console.error("Gagal mengunggah berkas ke sparring:", err);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      processUploadedFiles(e.target.files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processUploadedFiles(e.dataTransfer.files);
    }
  };

  const removeAttachment = (id: string) => {
    setAttachments((prev) => prev.filter((a) => a.id !== id));
  };

  useEffect(() => {
    fetchRoles()
      .then((roles) => setAvailableRoles(roles.filter((r) => r.is_active)))
      .catch((err) => console.error("Gagal load roles untuk autocomplete:", err));
  }, []);

  const handleChatInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setChatInput(val);
    const cursor = e.target.selectionStart || val.length;
    const textBeforeCursor = val.slice(0, cursor);
    const atIndex = textBeforeCursor.lastIndexOf("@");
    if (atIndex !== -1 && !/\s/.test(textBeforeCursor.slice(atIndex + 1))) {
      setMentionQuery(textBeforeCursor.slice(atIndex + 1));
      setMentionIndex(atIndex);
    } else {
      setMentionQuery(null);
      setMentionIndex(-1);
    }
  };

  const insertMention = (name: string) => {
    if (mentionIndex === -1) return;
    const before = chatInput.slice(0, mentionIndex);
    const after = chatInput.slice(mentionIndex + 1 + (mentionQuery?.length || 0));
    const nextVal = `${before}@${name} ${after}`;
    setChatInput(nextVal);
    setMentionQuery(null);
    setMentionIndex(-1);
    setTimeout(() => chatInputRef.current?.focus(), 50);
  };

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

        // Jika ada event logs awal, populate ke messages dengan deduplikasi pesan beruntun identik
        if (data.event_logs && data.event_logs.length > 0) {
          const initMsgs: { id: string; sender: string; content: string; timestamp: string; isStreaming: boolean }[] = [];
          data.event_logs.forEach((log, idx) => {
            const sender = log.includes("[CEO]") || log.startsWith("Founder")
              ? "CEO"
              : log.includes("[COS]")
              ? "COS"
              : log.includes("[CTO]")
              ? "CTO"
              : "SYSTEM";
            const content = log.replace(/^\[(COS|CTO|CEO|SYSTEM)\]\s*/, "").trim();
            const prev = initMsgs[initMsgs.length - 1];
            if (prev && prev.sender === sender && prev.content === content) {
              return;
            }
            initMsgs.push({
              id: `init_${idx}`,
              sender,
              content,
              timestamp: "",
              isStreaming: false,
            });
          });
          setMessages(initMsgs);
        }
      })
      .catch((err) => console.error("Gagal load project detail:", err));
  }, [projectId, setCurrentStage, setMessages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    const lastMsg = messages[messages.length - 1];
    if (lastMsg && (lastMsg.sender !== "CEO" || lastMsg.isStreaming)) {
      setIsWaitingResponse(false);
    }
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if ((!chatInput.trim() && attachments.length === 0) || isSending || isUploading) return;

    const msg = chatInput.trim();
    const currentAttachments = [...attachments];
    setChatInput("");
    setMentionQuery(null);
    setMentionIndex(-1);
    setAttachments([]);
    setIsSending(true);
    setIsWaitingResponse(true);

    // Tambahkan pesan CEO ke UI secara optimistik dengan lampiran
    addLocalMessage("CEO", msg, currentAttachments);

    try {
      await postSparringChat(projectId, {
        message: msg,
        attachments: currentAttachments,
      });
    } catch (err) {
      console.error("Gagal mengirim chat:", err);
      setIsWaitingResponse(false);
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
                isWaitingResponse
                  ? "bg-amber-400 animate-ping"
                  : isConnected
                  ? "bg-emerald-400 animate-pulse"
                  : "bg-slate-600"
              }`}
            />
            <span className="text-slate-400 hidden sm:inline font-mono">
              {isWaitingResponse ? (
                <span className="text-amber-300 font-semibold animate-pulse">
                  ⚡ Agen AI sedang menganalisis...
                </span>
              ) : (
                agentStatus
              )}
            </span>
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
                      <span className="inline-block w-2 h-4 ml-1 bg-amber-400 animate-pulse align-middle rounded-sm shadow-[0_0_8px_rgba(251,191,36,0.8)]" />
                    )}
                  </div>

                  {/* Attachments if any */}
                  {msg.attachments && msg.attachments.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-2 border-t border-white/10">
                      {msg.attachments.map((att: any) => (
                        <a
                          key={att.id}
                          href={att.download_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-black/30 border border-white/15 hover:border-white/30 text-white text-[11px] font-mono transition-all"
                        >
                          {att.file_type?.startsWith("image/") ? (
                            <ImageIcon className="w-3 h-3 text-cyan-300" />
                          ) : (
                            <FileText className="w-3 h-3 text-amber-300" />
                          )}
                          <span className="truncate max-w-[140px]">{att.filename}</span>
                          <span className="opacity-60 text-[9px]">({(att.size_bytes / 1024).toFixed(0)}KB)</span>
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {/* Animated Agent Typing Indicator */}
          {isWaitingResponse && (
            <div className="flex items-start gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 border shadow-lg bg-amber-500/20 text-amber-300 border-amber-500/40">
                <Bot className="w-4 h-4 animate-spin" />
              </div>
              <div className="p-3.5 rounded-2xl max-w-lg bg-slate-900/90 border border-amber-500/30 text-slate-200 shadow-xl backdrop-blur-md">
                <div className="flex items-center gap-2 pb-1.5 border-b border-amber-500/20 text-xs font-bold text-amber-300">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                  </span>
                  <span>
                    Agen AI Korporat
                  </span>
                  <span className="text-[10px] font-normal text-amber-400/70 ml-auto">Sedang menganalisis...</span>
                </div>
                <div className="flex items-center gap-2 pt-2 text-xs text-slate-300">
                  <span className="italic">Merumuskan evaluasi bisnis & analisis strategi...</span>
                  <div className="flex items-center gap-1 pl-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce [animation-delay:-0.15s]"></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce"></span>
                  </div>
                </div>
              </div>
            </div>
          )}

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
        <form
          onSubmit={handleSendMessage}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`max-w-3xl mx-auto space-y-2 relative transition-all ${
            isDragging ? "scale-[1.01]" : ""
          }`}
        >
          {/* Drag & Drop Visual Dropzone Overlay */}
          {isDragging && (
            <div className="absolute inset-0 z-30 rounded-2xl bg-indigo-950/95 border-2 border-dashed border-cyan-400 flex items-center justify-center text-cyan-300 text-xs font-semibold backdrop-blur-md shadow-2xl animate-pulse pointer-events-none">
              <Paperclip className="w-4 h-4 mr-2 text-cyan-400 animate-bounce" />
              <span>Lepaskan berkas di sini untuk melampirkan ke Sparring Room (Gambar, PDF, Teks, Kode)...</span>
            </div>
          )}
          {/* Floating @mention Autocomplete Popover */}
          {mentionQuery !== null && (
            <div className="absolute bottom-full mb-3 left-0 right-0 z-40 max-h-60 overflow-y-auto rounded-2xl bg-[#0c0d14]/95 border border-cyan-500/40 shadow-2xl backdrop-blur-xl p-2 animate-in fade-in slide-in-from-bottom-2 duration-150">
              <div className="px-3 py-1.5 text-[10px] uppercase font-bold tracking-wider text-cyan-400 flex items-center justify-between border-b border-white/10 mb-1">
                <span className="flex items-center gap-1.5">
                  <Bot className="w-3 h-3 text-cyan-400" />
                  <span>Sebut Peran AI (@mention)</span>
                </span>
                <span className="text-slate-500 lowercase font-mono text-[9px]">Tekan Esc untuk menutup</span>
              </div>
              <div className="space-y-0.5">
                {/* Broadcast Option */}
                {("all".includes(mentionQuery.toLowerCase()) || "broadcast".includes(mentionQuery.toLowerCase()) || "executives".includes(mentionQuery.toLowerCase())) && (
                  <button
                    type="button"
                    onClick={() => insertMention("All Executives")}
                    className="w-full text-left px-3 py-2 rounded-xl flex items-center justify-between hover:bg-cyan-500/10 text-white transition-colors group"
                  >
                    <div className="flex items-center space-x-2.5">
                      <div className="w-7 h-7 rounded-lg bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 flex items-center justify-center text-xs font-bold">
                        📢
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-indigo-300 group-hover:text-white">@All Executives</div>
                        <div className="text-[10px] text-slate-400">Siarkan pesan ke seluruh dewan eksekutif</div>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono text-indigo-400/80">Broadcast</span>
                  </button>
                )}

                {/* Filtered Active Roles from DB */}
                {availableRoles
                  .filter((r) => r.name.toLowerCase().includes(mentionQuery.toLowerCase()))
                  .map((r) => (
                    <button
                      key={r.id}
                      type="button"
                      onClick={() => insertMention(r.name)}
                      className="w-full text-left px-3 py-2 rounded-xl flex items-center justify-between hover:bg-cyan-500/10 text-white transition-colors group"
                    >
                      <div className="flex items-center space-x-2.5">
                        <div className="w-7 h-7 rounded-lg bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 flex items-center justify-center text-xs font-bold">
                          <Bot className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-white group-hover:text-cyan-300">@{r.name}</div>
                          <div className="text-[10px] text-slate-400 line-clamp-1 max-w-[420px]">
                            {r.job_description || r.model_name}
                          </div>
                        </div>
                      </div>
                      <span className="text-[10px] font-mono text-cyan-400/70">{r.model_name.split("/").pop()}</span>
                    </button>
                  ))}
              </div>
            </div>
          )}

          {/* Attachment Chips Preview */}
          {attachments.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 px-1 pb-1">
              {attachments.map((att) => (
                <div
                  key={att.id}
                  className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs shadow-sm"
                >
                  {att.file_type.startsWith("image/") ? (
                    <ImageIcon className="w-3.5 h-3.5 text-cyan-400" />
                  ) : (
                    <FileText className="w-3.5 h-3.5 text-amber-400" />
                  )}
                  <span className="max-w-[140px] truncate">{att.filename}</span>
                  <button
                    type="button"
                    onClick={() => removeAttachment(att.id)}
                    className="text-slate-400 hover:text-rose-400 ml-1"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center space-x-2">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={handleFileChange}
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              title="Upload gambar, PDF, teks, atau kode sumber"
              className="p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors shrink-0"
            >
              {isUploading ? <Loader2 className="w-4 h-4 animate-spin text-indigo-400" /> : <Paperclip className="w-4 h-4" />}
            </button>
            <input
              ref={chatInputRef}
              type="text"
              value={chatInput}
              onChange={handleChatInputChange}
              onKeyDown={(e) => {
                if (e.key === "Escape") setMentionQuery(null);
              }}
              placeholder="Ketik pesan... (Gunakan @ untuk mention peran, misal: @Chief of Staff)"
              className="flex-1 px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500 transition-colors"
            />
            <button
              type="submit"
              disabled={isSending || (!chatInput.trim() && attachments.length === 0)}
              className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/25 disabled:opacity-50 transition-all hover:scale-105 active:scale-95 shrink-0"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
