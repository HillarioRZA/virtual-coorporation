/**
 * Custom React Hook untuk koneksi WebSocket Interactive Sandbox Terminal.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { TerminalMessage, TerminalStatus } from "../lib/types/sandbox";
import { getWsBase } from "../lib/config";

export interface TerminalLine {
  id: string;
  type: "stdout" | "stderr" | "system" | "prompt";
  text: string;
  timestamp: string;
}

export function useTerminalWebSocket(projectId: string) {
  const [status, setStatus] = useState<TerminalStatus>("connecting");
  const [lines, setLines] = useState<TerminalLine[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!projectId) return;

    const wsUrl = `${getWsBase()}/api/v1/sandbox/ws/terminal/${projectId}`;

    setStatus("connecting");
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus("connected");
    };

    ws.onmessage = (event) => {
      try {
        const msg: TerminalMessage = JSON.parse(event.data);
        const newLine: TerminalLine = {
          id: `${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
          type: (msg.type === "stdout" || msg.type === "stderr" || msg.type === "system")
            ? msg.type
            : "stdout",
          text: msg.data || (msg.command ? `$ ${msg.command}` : ""),
          timestamp: new Date().toLocaleTimeString(),
        };

        if (msg.type === "start") {
          setStatus("running");
        } else if (msg.type === "exit") {
          setStatus("connected");
        }

        if (newLine.text) {
          setLines((prev) => [...prev, newLine]);
        }
      } catch (err) {
        console.error("Gagal parse pesan terminal:", err);
      }
    };

    ws.onclose = () => {
      setStatus("disconnected");
    };

    ws.onerror = (err) => {
      console.warn("Terminal WS error:", err);
      setStatus("disconnected");
    };
  }, [projectId]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendCommand = useCallback((command: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    const cleanCmd = command.trim();
    if (!cleanCmd) return;

    setLines((prev) => [
      ...prev,
      {
        id: `${Date.now()}_prompt`,
        type: "prompt",
        text: `$ ${cleanCmd}`,
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);

    wsRef.current.send(JSON.stringify({ action: "exec", command: cleanCmd }));
  }, []);

  const clearOutput = useCallback(() => {
    setLines([]);
  }, []);

  return { status, lines, sendCommand, clearOutput, reconnect: connect };
}
