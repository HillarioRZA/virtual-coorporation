/**
 * Procedural HDR Environment Map & Studio PMREM Skylight Generator.
 * Creates an in-memory 360-degree HDR radiance cube map for realistic PBR reflections.
 * Utilizes Three.js PMREMGenerator for physically-accurate rough/smooth sheen.
 */

import * as THREE from "three";

export class OfficeEnvGenerator {
  private static canvas: HTMLCanvasElement | null = null;
  private static ctx: CanvasRenderingContext2D | null = null;
  private static pmrem: THREE.PMREMGenerator | null = null;
  private static currentEnvMap: THREE.Texture | null = null;
  private static lastMoodKey = "";

  /**
   * Generates or retrieves cached PMREM radiance environment map.
   * @param renderer Active Three.js WebGLRenderer.
   * @param skyHex Color hex of sky zenith.
   * @param horizonHex Color hex of horizon haze.
   * @param groundHex Color hex of ground bounce.
   */
  public static generateEnvironmentMap(
    renderer: THREE.WebGLRenderer,
    skyHex: string,
    horizonHex: string,
    groundHex: string
  ): THREE.Texture {
    const moodKey = `${skyHex}_${horizonHex}_${groundHex}`;
    if (moodKey === this.lastMoodKey && this.currentEnvMap) {
      return this.currentEnvMap;
    }
    this.lastMoodKey = moodKey;

    if (!this.canvas && typeof document !== "undefined") {
      this.canvas = document.createElement("canvas");
      this.canvas.width = 1024;
      this.canvas.height = 512;
      this.ctx = this.canvas.getContext("2d");
    }

    if (!this.pmrem) {
      this.pmrem = new THREE.PMREMGenerator(renderer);
      this.pmrem.compileEquirectangularShader();
    }

    const ctx = this.ctx;
    if (ctx && this.canvas) {
      // 1. Hemispheric Sky-Horizon-Ground Gradient
      const grad = ctx.createLinearGradient(0, 0, 0, 512);
      grad.addColorStop(0.0, skyHex);
      grad.addColorStop(0.48, horizonHex);
      grad.addColorStop(0.52, "#334155");
      grad.addColorStop(1.0, groundHex);
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 1024, 512);

      // 2. High-Dynamic Range Specular Sun Hotspot
      const sunGrad = ctx.createRadialGradient(512, 220, 8, 512, 220, 180);
      sunGrad.addColorStop(0, "rgba(255, 255, 250, 1.0)");
      sunGrad.addColorStop(0.25, "rgba(254, 240, 138, 0.65)");
      sunGrad.addColorStop(0.6, "rgba(251, 146, 60, 0.25)");
      sunGrad.addColorStop(1.0, "rgba(251, 146, 60, 0.0)");
      ctx.fillStyle = sunGrad;
      ctx.fillRect(0, 0, 1024, 512);

      const rawTex = new THREE.CanvasTexture(this.canvas);
      rawTex.mapping = THREE.EquirectangularReflectionMapping;

      const renderTarget = this.pmrem.fromEquirectangular(rawTex);
      rawTex.dispose();

      if (this.currentEnvMap) this.currentEnvMap.dispose();
      this.currentEnvMap = renderTarget.texture;
      return renderTarget.texture;
    }

    return new THREE.Texture();
  }

  /** Cleans up GPU render targets upon application destruction. */
  public static dispose(): void {
    if (this.currentEnvMap) this.currentEnvMap.dispose();
    if (this.pmrem) this.pmrem.dispose();
    this.currentEnvMap = null;
    this.pmrem = null;
    this.lastMoodKey = "";
  }
}
