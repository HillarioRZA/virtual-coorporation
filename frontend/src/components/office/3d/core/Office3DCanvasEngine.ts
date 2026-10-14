/**
 * WebGL Engine & Animation Loop Controller for Apple Park 3D Campus.
 * Encapsulates Three.js lifecycle, 60-120 FPS animation loop, agent simulation, and elevator sync.
 */

import * as THREE from "three";
import { AgentSpatialData } from "../../../../lib/types/office";
import { Office3DSceneManager } from "./Office3DSceneManager";
import { OfficeCameraController } from "../controls/OfficeCameraController";
import { OfficeSkyTimeline } from "../environment/OfficeSkyTimeline";
import { Office3DHelpers } from "./Office3DHelpers";
import { OfficeTerrainPark } from "../environment/OfficeTerrainPark";
import { OfficeVoxelCharacter } from "../characters/OfficeVoxelCharacter";
import { OfficeAgentCoordinator } from "../characters/OfficeAgentCoordinator";
import { OfficeElevatorManager } from "../buildings/OfficeElevatorManager";
import { OfficeAgentRoutineEngine } from "../characters/OfficeAgentRoutineEngine";
import { OfficeAutomaticDoors } from "../buildings/OfficeAutomaticDoors";
import { CameraViewMode, VoxelCharacterRig } from "./Office3DTypes";

export interface EngineTelemetry {
  fps: number;
  playerPos: THREE.Vector3;
  camTarget: THREE.Vector3;
  timeStr: string;
  camMode: CameraViewMode;
  isNearElevator: boolean;
  isMenuOpen: boolean;
  currentFloor: number;
  isMoving: boolean;
}

export class Office3DCanvasEngine {
  public sceneMgr: Office3DSceneManager;
  public cameraCtrl: OfficeCameraController;
  public timeline: OfficeSkyTimeline;
  public elevatorMgr: OfficeElevatorManager;
  public doorsMgr: OfficeAutomaticDoors;
  public characterRigs = new Map<string, VoxelCharacterRig>();

  private animId = 0;
  private prevTime = performance.now();
  private lastFpsTime = performance.now();
  private frameCount = 0;
  private currentFps = 60;
  private agentsGroup = new THREE.Group();
  private agentsList: AgentSpatialData[] = [];

  constructor(
    container: HTMLElement,
    activeFloor: number,
    agents: AgentSpatialData[],
    private onTelemetry: (t: EngineTelemetry) => void,
    private isDemoMode: () => boolean
  ) {
    this.agentsList = agents;
    this.sceneMgr = new Office3DSceneManager(container);
    this.cameraCtrl = new OfficeCameraController(this.sceneMgr.camera, this.sceneMgr.renderer.domElement);
    this.timeline = new OfficeSkyTimeline(this.sceneMgr.scene, this.sceneMgr.dirLight, this.sceneMgr.renderer);

    this.sceneMgr.scene.add(Office3DHelpers.buildCampusWorld(activeFloor), Office3DHelpers.buildCampusInteriors());
    this.elevatorMgr = new OfficeElevatorManager(this.sceneMgr.scene);
    this.doorsMgr = new OfficeAutomaticDoors();
    this.sceneMgr.scene.add(this.doorsMgr.group);

    this.agentsGroup.name = "ApplePark_Agents";
    this.sceneMgr.scene.add(this.agentsGroup);
    this.spawnAgents(agents);
    this.startLoop();
  }

  public updateAgents(agents: AgentSpatialData[]): void {
    this.agentsList = agents;
  }

  private spawnAgents(agents: AgentSpatialData[]): void {
    agents.forEach((agent) => {
      const rig = OfficeVoxelCharacter.createCharacterRig(agent.role_id, agent.name);
      rig.root.position.copy(OfficeAgentCoordinator.getWorkstationPosition(agent.role_id));
      this.characterRigs.set(agent.role_id, rig);
      this.agentsGroup.add(rig.root);
    });
  }

  private startLoop(): void {
    const loop = (time: number) => {
      const delta = Math.min((time - this.prevTime) / 1000, 0.1);
      this.prevTime = time;

      this.timeline.update(delta, this.sceneMgr.scene, this.cameraCtrl.camera.position);
      this.cameraCtrl.update(delta);
      OfficeTerrainPark.updateWater(time);
      this.elevatorMgr.update(delta, this.cameraCtrl);
      this.doorsMgr.update(delta, this.cameraCtrl.fpPosition);

      // Living Agent Routines
      const demo = this.isDemoMode();
      this.agentsList.forEach((agent, idx) => {
        const rig = this.characterRigs.get(agent.role_id);
        if (rig) {
          const isMtg = agent.activity_state.toLowerCase().includes("meeting");
          const { target, activity } = OfficeAgentRoutineEngine.getDynamicAgentTarget(agent.role_id, idx, isMtg, demo, time);
          const isMoving = Math.hypot(rig.root.position.x - target.x, rig.root.position.z - target.z) > 0.08;
          rig.root.position.lerp(target, 0.08);
          rig.updateAnimation(activity, isMoving, time);
        }
      });

      // FPS & Real-Time Position Telemetry
      this.frameCount++;
      if (time - this.lastFpsTime >= 500) {
        this.currentFps = Math.round((this.frameCount * 1000) / (time - this.lastFpsTime));
        this.frameCount = 0;
        this.lastFpsTime = time;
      }

      this.onTelemetry({
        fps: this.currentFps,
        playerPos: this.cameraCtrl.fpPosition.clone(),
        camTarget: this.cameraCtrl.currentTarget.clone(),
        timeStr: this.timeline.getTimeString(),
        camMode: this.cameraCtrl.mode,
        isNearElevator: this.elevatorMgr.isNearElevator,
        isMenuOpen: this.elevatorMgr.isMenuOpen,
        currentFloor: this.elevatorMgr.currentFloor,
        isMoving: this.elevatorMgr.isMoving,
      });

      this.sceneMgr.render();
      this.animId = requestAnimationFrame(loop);
    };
    this.animId = requestAnimationFrame(loop);
  }

  public destroy(): void {
    cancelAnimationFrame(this.animId);
    this.cameraCtrl.destroy();
    this.elevatorMgr.destroy();
    this.sceneMgr.destroy();
    this.doorsMgr.group.clear();
    this.characterRigs.clear();
  }
}
