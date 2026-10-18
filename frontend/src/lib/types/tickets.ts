/**
 * TypeScript Contracts untuk Virtual Kanban Board & Live Lounge.
 */

export type TicketStatus = "BACKLOG" | "TODO" | "IN_PROGRESS" | "REVIEW" | "DONE";
export type TicketPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type ProductLine = "SOFTWARE" | "EDUCATION" | "COPYWRITING" | "RESEARCH";

export interface TicketResponse {
  id: string;
  branch_id: string;
  project_id: string;
  division_id: string;
  assigned_role_id?: string | null;
  title: string;
  description: string;
  product_line: ProductLine;
  priority: TicketPriority;
  status: TicketStatus;
  artifact_refs: string[];
  dependencies: string[];
  parent_ticket_id?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface TicketCreate {
  branch_id: string;
  project_id: string;
  division_id: string;
  title: string;
  description: string;
  product_line?: ProductLine;
  priority?: TicketPriority;
  assigned_role_id?: string | null;
  dependencies?: string[];
  parent_ticket_id?: string | null;
}

export interface TicketUpdate {
  title?: string;
  description?: string;
  assigned_role_id?: string | null;
  priority?: TicketPriority;
  status?: TicketStatus;
  artifact_refs?: string[];
  dependencies?: string[];
}

export interface LoungeMessage {
  id: number;
  branch_id: string;
  project_id: string;
  channel_type: string;
  sender_role_id: string;
  recipient_role_id?: string | null;
  ticket_id?: string | null;
  event_type: string;
  content: string;
  token_cost?: number;
  created_at: string;
}
