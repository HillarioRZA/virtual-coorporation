/**
 * Interactive Glass Elevator Manager for 4-Story The Grand Ring.
 * Controls vertical lift movement, car animation, floor summoning, and player carrying.
 */

import * as THREE from "three";
import { OfficeCameraController } from "../controls/OfficeCameraController";

export class OfficeElevatorManager {
  private static readonly SHAFT_POS = new THREE.Vector3(117.0, 0, 0);
  private static readonly FLOOR_HEIGHTS: { [floor: number]: number } = {
    1: 1.4,
    2: 5.4,
    3: 9.4,
    4: 13.4,
  };

  private carMesh: THREE.Object3D | null = null;
  public currentFloor = 1;
  public targetFloor = 1;
  public carY = 1.4;
  public isMoving = false;
  public isNearElevator = false;
  public isPlayerInside = false;
  public isMenuOpen = false;
  private moveSpeed = 4.2; // meters per second

  constructor(scene: THREE.Scene) {
    this.findCarMesh(scene);
    this.setupKeyboardListeners();
  }

  public findCarMesh(scene: THREE.Scene): void {
    scene.traverse((obj) => {
      if (obj.name === "ElevatorCar_Ring") {
        this.carMesh = obj;
        this.carY = obj.position.y;
      }
    });
  }

  public callElevator(floor: number): void {
    if (floor < 1 || floor > 4) return;
    this.targetFloor = floor;
    this.isMoving = true;
    this.isMenuOpen = false;
  }

  public toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
  }

  private handleKeyDown = (e: KeyboardEvent): void => {
    if (!this.isNearElevator) return;
    if (e.code === "KeyF") {
      e.preventDefault();
      this.toggleMenu();
    } else if (this.isMenuOpen || this.isPlayerInside) {
      if (e.code === "Digit1" || e.code === "Numpad1") this.callElevator(1);
      if (e.code === "Digit2" || e.code === "Numpad2") this.callElevator(2);
      if (e.code === "Digit3" || e.code === "Numpad3") this.callElevator(3);
      if (e.code === "Digit4" || e.code === "Numpad4") this.callElevator(4);
      if (e.code === "Escape") this.isMenuOpen = false;
    }
  };

  private setupKeyboardListeners(): void {
    window.addEventListener("keydown", this.handleKeyDown);
  }

  public destroy(): void {
    window.removeEventListener("keydown", this.handleKeyDown);
  }

  /** Updates elevator car physics and smoothly carries player across floors without falling. */
  public update(delta: number, cameraCtrl?: OfficeCameraController): boolean {
    const targetY = OfficeElevatorManager.FLOOR_HEIGHTS[this.targetFloor] ?? 1.4;
    const diff = targetY - this.carY;
    const playerPos = cameraCtrl?.fpPosition;

    if (playerPos) {
      const dist = Math.hypot(playerPos.x - OfficeElevatorManager.SHAFT_POS.x, playerPos.z - OfficeElevatorManager.SHAFT_POS.z);
      this.isNearElevator = dist < 3.8;
      this.isPlayerInside = dist < 2.0 && Math.abs(playerPos.y - (this.carY + 0.3)) < 2.5;
    } else {
      this.isNearElevator = false;
      this.isPlayerInside = false;
    }

    if (Math.abs(diff) > 0.02) {
      this.isMoving = true;
      const step = Math.sign(diff) * Math.min(Math.abs(diff), this.moveSpeed * delta);
      this.carY += step;

      if (this.isPlayerInside && cameraCtrl) {
        cameraCtrl.setElevatorRiding(true, this.carY);
      }
    } else {
      const wasMoving = this.isMoving;
      this.carY = targetY;
      this.currentFloor = this.targetFloor;
      this.isMoving = false;

      if (wasMoving && cameraCtrl) {
        cameraCtrl.setElevatorRiding(false, this.carY);
        cameraCtrl.jumpToFloor(this.targetFloor);
      }
    }

    if (this.carMesh) this.carMesh.position.y = this.carY;
    return this.isPlayerInside;
  }

  public getElevatorFloor(): number {
    return this.currentFloor;
  }

  public static getShaftPosition(): THREE.Vector3 {
    return this.SHAFT_POS.clone();
  }
}
