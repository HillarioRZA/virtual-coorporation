/**
 * Photorealistic Celestial Atmosphere Engine: Realistic Sun with Atmospheric Corona,
 * High-Resolution Textured Moon with Cratered Maria, and Drifting Cumulus Clouds.
 * 100% Zero-Asset: Procedural lunar surface mapping & additive optical halos.
 */

import * as THREE from "three";

export class OfficeSkyAtmosphere {
  public group: THREE.Group;
  public sunGroup: THREE.Group;
  public moonGroup: THREE.Group;
  public cloudsGroup: THREE.Group;
  private sunCoreMat: THREE.MeshBasicMaterial;
  private sunCoronaMat: THREE.MeshBasicMaterial;
  private moonHaloMat: THREE.MeshBasicMaterial;
  private cloudMaterials: THREE.MeshStandardMaterial[] = [];

  constructor() {
    this.group = new THREE.Group();
    this.group.name = "ApplePark_CelestialAtmosphere_Realistic";

    // 1. Realistic Celestial Sun with Radiant Core & Atmospheric Corona
    this.sunGroup = new THREE.Group();
    this.sunCoreMat = new THREE.MeshBasicMaterial({ color: 0xffffff, fog: false });
    const sunCore = new THREE.Mesh(new THREE.SphereGeometry(22.0, 32, 32), this.sunCoreMat);
    const coronaTex = this.createRadialHalo("rgba(255, 255, 255, 1)", "rgba(254, 240, 138, 0.7)", "rgba(251, 146, 60, 0.25)");
    this.sunCoronaMat = new THREE.MeshBasicMaterial({
      map: coronaTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, fog: false, color: 0xfef08a, opacity: 0.85,
    });
    this.sunGroup.add(sunCore, new THREE.Mesh(new THREE.PlaneGeometry(180, 180), this.sunCoronaMat));
    this.group.add(this.sunGroup);

    // 2. Photorealistic Moon with Maria & Ethereal Blue-Silver Halo
    this.moonGroup = new THREE.Group();
    const moonMat = new THREE.MeshBasicMaterial({ map: this.createLunarSurfaceTexture(), fog: false });
    const moonGlowTex = this.createRadialHalo("rgba(224, 242, 254, 0.8)", "rgba(186, 230, 253, 0.35)", "rgba(147, 197, 253, 0.1)");
    this.moonHaloMat = new THREE.MeshBasicMaterial({
      map: moonGlowTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, fog: false, color: 0x93c5fd, opacity: 0.55,
    });
    this.moonGroup.add(new THREE.Mesh(new THREE.SphereGeometry(16.0, 32, 32), moonMat), new THREE.Mesh(new THREE.PlaneGeometry(120, 120), this.moonHaloMat));
    this.group.add(this.moonGroup);

    // 3. Drifting Cumulus Cloud Layer
    this.cloudsGroup = this.buildCloudCluster();
    this.group.add(this.cloudsGroup);
  }

  /** Generates procedural high-resolution lunar surface texture with maria & craters. */
  private createLunarSurfaceTexture(): THREE.CanvasTexture {
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = 512;
    const ctx = canvas.getContext("2d");
    if (!ctx) return new THREE.CanvasTexture(canvas);

    ctx.fillStyle = "#cbd5e1";
    ctx.fillRect(0, 0, 512, 512);

    // Basaltic dark maria (Oceanus Procellarum, Mare Serenitatis, etc.)
    ctx.fillStyle = "rgba(71, 85, 105, 0.45)";
    [[180, 170, 95, 75], [320, 210, 115, 90], [130, 280, 75, 65], [260, 340, 85, 75], [370, 130, 50, 40]].forEach(([x, y, rx, ry]) => {
      ctx.beginPath();
      ctx.ellipse(x, y, rx, ry, 0.35, 0, Math.PI * 2);
      ctx.fill();
    });

    // Tycho bright crater rays
    ctx.strokeStyle = "rgba(255, 255, 255, 0.25)";
    ctx.lineWidth = 1.2;
    for (let a = 0; a < 14; a++) {
      const angle = (a / 14) * Math.PI * 2;
      ctx.beginPath();
      ctx.moveTo(256, 410);
      ctx.lineTo(256 + Math.cos(angle) * 160, 410 + Math.sin(angle) * 160);
      ctx.stroke();
    }

    // Impact craters with shaded depth and lit rim
    for (let c = 0; c < 80; c++) {
      const cx = (c * 71) % 512, cy = (c * 97) % 512, cr = 3 + (c % 12);
      ctx.strokeStyle = "rgba(255, 255, 255, 0.75)";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(cx, cy, cr, Math.PI * 0.75, Math.PI * 1.75);
      ctx.stroke();
      ctx.strokeStyle = "rgba(30, 41, 59, 0.55)";
      ctx.beginPath();
      ctx.arc(cx, cy, cr, -Math.PI * 0.25, Math.PI * 0.75);
      ctx.stroke();
      ctx.fillStyle = "rgba(51, 65, 85, 0.35)";
      ctx.beginPath();
      ctx.arc(cx + 1, cy + 1, cr * 0.7, 0, Math.PI * 2);
      ctx.fill();
    }
    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    return tex;
  }

