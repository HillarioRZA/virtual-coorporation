/**
 * Multi-Mode 3D Camera Controller: First-Person PoV, God-Mode Spectator & Orbit Helper.
 * Features Minecraft-like free-fly, Alt-hold cursor release, Tab mode toggling, and elevator carrying.
 */

import * as THREE from "three";
import { CameraViewMode } from "../core/Office3DTypes";
import { OfficeCollisionSystem } from "./OfficeCollisionSystem";
import { OfficePlayerPhysics } from "./OfficePlayerPhysics";

export class OfficeCameraController {
  public mode: CameraViewMode = "FIRST_PERSON";
  public camera: THREE.PerspectiveCamera;
  private domElement: HTMLElement;
  private physics = new OfficePlayerPhysics();
  private isOrbitDragging = false;
  private prevMouseX = 0;
  private prevMouseY = 0;
  public target = new THREE.Vector3(117, 1.8, 0);
  public currentTarget = new THREE.Vector3(117, 1.8, 0);
  private spherical = new THREE.Spherical(25, 1.3, 0.1);
  public fpPosition = new THREE.Vector3(117, 1.7, 0);
  public targetFloorY = 0;
  public isRidingElevator = false;
  private yaw = 0;
  private pitch = 0;
  private keys: { [key: string]: boolean } = {};
  public isPointerLocked = false;
  private isAltHeld = false;

  constructor(camera: THREE.PerspectiveCamera, domElement: HTMLElement) {
    this.camera = camera;
    this.domElement = domElement;
    this.setupListeners();
    this.setMode("FIRST_PERSON");
  }

  public setMode(newMode: CameraViewMode): void {
    this.mode = newMode;
    if (newMode === "FIRST_PERSON" || newMode === "GOD_MODE") {
      this.camera.position.copy(this.fpPosition);
      this.updateFirstPersonRotation();
      if (!this.isAltHeld) this.requestLock();
    } else {
      this.unlockPointer();
      this.updateOrbitCamera();
    }
  }

  public toggleFirstPersonGodMode(): void {
    const next = this.mode === "GOD_MODE" ? "FIRST_PERSON" : "GOD_MODE";
    this.setMode(next);
  }

  public jumpToFloor(fl: number): void {
    this.targetFloorY = (fl - 1) * 4.0;
    if (this.mode === "FIRST_PERSON" && !this.isRidingElevator) this.fpPosition.y = this.targetFloorY + 1.7;
  }

  public setElevatorRiding(riding: boolean, carY: number): void {
    this.isRidingElevator = riding;
    if (riding) {
      this.fpPosition.y = carY + 0.3;
      this.targetFloorY = Math.floor(carY / 4.0) * 4.0;
    }
  }

  private handleKeyDown = (e: KeyboardEvent): void => {
    this.keys[e.code] = true;
    if (e.code === "Tab") {
      e.preventDefault();
      this.toggleFirstPersonGodMode();
    } else if (e.code === "AltLeft" || e.code === "AltRight") {
      this.isAltHeld = true;
      this.unlockPointer();
    }
  };

  private handleKeyUp = (e: KeyboardEvent): void => {
    this.keys[e.code] = false;
    if (e.code === "AltLeft" || e.code === "AltRight") {
      this.isAltHeld = false;
      if (this.mode === "FIRST_PERSON" || this.mode === "GOD_MODE") this.requestLock();
    }
  };

  private handleMouseMove = (e: MouseEvent): void => {
    if (this.mode === "ORBIT" && this.isOrbitDragging) {
      this.spherical.theta -= (e.clientX - this.prevMouseX) * 0.005;
      this.spherical.phi = Math.max(0.1, Math.min(Math.PI / 2.05, this.spherical.phi - (e.clientY - this.prevMouseY) * 0.005));
      this.prevMouseX = e.clientX;
      this.prevMouseY = e.clientY;
      this.updateOrbitCamera();
    } else if ((this.mode === "FIRST_PERSON" || this.mode === "GOD_MODE") && this.isPointerLocked) {
      this.yaw -= e.movementX * 0.0022;
      this.pitch = Math.max(-1.45, Math.min(1.45, this.pitch - e.movementY * 0.0022));
      this.updateFirstPersonRotation();
    }
  };

