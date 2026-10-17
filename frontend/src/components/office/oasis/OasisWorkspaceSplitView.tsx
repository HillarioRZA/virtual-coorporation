"use client";

import { AgentSpatialData, OasisStreamCategory, OasisStreamEvent } from "../../../lib/types/office";
import { OasisLiveStreamFeed } from "./OasisLiveStreamFeed";
import { AgentLiveScreenSharePane } from "./AgentLiveScreenSharePane";

interface OasisWorkspaceSplitViewProps {
  events: OasisStreamEvent[];
  selectedProjectId: string;
  categoryFilter: OasisStreamCategory;
  selectedAgent: AgentSpatialData | null;
  onSelectAgent: (agent: AgentSpatialData | null) => void;
  onInterrupt: (roleId: string, ticketId?: string) => void;
  onHold: (ticketId: string) => void;
  onApproveGate?: (ticketId: string) => void;
}

export function OasisWorkspaceSplitView({
  events,
  selectedProjectId,
  categoryFilter,
  selectedAgent,
  onSelectAgent,
  onInterrupt,
  onHold,
  onApproveGate,
}: OasisWorkspaceSplitViewProps) {
  const handleWatchScreen = (roleId: string) => {
    // Find agent if not selected yet
    onInterrupt(roleId);
  };

  return (
    <div className="flex-1 flex flex-col lg:flex-row gap-3 overflow-hidden h-full relative">
      {/* Primary Oasis Multi-Agent Live Stream Feed */}
      <div className={`flex-1 h-full min-w-0 transition-all ${selectedAgent ? "lg:w-[52%]" : "w-full"}`}>
        <OasisLiveStreamFeed
          events={events}
          selectedProjectId={selectedProjectId}
          categoryFilter={categoryFilter}
          onInterrupt={onInterrupt}
          onHold={onHold}
          onWatchScreen={handleWatchScreen}
          onApproveGate={onApproveGate}
        />
      </div>

      {/* Right Split: Live Agent Screen-Share Pane */}
      {selectedAgent && (
        <AgentLiveScreenSharePane
          agent={selectedAgent}
          projectId={selectedProjectId}
          onClose={() => onSelectAgent(null)}
          onInterrupt={(rId) => onInterrupt(rId)}
        />
      )}
    </div>
  );
}
