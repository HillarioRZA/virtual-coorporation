/**
 * Ring Floor 2: Product Strategy, UX Design Studio & Growth Marketing Arena.
 * Features 6 division workstations, Design Sprint collaboration island,
 * Growth telemetry wall, creative brainstorming lounge, and overhead lighting.
 */

import * as THREE from "three";
import { OfficeProceduralMaterials } from "../materials/OfficeProceduralMaterials";

export class RingFloor2Strategy {
  private static readonly R_MID = 117.0; // Mid-radius of The Grand Ring (R_in=98, R_out=136)

  /** Builds the Floor 2 Strategy & Creative Suites along the curved arc. */
  public static buildStrategyFloor(): THREE.Group {
    const floorGroup = new THREE.Group();
    floorGroup.name = "Ring_Floor2_Strategy";
    floorGroup.position.set(0, 4.0, 0); // Elevation Y = 4.0m

    const deskMat = new THREE.MeshStandardMaterial({
      map: OfficeProceduralMaterials.getBlondeOakTexture(),
      roughness: 0.45,
    });
    const legMat = OfficeProceduralMaterials.createTitaniumFrameMaterial();
    const glassMat = OfficeProceduralMaterials.createAppleGlassMaterial();

    // 1. Division Workstations along the crescent arc
    const roles = [
      { id: "role_cto", label: "CTO Architecture Suite", angle: -0.9, glow: 0x8b5cf6 },
      { id: "role_pm", label: "Product Management Pod", angle: -0.5, glow: 0x3b82f6 },
      { id: "role_growth", label: "Growth Strategy Pod", angle: -0.15, glow: 0x10b981 },
      { id: "role_ui_ux", label: "UI/UX Design Studio", angle: 0.15, glow: 0xec4899 },
      { id: "role_copywriter", label: "Content & Copy Pod", angle: 0.5, glow: 0xf59e0b },
      { id: "role_seo", label: "SEO Analytics Pod", angle: 0.9, glow: 0x06b6d4 },
    ];

    roles.forEach((rInfo) => {
      const px = Math.cos(rInfo.angle) * this.R_MID;
      const pz = Math.sin(rInfo.angle) * this.R_MID;

      const desk = this.createStrategyDesk(deskMat, legMat, rInfo.id, rInfo.glow);
      desk.position.set(px, 0, pz);
      desk.rotation.y = -rInfo.angle + Math.PI / 2;
      floorGroup.add(desk);
    });

    // 2. Central Design Sprint Collaboration Island (angle = 0, inner zone)
    const sprintIsland = this.createDesignSprintIsland(deskMat, legMat, glassMat);
    sprintIsland.position.set(this.R_MID - 6.5, 0, 0);
    sprintIsland.rotation.y = Math.PI / 2;
    floorGroup.add(sprintIsland);

    // 3. Creative Brainstorming Lounge (outer zone)
    const lounge = this.createCreativeLounge(deskMat);
    lounge.position.set(this.R_MID + 6.5, 0, 0);
    lounge.rotation.y = Math.PI / 2;
    floorGroup.add(lounge);

    return floorGroup;
  }

  /** Constructs an executive strategy desk with widescreen curved monitor and task lamp. */
  private static createStrategyDesk(
    topMat: THREE.Material,
    legMat: THREE.Material,
    roleId: string,
    glowColor: number
  ): THREE.Group {
    const group = new THREE.Group();
    group.name = `Desk_${roleId}`;

    const top = new THREE.Mesh(new THREE.BoxGeometry(3.0, 0.08, 1.15), topMat);
    top.position.y = 0.75;
    top.castShadow = true;

    [-1.3, 1.3].forEach((lx) => {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.74, 1.05), legMat);
      leg.position.set(lx, 0.37, 0);
      group.add(leg);
    });

    // Dual 4K Curved Displays with role glow
    const screenMat = new THREE.MeshStandardMaterial({
      color: 0x0f172a,
      emissive: glowColor,
      emissiveIntensity: 0.85,
      roughness: 0.15,
    });
    const s1 = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.65, 0.03), screenMat);
    s1.position.set(-0.62, 1.2, -0.25);
    s1.rotation.y = 0.12;
    const s2 = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.65, 0.03), screenMat);
    s2.position.set(0.62, 1.2, -0.25);
    s2.rotation.y = -0.12;

    // Vitra Pacific Ergonomic Chair
    const chairMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.5 });
    const chair = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.9, 0.6), chairMat);
    chair.position.set(0, 0.52, 0.55);

    // Overhead Downlight PointLight
    const downlight = new THREE.PointLight(0xffedd5, 1.5, 12, 1.4);
    downlight.position.set(0, 3.2, 0);

    group.add(top, s1, s2, chair, downlight);
    return group;
  }

  /** Constructs circular Design Sprint island with rolling stools and glass board. */
  private static createDesignSprintIsland(
    woodMat: THREE.Material,
    metalMat: THREE.Material,
    glassMat: THREE.Material
  ): THREE.Group {
    const island = new THREE.Group();

    // Large Circular Solid Oak Collaboration Table (Dia = 3.6m)
    const table = new THREE.Mesh(new THREE.CylinderGeometry(1.8, 1.8, 0.1, 32), woodMat);
    table.position.y = 0.75;
    const centerLeg = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.65, 0.74, 16), metalMat);
    centerLeg.position.y = 0.37;
    island.add(table, centerLeg);

    // 6 Rolling Stools around table
    const stoolMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.6 });
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * Math.PI * 2;
      const stool = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.48, 16), stoolMat);
      stool.position.set(Math.cos(a) * 2.4, 0.24, Math.sin(a) * 2.4);
      island.add(stool);
    }

    // Curved Interactive Glass Whiteboard Panel (Width 3.8m, Height 2.2m)
    const board = new THREE.Mesh(new THREE.BoxGeometry(3.8, 2.2, 0.05), glassMat);
    board.position.set(0, 1.4, -2.8);
    island.add(board);

    return island;
  }

  /** Constructs creative brainstorming lounge with modular curved sofa and low table. */
  private static createCreativeLounge(woodMat: THREE.Material): THREE.Group {
    const lounge = new THREE.Group();

    // Modular Curved Grey Wool Sofa (Dia = 4.2m arc)
    const sofaMat = new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.85 });
    const sofa = new THREE.Mesh(
      new THREE.CylinderGeometry(2.1, 2.1, 0.45, 24, 1, false, -Math.PI / 3, (Math.PI * 2) / 3),
      sofaMat
    );
    sofa.position.set(0, 0.225, 0.8);
    lounge.add(sofa);

    // Low Round Solid Oak Coffee Table
    const table = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 0.9, 0.35, 24), woodMat);
    table.position.set(0, 0.175, -0.4);
    lounge.add(table);

    // Warm Ambient Lounge Light
    const loungeLight = new THREE.PointLight(0xfef08a, 1.8, 14, 1.2);
    loungeLight.position.set(0, 3.0, 0);
    lounge.add(loungeLight);

    return lounge;
  }
}
