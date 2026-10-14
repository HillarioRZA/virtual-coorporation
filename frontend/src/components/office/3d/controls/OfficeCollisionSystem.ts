/**
 * 360-Degree Spatial Collision Detection & Resolution Engine for Apple Park Mega-Campus.
 * Smooth concentric boundaries (R_in=98m, R_out=136m), portals, 5x satellite colliders, and pools.
 */

import * as THREE from "three";
import { OfficeAutomaticDoors } from "../buildings/OfficeAutomaticDoors";

export interface CircleCollider {
  x: number;
  z: number;
  radius: number;
}

export class OfficeCollisionSystem {
  private static readonly PLAYER_RADIUS = 0.5;
  private static readonly R_IN = 98.0;
  private static readonly R_OUT = 136.0;

  // Solid Circular Colliders: Pool Basin & Satellite Pavilion Cores
  private static circles: CircleCollider[] = [
    { x: 0, z: 0, radius: 24.5 },         // Central Reflection Pool Basin (24.5m)
    { x: 40, z: 230, radius: 25.2 },      // Steve Jobs Theater 5x Core
  ];

  /** Adds a tree trunk circular collider dynamically. */
  public static addTreeCollider(x: number, z: number, r: number = 0.6): void {
    this.circles.push({ x, z, radius: r });
  }

  /** Clears dynamic tree colliders upon hot reload. */
  public static resetTreeColliders(): void {
    this.circles = this.circles.slice(0, 2);
  }

  /**
   * Resolves player movement against all Apple Park structures and 360 ring boundaries.
   * Slides player smoothly along curves preventing ghost noclip penetration.
   */
  public static resolveMovement(
    currentPos: THREE.Vector3,
    desiredPos: THREE.Vector3,
    floorLevel: number = 0
  ): THREE.Vector3 {
    const resolved = desiredPos.clone();
    const pr = this.PLAYER_RADIUS;

    // 1. Resolve Against Circular Colliders (Reflection Pool, Trees, Theater)
    for (const c of this.circles) {
      const dx = resolved.x - c.x;
      const dz = resolved.z - c.z;
      const dist = Math.hypot(dx, dz);

      // Steve Jobs Theater at (40, 230) with entrance portal on North side
      if (c.x === 40 && c.z === 230) {
        const curDist = Math.hypot(currentPos.x - c.x, currentPos.z - c.z);
        const isDoorway = dz < 0 && Math.abs(dx) < 4.2 && OfficeAutomaticDoors.isDoorOpen("theater_north");

        // Central Glass Elevator Core obstacle
        if (dist < 4.8 + pr) {
          const pushX = (dx / (dist || 1)) * (4.8 + pr);
          const pushZ = (dz / (dist || 1)) * (4.8 + pr);
          resolved.x = c.x + pushX;
          resolved.z = c.z + pushZ;
          continue;
        }

        // Glass cylinder boundary
        if (curDist >= c.radius && dist < c.radius + pr && !isDoorway) {
          resolved.x = c.x + (dx / dist) * (c.radius + pr);
          resolved.z = c.z + (dz / dist) * (c.radius + pr);
        } else if (curDist < c.radius && dist > c.radius - pr && !isDoorway) {
          resolved.x = c.x + (dx / dist) * (c.radius - pr);
          resolved.z = c.z + (dz / dist) * (c.radius - pr);
        }
        continue;
      }

      // Standard solid circular obstacles
      const minDist = c.radius + pr;
      if (dist < minDist && dist > 0.001) {
        resolved.x = c.x + (dx / dist) * minDist;
        resolved.z = c.z + (dz / dist) * minDist;
      }
    }

    // 2. Resolve Against Tantau SecOps Cube at (60, -230) size 52m x 36m
    const minX = 34, maxX = 86, minZ = -248, maxZ = -212;
    if (
      resolved.x + pr > minX &&
      resolved.x - pr < maxX &&
      resolved.z + pr > minZ &&
      resolved.z - pr < maxZ
    ) {
      // Airlock doorway portal at front: |x - 60| < 4.2, z = maxZ
      const inAirlock =
        Math.abs(resolved.x - 60) < 4.2 &&
        Math.abs(resolved.z - maxZ) < 3.0 &&
        OfficeAutomaticDoors.isDoorOpen("tantau_south");

      if (!inAirlock) {
        const dL = Math.abs(resolved.x + pr - minX);
        const dR = Math.abs(maxX - (resolved.x - pr));
        const dB = Math.abs(resolved.z + pr - minZ);
        const dT = Math.abs(maxZ - (resolved.z - pr));
        const minEdge = Math.min(dL, dR, dB, dT);
        if (minEdge === dL) resolved.x = minX - pr;
        else if (minEdge === dR) resolved.x = maxX + pr;
        else if (minEdge === dB) resolved.z = minZ - pr;
        else resolved.z = maxZ + pr;
      }
    }

    // 3. Resolve Against The Grand Ring 360-Degree Concentric Walls
    const curR = Math.hypot(currentPos.x, currentPos.z);
    const newR = Math.hypot(resolved.x, resolved.z);
    const angle = Math.atan2(resolved.z, resolved.x);

    // Doorway portals into The Ring (Ground Floor Only, synced to sliding doors)
    const isGround = Math.abs(floorLevel) <= 0.8;
    const isEastPortal =
      isGround && Math.abs(angle) < 0.045 && resolved.x > 0 && OfficeAutomaticDoors.isDoorOpen("ring_east");
    const isWestPortal =
      isGround && Math.abs(Math.abs(angle) - Math.PI) < 0.055 && OfficeAutomaticDoors.isDoorOpen("ring_west");
    const inDoorway = isEastPortal || isWestPortal;

    // A. Inner Ring Wall (R = 98.0m)
    if (!inDoorway) {
      if (curR < this.R_IN && newR >= this.R_IN - pr) {
        resolved.x = (resolved.x / newR) * (this.R_IN - pr);
        resolved.z = (resolved.z / newR) * (this.R_IN - pr);
      } else if (curR >= this.R_IN && curR <= this.R_OUT && newR <= this.R_IN + pr) {
        resolved.x = (resolved.x / newR) * (this.R_IN + pr);
        resolved.z = (resolved.z / newR) * (this.R_IN + pr);
      }
    }

    // B. Outer Ring Wall (R = 136.0m)
    if (curR <= this.R_OUT && newR >= this.R_OUT - pr) {
      resolved.x = (resolved.x / newR) * (this.R_OUT - pr);
      resolved.z = (resolved.z / newR) * (this.R_OUT - pr);
    } else if (curR > this.R_OUT && newR <= this.R_OUT + pr) {
      resolved.x = (resolved.x / newR) * (this.R_OUT + pr);
      resolved.z = (resolved.z / newR) * (this.R_OUT + pr);
    }

    return resolved;
  }
}
