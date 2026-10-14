/**
 * Sovereign AI Multi-Building Corporate Campus 3D World Simulator.
 * Interactive 3D Cyber-Voxel WebGL campus with First-Person Founder Walk, Orbit cam, and Device Gatekeeper.
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Building2, Radio } from "lucide-react";
import { useOfficeSimulation } from "../../components/office/useOfficeSimulation";
import { Office3DCanvas } from "../../components/office/3d/Office3DCanvas";
import { DeviceGatekeeper } from "../../components/office/DeviceGatekeeper";
import { OfficeControlBar } from "../../components/office/OfficeControlBar";
import { AgentRosterSidebar } from "../../components/office/AgentRosterSidebar";
import { OfficeChatConsole } from "../../components/office/OfficeChatConsole";
import { AgentTerminalDrawer } from "../../components/office/AgentTerminalDrawer";

export default function OfficeSimulatorPage() {
  const [projectId] = useState<string>("default_venture");

  const {
    agents,
    connected,
    demoMode,
    setDemoMode,
    selectedBuilding,
    setSelectedBuilding,
    activeFloor,
    setActiveFloor,
    selectedAgent,
    setSelectedAgent,
    callAllHandsMeeting,
    dispatchDirective,
  } = useOfficeSimulation(projectId);

  return (
    <DeviceGatekeeper>
      <div className="flex-1 flex flex-col h-[calc(100vh-61px)] overflow-hidden bg-slate-950 text-slate-100">
        {/* Top Header Navbar */}
        <div className="border-b border-slate-800 bg-slate-950 px-5 py-2 flex items-center justify-between z-10 flex-shrink-0">
          <div className="flex items-center space-x-3">
            <Link
              href="/"
              className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div className="flex items-center space-x-2">
              <Building2 className="w-5 h-5 text-indigo-400" />
              <div>
                <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                  <span>3D Cyber-Voxel Tech Mega-Campus</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    WebGL 60 FPS • Apollo • Da Vinci • Olympus
                  </span>
                </h2>
                <p className="text-xs text-slate-400 font-mono">
                  Procedural Voxels • Dual Camera (Orbit / WASD First-Person) • RTX Lighting
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 font-mono flex items-center gap-1.5">
              <Radio className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
              <span>3D Spatial WebGL Bus</span>
            </span>
          </div>
        </div>

        {/* Main Workspace */}
        <div className="flex-1 flex overflow-hidden relative">
          <AgentRosterSidebar
            agents={agents}
            selectedAgent={selectedAgent}
            onSelectAgent={(agent) => setSelectedAgent(agent)}
            demoMode={demoMode}
          />

          <div className="flex-1 p-3 flex flex-col space-y-2 overflow-hidden bg-slate-900/30 relative">
            <OfficeControlBar
              connected={connected}
              demoMode={demoMode}
              setDemoMode={setDemoMode}
              selectedBuilding={selectedBuilding}
              setSelectedBuilding={setSelectedBuilding}
              activeFloor={activeFloor}
              setActiveFloor={setActiveFloor}
              callAllHandsMeeting={callAllHandsMeeting}
            />

            {/* 3D WebGL Three.js Viewport */}
            <div className="flex-1 rounded-2xl border border-slate-800 shadow-2xl overflow-hidden relative bg-slate-950">
              <Office3DCanvas
                agents={agents}
                selectedBuilding={selectedBuilding}
                activeFloor={activeFloor}
                selectedAgent={selectedAgent}
                onSelectAgent={(agent) => setSelectedAgent(agent)}
                demoMode={demoMode}
              />

              {/* Oasis @Mention Multi-Agent Command Console */}
              <div className="absolute bottom-4 left-6 right-6 z-10 pointer-events-auto">
                <OfficeChatConsole agents={agents} onSendDirective={dispatchDirective} />
              </div>
            </div>
          </div>

          {/* Live Terminal & Scratchpad Drawer */}
          <AgentTerminalDrawer
            agent={selectedAgent}
            onClose={() => setSelectedAgent(null)}
            onIntervene={(instruction) => {
              if (selectedAgent) dispatchDirective([selectedAgent.role_id], instruction);
            }}
          />
        </div>
      </div>
    </DeviceGatekeeper>
  );
}
