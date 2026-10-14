/**
 * 3D Cyber-Voxel Spatial Campus Types and State Definitions.
 * Canonical interfaces for Three.js voxel rendering, camera modes, and humanoid rigs.
 */

import * as THREE from "three";

export type CameraViewMode = "ORBIT" | "FIRST_PERSON" | "GOD_MODE" | "THIRD_PERSON";

export interface VoxelPosition {
  x: number;
  y: number;
  z: number;
}

export interface VoxelSize {
  w: number;
  h: number;
  d: number;
}

export interface VoxelMeshBundle {
  group: THREE.Group;
  update?: (timestamp: number) => void;
  cleanup?: () => void;
}

export interface VoxelCharacterRig {
  root: THREE.Group;
  head: THREE.Mesh;
  torso: THREE.Mesh;
  leftArm: THREE.Mesh;
  rightArm: THREE.Mesh;
  leftLeg: THREE.Mesh;
  rightLeg: THREE.Mesh;
  roleId: string;
  updateAnimation: (state: string, isMoving: boolean, timestamp: number) => void;
}

export interface Building3DBound {
  id: string;
  name: string;
  center: THREE.Vector3;
  size: THREE.Vector3;
}
