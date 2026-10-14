/**
 * The Grand Ring (The Spaceship) True-Scale 360-Degree Torus Architecture Builder.
 * 2x Enlarged Diameter (R_in=98m, R_out=136m, D=272m), 4 full floors, aerodynamic fins, and solar canopy.
 */

import * as THREE from "three";
import { OfficeProceduralMaterials } from "../materials/OfficeProceduralMaterials";

export class OfficeRingBuilding {
  public static readonly R_IN = 98;
  public static readonly R_OUT = 136;
  public static readonly FLOORS = 4;
  public static readonly FLOOR_HEIGHT = 4.0;

  /** Constructs the complete 2x scale 360-degree 4-story physical Grand Ring. */
  public static buildRing(activeFloor: number = 1): THREE.Group {
    const ringGroup = new THREE.Group();
    ringGroup.name = "ApplePark_TheGrandRing_360";

    const glassMat = OfficeProceduralMaterials.createAppleGlassMaterial();
    const finMat = OfficeProceduralMaterials.createCanopyFinMaterial();
    const oakMat = new THREE.MeshStandardMaterial({
      map: OfficeProceduralMaterials.getBlondeOakTexture(),
      roughness: 0.35,
    });
    const ceilMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.3 });
    const solarMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      map: OfficeProceduralMaterials.getSolarGridTexture(),
      roughness: 0.5,
      metalness: 0.2,
    });
    const frameMat = OfficeProceduralMaterials.createTitaniumFrameMaterial();

    // Build 4 complete physical floors
    for (let fl = 1; fl <= this.FLOORS; fl++) {
      const flY = (fl - 1) * this.FLOOR_HEIGHT;
      const h = 3.65;
      this.buildSolidCurvedSlab(ringGroup, flY, 0.45, oakMat, ceilMat, finMat);

      // Inner and Outer 360-degree Curved Glass Curtain Walls
      const outGlass = new THREE.Mesh(this.makeCurvedWallGeo(this.R_OUT, flY + 0.45, flY + h + 0.45), glassMat);
      ringGroup.add(outGlass);

      if (fl === 1) {
        // Floor 1 Portal Openings: East Entrance (~6.8m) & West Caffe (~8.8m)
        const g1 = new THREE.Mesh(this.makeCurvedWallGeo(this.R_IN, flY + 0.45, flY + h + 0.45, 0.035, Math.PI - 0.08, 64), glassMat);
        const g2 = new THREE.Mesh(this.makeCurvedWallGeo(this.R_IN, flY + 0.45, flY + h + 0.45, Math.PI + 0.045, Math.PI - 0.08, 64), glassMat);
        ringGroup.add(g1, g2);
      } else {
        const inGlass = new THREE.Mesh(this.makeCurvedWallGeo(this.R_IN, flY + 0.45, flY + h + 0.45), glassMat);
        ringGroup.add(inGlass);
      }

      // Dual Aerodynamic White Cantilevered Sun Fins (Inner and Outer)
      this.buildCurvedFin(ringGroup, flY + h + 0.35, this.R_OUT - 0.2, this.R_OUT + 4.5, finMat);
      this.buildCurvedFin(ringGroup, flY + h + 0.35, this.R_IN - 3.8, this.R_IN + 0.2, finMat);
      this.addMullionsAndPillars(ringGroup, flY, h, frameMat);
    }

    // Heavy Volumetric Rooftop with 360-degree Photovoltaic Solar Array (Y = 16m)
    this.buildSolidCurvedSlab(ringGroup, 16.0, 0.55, solarMat, ceilMat, finMat);
    this.buildGrandEntrancePortal(ringGroup, frameMat, finMat);

    return ringGroup;
  }

  /** Unified procedural curved wall BufferGeometry supporting custom arcs. */
  private static makeCurvedWallGeo(
    r: number,
    y0: number,
    y1: number,
    startAngle = 0,
    sweepAngle = Math.PI * 2,
    segs = 128
  ): THREE.BufferGeometry {
    const geo = new THREE.BufferGeometry();
    const pos: number[] = [], uv: number[] = [], idx: number[] = [];

    for (let i = 0; i <= segs; i++) {
      const a = startAngle + (i / segs) * sweepAngle;
      const x = r * Math.cos(a), z = r * Math.sin(a);
      pos.push(x, y0, z, x, y1, z);
      uv.push((i / segs) * 32, 0, (i / segs) * 32, 1);
    }

    for (let i = 0; i < segs; i++) {
      const b1 = i * 2, t1 = b1 + 1, b2 = (i + 1) * 2, t2 = b2 + 1;
      idx.push(b1, b2, t1, t1, b2, t2);
    }

    geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
    geo.setIndex(idx);
    geo.computeVertexNormals();
    return geo;
  }

  /** Unified procedural curved horizontal slab with proper normals. */
  private static makeCurvedSlabGeo(rIn: number, rOut: number, y: number, isCeiling = false, segs = 128): THREE.BufferGeometry {
    const geo = new THREE.BufferGeometry();
    const pos: number[] = [], uv: number[] = [], idx: number[] = [];

    for (let i = 0; i <= segs; i++) {
      const a = (i / segs) * Math.PI * 2;
      const c = Math.cos(a), s = Math.sin(a);
      pos.push(rIn * c, y, rIn * s, rOut * c, y, rOut * s);
      uv.push((i / segs) * 24, 0, (i / segs) * 24, 1);
    }

    for (let i = 0; i < segs; i++) {
      const in1 = i * 2, out1 = in1 + 1, in2 = (i + 1) * 2, out2 = in2 + 1;
      if (!isCeiling) idx.push(in1, out1, in2, out1, out2, in2);
      else idx.push(in1, in2, out1, out1, in2, out2);
    }

    geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
    geo.setIndex(idx);
    geo.computeVertexNormals();
    return geo;
  }

  /** Builds solid curved floor slab with top, bottom, and fascia. */
  private static buildSolidCurvedSlab(
    group: THREE.Group,
    y: number,
    th: number,
    topM: THREE.Material,
    botM: THREE.Material,
    fasciaM: THREE.Material
  ): void {
    const top = new THREE.Mesh(this.makeCurvedSlabGeo(this.R_IN, this.R_OUT, y + th, false), topM);
    top.receiveShadow = true;
    const bot = new THREE.Mesh(this.makeCurvedSlabGeo(this.R_IN, this.R_OUT, y, true), botM);
    const outFascia = new THREE.Mesh(this.makeCurvedWallGeo(this.R_OUT, y, y + th), fasciaM);
    outFascia.castShadow = true;
    const inFascia = new THREE.Mesh(this.makeCurvedWallGeo(this.R_IN, y, y + th), fasciaM);
    group.add(top, bot, outFascia, inFascia);
  }

  /** Builds an aerodynamic cantilevered fin with top and bottom faces. */
  private static buildCurvedFin(group: THREE.Group, y: number, r1: number, r2: number, mat: THREE.Material): void {
    const topFin = new THREE.Mesh(this.makeCurvedSlabGeo(r1, r2, y, false), mat);
    topFin.castShadow = true;
    group.add(topFin, new THREE.Mesh(this.makeCurvedSlabGeo(r1, r2, y - 0.05, true), mat));
  }

  /** Constructs Grand Entrance Lobby Portal at ground level (angle = 0, East). */
  private static buildGrandEntrancePortal(group: THREE.Group, frameMat: THREE.Material, canopyMat: THREE.Material): void {
    const portal = new THREE.Group();
    portal.position.set(this.R_IN - 1.5, 0, 0);

    const canopy = new THREE.Mesh(new THREE.BoxGeometry(6.5, 0.45, 12.0), canopyMat);
    canopy.position.set(0, 4.3, 0);
    canopy.castShadow = true;

    const colGeo = new THREE.CylinderGeometry(0.35, 0.35, 4.3, 16);
    const colL = new THREE.Mesh(colGeo, frameMat);
    colL.position.set(-2.0, 2.15, -5.2);
    const colR = colL.clone();
    colR.position.z = 5.2;

    // Solid Travertine Vestibule Plinth matching floor height (0.45m) & Entry Mat
    const plinth = new THREE.Mesh(new THREE.BoxGeometry(6.6, 0.45, 11.0), new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.35 }));
    plinth.position.set(0, 0.225, 0);
    plinth.receiveShadow = true;

    const matMesh = new THREE.Mesh(new THREE.BoxGeometry(5.2, 0.04, 7.5), new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.5 }));
    matMesh.position.set(0, 0.46, 0);
    matMesh.receiveShadow = true;

    portal.add(canopy, colL, colR, plinth, matMesh);
    group.add(portal);
  }

  /** Adds vertical titanium mullions and load-bearing pillars along the 360 circle. */
  private static addMullionsAndPillars(group: THREE.Group, flY: number, h: number, frameMat: THREE.Material): void {
    const count = 48;
    const pGeo = new THREE.CylinderGeometry(0.45, 0.45, h, 14);
    const mGeo = new THREE.BoxGeometry(0.12, h, 0.18);
    const midR = (this.R_IN + this.R_OUT) / 2;

    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2;
      const pillar = new THREE.Mesh(pGeo, frameMat);
      pillar.position.set(Math.cos(angle) * midR, flY + h / 2 + 0.22, Math.sin(angle) * midR);
      pillar.castShadow = true;

      const mullion = new THREE.Mesh(mGeo, frameMat);
      mullion.position.set(Math.cos(angle) * this.R_OUT, flY + h / 2 + 0.22, Math.sin(angle) * this.R_OUT);
      mullion.rotation.y = -angle + Math.PI / 2;
      group.add(pillar, mullion);
    }
  }
}
