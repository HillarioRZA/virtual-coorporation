"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { getApiV1Base } from "../lib/config";
import { SSETokenPayload, SSEStateChangePayload, StageName } from "../lib/types/api";

const API_BASE = getApiV1Base();

export interface ChatMessage {
  id: string;
  sender: string;
  content: string;
  timestamp: string;
  isStreaming?: boolean;
  attachments?: any[];
}

export function useSSEStream(projectId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [agentStatus, setAgentStatus] = useState<string>("Standby");
  const [currentStage, setCurrentStage] = useState<StageName | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  const addLocalMessage = useCallback((sender: string, content: string, attachments?: any[]) => {
    const newMsg: ChatMessage = {
      id: `local_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
      sender: sender.toUpperCase(),
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      isStreaming: false,
      attachments,
    };
    setMessages((prev) => [...prev, newMsg]);
  }, []);

  useEffect(() => {
    if (!projectId) return;

    const token = typeof window !== "undefined" ? sessionStorage.getItem("venture_session_token") : null;
    const streamUrl = token
      ? `${API_BASE}/projects/${projectId}/stream?token=${encodeURIComponent(token)}`
      : `${API_BASE}/projects/${projectId}/stream`;
    const es = new EventSource(streamUrl);
    eventSourceRef.current = es;

    es.addEventListener("connected", () => {
      setIsConnected(true);
      setAgentStatus("Connected to Multi-Agent Hub");
    });

    es.addEventListener("sparring_token", (event: MessageEvent) => {
      try {
        const payload: SSETokenPayload = JSON.parse(event.data);
        const role = payload.sender_role.toUpperCase();

        setMessages((prev) => {
          // Jika pesan terakhir berasal dari agen yang sama dan masih streaming, append token
          const last = prev[prev.length - 1];
          if (last && last.sender === role && last.isStreaming) {
            const updated = [...prev];
            updated[updated.length - 1] = {
              ...last,
              content: last.content + payload.token,
            };
            return updated;
          }

          // Cegah duplikasi jika pesan berasal dari CEO yang sudah ditambahkan secara optimistik di UI
          if (role === "CEO" && last && last.sender === "CEO" && last.content.trim() === payload.token.trim()) {
            return prev;
          }

          // Buat entri chat baru jika pesan pertama
          return [
            ...prev,
            {
              id: `stream_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
              sender: role,
              content: payload.token,
              timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
              isStreaming: role !== "CEO",
            },
          ];
        });
      } catch (err) {
        console.error("Gagal parse SSE sparring_token:", err);
      }
    });

    es.addEventListener("agent_status", (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        setAgentStatus(data.status || "Thinking...");
      } catch {
        setAgentStatus(event.data);
      }
    });

    es.addEventListener("state_change", (event: MessageEvent) => {
      try {
        const payload: SSEStateChangePayload = JSON.parse(event.data);
        if (payload.to_stage) {
          setCurrentStage(payload.to_stage);
          setAgentStatus(`Transisi State: ${payload.to_stage}`);
        }
      } catch (err) {
        console.error("Gagal parse SSE state_change:", err);
      }
    });

    es.addEventListener("preview_ready", (event: MessageEvent) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.url) setPreviewUrl(payload.url);
      } catch (err) {
        console.error("Gagal parse SSE preview_ready:", err);
      }
    });

    es.addEventListener("done", () => {
      setMessages((prev) =>
        prev.map((m) => (m.isStreaming ? { ...m, isStreaming: false } : m))
      );
      setAgentStatus("Standby");
    });

    es.onerror = () => {
      setIsConnected(false);
      setAgentStatus("Reconnecting...");
    };

    return () => {
      es.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    };
  }, [projectId]);

  return {
    messages,
    agentStatus,
    currentStage,
    previewUrl,
    isConnected,
    addLocalMessage,
    setMessages,
    setCurrentStage,
  };
}
