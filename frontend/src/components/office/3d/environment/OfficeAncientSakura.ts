/**
 * The Sacred Ancient Grand Sakura Sanctuary for Apple Park.
 * A monumental, iconic cherry blossom tree with gnarled branching limbs, circular teak deck, and relaxation benches.
 */

import * as THREE from "three";
import { OfficeCollisionSystem } from "../controls/OfficeCollisionSystem";

export class OfficeAncientSakura {
  /** Builds the majestic Grand Ancient Sakura Tree and relaxation deck. */
  public static buildAncientSakura(): THREE.Group {
    const group = new THREE.Group();
    group.name = "ApplePark_GrandAncientSakura";
    const posX = 32;
    const posZ = 16;
    group.position.set(posX, 0, posZ);

    // Register solid trunk collision (R = 1.6m)
    OfficeCollisionSystem.addTreeCollider(posX, posZ, 1.6);

    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x2e231c, roughness: 0.9 });
    const leafPinkMat = new THREE.MeshStandardMaterial({
      color: 0xec4899, // Rich vibrant sakura pink
      roughness: 0.7,
      metalness: 0.05,
      flatShading: false,
    });
    const leafBlushMat = new THREE.MeshStandardMaterial({
      color: 0xf472b6, // Soft cherry blossom pink
      roughness: 0.7,
      metalness: 0.05,
      flatShading: false,
    });

    // 1. Massive Sculpted Trunk (Root flare R=1.1m, waist R=0.65m, top crown flare R=1.0m)
    const trunkLower = new THREE.Mesh(new THREE.CylinderGeometry(0.68, 1.15, 2.4, 14), trunkMat);
    trunkLower.position.y = 1.2;
    trunkLower.castShadow = true;

    const trunkUpper = new THREE.Mesh(new THREE.CylinderGeometry(1.05, 0.68, 2.2, 14), trunkMat);
    trunkUpper.position.y = 3.5;
    trunkUpper.castShadow = true;

    // Organic Root Buttresses anchoring into the deck
    for (let r = 0; r < 5; r++) {
      const rAng = (r / 5) * Math.PI * 2;
      const root = new THREE.Mesh(new THREE.ConeGeometry(0.35, 1.6, 6), trunkMat);
      root.position.set(Math.cos(rAng) * 0.95, 0.4, Math.sin(rAng) * 0.95);
      root.rotation.z = Math.cos(rAng) * 0.35;
      root.rotation.x = -Math.sin(rAng) * 0.35;
      root.castShadow = true;
      group.add(root);
    }
    group.add(trunkLower, trunkUpper);

    // 2. Continuous Upward Branch Limbs (Originating safely inside trunk at Y=3.6)
    const branchAngles = [0.3, 1.6, 2.9, 4.2, 5.4];
    branchAngles.forEach((ang) => {
      const bLen = 2.8;
      const branch = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.38, bLen, 8), trunkMat);
      branch.position.set(Math.cos(ang) * 0.55, 4.4, Math.sin(ang) * 0.55);
      branch.rotation.z = -Math.cos(ang) * 0.38;
      branch.rotation.x = Math.sin(ang) * 0.38;
      branch.castShadow = true;
      group.add(branch);
    });

    // 3. Luxurious Fluffy Multi-Cluster Canopy (Lower puffs cover all branch joints seamlessly)
    const puffConfigs = [
      { x: 0, y: 6.2, z: 0, r: 3.8, mat: leafPinkMat },       // Central Top Dome
      { x: 2.2, y: 4.8, z: 1.0, r: 2.6, mat: leafBlushMat }, // East Lower Puff
      { x: -2.2, y: 4.8, z: 1.0, r: 2.6, mat: leafPinkMat },  // West Lower Puff
      { x: 1.0, y: 4.9, z: -2.2, r: 2.7, mat: leafBlushMat }, // North Lower Puff
      { x: -1.0, y: 4.9, z: 2.2, r: 2.7, mat: leafPinkMat },  // South Lower Puff
      { x: 0, y: 4.4, z: 0, r: 2.5, mat: leafBlushMat },       // Collar Puff hiding all joints
    ];

    puffConfigs.forEach((cfg) => {
      const puff = new THREE.Mesh(new THREE.IcosahedronGeometry(cfg.r, 2), cfg.mat);
      puff.position.set(cfg.x, cfg.y, cfg.z);
      puff.scale.set(1.35, 0.85, 1.35);
      puff.castShadow = true;
      puff.receiveShadow = true;
      group.add(puff);
    });

    // 4. Circular Teak Relaxation Deck & Bench around Trunk Base
    group.add(this.buildWrapAroundDeck());

    // 5. Fallen Petals Carpet on Ground
    const carpetMat = new THREE.MeshStandardMaterial({
      color: 0xec4899,
      transparent: true,
      opacity: 0.65,
      roughness: 0.9,
    });
    const carpet = new THREE.Mesh(new THREE.CircleGeometry(6.5, 24), carpetMat);
    carpet.rotateX(-Math.PI / 2);
    carpet.position.y = 0.02;
    group.add(carpet);

    return group;
  }

  /** Constructs a circular wrap-around wooden deck and bench around the grand trunk. */
  private static buildWrapAroundDeck(): THREE.Group {
    const deckGroup = new THREE.Group();
    const teakMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.45 });
    const metalMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.8 });

    // Circular Plinth Deck (R = 3.6m)
    const plinth = new THREE.Mesh(new THREE.CylinderGeometry(3.6, 3.8, 0.22, 24), teakMat);
    plinth.position.y = 0.11;
    plinth.receiveShadow = true;
    deckGroup.add(plinth);

    // Circular Wrap-Around Bench (R = 2.2m)
    const benchRing = new THREE.Mesh(new THREE.RingGeometry(1.8, 2.6, 24), teakMat);
    benchRing.rotateX(-Math.PI / 2);
    benchRing.position.y = 0.52;
    benchRing.castShadow = true;

    // Bench support posts
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2;
      const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.52, 8), metalMat);
      leg.position.set(Math.cos(a) * 2.2, 0.26, Math.sin(a) * 2.2);
      deckGroup.add(leg);
    }

    deckGroup.add(benchRing);
    return deckGroup;
  }
}
