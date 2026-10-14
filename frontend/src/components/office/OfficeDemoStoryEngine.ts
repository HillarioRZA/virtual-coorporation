/**
 * Autonomous Venture Story Engine for Corporate Office Simulator.
 * Orchestrates a 5-Act startup simulation cycle with realistic roles, tasks, and audio cues.
 */

import { AgentSpatialData } from "../../lib/types/office";
import { OfficeMeetingManager } from "./OfficeMeetingManager";

export interface StoryStepResult {
  agents: AgentSpatialData[];
  actTitle: string;
  soundType?: "TYPING" | "MEETING" | "APPROVAL";
}

export class OfficeDemoStoryEngine {
  public static executeStep(stepIndex: number, currentAgents: AgentSpatialData[]): StoryStepResult {
    const act = stepIndex % 5;

    switch (act) {
      case 0:
        return this.actMorningStandup(currentAgents);
      case 1:
        return this.actEngineeringSprint(currentAgents);
      case 2:
        return this.actCoffeeBreak(currentAgents);
      case 3:
        return this.actQASecurityScan(currentAgents);
      case 4:
        return this.actCEOApproval(currentAgents);
      default:
        return { agents: currentAgents, actTitle: "Office Operations" };
    }
  }

  private static actMorningStandup(agents: AgentSpatialData[]): StoryStepResult {
    const updated = agents.map((a) => {
      const seat = OfficeMeetingManager.getSeatForAgent(a.role_id, "ALL_HANDS");
      return {
        ...a,
        target_x: seat.x,
        target_y: seat.y,
        activity_state: "MEETING" as const,
        speech_bubble: seat.isSpeaker ? "📢 Sprint 3.6: Launching Autonomous Office Hub!" : "👂 Listening",
      };
    });
    return { agents: updated, actTitle: "Act 1: Morning All-Hands Standup", soundType: "MEETING" };
  }

  private static actEngineeringSprint(agents: AgentSpatialData[]): StoryStepResult {
    const updated = agents.map((a) => {
      const isDev = ["role_fe", "role_be", "role_qa", "role_devsecops"].includes(a.role_id);
      return {
        ...a,
        target_x: a.home_x ?? a.x,
        target_y: a.home_y ?? a.y,
        activity_state: isDev ? ("CODING" as const) : ("IDLE" as const),
        speech_bubble: isDev ? "💻 Compiling Canvas & WS State..." : undefined,
      };
    });
    return { agents: updated, actTitle: "Act 2: Active Engineering Sprint", soundType: "TYPING" };
  }

  private static actCoffeeBreak(agents: AgentSpatialData[]): StoryStepResult {
    const updated = agents.map((a) => {
      if (a.role_id === "role_copywriter" || a.role_id === "role_seo") {
        return {
          ...a,
          target_x: 600 + (a.role_id === "role_seo" ? 40 : -40),
          target_y: 640,
          activity_state: "WALKING" as const,
          speech_bubble: "☕ Discussing SEO growth over latte...",
        };
      }
      if (a.role_id === "role_cto") {
        return {
          ...a,
          target_x: 300,
          target_y: 385,
          activity_state: "WALKING" as const,
          speech_bubble: "🤝 Aligning API schema with Backend...",
        };
      }
      return a;
    });
    return { agents: updated, actTitle: "Act 3: Coffee Break & Cross-Pod Collab" };
  }

  private static actQASecurityScan(agents: AgentSpatialData[]): StoryStepResult {
    const updated = agents.map((a) => {
      if (a.role_id === "role_qa") {
        return {
          ...a,
          target_x: a.home_x ?? a.x,
          target_y: a.home_y ?? a.y,
          activity_state: "CODING" as const,
          speech_bubble: "🛡️ Running OWASP scan & 130 pytests... Passed!",
        };
      }
      if (a.role_id === "role_devsecops") {
        return {
          ...a,
          target_x: 1120,
          target_y: 650, // Server Room
          activity_state: "CODING" as const,
          speech_bubble: "🔒 Verifying Docker container bridge isolation...",
        };
      }
      return a;
    });
    return { agents: updated, actTitle: "Act 4: QA Security Audit & Sandboxing" };
  }

  private static actCEOApproval(agents: AgentSpatialData[]): StoryStepResult {
    const updated = agents.map((a) => {
      if (a.role_id === "role_founder") {
        return {
          ...a,
          target_x: a.home_x ?? a.x,
          target_y: a.home_y ?? a.y,
          activity_state: "MEETING" as const,
          speech_bubble: "🚀 Stage-Gate Approved: Deploy to Production!",
        };
      }
      return {
        ...a,
        activity_state: "IDLE" as const,
        speech_bubble: "🎉 Celebration!",
      };
    });
    return { agents: updated, actTitle: "Act 5: CEO Approval & Ship Code", soundType: "APPROVAL" };
  }
}
