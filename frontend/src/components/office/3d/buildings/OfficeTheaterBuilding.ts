/**
 * Steve Jobs Theater Upper Glass Pavilion & Structural Architecture Builder.
 * 5x Enlarged Scale (R_cyl=25m, R_roof=34m, H=7.5m), positioned in the South Hill at (40, 0, 230).
 */

import * as THREE from "three";
import { OfficeProceduralMaterials } from "../materials/OfficeProceduralMaterials";

export class OfficeTheaterBuilding {
  public static readonly THEATER_POS = new THREE.Vector3(40, 0, 230);
  public static readonly CYLINDER_RADIUS = 25.0;
  public static readonly ROOF_RADIUS = 34.0;
  public static readonly CYLINDER_HEIGHT = 7.5;

  /** Constructs the 5x scaled ground-level glass pavilion and structural shell. */
  public static buildTheater(): THREE.Group {
    const group = new THREE.Group();
    group.name = "ApplePark_SteveJobsTheater_5X";
    group.position.copy(this.THEATER_POS);

    const glassMat = OfficeProceduralMaterials.createAppleGlassMaterial();
    const finMat = OfficeProceduralMaterials.createCanopyFinMaterial();
    const frameMat = OfficeProceduralMaterials.createTitaniumFrameMaterial();

    // 1. Two-Tiered Italian Travertine Marble Plinth Base (5x Scale)
    this.buildTravertinePlinth(group);

    // 2. 360° Unsupported Structural Glass Cylinder facing North towards The Ring
    this.buildGlassCylinderPavilion(group, glassMat, frameMat);

    // 3. Colossal Floating Carbon-Fiber Disc Roof with White Perimeter Rim
    this.buildCarbonFiberRoof(group, finMat);

    // 4. Central Glass Elevator Core & Helical Marble Spiral Staircase
    this.buildElevatorAndSpiralCore(group, glassMat, frameMat);

    // 5. Subterranean Foundation Drum Enclosure (Outer well shell)
    const wellMat = new THREE.MeshStandardMaterial({ color: 0x090d16, roughness: 0.85 });
    const wellShell = new THREE.Mesh(new THREE.CylinderGeometry(38, 38, 9.0, 48, 1, true), wellMat);
    wellShell.position.y = -4.5;
    group.add(wellShell);

    return group;
  }

  /** Constructs stepped travertine plinth with gentle entry threshold. */
  private static buildTravertinePlinth(group: THREE.Group): void {
    const plinthMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.32, metalness: 0.05 });

    // Lower tier step (R = 28m, H = 0.35m)
    const lowerStep = new THREE.Mesh(new THREE.CylinderGeometry(28.0, 28.5, 0.35, 64), plinthMat);
    lowerStep.position.y = 0.175;
    lowerStep.receiveShadow = true;

    // Upper terrace plinth (R = 26m, H = 0.35m)
    const upperStep = new THREE.Mesh(new THREE.CylinderGeometry(26.0, 26.0, 0.35, 64), plinthMat);
    upperStep.position.y = 0.525;
    upperStep.receiveShadow = true;

    group.add(lowerStep, upperStep);
  }

  /** Constructs 360° curved structural glass cylinder with entrance opening towards The Ring. */
  private static buildGlassCylinderPavilion(
    group: THREE.Group,
    glassMat: THREE.Material,
    frameMat: THREE.Material
  ): void {
    // Door opening facing north towards The Grand Ring (angle = -PI/2)
    const doorCenter = -Math.PI / 2;
    const doorHalfAngle = 0.16; // ~8m open doorway portal
    const startAngle = doorCenter + doorHalfAngle;
    const sweepAngle = Math.PI * 2 - doorHalfAngle * 2;

    const glassCyl = new THREE.Mesh(
      new THREE.CylinderGeometry(this.CYLINDER_RADIUS, this.CYLINDER_RADIUS, this.CYLINDER_HEIGHT, 64, 1, true, startAngle, sweepAngle),
      glassMat
    );
    glassCyl.position.y = this.CYLINDER_HEIGHT / 2 + 0.7;
    group.add(glassCyl);

    // Slim Titanium Door Stanchions
    [-1, 1].forEach((dir) => {
      const ang = doorCenter + dir * doorHalfAngle;
      const col = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, this.CYLINDER_HEIGHT, 12), frameMat);
      col.position.set(Math.cos(ang) * this.CYLINDER_RADIUS, this.CYLINDER_HEIGHT / 2 + 0.7, Math.sin(ang) * this.CYLINDER_RADIUS);
      col.castShadow = true;
      group.add(col);
    });
  }

  /** Constructs ultra-thin floating carbon-fiber disc roof with white aerodynamic rim. */
  private static buildCarbonFiberRoof(group: THREE.Group, rimMat: THREE.Material): void {
    const carbonMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.35, metalness: 0.75 });
    const roofY = this.CYLINDER_HEIGHT + 0.7 + 0.3;

    // Main Carbon-Fiber Disc Roof (R = 34m, H = 0.6m)
    const disc = new THREE.Mesh(new THREE.CylinderGeometry(this.ROOF_RADIUS, this.ROOF_RADIUS - 0.4, 0.6, 64), carbonMat);
    disc.position.y = roofY;
    disc.castShadow = true;

    // Aerodynamic Satin-White Perimeter Fascia Rim
    const rim = new THREE.Mesh(new THREE.TorusGeometry(this.ROOF_RADIUS, 0.28, 12, 64), rimMat);
    rim.rotateX(Math.PI / 2);
    rim.position.y = roofY;
    rim.castShadow = true;

    // Under-Canopy Recessed Warm Downlight Halo
    const haloMat = new THREE.MeshStandardMaterial({ color: 0xfef08a, emissive: 0xfef08a, emissiveIntensity: 0.85 });
    const halo = new THREE.Mesh(new THREE.RingGeometry(22.0, 23.2, 48), haloMat);
    halo.rotateX(Math.PI / 2);
    halo.position.y = roofY - 0.32;

    group.add(disc, rim, halo);
  }

  /** Constructs central cylindrical glass elevator and spiral marble staircase. */
  private static buildElevatorAndSpiralCore(
    group: THREE.Group,
    glassMat: THREE.Material,
    frameMat: THREE.Material
  ): void {
    const core = new THREE.Group();

    // 16m Tall Structural Cylindrical Glass Elevator Shaft
    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(4.5, 4.5, 16.0, 32, 1, true), glassMat);
    shaft.position.y = 1.0;
    core.add(shaft);

    // Active Glass Elevator Car
    const carMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.55,
      emissive: 0x0284c7,
      emissiveIntensity: 0.4,
    });
    const car = new THREE.Mesh(new THREE.CylinderGeometry(4.1, 4.1, 4.0, 24), carMat);
    car.position.y = 2.7;
    core.add(car);

    // Helical Travertine Spiral Stair Steps wrapping around the shaft down to basement
    const stepMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.35 });
    const stepCount = 28;
    for (let i = 0; i < stepCount; i++) {
      const ang = (i / stepCount) * Math.PI * 2.4;
      const y = 0.5 - (i / stepCount) * 8.0;
      const step = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.18, 0.9), stepMat);
      step.position.set(Math.cos(ang) * 5.8, y, Math.sin(ang) * 5.8);
      step.rotation.y = -ang + Math.PI / 2;
      step.castShadow = true;
      core.add(step);
    }

    group.add(core);
  }
}