  public update(delta: number): void {
    if (this.mode === "GOD_MODE") {
      const speed = (this.keys["ShiftLeft"] ? 35 : 18) * delta;
      const lookDir = new THREE.Vector3(0, 0, -1).applyEuler(new THREE.Euler(this.pitch, this.yaw, 0, "YXZ"));
      const rightDir = new THREE.Vector3(1, 0, 0).applyEuler(new THREE.Euler(0, this.yaw, 0, "YXZ"));
      if (this.keys["KeyW"]) this.fpPosition.addScaledVector(lookDir, speed);
      if (this.keys["KeyS"]) this.fpPosition.addScaledVector(lookDir, -speed);
      if (this.keys["KeyA"]) this.fpPosition.addScaledVector(rightDir, -speed);
      if (this.keys["KeyD"]) this.fpPosition.addScaledVector(rightDir, speed);
      if (this.keys["Space"] || this.keys["KeyE"]) this.fpPosition.y += speed;
      if (this.keys["KeyQ"] || this.keys["ControlLeft"]) this.fpPosition.y -= speed;
      this.camera.position.copy(this.fpPosition);
      this.updateFirstPersonRotation();
    } else if (this.mode === "FIRST_PERSON") {
      if (!this.isRidingElevator) {
        const curR = Math.hypot(this.fpPosition.x, this.fpPosition.z);
        if (curR < 97.5 || curR > 136.5) this.targetFloorY = 0;
        const res = this.physics.update(delta, this.keys, this.yaw, this.fpPosition, this.targetFloorY);
        this.fpPosition.copy(res.pos);
        this.camera.position.copy(this.fpPosition).add(res.bobOffset);
        if (Math.abs(this.camera.fov - res.targetFov) > 0.05) {
          this.camera.fov = res.targetFov;
          this.camera.updateProjectionMatrix();
        }
        this.camera.quaternion.setFromEuler(new THREE.Euler(this.pitch, this.yaw, res.rollTilt, "YXZ"));
      } else {
        this.camera.position.copy(this.fpPosition);
        this.updateFirstPersonRotation();
      }
    } else if (this.currentTarget.distanceTo(this.target) > 0.05) {
      this.currentTarget.lerp(this.target, 0.08);
      this.updateOrbitCamera();
    }
  }

  private updateFirstPersonRotation(): void {
    this.camera.quaternion.setFromEuler(new THREE.Euler(this.pitch, this.yaw, 0, "YXZ"));
  }

  public updateOrbitCamera(): void {
    this.camera.position.setFromSpherical(this.spherical).add(this.currentTarget);
    this.camera.lookAt(this.currentTarget);
  }

  public focusOn(pos: THREE.Vector3, radius: number = 55, phi?: number, theta?: number): void {
    this.target.copy(pos);
    this.spherical.radius = radius;
    if (phi !== undefined) this.spherical.phi = phi;
    if (theta !== undefined) this.spherical.theta = theta;
    if (this.mode === "ORBIT") this.targetFloorY = Math.floor(Math.max(0, pos.y) / 4.0) * 4.0;
  }

  private requestLock(): void {
    try {
      if (!this.isPointerLocked && this.domElement.isConnected) this.domElement.requestPointerLock?.();
    } catch {}
  }

  private unlockPointer(): void {
    try {
      if (document.pointerLockElement) document.exitPointerLock?.();
    } catch {}
  }

  private handleMouseUp = (): void => {
    this.isOrbitDragging = false;
  };

  private handlePointerLockChange = (): void => {
    this.isPointerLocked = document.pointerLockElement === this.domElement;
  };

  private setupListeners(): void {
    this.domElement.addEventListener("click", () => {
      if ((this.mode === "FIRST_PERSON" || this.mode === "GOD_MODE") && !this.isAltHeld) this.requestLock();
    });
    this.domElement.addEventListener("mousedown", (e) => {
      if (this.mode === "ORBIT") {
        this.isOrbitDragging = true;
        this.prevMouseX = e.clientX;
        this.prevMouseY = e.clientY;
      }
    });
    window.addEventListener("mouseup", this.handleMouseUp);
    window.addEventListener("mousemove", this.handleMouseMove);
    window.addEventListener("keydown", this.handleKeyDown);
    window.addEventListener("keyup", this.handleKeyUp);
    document.addEventListener("pointerlockchange", this.handlePointerLockChange);
  }

  public destroy(): void {
    window.removeEventListener("mousemove", this.handleMouseMove);
    window.removeEventListener("keydown", this.handleKeyDown);
    window.removeEventListener("keyup", this.handleKeyUp);
    window.removeEventListener("mouseup", this.handleMouseUp);
    document.removeEventListener("pointerlockchange", this.handlePointerLockChange);
    this.unlockPointer();
  }
}
