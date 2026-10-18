/**
 * TypeScript Contracts for Global Oasis Live Command HQ.
 * Strictly typed interfaces for multi-agent live streams, handoffs, and 2D agent roster.
 */

export type SpatialTier = "EXECUTIVE" | "LEAD_MANAGEMENT" | "WORKER_SPECIALIST" | "COMMONS";

export type AgentActivityState = "IDLE" | "CODING" | "REVIEWING" | "WALKING" | "MEETING" | "BLOCKED";

export type OasisStreamCategory = "ALL" | "EXECUTION" | "GATES" | "LOUNGE";

export interface OasisHandoff {
  fromRoleId: string;
  toRoleId: string;
  summary: string;
}

export interface OasisStreamEvent {
  id: string | number;
  projectId: string;
  projectName?: string;
  senderRoleId: string;
  recipientRoleId?: string | null;
  ticketId?: string | null;
  eventType: string;
  content: string;
  category: OasisStreamCategory;
  timestamp: string;
  tokenCost?: number;
  handoff?: OasisHandoff;
  gateStatus?: "WAITING_APPROVAL" | "APPROVED" | "REVISED" | "REJECTED";
}

export interface AgentSpatialData {
  role_id: string;
  name: string;
  tier: SpatialTier;
  activity_state: AgentActivityState;
  color?: string;
  active_file?: string;
  scratchpad?: string;
  speech_bubble?: string;
}

export interface OfficeDirectivePayload {
  projectId: string;
  mentions: string[];
  instruction: string;
  ticketId?: string;
}
