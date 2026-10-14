/**
 * Automatic Proximity Sliding Doors Engine for Apple Park Campus Mega-Complex.
 * Procedural titanium-framed laminated glass doors with motion sensors & reactive LEDs.
 * Serves The Grand Ring (East & West), Steve Jobs Theater, and Tantau SecOps.
 */

import * as THREE from "three";
import { OfficeProceduralMaterials } from "../materials/OfficeProceduralMaterials";

export interface DoorPortalData {
  id: "ring_east" | "ring_west" | "theater_north" | "tantau_south";
  pos: THREE.Vector3;
  slideAxis: "X" | "Z";
  slideDist: number;
  currentOpen: number;
  targetOpen: number;
  leftPanel: THREE.Mesh;
  rightPanel: THREE.Mesh;
  sensorLed: THREE.Mesh;
  baseL: number;
  baseR: number;
}

export class OfficeAutomaticDoors {
  public group = new THREE.Group();
  private static portals: Map<string, DoorPortalData> = new Map();

  constructor() {
    this.group.name = "ApplePark_AutomaticDoors_Campus";
    OfficeAutomaticDoors.portals.clear();
    this.buildCampusDoors();
  }

  /** Constructs all 4 interactive sliding door portals. */
  private buildCampusDoors(): void {
    const glassMat = OfficeProceduralMaterials.createAppleGlassMaterial();
    const frameMat = OfficeProceduralMaterials.createTitaniumFrameMaterial();

    // 1. The Grand Ring East Main Portal (x=98, y=0.45, z=0)
    this.createPortal("ring_east", new THREE.Vector3(98.0, 0.45, 0.0), "Z", 2.2, 2.2, 3.4, glassMat, frameMat);
    // 2. The Grand Ring Caffè Macs West Portal (x=-98, y=0.45, z=0)
    this.createPortal("ring_west", new THREE.Vector3(-98.0, 0.45, 0.0), "Z", 2.6, 2.5, 3.6, glassMat, frameMat);
    // 3. Steve Jobs Theater North Pavilion (x=40, y=0.7, z=205)
    this.createPortal("theater_north", new THREE.Vector3(40.0, 0.7, 205.0), "X", 2.0, 2.1, 3.6, glassMat, frameMat);
    // 4. Tantau SecOps South Airlock (x=60, y=0.5, z=-212)
    this.createPortal("tantau_south", new THREE.Vector3(60.0, 0.5, -212.0), "X", 2.0, 2.1, 4.0, glassMat, frameMat);
  }

  /** Constructs an individual procedural sliding door set. */
  private createPortal(
    id: DoorPortalData["id"],
    pos: THREE.Vector3,
    slideAxis: "X" | "Z",
    slideDist: number,
    halfW: number,
    h: number,
    glassMat: THREE.Material,
    frameMat: THREE.Material
  ): void {
    const pGroup = new THREE.Group();
    pGroup.position.copy(pos);

    const w = halfW * 2;
    const isZ = slideAxis === "Z";

    // Overhead Header Transom & Track Rail
    const headGeo = isZ ? new THREE.BoxGeometry(0.35, 0.25, w + slideDist * 2) : new THREE.BoxGeometry(w + slideDist * 2, 0.25, 0.35);
    const header = new THREE.Mesh(headGeo, frameMat);
    header.position.y = h + 0.125;
    header.castShadow = true;

    // Motion Sensor with illuminated LED
    const ledMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, emissive: 0x0284c7, emissiveIntensity: 0.8 });
    const led = new THREE.Mesh(new THREE.BoxGeometry(isZ ? 0.4 : 0.6, 0.08, isZ ? 0.6 : 0.4), ledMat);
    led.position.set(0, h + 0.125, 0);

    // Left and Right Glass Sliding Panels
    const pGeo = isZ ? new THREE.BoxGeometry(0.08, h, halfW) : new THREE.BoxGeometry(halfW, h, 0.08);
    const leftPanel = new THREE.Mesh(pGeo, glassMat);
    const rightPanel = new THREE.Mesh(pGeo, glassMat);

    const baseL = -halfW / 2;
    const baseR = halfW / 2;

    if (isZ) {
      leftPanel.position.set(0, h / 2, baseL);
      rightPanel.position.set(0, h / 2, baseR);
    } else {
      leftPanel.position.set(baseL, h / 2, 0);
      rightPanel.position.set(baseR, h / 2, 0);
    }

    pGroup.add(header, led, leftPanel, rightPanel);
    this.group.add(pGroup);

    OfficeAutomaticDoors.portals.set(id, {
      id,
      pos,
      slideAxis,
      slideDist,
      currentOpen: 0.0,
      targetOpen: 0.0,
      leftPanel,
      rightPanel,
      sensorLed: led,
      baseL,
      baseR,
    });
  }

  /**
   * Updates proximity sensors, smooth sliding animations, and LED reactivity.
   * @param delta Frame time delta in seconds.
   * @param playerPos Current 3D position of player or camera.
   */
  public update(delta: number, playerPos: THREE.Vector3): void {
    const triggerRadius = 4.8;

    OfficeAutomaticDoors.portals.forEach((p) => {
      const dx = playerPos.x - p.pos.x;
      const dz = playerPos.z - p.pos.z;
      const dist = Math.hypot(dx, dz);
      const isHeightMatch = Math.abs(playerPos.y - (p.pos.y + 1.2)) < 2.8;

      p.targetOpen = dist < triggerRadius && isHeightMatch ? 1.0 : 0.0;
      p.currentOpen = THREE.MathUtils.lerp(p.currentOpen, p.targetOpen, Math.min(1.0, delta * 4.8));

      // Slide door meshes
      const shift = p.slideDist * p.currentOpen;
      if (p.slideAxis === "Z") {
        p.leftPanel.position.z = p.baseL - shift;
        p.rightPanel.position.z = p.baseR + shift;
      } else {
        p.leftPanel.position.x = p.baseL - shift;
        p.rightPanel.position.x = p.baseR + shift;
      }

      // Responsive Motion Sensor LED Glow
      const ledMat = p.sensorLed.material as THREE.MeshStandardMaterial;
      if (ledMat) {
        if (p.currentOpen > 0.15) {
          ledMat.color.setHex(0x10b981);
          ledMat.emissive.setHex(0x34d399);
          ledMat.emissiveIntensity = 1.4;
        } else {
          ledMat.color.setHex(0x0284c7);
          ledMat.emissive.setHex(0x0284c7);
          ledMat.emissiveIntensity = 0.6;
        }
      }
    });
  }

  /** Checks whether the specified door portal is sufficiently open to pass through. */
  public static isDoorOpen(id: "ring_east" | "ring_west" | "theater_north" | "tantau_south"): boolean {
    const portal = this.portals.get(id);
    return portal ? portal.currentOpen > 0.35 : true;
  }
}
