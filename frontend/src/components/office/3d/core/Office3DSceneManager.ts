/**
 * 3D WebGL Scene & Renderer Manager for Apple Park Campus Simulator.
 * Handles renderer lifecycle, antialiasing, cinematic lighting, and ACESFilmic tone mapping.
 */

import * as THREE from "three";
import { OfficePostProcessing } from "./OfficePostProcessing";

export class Office3DSceneManager {
  public scene: THREE.Scene;
  public renderer: THREE.WebGLRenderer;
  public camera: THREE.PerspectiveCamera;
  public dirLight: THREE.DirectionalLight;
  public postProcessing: OfficePostProcessing;
  private container: HTMLElement;

  constructor(container: HTMLElement) {
    this.container = container;

    // 1. Initialize Scene & Atmospheric Horizon Fog
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color("#38bdf8");
    this.scene.fog = new THREE.Fog("#38bdf8", 180, 850);

    // 2. Initialize Perspective Camera with Cinematic Apple Park Overview
    const width = container.clientWidth || 1280;
    const height = container.clientHeight || 720;
    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 2500);
    this.camera.position.set(0, 110, 160);

    // 3. Initialize WebGLRenderer with RTX Shadow & PBR Tone Mapping
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: "high-performance",
    });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;

    this.renderer.domElement.style.width = "100%";
    this.renderer.domElement.style.height = "100%";
    this.renderer.domElement.style.display = "block";
    container.appendChild(this.renderer.domElement);

    // 4. Setup Lighting & Unreal Cinematic Post-Processing
    this.dirLight = this.setupLighting();
    this.postProcessing = new OfficePostProcessing(this.renderer, this.scene, this.camera, width, height);

    // 5. Setup Resize Listener
    window.addEventListener("resize", this.handleResize);
  }

  private setupLighting(): THREE.DirectionalLight {
    // 1. Main directional sunlight with soft RTX penumbra shadows
    const dirLight = new THREE.DirectionalLight(0xfffbeb, 1.35);
    dirLight.position.set(120, 180, 90);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 10;
    dirLight.shadow.camera.far = 550;
    dirLight.shadow.camera.left = -240;
    dirLight.shadow.camera.right = 240;
    dirLight.shadow.camera.top = 240;
    dirLight.shadow.camera.bottom = -240;
    dirLight.shadow.bias = -0.0004;
    dirLight.shadow.radius = 2.5;
    this.scene.add(dirLight);

    // 2. Realistic Sky/Ground Ambient Bounce (Global Illumination Fill)
    const hemiLight = new THREE.HemisphereLight(0xbae6fd, 0x1e293b, 0.45);
    hemiLight.position.set(0, 200, 0);
    this.scene.add(hemiLight);

    return dirLight;
  }

  public handleResize = (): void => {
    if (!this.container) return;
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.postProcessing.setSize(width, height);
  };

  public render(): void {
    this.postProcessing.render(this.renderer, this.scene, this.camera);
  }

  public destroy(): void {
    window.removeEventListener("resize", this.handleResize);
    this.postProcessing.dispose();
    this.scene.traverse((obj) => {
      if ((obj as THREE.Mesh).isMesh) {
        const mesh = obj as THREE.Mesh;
        mesh.geometry?.dispose();
        if (Array.isArray(mesh.material)) {
          mesh.material.forEach((m) => m.dispose());
        } else if (mesh.material) {
          mesh.material.dispose();
        }
      }
    });
    if (this.renderer.domElement && this.renderer.domElement.parentNode) {
      this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
    }
    this.renderer.dispose();
  }
}
