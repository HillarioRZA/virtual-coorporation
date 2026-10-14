/**
 * Procedural Humanoid Voxel Character Generator (Steve/Alex Proportions).
 * Constructs hierarchical 3D voxel rigs with role-based outfits and procedural walk/type animations.
 */

import * as THREE from "three";
import { VoxelCharacterRig } from "../core/Office3DTypes";

export class OfficeVoxelCharacter {
  public static createCharacterRig(roleId: string, roleName: string): VoxelCharacterRig {
    const root = new THREE.Group();
    root.name = `Agent_${roleId}`;

    const outfitColor = this.getRoleOutfitColor(roleId);

    // 1. Torso
    const torsoGeo = new THREE.BoxGeometry(0.45, 0.65, 0.25);
    const torsoMat = new THREE.MeshStandardMaterial({ color: outfitColor, roughness: 0.5 });
    const torso = new THREE.Mesh(torsoGeo, torsoMat);
    torso.position.y = 1.0;
    torso.castShadow = true;
    root.add(torso);

    // 2. Head with face
    const headGeo = new THREE.BoxGeometry(0.4, 0.4, 0.4);
    const skinMat = new THREE.MeshStandardMaterial({ color: 0xfbd38d, roughness: 0.6 });
    const head = new THREE.Mesh(headGeo, skinMat);
    head.position.y = 1.55;
    head.castShadow = true;
    root.add(head);

    // Eyes
    const eyeMat = new THREE.MeshBasicMaterial({ color: 0x0f172a });
    const eyeL = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.06, 0.02), eyeMat);
    eyeL.position.set(-0.1, 0.04, 0.21);
    const eyeR = eyeL.clone();
    eyeR.position.x = 0.1;
    head.add(eyeL, eyeR);

    // 3. Arms (Pivot at shoulder)
    const armGeo = new THREE.BoxGeometry(0.16, 0.6, 0.16);
    const armMat = new THREE.MeshStandardMaterial({ color: outfitColor, roughness: 0.5 });

    const leftArm = new THREE.Mesh(armGeo, armMat);
    leftArm.position.set(-0.32, 1.0, 0);
    leftArm.castShadow = true;

    const rightArm = new THREE.Mesh(armGeo, armMat);
    rightArm.position.set(0.32, 1.0, 0);
    rightArm.castShadow = true;
    root.add(leftArm, rightArm);

    // 4. Legs (Pivot at hip)
    const legGeo = new THREE.BoxGeometry(0.18, 0.65, 0.18);
    const pantsMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.7 });

    const leftLeg = new THREE.Mesh(legGeo, pantsMat);
    leftLeg.position.set(-0.11, 0.35, 0);
    leftLeg.castShadow = true;

    const rightLeg = new THREE.Mesh(legGeo, pantsMat);
    rightLeg.position.set(0.11, 0.35, 0);
    rightLeg.castShadow = true;
    root.add(leftLeg, rightLeg);

    // 5. Procedural 3D Role Badge
    const badgeGeo = new THREE.BoxGeometry(0.5, 0.12, 0.02);
    const badgeMat = new THREE.MeshBasicMaterial({ color: 0x6366f1 });
    const badge = new THREE.Mesh(badgeGeo, badgeMat);
    badge.position.set(0, 1.9, 0);
    root.add(badge);

    // 6. Animation State Machine
    const updateAnimation = (state: string, isMoving: boolean, timestamp: number): void => {
      const t = timestamp * 0.008;

      if (isMoving) {
        // Natural walking swing
        leftLeg.rotation.x = Math.sin(t) * 0.6;
        rightLeg.rotation.x = -Math.sin(t) * 0.6;
        leftArm.rotation.x = -Math.sin(t) * 0.6;
        rightArm.rotation.x = Math.sin(t) * 0.6;
        head.rotation.y = Math.sin(t * 0.5) * 0.1;
      } else if (state.toLowerCase().includes("coding") || state.toLowerCase().includes("working")) {
        // Typing at desk
        leftLeg.rotation.x = 0;
        rightLeg.rotation.x = 0;
        leftArm.rotation.x = -1.1 + Math.sin(t * 2) * 0.08;
        rightArm.rotation.x = -1.1 + Math.cos(t * 2) * 0.08;
        head.rotation.x = 0.2;
      } else if (state.toLowerCase().includes("meeting") || state.toLowerCase().includes("listening")) {
        // Seated in meeting
        leftLeg.rotation.x = -1.3;
        rightLeg.rotation.x = -1.3;
        leftArm.rotation.x = -0.3;
        rightArm.rotation.x = -0.3;
        head.rotation.x = 0;
      } else {
        // Idle breathing
        leftLeg.rotation.x = 0;
        rightLeg.rotation.x = 0;
        leftArm.rotation.x = Math.sin(t * 0.4) * 0.05;
        rightArm.rotation.x = -Math.sin(t * 0.4) * 0.05;
        head.position.y = 1.55 + Math.sin(t * 0.4) * 0.015;
      }
    };

    return {
      root,
      head,
      torso,
      leftArm,
      rightArm,
      leftLeg,
      rightLeg,
      roleId,
      updateAnimation,
    };
  }

  private static getRoleOutfitColor(roleId: string): number {
    switch (roleId) {
      case "role_founder":
        return 0x1e3a8a; // Royal Navy Blue
      case "role_cos":
        return 0x475569; // Charcoal Grey
      case "role_cfo":
        return 0x065f46; // Emerald Forest
      case "role_cto":
        return 0x0284c7; // Cyber Sky Blue
      case "role_cpo":
      case "role_pm":
        return 0x9333ea; // Purple Violet
      case "role_fe":
      case "role_be":
        return 0x0d9488; // Deep Teal
      case "role_qa":
      case "role_devsecops":
        return 0xd97706; // Amber Bronze
      default:
        return 0x334155; // Slate Steel
    }
  }
}
