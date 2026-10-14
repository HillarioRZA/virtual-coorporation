/**
 * Tantau R&D & SecOps Complex 2-Story Pavilion Builder for Apple Park.
 * 5x Scaled Megastructure (W=52m, D=36m, H=10.5m), positioned along North Tantau Ave at (60, 0, -230).
 */

import * as THREE from "three";
import { OfficeProceduralMaterials } from "../materials/OfficeProceduralMaterials";

export class OfficeTantauBuilding {
  public static readonly TANTAU_POS = new THREE.Vector3(60, 0, -230);
  public static readonly WIDTH = 52.0;
  public static readonly DEPTH = 36.0;
  public static readonly FLOOR_HEIGHT = 5.0;

  /** Constructs the 5x scaled 2-story Tantau R&D & SecOps megastructure. */
  public static buildTantau(): THREE.Group {
    const group = new THREE.Group();
    group.name = "ApplePark_TantauSecOps_5X";
    group.position.copy(this.TANTAU_POS);

    const titaniumMat = OfficeProceduralMaterials.createTitaniumFrameMaterial();
    const finMat = OfficeProceduralMaterials.createCanopyFinMaterial();
    const glassMat = OfficeProceduralMaterials.createAppleGlassMaterial();

    // 1. Plinth Base & Front Airlock Entry Portal
    this.buildPlinthAndAirlock(group, titaniumMat);

    // 2. Multi-Story Levels (Fl 1 Sandbox Lab, Fl 2 Datacenter Vault)
    this.buildGlassFloorsAndFins(group, glassMat, finMat, titaniumMat);

    // 3. Cantilevered Roof, Mechanical Louver Penthouse & Satellite Comms Uplink
    this.buildRoofAndCommsArray(group, finMat, titaniumMat);

    return group;
  }

