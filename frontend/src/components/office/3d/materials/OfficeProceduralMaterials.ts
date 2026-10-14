/**
 * Procedural Canvas Textures & PBR Materials Factory for Apple Park Simulator.
 * Generates blonde oak, granite pavers, solar panels, and physical glass in-memory without external assets.
 */

import * as THREE from "three";

export class OfficeProceduralMaterials {
  private static cachedTextures: Map<string, THREE.CanvasTexture> = new Map();

  /** Generates procedural blonde white oak wood grain texture. */
  public static getBlondeOakTexture(): THREE.CanvasTexture {
    const key = "blonde_oak";
    if (this.cachedTextures.has(key)) return this.cachedTextures.get(key)!;

    const canvas = document.createElement("canvas");
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext("2d");
    if (!ctx) return new THREE.CanvasTexture(canvas);

    // Warm Scandinavian blonde base
    ctx.fillStyle = "#ebd5b3";
    ctx.fillRect(0, 0, 512, 512);

    // Subtle grain lines
    ctx.fillStyle = "rgba(180, 140, 95, 0.12)";
    for (let i = 0; i < 512; i += 4) {
      const offset = Math.sin(i * 0.05) * 8;
      ctx.fillRect(0, i + offset, 512, 2);
    }

    // Plank gaps
    ctx.strokeStyle = "rgba(130, 95, 60, 0.25)";
    ctx.lineWidth = 1.5;
    for (let x = 64; x < 512; x += 64) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, 512);
      ctx.stroke();
    }

    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
    tex.repeat.set(4, 4);
    this.cachedTextures.set(key, tex);
    return tex;
  }

  /** Generates decomposed granite paver texture for park pathways. */
  public static getGranitePaverTexture(): THREE.CanvasTexture {
    const key = "granite_paver";
    if (this.cachedTextures.has(key)) return this.cachedTextures.get(key)!;

    const canvas = document.createElement("canvas");
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext("2d");
    if (!ctx) return new THREE.CanvasTexture(canvas);

    ctx.fillStyle = "#dfd7ca";
    ctx.fillRect(0, 0, 256, 256);

    // Subtle mineral speckles
    for (let i = 0; i < 900; i++) {
      const g = Math.floor(Math.random() * 60) + 120;
      ctx.fillStyle = `rgba(${g}, ${g - 10}, ${g - 20}, 0.25)`;
      ctx.fillRect(Math.random() * 256, Math.random() * 256, 1.5, 1.5);
    }
    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    tex.repeat.set(8, 8);
    this.cachedTextures.set(key, tex);
    return tex;
  }

  /** Generates photovoltaic dark-blue solar panel grid texture. */
  public static getSolarGridTexture(): THREE.CanvasTexture {
    const key = "solar_grid_v4";
    if (this.cachedTextures.has(key)) return this.cachedTextures.get(key)!;
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = 512;
    const ctx = canvas.getContext("2d");
    if (!ctx) return new THREE.CanvasTexture(canvas);

    ctx.fillStyle = "#090d16";
    ctx.fillRect(0, 0, 512, 512);
    for (let x = 6; x < 512; x += 64) {
      for (let y = 6; y < 512; y += 64) {
        ctx.fillStyle = "#172554";
        ctx.fillRect(x, y, 52, 52);
        ctx.strokeStyle = "#1e40af";
        ctx.lineWidth = 1.5;
        ctx.strokeRect(x, y, 52, 52);
      }
    }
    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    tex.repeat.set(32, 4);
    this.cachedTextures.set(key, tex);
    return tex;
  }

  /** Generates procedural architectural glass panel texture with vertical silicone seams. */
  public static getArchitecturalGlassTexture(): THREE.CanvasTexture {
    const key = "arch_glass_v4";
    if (this.cachedTextures.has(key)) return this.cachedTextures.get(key)!;
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = 512;
    const ctx = canvas.getContext("2d");
    if (!ctx) return new THREE.CanvasTexture(canvas);

    ctx.fillStyle = "rgba(224, 242, 254, 0.1)";
    ctx.fillRect(0, 0, 512, 512);
    ctx.strokeStyle = "rgba(255, 255, 255, 0.45)";
    ctx.lineWidth = 2;
    for (let x = 128; x <= 512; x += 128) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, 512);
      ctx.stroke();
    }
    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    tex.repeat.set(1, 1);
    this.cachedTextures.set(key, tex);
    return tex;
  }

  /** Generates procedural micro-bump texture for oak planks. */
  public static getOakBumpMap(): THREE.CanvasTexture {
    const key = "oak_bump";
    if (this.cachedTextures.has(key)) return this.cachedTextures.get(key)!;
    const canvas = document.createElement("canvas");
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.fillStyle = "#808080";
      ctx.fillRect(0, 0, 256, 256);
      ctx.fillStyle = "#555555";
      for (let i = 0; i < 256; i += 6) {
        ctx.fillRect(0, i + Math.sin(i * 0.1) * 2, 256, 1.5);
      }
    }
    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
    tex.repeat.set(4, 4);
    this.cachedTextures.set(key, tex);
    return tex;
  }

  /** Returns pristine physical Apple-grade curved glass material with true PBR refraction. */
  public static createAppleGlassMaterial(): THREE.MeshPhysicalMaterial {
    return new THREE.MeshPhysicalMaterial({
      color: 0xbae6fd,
      transparent: true,
      opacity: 0.26,
      roughness: 0.03,
      metalness: 0.08,
      reflectivity: 0.85,
      clearcoat: 1.0,
      clearcoatRoughness: 0.03,
      ior: 1.52,
      side: THREE.DoubleSide,
      depthWrite: false,
    });
  }

  /** Returns crisp satin off-white finish for architectural canopy fins. */
  public static createCanopyFinMaterial(): THREE.MeshStandardMaterial {
    return new THREE.MeshStandardMaterial({
      color: 0xf8fafc,
      roughness: 0.22,
      metalness: 0.25,
    });
  }

  /** Returns titanium brushed metal material for window mullions and frames. */
  public static createTitaniumFrameMaterial(): THREE.MeshStandardMaterial {
    return new THREE.MeshStandardMaterial({
      color: 0x94a3b8,
      roughness: 0.32,
      metalness: 0.78,
    });
  }
}
