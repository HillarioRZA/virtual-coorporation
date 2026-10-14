"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { LoungeMessage } from "@/lib/types/tickets";
import { getWsBase } from "@/lib/config";

export function useLoungeWebSocket(projectId: string) {
  const [messages, setMessages] = useState<LoungeMessage[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!projectId) return;

    const wsUrl = `${getWsBase()}/api/v1/corporate/ws/lounge/${projectId}`;

    try {
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          if (parsed.type === "HISTORY" && Array.isArray(parsed.messages)) {
            setMessages(parsed.messages);
          } else if (parsed.type === "MESSAGE" && parsed.data) {
            setMessages((prev) => [...prev, parsed.data]);
          }
        } catch (err) {
          console.error("Gagal parse pesan WebSocket Lounge:", err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Coba hubungkan kembali setelah 3 detik
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };

      ws.onerror = (err) => {
        console.error("WebSocket Lounge Error:", err);
        ws.close();
      };
    } catch (err) {
      console.error("Gagal menginisialisasi WebSocket Lounge:", err);
    }
  }, [projectId]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (socketRef.current) {
        socketRef.current.onclose = null; // Mencegah reconnect loop saat unmount
        socketRef.current.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback((content: string, senderRoleId: string = "CHAIRMAN") => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ content, sender_role_id: senderRoleId }));
    }
  }, []);

  return { messages, isConnected, sendMessage };
}
