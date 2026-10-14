/**
 * Tantau R&D & SecOps Interior: Hardware Sandbox Testing Lab & Datacenter Vault.
 * 5x Scaled Interior: Diagnostic benchmark stations, airlock scanners, and 8 server monoliths at (60, 0, -230).
 */

import * as THREE from "three";

export class TantauDatacenterVault {
  public static readonly TANTAU_POS = new THREE.Vector3(60, 0, -230);

  /** Builds the 5x scaled Tantau interior: Fl 1 Sandbox Lab, Fl 2 Datacenter Vault. */
  public static buildTantauInterior(): THREE.Group {
    const group = new THREE.Group();
    group.name = "Tantau_Interior_Vault_5X";
    group.position.copy(this.TANTAU_POS);

    // 1. Floor 1: Sandbox Testing & Diagnostic Benchmark Lab (Y = 0.5m)
    const labGroup = this.createSandboxLab();
    labGroup.position.set(0, 0.5, 0);
    group.add(labGroup);

    // 2. Floor 2: High-Security Datacenter Server Vault (Y = 5.5m)
    const vaultGroup = this.createDatacenterVault();
    vaultGroup.position.set(0, 5.5, 0);
    group.add(vaultGroup);

    return group;
  }

  /** Constructs Floor 1 hardware sandbox, security scanner, and benchmark tables. */
  private static createSandboxLab(): THREE.Group {
    const lab = new THREE.Group();
    const tableMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.45, metalness: 0.3 });
    const monMat = new THREE.MeshStandardMaterial({
      color: 0x06b6d4,
      emissive: 0x06b6d4,
      emissiveIntensity: 0.85,
    });

    // 4 Diagnostic Testing Island Benches
    for (let i = 0; i < 4; i++) {
      const z = -10.0 + i * 6.5;
      const bench = new THREE.Mesh(new THREE.BoxGeometry(16.0, 0.9, 2.4), tableMat);
      bench.position.set(0, 0.45, z);
      bench.castShadow = true;

      // Multi-Monitor Benchmark Displays
      [-5.0, 0.0, 5.0].forEach((x) => {
        const mon = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.1, 0.06), monMat);
        mon.position.set(x, 1.5, z);
        lab.add(mon);
      });

      lab.add(bench);
    }

    // Security Scanner Post at Entrance (Z = +16.0m)
    const postMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.8 });
    const scannerMat = new THREE.MeshStandardMaterial({
      color: 0x10b981,
      emissive: 0x10b981,
      emissiveIntensity: 0.9,
    });

    [-3.2, 3.2].forEach((x) => {
      const post = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 3.2, 12), postMat);
      post.position.set(x, 1.6, 16.0);
      const ring = new THREE.Mesh(new THREE.TorusGeometry(0.24, 0.05, 8, 16), scannerMat);
      ring.position.set(x, 2.5, 16.0);
      lab.add(post, ring);
    });

    return lab;
  }

  /** Constructs Floor 2 Datacenter server racks with active fiber-optic LEDs. */
  private static createDatacenterVault(): THREE.Group {
    const vault = new THREE.Group();
    const rackMat = new THREE.MeshStandardMaterial({ color: 0x090d16, roughness: 0.25, metalness: 0.85 });
    const ledCyan = new THREE.MeshStandardMaterial({ color: 0x06b6d4, emissive: 0x06b6d4, emissiveIntensity: 1.3 });
    const ledGreen = new THREE.MeshStandardMaterial({ color: 0x10b981, emissive: 0x10b981, emissiveIntensity: 1.3 });

    // 8 Monolithic Server Cabinets
    for (let r = 0; r < 8; r++) {
      const x = -17.5 + r * 5.0;
      const rack = new THREE.Mesh(new THREE.BoxGeometry(2.8, 3.8, 10.0), rackMat);
      rack.position.set(x, 1.9, 0);
      rack.castShadow = true;
      vault.add(rack);

      // Active Pulsing Fiber-Optic Status LED Strips
      for (let s = 0; s < 8; s++) {
        const mat = (r + s) % 2 === 0 ? ledCyan : ledGreen;
        const led = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.14, 9.6), mat);
        led.position.set(x + 1.42, 0.5 + s * 0.45, 0);
        vault.add(led);
      }
    }

    // Overhead Cable Raceways
    const trayMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.7 });
    const tray = new THREE.Mesh(new THREE.BoxGeometry(38.0, 0.1, 1.2), trayMat);
    tray.position.set(0, 4.2, 0);
    vault.add(tray);

    // Docker Sandboxing Holographic Cage Boundary
    const cageMat = new THREE.MeshStandardMaterial({
      color: 0x0284c7,
      transparent: true,
      opacity: 0.2,
      roughness: 0.1,
    });
    const cage = new THREE.Mesh(new THREE.BoxGeometry(42.0, 4.0, 24.0), cageMat);
    cage.position.set(0, 2.0, 0);
    vault.add(cage);

    return vault;
  }
}
