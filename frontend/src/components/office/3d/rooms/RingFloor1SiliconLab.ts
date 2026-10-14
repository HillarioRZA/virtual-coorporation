/**
 * Ring Floor 1: Silicon Engineering Lab & Hardware Diagnostics Center.
 * Houses 4 team engineering clusters (FE, BE, QA, DevSecOps), diagnostics rack,
 * breakout huddle lounge, and the central 4-story glass elevator shaft.
 */

import * as THREE from "three";
import { OfficeProceduralMaterials } from "../materials/OfficeProceduralMaterials";

export class RingFloor1SiliconLab {
  private static readonly R_MID = 117.0; // Mid-radius of The Grand Ring (R_in=98, R_out=136)

  /** Builds the complete Floor 1 Silicon Lab engineering wing. */
  public static buildLab(): THREE.Group {
    const labGroup = new THREE.Group();
    labGroup.name = "Ring_Floor1_SiliconLab";

    const deskMat = new THREE.MeshStandardMaterial({
      map: OfficeProceduralMaterials.getBlondeOakTexture(),
      roughness: 0.45,
    });
    const legMat = OfficeProceduralMaterials.createTitaniumFrameMaterial();
    const glassMat = OfficeProceduralMaterials.createAppleGlassMaterial();

    // 1. Engineering Pods: FE, BE, QA, DevSecOps double-sided team clusters
    const angles = [-0.8, -0.4, 0.4, 0.8];
    const roles = ["role_fe", "role_be", "role_qa", "role_devsecops"];
    const labels = ["Frontend Pod", "Backend Pod", "QA Security Pod", "DevSecOps Pod"];

    for (let i = 0; i < angles.length; i++) {
      const theta = angles[i];
      const pod = this.createEngineeringCluster(deskMat, legMat, glassMat, roles[i], labels[i]);
      pod.position.set(Math.cos(theta) * this.R_MID, 0, Math.sin(theta) * this.R_MID);
      pod.rotation.y = -theta + Math.PI / 2;
      labGroup.add(pod);
    }

    // Diagnostics Bench & Breakout Huddle
    const diagBench = this.createDiagnosticsBench(deskMat, legMat);
    diagBench.position.set(Math.cos(0.0) * (this.R_MID + 6.0), 0, Math.sin(0.0) * (this.R_MID + 6.0));
    diagBench.rotation.y = Math.PI / 2;
    labGroup.add(diagBench);

    const huddle = this.createBreakoutHuddle(glassMat, deskMat);
    huddle.position.set(Math.cos(-0.15) * (this.R_MID - 6.5), 0, Math.sin(-0.15) * (this.R_MID - 6.5));
    huddle.rotation.y = 0.15 + Math.PI / 2;
    labGroup.add(huddle);

    const elevatorShaft = this.createAtriumElevator();
    elevatorShaft.position.set(Math.cos(0) * this.R_MID, 0, Math.sin(0) * this.R_MID);
    labGroup.add(elevatorShaft);

    return labGroup;
  }

