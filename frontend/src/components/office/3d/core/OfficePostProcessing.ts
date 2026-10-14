/**
 * Cinematic Post-Processing Pipeline for 80% Realistic RTX / Cyberpunk Look.
 * Encapsulates Three.js EffectComposer, RenderPass, and UnrealBloomPass.
 * Features selective threshold bloom for LED troffers, server racks, and sun glares.
 */

import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";

export class OfficePostProcessing {
  private composer: EffectComposer;
  private renderPass: RenderPass;
  private bloomPass: UnrealBloomPass;
  public isEnabled = true;

  constructor(
    renderer: THREE.WebGLRenderer,
    scene: THREE.Scene,
    camera: THREE.PerspectiveCamera,
    width: number,
    height: number
  ) {
    this.composer = new EffectComposer(renderer);

    // 1. Base Scene Render Pass
    this.renderPass = new RenderPass(scene, camera);
    this.composer.addPass(this.renderPass);

    // 2. High-Fidelity Unreal Bloom Pass (Half-resolution buffer for 60-120 FPS performance)
    const bloomRes = new THREE.Vector2(Math.floor(width / 2), Math.floor(height / 2));
    this.bloomPass = new UnrealBloomPass(bloomRes, 0.36, 0.42, 0.82);
    this.composer.addPass(this.bloomPass);
  }

  /**
   * Resizes the composer render buffers matching canvas viewport.
   * @param width Canvas width in pixels.
   * @param height Canvas height in pixels.
   */
  public setSize(width: number, height: number): void {
    this.composer.setSize(width, height);
    const bloomW = Math.floor(width / 2);
    const bloomH = Math.floor(height / 2);
    this.bloomPass.resolution.set(bloomW, bloomH);
  }

  /**
   * Renders the post-processed scene frame, or falls back to raw render.
   * @param renderer Fallback WebGL renderer.
   * @param scene Three.js scene.
   * @param camera Active perspective camera.
   */
  public render(renderer: THREE.WebGLRenderer, scene: THREE.Scene, camera: THREE.PerspectiveCamera): void {
    if (this.isEnabled) {
      this.composer.render();
    } else {
      renderer.render(scene, camera);
    }
  }

  /**
   * Adjusts bloom intensity for day vs. night atmospheric contrast.
   * @param strength Bloom glow intensity multiplier (e.g. 0.25 day, 0.45 night).
   */
  public setBloomStrength(strength: number): void {
    this.bloomPass.strength = Math.max(0.1, Math.min(1.2, strength));
  }

  /** Cleans up GPU render targets upon canvas destruction. */
  public dispose(): void {
    this.composer.passes.forEach((p) => {
      if ("dispose" in p && typeof (p as { dispose: () => void }).dispose === "function") {
        (p as { dispose: () => void }).dispose();
      }
    });
  }
}
