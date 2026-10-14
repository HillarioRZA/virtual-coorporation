/**
 * Caffè Macs 4-Storey Great Atrium Builder.
 * Integrates monumental glass dining atrium into the inner arc of The Grand Ring (R_in=98m),
 * featuring curved 440,000-lb glass sliding doors, Arco oak tables, and meadow terrace.
 */

import * as THREE from "three";
import { OfficeProceduralMaterials } from "../materials/OfficeProceduralMaterials";

export class OfficeRingAtriumCaffe {
  private static readonly R_IN = 98;
  private static readonly ATRIUM_ANGLE = Math.PI; // West sector
  private static readonly ATRIUM_SPAN = 0.35; // ~20 degrees arc on giant ring

  /** Constructs the integrated 4-story Caffè Macs Great Atrium in The Ring. */
  public static buildAtrium(): THREE.Group {
    const caffeGroup = new THREE.Group();
    caffeGroup.name = "ApplePark_CaffeMacs_Atrium";

    const glassMat = OfficeProceduralMaterials.createAppleGlassMaterial();
    const frameMat = OfficeProceduralMaterials.createTitaniumFrameMaterial();
    const oakMat = new THREE.MeshStandardMaterial({
      map: OfficeProceduralMaterials.getBlondeOakTexture(),
      roughness: 0.35,
    });
    const steelMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.85, roughness: 0.2 });

    // 1. Monumental 4-Storey Upper Glass Transom & Track (Floor 1 open for sliding doors)
    const transomGeo = this.makeCurvedDoorGeo(this.R_IN - 0.2, 4.2, 15.2, 32);
    const transomMesh = new THREE.Mesh(transomGeo, glassMat);
    transomMesh.name = "CaffeMacs_UpperGlassTransom";
    caffeGroup.add(transomMesh);

    // Frame tracks for sliding door
    const trackGeo = new THREE.RingGeometry(this.R_IN - 0.8, this.R_IN + 0.6, 32, 1, this.ATRIUM_ANGLE - this.ATRIUM_SPAN / 2, this.ATRIUM_SPAN);
    trackGeo.rotateX(-Math.PI / 2);
    const track = new THREE.Mesh(trackGeo, frameMat);
    track.position.y = 0.05;
    caffeGroup.add(track);

    // 2. Stainless Steel Barista Counter & Boba Island (Located at mid-depth inside Ring, R=110m)
    const barMidR = 110;
    const barX = barMidR * Math.cos(this.ATRIUM_ANGLE);
    const barZ = barMidR * Math.sin(this.ATRIUM_ANGLE);

    const counter = new THREE.Mesh(new THREE.BoxGeometry(10.5, 1.1, 2.2), steelMat);
    counter.position.set(barX, 0.55, barZ);
    counter.rotation.y = -this.ATRIUM_ANGLE + Math.PI / 2;
    counter.castShadow = true;

    // Espresso machine & taps
    const esp = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.8, 0.9), steelMat);
    esp.position.set(barX - 2.0, 1.5, barZ);
    const tap = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.55, 8), steelMat);
    tap.position.set(barX + 2.0, 1.38, barZ);
    caffeGroup.add(counter, esp, tap);

    // 3. Solid Arco European Oak Communal Tables
    for (let t = -3; t <= 3; t++) {
      if (t === 0) continue;
      const angle = this.ATRIUM_ANGLE + t * 0.05;
      const tx = 105 * Math.cos(angle);
      const tz = 105 * Math.sin(angle);

      const table = new THREE.Mesh(new THREE.BoxGeometry(6.5, 0.14, 1.4), oakMat);
      table.position.set(tx, 0.75, tz);
      table.rotation.y = -angle + Math.PI / 2;
      table.castShadow = true;

      const legs = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.72, 1.3), oakMat);
      legs.position.set(tx, 0.36, tz);
      legs.rotation.y = -angle + Math.PI / 2;
      caffeGroup.add(table, legs);
    }

    // 4. Outdoor Garden Terrace Dining into Central Meadow
    this.addOutdoorMeadowTerrace(caffeGroup, oakMat);

    return caffeGroup;
  }

  /** Curved door geometry for the monumental 4-story atrium opening. */
  private static makeCurvedDoorGeo(r: number, y0: number, y1: number, segs = 32): THREE.BufferGeometry {
    const geo = new THREE.BufferGeometry();
    const pos: number[] = [], uv: number[] = [], idx: number[] = [];
    const start = this.ATRIUM_ANGLE - this.ATRIUM_SPAN / 2;

    for (let i = 0; i <= segs; i++) {
      const a = start + (i / segs) * this.ATRIUM_SPAN;
      pos.push(r * Math.cos(a), y0, r * Math.sin(a), r * Math.cos(a), y1, r * Math.sin(a));
      uv.push(i / segs, 0, i / segs, 1);
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

  /** Outdoor umbrella dining on lawn in front of Caffè Macs. */
  private static addOutdoorMeadowTerrace(group: THREE.Group, woodMat: THREE.Material): void {
    const canvasMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.5 });
    const poleMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.7 });

    for (let u = -3; u <= 3; u++) {
      const angle = this.ATRIUM_ANGLE + u * 0.045;
      const ux = (this.R_IN - 8) * Math.cos(angle);
      const uz = (this.R_IN - 8) * Math.sin(angle);

      // Umbrella pole & canvas canopy
      const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 3.2, 8), poleMat);
      pole.position.set(ux, 1.6, uz);
      const canopy = new THREE.Mesh(new THREE.ConeGeometry(2.2, 0.8, 14), canvasMat);
      canopy.position.set(ux, 3.0, uz);

      // Round outdoor table & 4 chairs
      const table = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 0.9, 0.08, 16), woodMat);
      table.position.set(ux, 0.74, uz);
      table.castShadow = true;

      group.add(pole, canopy, table);
    }
  }
}
