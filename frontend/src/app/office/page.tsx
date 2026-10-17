"use client";

import Link from "next/link";
import { ArrowLeft, Building2, Radio, Sparkles } from "lucide-react";
import { useOfficeOasisState } from "../../components/office/useOfficeOasisState";
import { OfficeControlBar } from "../../components/office/OfficeControlBar";
import { AgentRosterSidebar } from "../../components/office/AgentRosterSidebar";
import { OfficeChatConsole } from "../../components/office/OfficeChatConsole";
import { OasisWorkspaceSplitView } from "../../components/office/oasis/OasisWorkspaceSplitView";
import { OasisAllHandsWarRoom } from "../../components/office/oasis/OasisAllHandsWarRoom";

export default function OfficeSimulatorPage() {
  const {
    projects,
    selectedProjectId,
    setSelectedProjectId,
    categoryFilter,
    setCategoryFilter,
    agents,
    selectedAgent,
    setSelectedAgent,
    streamEvents,
    allHandsActive,
    setAllHandsActive,
    replyContext,
    setReplyContext,
    connected,
    triggerInterrupt,
    handleHoldTicket,
    dispatchDirective,
  } = useOfficeOasisState("all");

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-61px)] overflow-hidden bg-[#090d16] text-slate-100 select-none">
      {/* Top Header Navbar */}
      <div className="border-b border-slate-800/80 bg-slate-950/90 px-5 py-2.5 flex items-center justify-between z-10 flex-shrink-0 backdrop-blur-xl">
        <div className="flex items-center space-x-3">
          <Link
            href="/"
            className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors border border-slate-800"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-500/20 to-cyan-500/20 border border-indigo-500/30 flex items-center justify-center text-cyan-400">
              <Building2 className="w-4 h-4" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                <span>Global Oasis Live Command HQ</span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
                  JoinOasis Engine • 120 FPS
                </span>
              </h1>
              <p className="text-[11px] text-slate-400 font-mono">
                Cross-Project Live Thoughts • Real-Time Handoffs • Instant Mid-Flight Interruption
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs px-2.5 py-1 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 font-mono flex items-center gap-1.5">
            <Radio className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
            <span>Oasis Event Bus</span>
          </span>
        </div>
      </div>

      {/* Main Workspace: Left Sidebar + Center Split Stream/Inspector + Bottom Console */}
      <div className="flex-1 flex overflow-hidden relative">
        <AgentRosterSidebar
          agents={agents}
          selectedAgent={selectedAgent}
          onSelectAgent={(agent) => setSelectedAgent(agent)}
        />

        <div className="flex-1 p-3 flex flex-col space-y-2.5 overflow-hidden bg-slate-950/40 relative">
          <OfficeControlBar
            connected={connected}
            projects={projects}
            selectedProjectId={selectedProjectId}
            onSelectProject={(pId) => setSelectedProjectId(pId)}
            categoryFilter={categoryFilter}
            onSelectCategory={(cat) => setCategoryFilter(cat)}
            onOpenAllHands={() => setAllHandsActive(true)}
          />

          {/* Oasis Live Stream and Live Screen-Share Split View */}
          <div className="flex-1 overflow-hidden relative">
            <OasisWorkspaceSplitView
              events={streamEvents}
              selectedProjectId={selectedProjectId}
              categoryFilter={categoryFilter}
              selectedAgent={selectedAgent}
              onSelectAgent={setSelectedAgent}
              onInterrupt={triggerInterrupt}
              onHold={handleHoldTicket}
            />
          </div>

          {/* Oasis Floating @Mention Console */}
          <div className="pt-1 flex-shrink-0">
            <OfficeChatConsole
              agents={agents}
              replyContext={replyContext}
              onClearReply={() => setReplyContext(null)}
              onSendDirective={dispatchDirective}
            />
          </div>
        </div>
      </div>

      {/* Executive War Room Modal */}
      <OasisAllHandsWarRoom
        isOpen={allHandsActive}
        onClose={() => setAllHandsActive(false)}
        onDispatchPlan={(plan) => dispatchDirective(["all"], plan)}
      />
    </div>
  );
}
