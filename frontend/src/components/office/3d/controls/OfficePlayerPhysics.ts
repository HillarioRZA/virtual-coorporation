/**
 * AAA First-Person Player Physics & Motion Immersion Engine.
 * Implements smooth acceleration/deceleration, head-bobbing, strafe camera banking,
 * dynamic sprint FoV zoom, and grounded jump gravity.
 */

import * as THREE from "three";
import { OfficeProceduralAudio } from "../environment/OfficeProceduralAudio";
import { OfficeCollisionSystem } from "./OfficeCollisionSystem";
import { OfficeTerrainElevation } from "../environment/OfficeTerrainElevation";

export interface PhysicsStepResult {
  pos: THREE.Vector3;
  bobOffset: THREE.Vector3;
  rollTilt: number;
  targetFov: number;
  isMoving: boolean;
}

export class OfficePlayerPhysics {
  private velocity = new THREE.Vector3();
  private verticalVelocity = 0;
  private isGrounded = true;
  private headBobTimer = 0;
  private currentRoll = 0;
  private currentFov = 72;
  private prevBobY = 0;

  private static readonly WALK_SPEED = 7.5;
  private static readonly SPRINT_SPEED = 13.0;
  private static readonly ACCEL = 40.0;
  private static readonly FRICTION = 11.0;
  private static readonly JUMP_VELOCITY = 4.8;
  private static readonly GRAVITY = 15.0;

  /**
   * Updates player movement physics, momentum, and cinematic headbobbing.
   */
  public update(
    delta: number,
    keys: Record<string, boolean>,
    yaw: number,
    currentPos: THREE.Vector3,
    targetFloorY: number
  ): PhysicsStepResult {
    const isSprint = !!keys["ShiftLeft"] && (!!keys["KeyW"] || !!keys["KeyS"] || !!keys["KeyA"] || !!keys["KeyD"]);
    const maxSpeed = isSprint ? OfficePlayerPhysics.SPRINT_SPEED : OfficePlayerPhysics.WALK_SPEED;

    // 1. Calculate Target Input Direction
    const fwd = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw)).normalize();
    const right = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw)).normalize();

    const inputDir = new THREE.Vector3();
    let strafeInput = 0;
    if (keys["KeyW"]) inputDir.add(fwd);
    if (keys["KeyS"]) inputDir.addScaledVector(fwd, -1);
    if (keys["KeyA"]) { inputDir.addScaledVector(right, -1); strafeInput -= 1; }
    if (keys["KeyD"]) { inputDir.add(right); strafeInput += 1; }

    const isMoving = inputDir.lengthSq() > 0.001;
    if (isMoving) inputDir.normalize();

    // 2. Smooth Inertial Acceleration & Friction
    const targetVel = inputDir.clone().multiplyScalar(isMoving ? maxSpeed : 0);
    this.velocity.lerp(targetVel, Math.min(1.0, delta * (isMoving ? OfficePlayerPhysics.ACCEL : OfficePlayerPhysics.FRICTION)));

    // 3. Jump & Vertical Gravity Physics
    const elev = OfficeTerrainElevation.getElevationAt(currentPos.x, currentPos.z);
    const baseGroundY = (targetFloorY > 0 ? targetFloorY : elev) + 1.7;
    if (keys["Space"] && this.isGrounded) {
      this.verticalVelocity = OfficePlayerPhysics.JUMP_VELOCITY;
      this.isGrounded = false;
    }

    let nextY = currentPos.y + this.verticalVelocity * delta;
    if (!this.isGrounded) {
      this.verticalVelocity -= OfficePlayerPhysics.GRAVITY * delta;
      if (nextY <= baseGroundY) {
        nextY = baseGroundY;
        this.verticalVelocity = 0;
        this.isGrounded = true;
      }
    } else {
      nextY = THREE.MathUtils.lerp(currentPos.y, baseGroundY, 0.22);
    }

    // 4. Resolve Horizontal Position with Concentric Campus Collision
    const desiredPos = currentPos.clone().addScaledVector(this.velocity, delta);
    desiredPos.y = nextY;
    const resolved = OfficeCollisionSystem.resolveMovement(currentPos, desiredPos, targetFloorY);
    resolved.y = nextY;

    // 5. Dynamic Head-Bobbing & Audio Footstep Rhythm
    const speed = this.velocity.length();
    const bobOffset = new THREE.Vector3();

    if (this.isGrounded && speed > 0.5) {
      const bobFreq = isSprint ? 14.0 : 10.5;
      this.headBobTimer += delta * bobFreq;

      const bobAmpY = isSprint ? 0.055 : 0.035;
      const bobAmpX = isSprint ? 0.028 : 0.016;

      const bobY = Math.sin(this.headBobTimer) * bobAmpY;
      const bobX = Math.cos(this.headBobTimer * 0.5) * bobAmpX;
      bobOffset.set(bobX, bobY, 0);

      // Footstep sound trigger at bottom trough of cycle
      if (bobY < -bobAmpY * 0.75 && this.prevBobY >= -bobAmpY * 0.75) {
        const surface = OfficeProceduralAudio.detectSurface(resolved.x, resolved.z, targetFloorY);
        OfficeProceduralAudio.playFootstep(surface, isSprint);
      }
      this.prevBobY = bobY;
    } else {
      this.headBobTimer = 0;
      this.prevBobY = 0;
    }

    // 6. Strafe Banking Roll Tilt & Sprint FoV
    const targetRoll = -strafeInput * (isSprint ? 0.032 : 0.022);
    this.currentRoll = THREE.MathUtils.lerp(this.currentRoll, targetRoll, delta * 9.0);

    const targetFov = isSprint && speed > 2.0 ? 81.0 : 72.0;
    this.currentFov = THREE.MathUtils.lerp(this.currentFov, targetFov, delta * 6.0);

    return {
      pos: resolved,
      bobOffset,
      rollTilt: this.currentRoll,
      targetFov: this.currentFov,
      isMoving: speed > 0.3,
    };
  }
}
