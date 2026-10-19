"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { fetchProjects } from "../../lib/api";
import { ProjectSummary } from "../../lib/types/api";
import { AgentSpatialData, OasisStreamCategory, OasisStreamEvent } from "../../lib/types/office";
import { DEFAULT_OFFICE_AGENTS } from "./officeConstants";
import { getOfficeWsUrl, dispatchOfficeDirective, holdOfficeTicket } from "../../lib/officeApi";

export function useOfficeOasisState(initialProjectId = "all") {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>(initialProjectId);
  const [categoryFilter, setCategoryFilter] = useState<OasisStreamCategory>("ALL");
  const [agents, setAgents] = useState<AgentSpatialData[]>(DEFAULT_OFFICE_AGENTS);
  const [selectedAgent, setSelectedAgent] = useState<AgentSpatialData | null>(null);
  const [streamEvents, setStreamEvents] = useState<OasisStreamEvent[]>([]);
  const [allHandsActive, setAllHandsActive] = useState<boolean>(false);
  const [replyContext, setReplyContext] = useState<{ roleId: string; ticketId?: string } | null>(null);
  const [connected, setConnected] = useState<boolean>(false);

  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetchProjects().then((res) => { if (res?.length) setProjects(res); }).catch(() => {});
  }, []);

  useEffect(() => {
    const targetProj = selectedProjectId === "all" ? (projects[0]?.project_id || "default_venture") : selectedProjectId;
    try {
      const ws = new WebSocket(getOfficeWsUrl(targetProj));
      wsRef.current = ws;
      ws.onopen = () => setConnected(true);
      ws.onclose = () => setConnected(false);
      ws.onerror = () => setConnected(false);
      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data);
          if (msg.type === "OFFICE_UPDATE") {
            if (msg.agents) setAgents(msg.agents);
            if (msg.stream_event && msg.stream_event.content) {
              setStreamEvents((prev) => {
                const se = msg.stream_event;
                if (prev.some((p) => p.content === se.content && p.senderRoleId === se.senderRoleId)) {
                  return prev;
                }
                const formatted = {
                  ...se,
                  timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                };
                return [formatted, ...prev];
              });
            }
          }
        } catch {}
      };
    } catch { setConnected(false); }
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, [selectedProjectId, projects]);

  const triggerInterrupt = useCallback((roleId: string, ticketId?: string) => {
    setReplyContext({ roleId, ticketId });
    const target = agents.find((a) => a.role_id === roleId);
    if (target) setSelectedAgent(target);
  }, [agents]);

  const handleHoldTicket = useCallback(async (ticketId: string) => {
    const proj = selectedProjectId === "all" ? (projects[0]?.project_id || "default_venture") : selectedProjectId;
    await holdOfficeTicket(proj, ticketId);
    setStreamEvents((prev) => [{ id: `hold_${Date.now()}`, projectId: proj, senderRoleId: "role_founder", ticketId, eventType: "CIRCUIT_BREAKER", content: `Tiket ${ticketId} di-HOLD oleh Founder. Token dihentikan.`, category: "GATES", timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }, ...prev]);
  }, [selectedProjectId, projects]);

  const dispatchDirective = useCallback(async (mentions: string[], message: string) => {
    if (mentions.includes("all")) { setAllHandsActive(true); return; }
    const proj = selectedProjectId === "all" ? (projects[0]?.project_id || "default_venture") : selectedProjectId;
    setStreamEvents((prev) => [{ id: `dir_${Date.now()}`, projectId: proj, senderRoleId: "role_founder", recipientRoleId: mentions[0], ticketId: replyContext?.ticketId, eventType: "DIRECTIVE", content: `Instruksi Founder ke ${mentions.join(", ")}: "${message}"`, category: "EXECUTION", timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }, ...prev]);
    setAgents((prev) => prev.map((a) => mentions.includes(a.role_id) ? { ...a, activity_state: "CONSULTING", speech_bubble: "🤔 Menelaah arahan..." } : a));
    await dispatchOfficeDirective({ projectId: proj, mentions, instruction: message, ticketId: replyContext?.ticketId });
    setReplyContext(null);
  }, [selectedProjectId, projects, replyContext]);

  return { projects, selectedProjectId, setSelectedProjectId, categoryFilter, setCategoryFilter, agents, selectedAgent, setSelectedAgent, streamEvents, allHandsActive, setAllHandsActive, replyContext, setReplyContext, connected, triggerInterrupt, handleHoldTicket, dispatchDirective };
}
