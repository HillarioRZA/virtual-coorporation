/**
 * Autonomous Living Agent Routine & Circulation Engine.
 * Simulates lifelike corporate routines: desk work, Caffè Macs breaks, and team huddles.
 */

import * as THREE from "three";
import { OfficeAgentCoordinator } from "./OfficeAgentCoordinator";

export type AgentActivityType = "DESK_FOCUS" | "COFFEE_BREAK" | "TEAM_HUDDLE" | "ALL_HANDS" | "CORRIDOR_WALK";

export class OfficeAgentRoutineEngine {
  private static readonly CAFFE_MACS_POS = new THREE.Vector3(-98, 0, 0);
  private static readonly HUDDLE_FL1_POS = new THREE.Vector3(115.5, 0, -17.5);
  private static readonly SPRINT_FL2_POS = new THREE.Vector3(116.0, 4.0, 0);
  private static readonly BALCONY_FL4_POS = new THREE.Vector3(117.0, 12.0, 4.5);

  /**
   * Computes the dynamic target destination for an agent based on time and state.
   *
   * @param roleId Unique identifier for the agent role.
   * @param agentIndex Numeric index of the agent.
   * @param isAllHands Whether company-wide All-Hands meeting is summoned.
   * @param demoMode Whether autonomous wander demo mode is active.
   * @param timestamp Current elapsed time in milliseconds.
   * @returns 3D world target coordinate for the agent.
   */
  public static getDynamicAgentTarget(
    roleId: string,
    agentIndex: number,
    isAllHands: boolean,
    demoMode: boolean,
    timestamp: number
  ): { target: THREE.Vector3; activity: string } {
    // 1. High Priority: All-Hands Assembly at Steve Jobs Theater
    if (isAllHands) {
      return {
        target: OfficeAgentCoordinator.getAllHandsSeatPosition(agentIndex),
        activity: "Attending All-Hands Keynote",
      };
    }

    const deskPos = OfficeAgentCoordinator.getWorkstationPosition(roleId);

    // 2. Default Routine when Demo Mode is OFF: Focused Work at Assigned Desks
    if (!demoMode) {
      return { target: deskPos, activity: "Working at Assigned Workstation" };
    }

    // 3. Living Agent Autonomous Ecosystem Simulation (Cycles every 40 seconds)
    const cycleTime = 40000;
    const agentOffset = agentIndex * 3100;
    const progress = ((timestamp + agentOffset) % cycleTime) / cycleTime;

    // Phase 1: 0% - 60% -> Working at Workstation
    if (progress < 0.6) {
      return { target: deskPos, activity: "Product Deep Work & Sprint Coding" };
    }

    // Phase 2: 60% - 85% -> Inter-Departmental Collaboration or Coffee Run
    if (progress < 0.85) {
      if (roleId === "role_founder") {
        return { target: this.BALCONY_FL4_POS, activity: "Surveying Apple Park from Sky Balcony" };
      }
      if (roleId.startsWith("role_fe") || roleId.startsWith("role_qa")) {
        return { target: this.HUDDLE_FL1_POS, activity: "Collaborating at Breakout Huddle" };
      }
      if (roleId.startsWith("role_pm") || roleId.startsWith("role_ui_ux")) {
        return { target: this.SPRINT_FL2_POS, activity: "Brainstorming at Design Sprint Island" };
      }
      if (agentIndex % 3 === 0) {
        return { target: this.CAFFE_MACS_POS, activity: "Grabbing Espresso at Caffè Macs Atrium" };
      }
    }

    // Phase 3: 85% - 100% -> 360° Corridor Stroll along the Ring
    const angle = ((timestamp * 0.00015 + agentIndex) % (Math.PI * 2)) - Math.PI;
    const floorY = deskPos.y;
    const strollPos = new THREE.Vector3(Math.cos(angle) * 117.0, floorY, Math.sin(angle) * 117.0);

    return { target: strollPos, activity: "Strolling along 360° Ring Promenade" };
  }
}
