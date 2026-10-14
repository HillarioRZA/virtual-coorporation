/**
 * React Three.js Canvas Container for Apple Park Virtual Office Simulator.
 * Features First-Person / God-Mode PoV, transparent corner spatial HUD, and interactive glass elevator.
 */

"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { AgentSpatialData } from "../../../lib/types/office";
import { Office3DCanvasEngine, EngineTelemetry } from "./core/Office3DCanvasEngine";
import { Office3DHelpers } from "./core/Office3DHelpers";
import { OfficeCanvasTopBar } from "./ui/OfficeCanvasTopBar";
import { OfficeSpatialCornerHUD } from "./ui/OfficeSpatialCornerHUD";
import { OfficeElevatorModalHUD } from "./ui/OfficeElevatorModalHUD";
import { CameraViewMode } from "./core/Office3DTypes";

interface Office3DCanvasProps {
  agents: AgentSpatialData[];
  selectedBuilding: string;
  activeFloor: number;
  selectedAgent: AgentSpatialData | null;
  onSelectAgent: (agent: AgentSpatialData | null) => void;
  demoMode?: boolean;
}

export function Office3DCanvas({
  agents,
  selectedBuilding,
  activeFloor,
  selectedAgent,
  onSelectAgent,
  demoMode = false,
}: Office3DCanvasProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [camMode, setCamMode] = useState<CameraViewMode>("FIRST_PERSON");
  const [timeDisplay, setTimeDisplay] = useState<string>("10:30 [Siang]");
  const [fps, setFps] = useState<number>(60);
  const [playerPos, setPlayerPos] = useState<THREE.Vector3>(new THREE.Vector3(117, 1.7, 0));
  const [isNearElevator, setIsNearElevator] = useState<boolean>(false);
  const [isMenuOpen, setIsMenuOpen] = useState<boolean>(false);
  const [elevatorFloor, setElevatorFloor] = useState<number>(1);
  const [isElevatorMoving, setIsElevatorMoving] = useState<boolean>(false);

  const engineRef = useRef<Office3DCanvasEngine | null>(null);
  const demoModeRef = useRef<boolean>(demoMode);
  demoModeRef.current = demoMode;

  // 1. WebGL Three.js Canvas Lifecycle
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const engine = new Office3DCanvasEngine(
      container,
      activeFloor,
      agents,
      (t: EngineTelemetry) => {
        setFps(t.fps);
        setPlayerPos(t.playerPos);
        setTimeDisplay(t.timeStr);
        setCamMode(t.camMode);
        setIsNearElevator(t.isNearElevator);
        setIsMenuOpen(t.isMenuOpen);
        setElevatorFloor(t.currentFloor);
        setIsElevatorMoving(t.isMoving);
      },
      () => demoModeRef.current
    );
    engineRef.current = engine;

    return () => {
      engine.destroy();
      engineRef.current = null;
    };
  }, []);

  // 2. Dynamically Update Agent State in 3D Scene
  useEffect(() => {
    engineRef.current?.updateAgents(agents);
  }, [agents]);

  // 2. React to Building and Floor Selection
  useEffect(() => {
    const engine = engineRef.current;
    if (!engine) return;
    if (selectedBuilding === "ring") {
      const flY = (activeFloor - 1) * 4.0 + 1.8;
      engine.cameraCtrl.focusOn(new THREE.Vector3(117, flY, 0), 19, 1.25, 0.1);
      engine.cameraCtrl.jumpToFloor(activeFloor);
    } else {
      const targetInfo = Office3DHelpers.getBuildingTarget(selectedBuilding);
      engine.cameraCtrl.focusOn(targetInfo.pos, targetInfo.dist, targetInfo.phi, targetInfo.theta);
    }
  }, [activeFloor, selectedBuilding]);

  const toggleCamMode = () => {
    const engine = engineRef.current;
    if (!engine) return;
    engine.cameraCtrl.toggleFirstPersonGodMode();
  };

  const handleSelectFloor = (fl: number) => {
    if (engineRef.current?.elevatorMgr) {
      engineRef.current.elevatorMgr.callElevator(fl);
    }
  };

  return (
    <div className="w-full h-full relative overflow-hidden rounded-2xl border border-slate-800 bg-slate-950">
      <div ref={containerRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Top HUD Controls Bar */}
      <OfficeCanvasTopBar
        camMode={camMode}
        onToggleCamMode={toggleCamMode}
        timeDisplay={timeDisplay}
        onSetPresetHour={(h) => engineRef.current?.timeline.setTime(h, engineRef.current.sceneMgr.scene)}
      />

      {/* Transparent Corner HUD: Real-time Player Coordinates (X, Y, Z) and FPS */}
      <OfficeSpatialCornerHUD fps={fps} playerPos={playerPos} camMode={camMode} />

      {/* Interactive Glass Elevator Floor Selector Modal */}
      <OfficeElevatorModalHUD
        isNearElevator={isNearElevator}
        isMenuOpen={isMenuOpen}
        currentFloor={elevatorFloor}
        isMoving={isElevatorMoving}
        onSelectFloor={handleSelectFloor}
        onToggleMenu={() => engineRef.current?.elevatorMgr.toggleMenu()}
      />
    </div>
  );
}