  /** Constructs a double-sided 4-seat team pod with dual monitors & acoustic dividers. */
  private static createEngineeringCluster(
    topMat: THREE.Material,
    legMat: THREE.Material,
    glassMat: THREE.Material,
    roleId: string,
    label: string
  ): THREE.Group {
    const pod = new THREE.Group();
    pod.name = `Cluster_${roleId}`;

    const desk = new THREE.Mesh(new THREE.BoxGeometry(4.2, 0.08, 1.4), topMat);
    desk.position.y = 0.75;
    desk.castShadow = true;

    // Slim Titanium Leg Supports
    [-1.9, 0, 1.9].forEach((lx) => {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.74, 1.3), legMat);
      leg.position.set(lx, 0.37, 0);
      pod.add(leg);
    });

    // Central Frosted Acoustic Glass Privacy Divider (Height = 1.3m)
    const divider = new THREE.Mesh(new THREE.BoxGeometry(4.0, 0.45, 0.04), glassMat);
    divider.position.set(0, 1.0, 0);

    // 4 Workstation Monitors (2 facing North, 2 facing South)
    const screenMat = new THREE.MeshStandardMaterial({
      color: 0x0f172a,
      emissive: 0x0ea5e9,
      emissiveIntensity: 0.85,
    });
    [-1.1, 1.1].forEach((mx) => {
      const sN = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.6, 0.03), screenMat);
      sN.position.set(mx, 1.15, -0.22);
      const sS = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.6, 0.03), screenMat);
      sS.position.set(mx, 1.15, 0.22);
      pod.add(sN, sS);
    });

    // 4 Ergonomic Vitra Task Chairs
    const chairMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.5 });
    [-1.1, 1.1].forEach((cx) => {
      [-0.9, 0.9].forEach((cz) => {
        const chair = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.85, 0.55), chairMat);
        chair.position.set(cx, 0.45, cz);
        chair.rotation.y = cz > 0 ? Math.PI : 0;
        pod.add(chair);
      });
    });

    // Overhead Linear LED Light Troffer Bar (Y = 3.5m)
    const lightBar = new THREE.Mesh(
      new THREE.BoxGeometry(4.0, 0.06, 0.2),
      new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffedd5, emissiveIntensity: 0.9 })
    );
    lightBar.position.set(0, 3.5, 0);
    const podLight = new THREE.PointLight(0xffedd5, 1.8, 14, 1.3);
    podLight.position.set(0, 3.2, 0);
    pod.add(desk, divider, lightBar, podLight);
    return pod;
  }

  /** Constructs hardware testing workbench with oscilloscope rack and LED blinkers. */
  private static createDiagnosticsBench(topMat: THREE.Material, legMat: THREE.Material): THREE.Group {
    const bench = new THREE.Group();
    const desk = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.08, 1.0), topMat);
    desk.position.y = 0.75;

    const rackMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.8, roughness: 0.3 });
    const rack = new THREE.Mesh(new THREE.BoxGeometry(2.8, 0.9, 0.35), rackMat);
    rack.position.set(0, 1.25, -0.3);

    const oscScreen = new THREE.Mesh(
      new THREE.BoxGeometry(1.2, 0.45, 0.02),
      new THREE.MeshStandardMaterial({ color: 0x022c22, emissive: 0x10b981, emissiveIntensity: 0.9 })
    );
    oscScreen.position.set(-0.6, 1.25, -0.12);

    const ledArray = new THREE.Mesh(
      new THREE.BoxGeometry(0.8, 0.15, 0.02),
      new THREE.MeshStandardMaterial({ color: 0x450a0a, emissive: 0xef4444, emissiveIntensity: 0.9 })
    );
    ledArray.position.set(0.6, 1.25, -0.12);

    bench.add(desk, rack, oscScreen, ledArray);
    return bench;
  }

  /** Constructs a collaborative breakout huddle with low oak table and glass whiteboard. */
  private static createBreakoutHuddle(glassMat: THREE.Material, oakMat: THREE.Material): THREE.Group {
    const huddle = new THREE.Group();
    const board = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.8, 0.05), glassMat);
    board.position.set(0, 1.1, -1.8);

    const table = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.8, 0.35, 24), oakMat);
    table.position.set(0, 0.18, 0);

    const chairMat = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.8 });
    [0, (Math.PI * 2) / 3, (Math.PI * 4) / 3].forEach((ang) => {
      const chair = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.6, 0.65), chairMat);
      chair.position.set(Math.cos(ang) * 1.5, 0.3, Math.sin(ang) * 1.5);
      chair.rotation.y = -ang - Math.PI / 2;
      huddle.add(chair);
    });

    huddle.add(board, table);
    return huddle;
  }

  /** Constructs central 4-story cylindrical glass elevator shaft connecting Fl 1 to Fl 4. */
  private static createAtriumElevator(): THREE.Group {
    const shaft = new THREE.Group();
    const glassMat = OfficeProceduralMaterials.createAppleGlassMaterial();
    const frameMat = OfficeProceduralMaterials.createTitaniumFrameMaterial();

    const glassTube = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 2.2, 16, 24, 1, true), glassMat);
    glassTube.position.y = 8.0;
    shaft.add(glassTube);

    for (let fl = 0; fl <= 4; fl++) {
      const ring = new THREE.Mesh(new THREE.TorusGeometry(2.25, 0.06, 8, 24), frameMat);
      ring.rotateX(Math.PI / 2);
      ring.position.y = fl * 4.0;
      shaft.add(ring);
    }

    const carMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.65,
      emissive: 0x0284c7,
      emissiveIntensity: 0.35,
    });
    const car = new THREE.Mesh(new THREE.CylinderGeometry(1.95, 1.95, 2.8, 16), carMat);
    car.name = "ElevatorCar_Ring";
    car.position.y = 1.4;
    shaft.add(car);

    return shaft;
  }
}

