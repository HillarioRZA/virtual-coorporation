/**
 * Real-Time 24-Hour Day-to-Night Timeline & Dynamic Atmosphere Engine.
 * Manages natural sun orbit, PBR shadow penumbra, celestial bodies, clouds, and fog.
 */

import * as THREE from "three";
import { OfficeSkyAtmosphere } from "./OfficeSkyAtmosphere";
import { OfficeEnvGenerator } from "./OfficeEnvGenerator";

export class OfficeSkyTimeline {
  public currentHour = 10.5; // Starts at pleasant mid-morning
  private dayDurationSeconds = 1080; // 18 minutes per full 24h day
  private sunLight: THREE.DirectionalLight;
  private hemiLight: THREE.HemisphereLight;
  private ambientLight: THREE.AmbientLight;
  private starDome: THREE.Points;
  private atmosphere: OfficeSkyAtmosphere;

  constructor(scene: THREE.Scene, sun: THREE.DirectionalLight, private renderer?: THREE.WebGLRenderer) {
    this.sunLight = sun;

    // Enhanced PBR soft shadow parameters
    this.sunLight.castShadow = true;
    this.sunLight.shadow.radius = 2.5;
    this.sunLight.shadow.bias = -0.0003;
    this.sunLight.shadow.normalBias = 0.02;

    this.hemiLight = new THREE.HemisphereLight(0xffffff, 0x1e293b, 0.9);
    this.hemiLight.position.set(0, 50, 0);
    scene.add(this.hemiLight);

    this.ambientLight = new THREE.AmbientLight(0xffffff, 0.55);
    scene.add(this.ambientLight);

    this.starDome = this.createStarDome();
    scene.add(this.starDome);

    this.atmosphere = new OfficeSkyAtmosphere();
    scene.add(this.atmosphere.group);

    this.applyAtmosphere(scene);
  }

  /** Advances the real-time simulation clock and smoothly updates atmospheric lighting. */
  public update(delta: number, scene: THREE.Scene, camPos?: THREE.Vector3): void {
    const hoursElapsed = (delta / this.dayDurationSeconds) * 24;
    this.currentHour = (this.currentHour + hoursElapsed) % 24;
    this.applyAtmosphere(scene, camPos);
  }

  /** Sets the exact virtual clock hour (0 to 24) from user slider or presets. */
  public setTime(hour: number, scene: THREE.Scene, camPos?: THREE.Vector3): void {
    this.currentHour = Math.max(0, Math.min(24, hour));
    this.applyAtmosphere(scene, camPos);
  }

