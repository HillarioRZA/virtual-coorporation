/**
 * Procedural Apple Park Parkland, Crystalline Reflection Pool & Curving Paths.
 * Mega-Park Scale: 320m lawn radius, 22m central pool, concentric promenades, and satellite avenues.
 */

import * as THREE from "three";
import { OfficeProceduralMaterials } from "../materials/OfficeProceduralMaterials";
import { OfficeTerrainElevation } from "./OfficeTerrainElevation";

export class OfficeTerrainPark {
  private static waterMesh: THREE.Mesh | null = null;

  /** Builds the entire campus mega-terrain, reflection pond, and pathways. */
  public static buildParkland(): THREE.Group {
    const parkGroup = new THREE.Group();
    parkGroup.name = "ApplePark_GroundAndPool_Mega";

    // 1. Grand Contoured Cupertino Parkland Lawn (R = 320m, Southern Hill Crest)
    const grassGeo = OfficeTerrainElevation.createContouredTerrainGeo(320, 96);
    const grassMat = new THREE.MeshStandardMaterial({
      color: 0x365f32,
      roughness: 0.85,
      metalness: 0.05,
    });
    const grassMesh = new THREE.Mesh(grassGeo, grassMat);
    grassMesh.receiveShadow = true;
    parkGroup.add(grassMesh);

    // 2. Smooth Circular Decomposed Granite Pathways
    const pathMat = new THREE.MeshStandardMaterial({
      map: OfficeProceduralMaterials.getGranitePaverTexture(),
      roughness: 0.7,
    });

    // Outer campus promenade loop (R = 148m to 154m, circling outside The Grand Ring)
    const outerLoop = new THREE.Mesh(new THREE.RingGeometry(148, 154, 96), pathMat);
    outerLoop.rotateX(-Math.PI / 2);
    outerLoop.position.set(0, 0.02, 0);
    outerLoop.receiveShadow = true;

    // Central meadow loop (R = 48m to 54m) around the reflection pool inside The Ring
    const innerLoop = new THREE.Mesh(new THREE.RingGeometry(48, 54, 64), pathMat);
    innerLoop.rotateX(-Math.PI / 2);
    innerLoop.position.set(0, 0.02, 0);
    innerLoop.receiveShadow = true;

    // Connecting avenues to Steve Jobs Theater (South) and Tantau (North)
    const aveTheater = new THREE.Mesh(new THREE.BoxGeometry(10.0, 0.02, 90.0), pathMat);
    aveTheater.position.set(40, 0.02, 190);
    const aveTantau = new THREE.Mesh(new THREE.BoxGeometry(10.0, 0.02, 90.0), pathMat);
    aveTantau.position.set(60, 0.02, -190);

    parkGroup.add(outerLoop, innerLoop, aveTheater, aveTantau);

    // 3. Central Courtyard Crystalline Reflection Pool (Radius = 22m)
    parkGroup.add(this.buildReflectionPool());

    // 4. Night LED Bollard Lights along outer promenade
    parkGroup.add(this.buildPathBollards());

    return parkGroup;
  }

  /** Constructs the serene sapphire reflection pool with travertine coping. */
  private static buildReflectionPool(): THREE.Group {
    const poolGroup = new THREE.Group();
    poolGroup.position.set(0, 0, 0);

    // Stepped Travertine Stone Coping Basin Rim (R = 24m)
    const rimGeo = new THREE.RingGeometry(21.5, 24.5, 64);
    rimGeo.rotateX(-Math.PI / 2);
    const rimMat = new THREE.MeshStandardMaterial({ color: 0xe7e5e4, roughness: 0.35 });
    const rim = new THREE.Mesh(rimGeo, rimMat);
    rim.position.y = 0.14;
    rim.receiveShadow = true;
    poolGroup.add(rim);

    // Crystalline Turquoise Sapphire Water Surface
    const waterGeo = new THREE.CircleGeometry(21.5, 64);
    waterGeo.rotateX(-Math.PI / 2);
    const waterMat = new THREE.MeshPhysicalMaterial({
      color: 0x0284c7,
      roughness: 0.05,
      metalness: 0.1,
      transmission: 0.75,
      ior: 1.333,
      reflectivity: 0.8,
      clearcoat: 1.0,
      clearcoatRoughness: 0.02,
    });
    this.waterMesh = new THREE.Mesh(waterGeo, waterMat);
    this.waterMesh.name = "ReflectionPoolWater";
    this.waterMesh.position.y = 0.1;
    this.waterMesh.receiveShadow = true;
    poolGroup.add(this.waterMesh);

    // Floating Sakura Blossom Petals on the Water
    const petalMat = new THREE.MeshStandardMaterial({ color: 0xfbcfe8, roughness: 0.6 });
    for (let p = 0; p < 36; p++) {
      const angle = (p / 36) * Math.PI * 2;
      const dist = 5.0 + ((p * 11) % 15.0);
      const petal = new THREE.Mesh(new THREE.CircleGeometry(0.38, 8), petalMat);
      petal.rotateX(-Math.PI / 2);
      petal.position.set(Math.cos(angle) * dist, 0.11, Math.sin(angle) * dist);
      poolGroup.add(petal);
    }

    // Teak Wood Minimalist Benches surrounding the pool
    const teakMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.5 });
    const legMat = new THREE.MeshStandardMaterial({ color: 0x1c1917, metalness: 0.8 });

    for (let i = 0; i < 12; i++) {
      const angle = (i / 12) * Math.PI * 2;
      const bx = Math.cos(angle) * 28.5;
      const bz = Math.sin(angle) * 28.5;

      const bench = new THREE.Group();
      const seat = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.1, 0.7), teakMat);
      seat.position.y = 0.44;
      seat.castShadow = true;

      const leg1 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.44, 0.55), legMat);
      leg1.position.set(-1.4, 0.22, 0);
      const leg2 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.44, 0.55), legMat);
      leg2.position.set(1.4, 0.22, 0);

      bench.add(seat, leg1, leg2);
      bench.position.set(bx, 0, bz);
      bench.rotation.y = -angle + Math.PI / 2;
      poolGroup.add(bench);
    }

    return poolGroup;
  }

  /** Generates minimalist LED pathway bollards along the outer concentric walkway. */
  private static buildPathBollards(): THREE.Group {
    const bollardGroup = new THREE.Group();
    bollardGroup.name = "PathBollardsGroup";

    const bollardMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.6 });
    const lampMat = new THREE.MeshStandardMaterial({ color: 0xfef08a, emissive: 0xfef08a, emissiveIntensity: 0.6 });

    for (let i = 0; i < 48; i++) {
      const angle = (i / 48) * Math.PI * 2;
      const px = Math.cos(angle) * 154.5;
      const pz = Math.sin(angle) * 154.5;

      const post = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.95, 8), bollardMat);
      post.position.set(px, 0.475, pz);
      const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.14, 8), lampMat);
      cap.position.set(px, 0.98, pz);

      bollardGroup.add(post, cap);
    }
    return bollardGroup;
  }

  /** Animates water ripples and subtle caustics reflection over time. */
  public static updateWater(time: number): void {
    if (!this.waterMesh) return;
    const mat = this.waterMesh.material as THREE.MeshPhysicalMaterial;
    mat.roughness = 0.04 + Math.sin(time * 0.002) * 0.02;
    this.waterMesh.position.y = 0.1 + Math.sin(time * 0.0015) * 0.008;
  }
}
