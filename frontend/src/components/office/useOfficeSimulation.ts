"use client";

import { useEffect, useRef, useState } from "react";
import { CampusLayout, AgentSpatialData, ThemeId } from "../../lib/types/office";
import { fetchOfficeState, getOfficeWsUrl, stepOfficeDemo } from "../../lib/officeApi";
import { DEFAULT_CAMPUS_LAYOUT, DEFAULT_OFFICE_AGENTS } from "./officeConstants";
import { officeSound } from "./OfficeSoundManager";
import { OfficeMeetingManager } from "./OfficeMeetingManager";
import { OfficeDemoStoryEngine } from "./OfficeDemoStoryEngine";

export function useOfficeSimulation(projectId: string) {
  const [layout, setLayout] = useState<CampusLayout>(DEFAULT_CAMPUS_LAYOUT);
  const [agents, setAgents] = useState<AgentSpatialData[]>(DEFAULT_OFFICE_AGENTS);
  const [connected, setConnected] = useState<boolean>(false);
  const [demoMode, setDemoMode] = useState<boolean>(false);
  const [themeId, setThemeId] = useState<ThemeId>("cyberpunk");
  const [selectedBuilding, setSelectedBuilding] = useState<string>("all");
  const [activeFloor, setActiveFloor] = useState<number>(1);
  const [selectedAgent, setSelectedAgent] = useState<AgentSpatialData | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const agentsRef = useRef<AgentSpatialData[]>(DEFAULT_OFFICE_AGENTS);
  const storyStepRef = useRef<number>(0);

  // 1. Initial State Fetch with Fallback
  useEffect(() => {
    if (!projectId) return;
    const savedTheme = localStorage.getItem("office_theme") as ThemeId;
    if (savedTheme) setThemeId(savedTheme);

    fetchOfficeState(projectId)
      .then((data) => {
        if (data.layout) setLayout(data.layout);
        if (data.agents?.length) {
          setAgents(data.agents);
          agentsRef.current = data.agents;
        }
      })
      .catch(() => {
        setLayout(DEFAULT_CAMPUS_LAYOUT);
        setAgents(DEFAULT_OFFICE_AGENTS);
        agentsRef.current = DEFAULT_OFFICE_AGENTS;
      });
  }, [projectId]);

  // 2. WebSocket Connection
  useEffect(() => {
    if (!projectId) return;
    const wsUrl = getOfficeWsUrl(projectId);
    let ws: WebSocket;
    try {
      ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);
      ws.onclose = () => setConnected(false);
      ws.onerror = () => setConnected(false);
      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "OFFICE_UPDATE" && msg.agents) {
            setAgents(msg.agents);
            agentsRef.current = msg.agents;
          }
        } catch {}
      };
    } catch {
      setConnected(false);
    }
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, [projectId]);

  // 3. 60 FPS Game Loop
  useEffect(() => {
    let animId: number;
    const loop = () => {
      if (agentsRef.current.length > 0) {
        let changed = false;
        const updated = agentsRef.current.map((a) => {
          const dx = a.target_x - a.x;
          const dy = a.target_y - a.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist > 1.5) {
            changed = true;
            return { ...a, x: a.x + dx * 0.12, y: a.y + dy * 0.12 };
          }
          return a;
        });
        if (changed) {
          agentsRef.current = updated;
          setAgents(updated);
        }
      }
      animId = requestAnimationFrame(loop);
    };
    animId = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(animId);
  }, []);

  // 4. Autonomous 5-Act Demo Mode Story Engine
  useEffect(() => {
    if (!demoMode) return;
    const interval = setInterval(() => {
      const step = storyStepRef.current;
      const res = OfficeDemoStoryEngine.executeStep(step, agentsRef.current);
      storyStepRef.current += 1;
      agentsRef.current = res.agents;
      setAgents(res.agents);

      if (res.soundType === "TYPING") officeSound.playTypingSound(themeId === "kawaii");
      else if (res.soundType === "MEETING") officeSound.playMeetingChime();

      stepOfficeDemo().catch(() => {});
    }, 4500);
    return () => clearInterval(interval);
  }, [demoMode, themeId]);

  const callAllHandsMeeting = () => {
    setActiveFloor(1);
    setSelectedBuilding("apollo");
    const updated = agentsRef.current.map((a) => {
      const seat = OfficeMeetingManager.getSeatForAgent(a.role_id, "ALL_HANDS");
      return {
        ...a,
        target_x: seat.x,
        target_y: seat.y,
        activity_state: "MEETING" as const,
        speech_bubble: seat.isSpeaker ? "📢 All-Hands: Sprint Review" : "👂 Listening",
      };
    });
    agentsRef.current = updated;
    setAgents(updated);
    officeSound.playMeetingChime();
  };

  const dispatchDirective = (mentions: string[], message: string) => {
    if (mentions.includes("all")) {
      callAllHandsMeeting();
      return;
    }

    const updated = agentsRef.current.map((a) => {
      const isTargeted = mentions.includes(a.role_id) || mentions.includes(a.role_id.replace("role_", ""));
      if (isTargeted) {
        return {
          ...a,
          activity_state: "CODING" as const,
          speech_bubble: `💬 ${message.slice(0, 30)}...`,
          scratchpad: `Directive from Founder: ${message}`,
        };
      }
      return a;
    });
    agentsRef.current = updated;
    setAgents(updated);
    officeSound.playTypingSound(false);
  };

  return {
    layout,
    agents,
    connected,
    demoMode,
    setDemoMode,
    themeId,
    changeTheme: (t: ThemeId) => { setThemeId(t); localStorage.setItem("office_theme", t); },
    selectedBuilding,
    setSelectedBuilding,
    activeFloor,
    setActiveFloor,
    selectedAgent,
    setSelectedAgent,
    callAllHandsMeeting,
    dispatchDirective,
  };
}
