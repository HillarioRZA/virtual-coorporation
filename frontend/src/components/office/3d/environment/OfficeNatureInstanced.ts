/**
 * Organic Multi-Branch Sakura & California Olive Nature Engine for Apple Park.
 * Features upright branching trunks, randomized Y-forks, rich vibrant pink canopies, and solid colliders.
 */

import * as THREE from "three";
import { OfficeCollisionSystem } from "../controls/OfficeCollisionSystem";

export class OfficeNatureInstanced {
  /** Builds the lush multi-cluster sakura grove and registers solid trunk colliders. */
  public static buildTreeGrove(): THREE.Group {
    const groveGroup = new THREE.Group();
    groveGroup.name = "ApplePark_SakuraGrove";
    OfficeCollisionSystem.resetTreeColliders();

    const treeCount = 90;
    const positions = this.generateTreePositions(treeCount);

    // 1. Upright Main Trunks
    const trunkGeo = new THREE.CylinderGeometry(0.18, 0.32, 3.4, 8);
    trunkGeo.translate(0, 1.7, 0);
    const trunkMat = new THREE.MeshStandardMaterial({ color: 0x3d352e, roughness: 0.85 });
    const trunkInst = new THREE.InstancedMesh(trunkGeo, trunkMat, treeCount);
    trunkInst.castShadow = true;

    // 2. Randomized Y-Fork Branches (for 45% of trees)
    const branchGeo = new THREE.CylinderGeometry(0.12, 0.18, 2.2, 7);
    branchGeo.translate(0, 1.1, 0);
    const branchInst = new THREE.InstancedMesh(branchGeo, trunkMat, treeCount);
    branchInst.castShadow = true;

    // 3. Multi-Cluster Organic Canopy: 5 Fluffy Puffs per Tree
    const puffGeo = new THREE.IcosahedronGeometry(1.35, 2);
    const totalPuffs = treeCount * 5;

    const foliageMat = new THREE.MeshStandardMaterial({
      color: 0xf472b6, // Rich sakura pink default
      roughness: 0.7,
      metalness: 0.05,
      flatShading: false,
    });
    const foliageInst = new THREE.InstancedMesh(puffGeo, foliageMat, totalPuffs);
    foliageInst.castShadow = true;
    foliageInst.receiveShadow = true;

    // 4. Fallen Blossom Petals Scatter on Grass
    const petalGeo = new THREE.CircleGeometry(2.2, 12);
    petalGeo.rotateX(-Math.PI / 2);
    const petalMat = new THREE.MeshStandardMaterial({
      color: 0xf472b6,
      transparent: true,
      opacity: 0.5,
      roughness: 0.9,
    });
    const petalInst = new THREE.InstancedMesh(petalGeo, petalMat, treeCount);

    const dummy = new THREE.Object3D();
    const puffOffsets = [
      { x: 0, y: 4.4, z: 0, s: 1.45 },       // Center high dome
      { x: -1.2, y: 3.7, z: 0.5, s: 1.15 }, // Left branch puff
      { x: 1.2, y: 3.7, z: -0.5, s: 1.15 }, // Right branch puff
      { x: 0.4, y: 3.6, z: 1.1, s: 1.05 },  // Front puff
      { x: -0.4, y: 3.6, z: -1.1, s: 1.05 },// Back puff
    ];

    for (let i = 0; i < treeCount; i++) {
      const p = positions[i];
      const isOlive = i % 5 === 0; // 20% olive trees, 80% sakura
      const hasYFork = i % 2 === 0; // 50% have natural Y-branch fork
      const treeScale = 0.95 + (Math.sin(i * 11) * 0.5 + 0.5) * 0.3;
      const rotY = (i * 2.399) % (Math.PI * 2);

      // Main Trunk (CRITICAL: Explicitly reset all 3 Euler axes to 0 to prevent tilting!)
      dummy.position.set(p.x, p.y, p.z);
      dummy.scale.set(treeScale, treeScale, treeScale);
      dummy.rotation.set(0, rotY, 0);
      dummy.updateMatrix();
      trunkInst.setMatrixAt(i, dummy.matrix);

      // Y-Fork Branch (angled outward at 28 degrees)
      if (hasYFork) {
        dummy.position.set(p.x, p.y + 1.8 * treeScale, p.z);
        dummy.rotation.set(0.35, rotY + 0.8, 0.25);
        dummy.scale.set(treeScale * 0.85, treeScale * 0.85, treeScale * 0.85);
        dummy.updateMatrix();
        branchInst.setMatrixAt(i, dummy.matrix);
      } else {
        dummy.scale.set(0.001, 0.001, 0.001);
        dummy.updateMatrix();
        branchInst.setMatrixAt(i, dummy.matrix);
      }

      // Blossom Petals on Ground
      dummy.position.set(p.x, 0.03, p.z);
      dummy.rotation.set(0, rotY, 0);
      dummy.scale.set(treeScale * 1.35, 1, treeScale * 1.35);
      dummy.updateMatrix();
      petalInst.setMatrixAt(i, dummy.matrix);

      // Solid collision so player cannot walk through trunk
      OfficeCollisionSystem.addTreeCollider(p.x, p.z, 0.55 * treeScale);

      // Rich Vibrant Sakura Colors (Hot Pink, Vibrant Rose, Soft Cherry)
      let leafColor = 0xf472b6; // Classic vibrant sakura pink
      if (isOlive) {
        leafColor = i % 10 === 0 ? 0x65a30d : 0x4d7c0f; // California olive green
      } else if (i % 3 === 0) {
        leafColor = 0xec4899; // Deep radiant cherry pink
      } else if (i % 4 === 0) {
        leafColor = 0xfbcfe8; // Soft pastel blush pink
      }

      // Position the 5 fluffy canopy clusters around the tree crown
      const colorObj = new THREE.Color(leafColor);
      for (let j = 0; j < 5; j++) {
        const off = puffOffsets[j];
        dummy.position.set(
          p.x + off.x * treeScale,
          p.y + off.y * treeScale,
          p.z + off.z * treeScale
        );
        const pScale = off.s * treeScale;
        dummy.scale.set(pScale, pScale * 0.95, pScale);
        dummy.rotation.set(j * 0.3, rotY + j * 0.7, j * 0.2);
        dummy.updateMatrix();

        const puffIndex = i * 5 + j;
        foliageInst.setMatrixAt(puffIndex, dummy.matrix);
        foliageInst.setColorAt(puffIndex, colorObj);
      }
    }

    trunkInst.instanceMatrix.needsUpdate = true;
    branchInst.instanceMatrix.needsUpdate = true;
    foliageInst.instanceMatrix.needsUpdate = true;
    petalInst.instanceMatrix.needsUpdate = true;
    if (foliageInst.instanceColor) foliageInst.instanceColor.needsUpdate = true;

    groveGroup.add(trunkInst, branchInst, foliageInst, petalInst);
    return groveGroup;
  }

  /** Generates organic distributed tree positions avoiding The Ring, buildings, and pool. */
  private static generateTreePositions(count: number): THREE.Vector3[] {
    const list: THREE.Vector3[] = [];
    let seed = 89;
    const random = () => {
      seed = (seed * 9301 + 49297) % 233280;
      return seed / 233280;
    };

    while (list.length < count) {
      const angle = random() * Math.PI * 2;
      const inMeadow = random() < 0.45;
      const dist = inMeadow ? 28 + random() * 62 : 145 + random() * 150;
      const x = Math.cos(angle) * dist;
      const z = Math.sin(angle) * dist;

      const r = Math.hypot(x, z);
      const inRing = r >= 94 && r <= 140;
      const inTheater = Math.hypot(x - 40, z - 230) < 38;
      const inTantau = Math.hypot(x - 60, z - -230) < 38;
      const inPool = r < 26;
      const inAncient = Math.hypot(x - 32, z - 16) < 10;

      if (!inRing && !inTheater && !inTantau && !inPool && !inAncient) {
        list.push(new THREE.Vector3(x, 0, z));
      }
    }
    return list;
  }
}