  /** Constructs raised plinth base, entrance threshold steps, and titanium airlock portal. */
  private static buildPlinthAndAirlock(group: THREE.Group, frameMat: THREE.Material): void {
    const plinthMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4 });
    const plinth = new THREE.Mesh(new THREE.BoxGeometry(this.WIDTH + 3.0, 0.5, this.DEPTH + 3.0), plinthMat);
    plinth.position.y = 0.25;
    plinth.receiveShadow = true;

    // Entry Threshold Steps at front facing South towards The Ring (Z = +DEPTH/2)
    const stepMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.3 });
    const step = new THREE.Mesh(new THREE.BoxGeometry(10.0, 0.25, 4.0), stepMat);
    step.position.set(0, 0.125, this.DEPTH / 2 + 2.0);
    step.receiveShadow = true;

    // Titanium Airlock Canopy & Columns
    const canopy = new THREE.Mesh(new THREE.BoxGeometry(9.6, 0.35, 3.8), frameMat);
    canopy.position.set(0, 5.0, this.DEPTH / 2 + 1.8);
    canopy.castShadow = true;

    const colGeo = new THREE.CylinderGeometry(0.18, 0.18, 5.0, 12);
    const colL = new THREE.Mesh(colGeo, frameMat);
    colL.position.set(-4.5, 2.5, this.DEPTH / 2 + 3.4);
    const colR = colL.clone();
    colR.position.x = 4.5;

    group.add(plinth, step, canopy, colL, colR);
  }

  /** Constructs electrochromic smart-glass walls, floor slabs, and cantilevered fins. */
  private static buildGlassFloorsAndFins(
    group: THREE.Group,
    glassMat: THREE.Material,
    finMat: THREE.Material,
    frameMat: THREE.Material
  ): void {
    const floorSlabMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.3 });
    const wallH = 4.65;

    for (let fl = 1; fl <= 2; fl++) {
      const flY = (fl - 1) * this.FLOOR_HEIGHT + 0.5;

      const slab = new THREE.Mesh(new THREE.BoxGeometry(this.WIDTH, 0.35, this.DEPTH), floorSlabMat);
      slab.position.y = flY + 0.175;
      slab.receiveShadow = true;
      group.add(slab);

      this.buildWallPanels(group, fl, flY, wallH, glassMat);
      this.addTitaniumMullions(group, flY, wallH, frameMat);
    }

    // Inter-Floor Aerodynamic Fin at Y = 5.15m
    const interFin = new THREE.Mesh(new THREE.BoxGeometry(this.WIDTH + 2.4, 0.35, this.DEPTH + 2.4), finMat);
    interFin.position.y = 5.15;
    interFin.castShadow = true;

    // Cyan SecOps Telemetry Beltline LED Strip
    const ledMat = new THREE.MeshStandardMaterial({ color: 0x06b6d4, emissive: 0x06b6d4, emissiveIntensity: 1.1 });
    const ledBelt = new THREE.Mesh(new THREE.BoxGeometry(this.WIDTH + 2.5, 0.1, this.DEPTH + 2.5), ledMat);
    ledBelt.position.y = 5.15;

    group.add(interFin, ledBelt);
  }

  /** Builds wall panels with entrance opening on Floor 1. */
  private static buildWallPanels(group: THREE.Group, fl: number, flY: number, h: number, mat: THREE.Material): void {
    const yCenter = flY + h / 2 + 0.35;

    const backWall = new THREE.Mesh(new THREE.BoxGeometry(this.WIDTH - 0.2, h, 0.12), mat);
    backWall.position.set(0, yCenter, -this.DEPTH / 2 + 0.06);

    const leftWall = new THREE.Mesh(new THREE.BoxGeometry(0.12, h, this.DEPTH - 0.2), mat);
    leftWall.position.set(-this.WIDTH / 2 + 0.06, yCenter, 0);
    const rightWall = leftWall.clone();
    rightWall.position.x = this.WIDTH / 2 - 0.06;

    group.add(backWall, leftWall, rightWall);

    if (fl === 1) {
      const wingW = (this.WIDTH - 8.0) / 2;
      const frontL = new THREE.Mesh(new THREE.BoxGeometry(wingW, h, 0.12), mat);
      frontL.position.set(-this.WIDTH / 2 + wingW / 2, yCenter, this.DEPTH / 2 - 0.06);
      const frontR = new THREE.Mesh(new THREE.BoxGeometry(wingW, h, 0.12), mat);
      frontR.position.set(this.WIDTH / 2 - wingW / 2, yCenter, this.DEPTH / 2 - 0.06);
      group.add(frontL, frontR);
    } else {
      const frontWall = new THREE.Mesh(new THREE.BoxGeometry(this.WIDTH - 0.2, h, 0.12), mat);
      frontWall.position.set(0, yCenter, this.DEPTH / 2 - 0.06);
      group.add(frontWall);
    }
  }

  /** Constructs cantilevered roof, mechanical penthouse louvers, and satellite comms uplink. */
  private static buildRoofAndCommsArray(group: THREE.Group, finMat: THREE.Material, frameMat: THREE.Material): void {
    const roofY = this.FLOOR_HEIGHT * 2 + 0.5;

    const roof = new THREE.Mesh(new THREE.BoxGeometry(this.WIDTH + 3.2, 0.5, this.DEPTH + 3.2), finMat);
    roof.position.y = roofY + 0.25;
    roof.castShadow = true;

    // Mechanical Penthouse Louver Enclosure
    const louverMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.6, metalness: 0.5 });
    const penthouse = new THREE.Mesh(new THREE.BoxGeometry(18.0, 2.4, 12.0), louverMat);
    penthouse.position.set(0, roofY + 1.45, 0);
    penthouse.castShadow = true;

    // Large Satellite Telemetry Dish Antenna
    const dishMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.25, metalness: 0.6 });
    const dish = new THREE.Mesh(new THREE.ConeGeometry(2.8, 1.2, 24, 1, true), dishMat);
    dish.position.set(-6.0, roofY + 4.2, 2.5);
    dish.rotation.x = -Math.PI / 3;
    dish.rotation.y = 0.4;

    const dishPole = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 2.8, 12), frameMat);
    dishPole.position.set(-6.0, roofY + 2.8, 2.5);

    group.add(roof, penthouse, dish, dishPole);
  }

  /** Adds vertical titanium mullions along building facade. */
  private static addTitaniumMullions(group: THREE.Group, flY: number, h: number, mat: THREE.Material): void {
    const mGeo = new THREE.BoxGeometry(0.2, h, 0.22);
    const countX = 10;
    for (let i = 0; i <= countX; i++) {
      const x = -this.WIDTH / 2 + (i / countX) * this.WIDTH;
      const mf = new THREE.Mesh(mGeo, mat);
      mf.position.set(x, flY + h / 2 + 0.35, this.DEPTH / 2);
      const mb = new THREE.Mesh(mGeo, mat);
      mb.position.set(x, flY + h / 2 + 0.35, -this.DEPTH / 2);
      group.add(mf, mb);
    }
  }
}
