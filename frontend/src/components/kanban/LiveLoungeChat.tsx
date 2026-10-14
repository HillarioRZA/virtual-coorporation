"use client";

import React, { useState, useRef, useEffect } from "react";
import { MessageSquare, Send, Bot, Crown, Radio, Sparkles } from "lucide-react";
import { useLoungeWebSocket } from "@/hooks/useLoungeWebSocket";

interface LiveLoungeChatProps {
  projectId: string;
}

export default function LiveLoungeChat({ projectId }: LiveLoungeChatProps) {
  const { messages, isConnected, sendMessage } = useLoungeWebSocket(projectId);
  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    sendMessage(inputText.trim(), "CHAIRMAN");
    setInputText("");
  };

  return (
    <div className="rounded-2xl bg-white/[0.03] border border-white/10 flex flex-col h-[650px] shadow-2xl overflow-hidden backdrop-blur-xl">
      {/* Header Lounge */}
      <div className="p-3.5 border-b border-white/10 flex items-center justify-between bg-white/[0.02]">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <MessageSquare className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white tracking-tight flex items-center gap-1.5">
              <span>Agent Lounge</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-purple-500/20 text-purple-300 font-mono">
                Live
              </span>
            </h4>
            <p className="text-[10px] text-slate-400">Inter-agent communication stream</p>
          </div>
        </div>

        <div className="flex items-center space-x-1.5">
          <span
            className={`w-2 h-2 rounded-full ${
              isConnected ? "bg-emerald-400 animate-pulse" : "bg-rose-400"
            }`}
          />
          <span className="text-[10px] font-mono text-slate-400">
            {isConnected ? "Connected" : "Reconnecting"}
          </span>
        </div>
      </div>

      {/* Message Feed */}
      <div className="flex-1 p-3.5 overflow-y-auto space-y-3">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4">
            <Radio className="w-6 h-6 text-slate-600 mb-2 animate-pulse" />
            <p className="text-xs text-slate-500">Menunggu siaran percakapan atau tugas agen...</p>
          </div>
        ) : (
          messages.map((msg, idx) => {
            const isChairman = msg.sender_role_id === "CHAIRMAN";
            const isAlert = msg.event_type === "TEST_ALERT" || msg.event_type === "TASK_COMPLETED";

            return (
              <div
                key={idx}
                className={`p-2.5 rounded-xl border text-xs space-y-1 transition-all ${
                  isChairman
                    ? "bg-amber-500/10 border-amber-500/30 text-amber-100 ml-4"
                    : isAlert
                    ? "bg-purple-500/10 border-purple-500/30 text-purple-100"
                    : "bg-white/[0.03] border-white/5 text-slate-200 mr-4"
                }`}
              >
                <div className="flex items-center justify-between text-[10px] font-mono">
                  <div className="flex items-center space-x-1.5 font-bold">
                    {isChairman ? (
                      <>
                        <Crown className="w-3 h-3 text-amber-400" />
                        <span className="text-amber-300">CHAIRMAN (Founder)</span>
                      </>
                    ) : (
                      <>
                        <Bot className="w-3 h-3 text-cyan-400" />
                        <span className="text-cyan-300">{msg.sender_role_id}</span>
                      </>
                    )}
                    {msg.event_type !== "MESSAGE" && (
                      <span className="px-1.5 py-0.2 rounded bg-white/10 text-slate-400 text-[9px]">
                        {msg.event_type}
                      </span>
                    )}
                  </div>
                  <span className="text-slate-500 text-[9px]">
                    {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ""}
                  </span>
                </div>

                <p className="text-xs leading-relaxed font-sans">{msg.content}</p>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Founder Input Box */}
      <form onSubmit={handleSend} className="p-2.5 border-t border-white/10 bg-white/[0.02] flex items-center gap-2">
        <input
          type="text"
          placeholder="Kirim instruksi langsung ke Lounge sebagai Chairman..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          className="flex-1 px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-amber-500/50"
        />
        <button
          type="submit"
          disabled={!inputText.trim()}
          className="p-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-black font-semibold transition-all disabled:opacity-30"
          title="Kirim instruksi Chairman"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}
