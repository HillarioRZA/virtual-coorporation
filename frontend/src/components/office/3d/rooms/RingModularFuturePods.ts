/**
 * Ring Modular Future Pods Builder.
 * Pre-provisions active modular expansion sectors across The Grand Ring (Fl 1-4)
 * with polished oak benching, frosted glass partitions, standby LED strips, and illuminated placards.
 */

import * as THREE from "three";
import { OfficeProceduralMaterials } from "../materials/OfficeProceduralMaterials";

interface FutureSectorConfig {
  floor: number;
  angle: number;
  label: string;
}

export class RingModularFuturePods {
  private static readonly R_MID = 117.0; // Mid-radius of The Grand Ring (R_in=98, R_out=136)

  private static readonly SECTORS: FutureSectorConfig[] = [
    // Floor 1 Engineering Wings
    { floor: 1, angle: 1.6, label: "FUTURE ENG // AI INFERENCE LAB" },
    { floor: 1, angle: 2.2, label: "FUTURE ENG // DATA PIPELINE POD" },
    { floor: 1, angle: -1.6, label: "FUTURE ENG // QUANTUM SIMULATOR" },
    { floor: 1, angle: -2.2, label: "FUTURE ENG // HARDWARE SANDBOX" },
    // Floor 2 Creative & Growth Wings
    { floor: 2, angle: 1.6, label: "FUTURE DESIGN // XR SPATIAL LAB" },
    { floor: 2, angle: 2.2, label: "FUTURE GROWTH // GLOBAL EXPANSION" },
    { floor: 2, angle: -1.6, label: "FUTURE CREATIVE // BRAND MATRIX" },
    { floor: 2, angle: -2.2, label: "FUTURE PRODUCT // INCUBATION LAB" },
    // Floor 3 Leadership & Operations Wings
    { floor: 3, angle: 1.6, label: "FUTURE OPS // STRATEGIC ADVISORY" },
    { floor: 3, angle: 2.2, label: "FUTURE GOV // COMPLIANCE & LEGAL" },
    { floor: 3, angle: -1.6, label: "FUTURE VENTURE // M&A WAR ROOM" },
    { floor: 3, angle: -2.2, label: "FUTURE TREASURY // CAPITAL WING" },
    // Floor 4 Founder Suites
    { floor: 4, angle: 1.6, label: "FOUNDER ARCHIVE // INNOVATION SALON" },
    { floor: 4, angle: 2.2, label: "FOUNDER PAVILION // VIP GALLERY" },
    { floor: 4, angle: -1.6, label: "FOUNDER OBSERVATORY // SKY SUITE" },
  ];

  /** Builds all modular expansion sectors across all 4 floors. */
  public static buildFuturePods(): THREE.Group {
    const podsGroup = new THREE.Group();
    podsGroup.name = "Ring_Modular_FuturePods";

    const deskMat = new THREE.MeshStandardMaterial({
      map: OfficeProceduralMaterials.getBlondeOakTexture(),
      roughness: 0.45,
    });
    const frameMat = OfficeProceduralMaterials.createTitaniumFrameMaterial();
    const glassMat = OfficeProceduralMaterials.createAppleGlassMaterial();
    const holoMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      emissive: 0x0284c7,
      emissiveIntensity: 0.85,
      transparent: true,
      opacity: 0.75,
    });
    const haloMat = new THREE.MeshStandardMaterial({
      color: 0xfef08a,
      emissive: 0xfef08a,
      emissiveIntensity: 0.6,
    });

    this.SECTORS.forEach((sec) => {
      const flY = (sec.floor - 1) * 4.0;
      const px = Math.cos(sec.angle) * this.R_MID;
      const pz = Math.sin(sec.angle) * this.R_MID;

      const sectorPod = new THREE.Group();
      sectorPod.position.set(px, flY, pz);
      sectorPod.rotation.y = -sec.angle + Math.PI / 2;

      // 1. Sleek Glass Wing Partition (Width 7.2m, Height 3.2m)
      const divider = new THREE.Mesh(new THREE.BoxGeometry(7.2, 3.2, 0.06), glassMat);
      divider.position.set(0, 1.6, -3.2);
      sectorPod.add(divider);

      // 2. Holographic Reservation Placard
      const sign = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.38, 0.04), holoMat);
      sign.position.set(0, 2.7, -3.15);
      sectorPod.add(sign);

      // 3. Modular Workstations (2 double-sided pairs)
      [-2.2, 2.2].forEach((dx) => {
        const desk = new THREE.Mesh(new THREE.BoxGeometry(2.8, 0.08, 1.2), deskMat);
        desk.position.set(dx, 0.75, 0);
        desk.castShadow = true;

        [-1.25, 1.25].forEach((lx) => {
          const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.75, 8), frameMat);
          leg.position.set(dx + lx, 0.375, 0);
          sectorPod.add(leg);
        });

        // Standby LED power bar
        const ledStrip = new THREE.Mesh(
          new THREE.BoxGeometry(2.8, 0.02, 0.02),
          new THREE.MeshStandardMaterial({ color: 0x0ea5e9, emissive: 0x0284c7, emissiveIntensity: 0.6 })
        );
        ledStrip.position.set(dx, 0.76, 0.58);
        sectorPod.add(desk, ledStrip);
      });

      // 4. Overhead Ambient Downlight Halo & PointLight
      const halo = new THREE.Mesh(new THREE.RingGeometry(1.8, 2.1, 24), haloMat);
      halo.rotateX(Math.PI / 2);
      halo.position.set(0, 3.55, 0);

      const light = new THREE.PointLight(0xfef08a, 1.4, 16, 1.4);
      light.position.set(0, 3.2, 0);

      sectorPod.add(halo, light);
      podsGroup.add(sectorPod);
    });

    return podsGroup;
  }
}
