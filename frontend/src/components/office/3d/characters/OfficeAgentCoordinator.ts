/**
 * Spatial Coordinator for Agent Workstations & All-Hands Meeting Choreography.
 * Maps 13 corporate agent roles across 4 floors of The Grand Ring and Steve Jobs Theater.
 */

import * as THREE from "three";
import { TheaterKeynoteAuditorium } from "../rooms/TheaterKeynoteAuditorium";

export class OfficeAgentCoordinator {
  private static cachedTheaterSeats = TheaterKeynoteAuditorium.calculateAllHandsSeating();
  private static readonly R_RING = 117.0; // Mid-radius of The Grand Ring (R_in=98, R_out=136)

  /** Returns the canonical Apple Park 3D workstation coordinate for an agent role. */
  public static getWorkstationPosition(roleId: string): THREE.Vector3 {
    const r = this.R_RING;

    switch (roleId) {
      // Floor 1: Silicon Engineering Labs (Y = 0.0m)
      case "role_fe":
        return new THREE.Vector3(Math.cos(-0.8) * r, 0, Math.sin(-0.8) * r + 0.35);
      case "role_be":
        return new THREE.Vector3(Math.cos(-0.4) * r, 0, Math.sin(-0.4) * r + 0.35);
      case "role_qa":
        return new THREE.Vector3(Math.cos(0.4) * r, 0, Math.sin(0.4) * r + 0.35);
      case "role_devsecops":
        return new THREE.Vector3(Math.cos(0.8) * r, 0, Math.sin(0.8) * r + 0.35);

      // Floor 2: Product Strategy, UX Studio & Growth Pods (Y = 4.0m)
      case "role_pm":
        return new THREE.Vector3(Math.cos(-0.5) * r, 4.0, Math.sin(-0.5) * r + 0.35);
      case "role_growth":
        return new THREE.Vector3(Math.cos(-0.15) * r, 4.0, Math.sin(-0.15) * r + 0.35);
      case "role_ui_ux":
        return new THREE.Vector3(Math.cos(0.15) * r, 4.0, Math.sin(0.15) * r + 0.35);
      case "role_copywriter":
        return new THREE.Vector3(Math.cos(0.5) * r, 4.0, Math.sin(0.5) * r + 0.35);
      case "role_seo":
        return new THREE.Vector3(Math.cos(0.9) * r, 4.0, Math.sin(0.9) * r + 0.35);

      // Floor 3: Strategic Leadership & Boardroom (Y = 8.0m)
      case "role_cto":
        return new THREE.Vector3(Math.cos(-0.75) * r, 8.0, Math.sin(-0.75) * r + 0.35);
      case "role_cos":
        return new THREE.Vector3(Math.cos(-0.35) * r, 8.0, Math.sin(-0.35) * r + 0.35);
      case "role_cfo":
        return new THREE.Vector3(Math.cos(0.35) * r, 8.0, Math.sin(0.35) * r + 0.35);

      // Floor 4: Founder's Apex Omni-Panoramic Penthouse (Y = 12.0m)
      case "role_founder":
        return new THREE.Vector3(r, 12.0, -0.6);

      default:
        return new THREE.Vector3(r, 0, 0);
    }
  }

  /** Returns the subterranean Steve Jobs Theater seat for All-Hands meeting. */
  public static getAllHandsSeatPosition(agentIndex: number): THREE.Vector3 {
    const idx = Math.abs(agentIndex) % this.cachedTheaterSeats.length;
    const localPos = this.cachedTheaterSeats[idx].position;
    // Steve Jobs Theater is positioned at (40, 0, 230), subterranean basement Y = -8.0m
    return new THREE.Vector3(40 + localPos.x, -8.0 + localPos.y, 230 + localPos.z);
  }

  /** Returns target position depending on whether All-Hands gathering is active. */
  public static getTargetPosition(
    roleId: string,
    agentIndex: number,
    isAllHands: boolean
  ): THREE.Vector3 {
    if (isAllHands) {
      return this.getAllHandsSeatPosition(agentIndex);
    }
    return this.getWorkstationPosition(roleId);
  }
}