  /** Generates procedural radial halo / corona flare texture. */
  private createRadialHalo(c1: string, c2: string, c3: string): THREE.CanvasTexture {
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = 256;
    const ctx = canvas.getContext("2d");
    if (ctx) {
      const grad = ctx.createRadialGradient(128, 128, 10, 128, 128, 128);
      grad.addColorStop(0.0, c1);
      grad.addColorStop(0.3, c2);
      grad.addColorStop(0.65, c3);
      grad.addColorStop(1.0, "rgba(0, 0, 0, 0.0)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 256, 256);
    }
    return new THREE.CanvasTexture(canvas);
  }

  /** Constructs multi-tiered procedural drifting cloud puffs. */
  private buildCloudCluster(): THREE.Group {
    const clouds = new THREE.Group();
    clouds.name = "CumulusClouds";
    const puffGeo = new THREE.IcosahedronGeometry(12.0, 2);

    for (let i = 0; i < 22; i++) {
      const cMat = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        roughness: 0.95,
        transparent: true,
        opacity: 0.55,
        depthWrite: false,
      });
      this.cloudMaterials.push(cMat);

      const cloudPuff = new THREE.Mesh(puffGeo, cMat);
      const angle = (i / 22) * Math.PI * 2;
      const dist = 320 + (i % 4) * 80;
      cloudPuff.position.set(Math.cos(angle) * dist, 190 + (i % 3) * 25, Math.sin(angle) * dist);
      const sX = 4.2 + (i % 3) * 1.1;
      cloudPuff.scale.set(sX, 1.2, sX);
      clouds.add(cloudPuff);
    }
    return clouds;
  }

  /** Updates celestial bodies and cloud drift in real time relative to camera. */
  public update(delta: number, sunPos: THREE.Vector3, currentHour: number, camPos: THREE.Vector3): void {
    this.sunGroup.position.copy(sunPos);
    this.sunGroup.lookAt(camPos);

    const moonPos = new THREE.Vector3(
      camPos.x - (sunPos.x - camPos.x) * 0.95,
      camPos.y - (sunPos.y - camPos.y) + 120,
      camPos.z - (sunPos.z - camPos.z) * 0.95
    );
    this.moonGroup.position.copy(moonPos);
    this.moonGroup.lookAt(camPos);

    const isDawn = currentHour >= 5.5 && currentHour < 8.5;
    const isDusk = currentHour >= 16.5 && currentHour < 19.5;
    const isNight = currentHour >= 19.5 || currentHour < 5.5;

    this.sunGroup.visible = (sunPos.y - camPos.y) > -80;
    this.moonGroup.visible = (moonPos.y - camPos.y) > -20;

    if (isDawn) {
      this.sunCoreMat.color.setHex(0xffedd5);
      this.sunCoronaMat.color.setHex(0xfb923c);
      this.sunCoronaMat.opacity = 0.95;
    } else if (isDusk) {
      this.sunCoreMat.color.setHex(0xff6b35);
      this.sunCoronaMat.color.setHex(0xf43f5e);
      this.sunCoronaMat.opacity = 1.0;
    } else {
      this.sunCoreMat.color.setHex(0xffffff);
      this.sunCoronaMat.color.setHex(0xfef08a);
      this.sunCoronaMat.opacity = isNight ? 0.0 : 0.75;
    }

    this.moonHaloMat.opacity = isNight ? 0.65 : 0.15;

    // Cloud drift
    const windSpeed = delta * 3.5;
    this.cloudsGroup.children.forEach((cloud) => {
      cloud.position.x += windSpeed;
      if (cloud.position.x > 650) cloud.position.x = -650;
    });

    const cColor = isDawn ? 0xfed7aa : isDusk ? 0xfb7185 : isNight ? 0x1e293b : 0xffffff;
    this.cloudMaterials.forEach((m) => m.color.setHex(cColor));
  }
}
