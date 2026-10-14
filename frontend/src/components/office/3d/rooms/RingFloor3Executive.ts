/**
 * Ring Floor 3: Strategic Leadership, CFO Treasury & Strategic Oval Boardroom.
 * Houses CTO Command, Chief of Staff Bridge, CFO Treasury Suite,
 * 16-seat Glass-Enclosed Oval Boardroom, and Wellness Sleep Capsule Lounge.
 */

import * as THREE from "three";
import { OfficeProceduralMaterials } from "../materials/OfficeProceduralMaterials";

export class RingFloor3Executive {
  private static readonly R_MID = 117.0; // Mid-radius of The Grand Ring (R_in=98, R_out=136)

  /** Builds the Floor 3 Strategic Leadership, Boardroom, and Wellness Suite. */
  public static buildExecutiveFloor(): THREE.Group {
    const floorGroup = new THREE.Group();
    floorGroup.name = "Ring_Floor3_Executive";
    floorGroup.position.set(0, 8.0, 0); // Elevation Y = 8.0m

    const walnutMat = new THREE.MeshStandardMaterial({ color: 0x27170e, roughness: 0.32 });
    const leatherMat = new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.5 });
    const glassMat = OfficeProceduralMaterials.createAppleGlassMaterial();

    // 1. Executive Command Suites along crescent arc
    const execs = [
      { id: "role_cto", label: "CTO Architecture Bridge", angle: -0.75, glow: 0x8b5cf6 },
      { id: "role_cos", label: "Chief of Staff Bridge", angle: -0.35, glow: 0xf59e0b },
      { id: "role_cfo", label: "CFO Capital Allocation", angle: 0.35, glow: 0x10b981 },
    ];

    execs.forEach((eInfo) => {
      const px = Math.cos(eInfo.angle) * this.R_MID;
      const pz = Math.sin(eInfo.angle) * this.R_MID;

      const desk = this.createExecutiveDesk(walnutMat, eInfo.id, eInfo.glow);
      desk.position.set(px, 0, pz);
      desk.rotation.y = -eInfo.angle + Math.PI / 2;
      floorGroup.add(desk);
    });

    // 2. The Strategic Oval Boardroom (Glass-Enclosed at center angle = 0, East)
    const boardroom = this.createStrategicBoardroom(walnutMat, leatherMat, glassMat);
    boardroom.position.set(this.R_MID, 0, 0);
    boardroom.rotation.y = Math.PI / 2;
    floorGroup.add(boardroom);

    // 3. Executive Wellness & Acoustic Nap Pods (angle 0.75)
    const wellness = this.createWellnessSanctuary(glassMat);
    wellness.position.set(Math.cos(0.75) * this.R_MID, 0, Math.sin(0.75) * this.R_MID);
    wellness.rotation.y = -0.75 + Math.PI / 2;
    floorGroup.add(wellness);

    return floorGroup;
  }

  /** Constructs an executive suite desk with dual curved monitors and leather armchair. */
  private static createExecutiveDesk(topMat: THREE.Material, roleId: string, glowColor: number): THREE.Group {
    const group = new THREE.Group();
    group.name = `Desk_${roleId}`;

    const top = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.1, 1.2), topMat);
    top.position.y = 0.75;
    top.castShadow = true;

    const legMat = OfficeProceduralMaterials.createTitaniumFrameMaterial();
    [-1.4, 1.4].forEach((lx) => {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.74, 1.1), legMat);
      leg.position.set(lx, 0.37, 0);
      group.add(leg);
    });

    const screenMat = new THREE.MeshStandardMaterial({
      color: 0x0f172a,
      emissive: glowColor,
      emissiveIntensity: 0.85,
    });
    const screen = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.75, 0.04), screenMat);
    screen.position.set(0, 1.25, -0.28);

    const chairMat = new THREE.MeshStandardMaterial({ color: 0x27272a, roughness: 0.45 });
    const chair = new THREE.Mesh(new THREE.BoxGeometry(0.68, 1.0, 0.65), chairMat);
    chair.position.set(0, 0.58, 0.58);

    const light = new THREE.PointLight(0xffedd5, 1.6, 12, 1.3);
    light.position.set(0, 3.2, 0);

    group.add(top, screen, chair, light);
    return group;
  }

  /** Constructs the 16-seat glass-enclosed Strategic Oval Boardroom with 8m curved display. */
  private static createStrategicBoardroom(
    tableMat: THREE.Material,
    chairMat: THREE.Material,
    glassMat: THREE.Material
  ): THREE.Group {
    const room = new THREE.Group();
    room.name = "Strategic_Boardroom";

    // Glass Enclosure Walls with Entrance Door Gap (Radius = 5.2m, Height = 3.6m)
    const wallGeo = new THREE.CylinderGeometry(5.2, 5.2, 3.6, 32, 1, true, 0.4, Math.PI * 1.8);
    const wall = new THREE.Mesh(wallGeo, glassMat);
    wall.position.y = 1.8;
    room.add(wall);

    // Oval Dark Walnut Conference Table (5.8m x 2.4m)
    const table = new THREE.Mesh(new THREE.CylinderGeometry(2.9, 2.9, 0.12, 32), tableMat);
    table.scale.set(1.0, 1.0, 0.45);
    table.position.y = 0.75;
    table.castShadow = true;
    room.add(table);

    // 16 Surrounding High-Back Executive Leather Chairs
    for (let i = 0; i < 16; i++) {
      const a = (i / 16) * Math.PI * 2;
      const cx = Math.cos(a) * 3.4;
      const cz = Math.sin(a) * 1.7;
      const chair = new THREE.Mesh(new THREE.BoxGeometry(0.52, 0.85, 0.5), chairMat);
      chair.position.set(cx, 0.55, cz);
      chair.rotation.y = -a - Math.PI / 2;
      room.add(chair);
    }

    // 8-Meter Curved Presentation Micro-LED Display Wall
    const dispMat = new THREE.MeshStandardMaterial({
      color: 0x090d16,
      emissive: 0x38bdf8,
      emissiveIntensity: 0.9,
    });
    const dispGeo = new THREE.CylinderGeometry(5.0, 5.0, 2.0, 24, 1, true, -0.6, 1.2);
    const display = new THREE.Mesh(dispGeo, dispMat);
    display.position.set(0, 1.9, -0.2);
    room.add(display);

    // Warm Overhead Cove Light Ring & PointLight
    const coveLight = new THREE.PointLight(0xfff7ed, 2.8, 16, 1.2);
    coveLight.position.set(0, 3.3, 0);
    room.add(coveLight);

    return room;
  }

  /** Constructs MetroNap sleep capsules and acoustic relaxation lounge. */
  private static createWellnessSanctuary(glassMat: THREE.Material): THREE.Group {
    const wellness = new THREE.Group();
    const pearlMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.25 });
    const blueMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      emissive: 0x0284c7,
      emissiveIntensity: 0.5,
    });

    [-2.0, 2.0].forEach((cx) => {
      const capsule = new THREE.Group();
      const base = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.6, 1.1), pearlMat);
      base.position.y = 0.3;
      const canopy = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 2.2, 16, 1, false, 0, Math.PI), blueMat);
      canopy.rotateZ(Math.PI / 2);
      canopy.position.set(0, 0.6, 0);
      capsule.position.set(cx, 0, 0);
      capsule.add(base, canopy);
      wellness.add(capsule);
    });

    // Acoustic divider screen
    const divider = new THREE.Mesh(new THREE.BoxGeometry(5.8, 2.8, 0.08), glassMat);
    divider.position.set(0, 1.4, -2.4);
    wellness.add(divider);

    return wellness;
  }
}