  /** Computes realistic PBR lighting, sun color temperature, fog, and celestial states. */
  private applyAtmosphere(scene: THREE.Scene, camPos?: THREE.Vector3): void {
    const angle = ((this.currentHour - 6) / 24) * Math.PI * 2;
    this.sunLight.position.set(Math.cos(angle) * 380, Math.max(-5, Math.sin(angle) * 320), Math.sin(angle * 0.5) * 220);

    if (camPos) {
      this.starDome.position.copy(camPos);
    }

    // True astronomical celestial positions (R = 1350m relative to camera)
    const celSunPos = new THREE.Vector3(
      Math.cos(angle) * 1350,
      Math.sin(angle) * 1150,
      Math.sin(angle * 0.5) * 850
    );
    if (camPos) celSunPos.add(camPos);
    this.atmosphere.update(0.016, celSunPos, this.currentHour, camPos || new THREE.Vector3(0, 0, 0));

    const isDawn = this.currentHour >= 5.5 && this.currentHour < 8.5;
    const isDusk = this.currentHour >= 16.5 && this.currentHour < 19.5;
    const isNight = this.currentHour >= 19.5 || this.currentHour < 5.5;

    let skyColor = new THREE.Color("#38bdf8");
    let sunColor = new THREE.Color("#fffaf0");
    let sunIntensity = 2.4;
    let starOpacity = 0.0;

    if (isDawn) {
      skyColor.set("#fed7aa"); // Warm peach/gold
      sunColor.set("#ff9e43"); // 2800K sunrise gold
      sunIntensity = 1.6;
    } else if (isDusk) {
      skyColor.set("#fb7185"); // Rich twilight rose
      sunColor.set("#ff6b35"); // 2200K fiery amber
      sunIntensity = 1.9;
      starOpacity = 0.35;
    } else if (isNight) {
      skyColor.set("#050c1e"); // Deep midnight navy-indigo
      sunColor.set("#93c5fd"); // Soft moon cyan
      sunIntensity = 0.35;
      starOpacity = 0.95;
    }

    scene.background = skyColor;
    if (scene.fog) {
      scene.fog.color = skyColor;
    }

    // Dynamic PMREM Radiance Environment Map & Reflections
    if (this.renderer) {
      const horizonHex = isDawn ? "#fed7aa" : isDusk ? "#fb7185" : isNight ? "#0f172a" : "#e0f2fe";
      const groundHex = isNight ? "#020617" : "#365f32";
      scene.environment = OfficeEnvGenerator.generateEnvironmentMap(
        this.renderer,
        "#" + skyColor.getHexString(),
        horizonHex,
        groundHex
      );
    }

    this.sunLight.color = sunColor;
    this.sunLight.intensity = sunIntensity;
    this.hemiLight.color = skyColor;
    this.hemiLight.intensity = isNight ? 0.35 : 0.85;
    this.ambientLight.intensity = isNight ? 0.25 : 0.6;

    const starMat = this.starDome.material as THREE.PointsMaterial;
    starMat.opacity = THREE.MathUtils.lerp(starMat.opacity, starOpacity, 0.1);
  }

  /** Generates realistic infinite celestial starfield at astronomical distance (R=1420m). */
  private createStarDome(): THREE.Points {
    const starCount = 2200;
    const starGeo = new THREE.BufferGeometry();
    const starPos = new Float32Array(starCount * 3);
    const starColors = new Float32Array(starCount * 3);

    for (let i = 0; i < starCount; i++) {
      const idx = i * 3;
      const u = Math.random();
      const v = Math.random();
      const theta = u * Math.PI * 2;
      const phi = Math.acos(v); // Upper hemisphere only (0 to PI/2)
      const r = 1400 + Math.random() * 40;

      // Realistic spherical distribution across infinite celestial canopy
      starPos[idx] = r * Math.sin(phi) * Math.cos(theta);
      starPos[idx + 1] = r * Math.cos(phi);
      starPos[idx + 2] = r * Math.sin(phi) * Math.sin(theta);

      // Subtle astronomical spectral colors (O, B, A, G, K star classes)
      const cRand = Math.random();
      if (cRand > 0.85) {
        starColors[idx] = 0.85; starColors[idx + 1] = 0.92; starColors[idx + 2] = 1.0;
      } else if (cRand > 0.7) {
        starColors[idx] = 1.0; starColors[idx + 1] = 0.95; starColors[idx + 2] = 0.75;
      } else {
        starColors[idx] = 1.0; starColors[idx + 1] = 1.0; starColors[idx + 2] = 1.0;
      }
    }

    starGeo.setAttribute("position", new THREE.BufferAttribute(starPos, 3));
    starGeo.setAttribute("color", new THREE.BufferAttribute(starColors, 3));

    const starMat = new THREE.PointsMaterial({
      size: 3.2,
      vertexColors: true,
      transparent: true,
      opacity: 0.0,
      depthWrite: false,
      fog: false,
    });
    return new THREE.Points(starGeo, starMat);
  }

  /** Formats virtual time for UI display (e.g. '07:30 [Pagi]'). */
  public getTimeString(): string {
    const h = Math.floor(this.currentHour);
    const m = Math.floor((this.currentHour - h) * 60);
    const padH = h.toString().padStart(2, "0");
    const padM = m.toString().padStart(2, "0");

    let tag = "Pagi";
    if (h >= 11 && h < 15) tag = "Siang";
    else if (h >= 15 && h < 19) tag = "Sore";
    else if (h >= 19 || h < 5) tag = "Malam";

    return `${padH}:${padM} [${tag}]`;
  }
}
