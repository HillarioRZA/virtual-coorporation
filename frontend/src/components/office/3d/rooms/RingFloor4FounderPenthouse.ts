/**
 * Ring Floor 4: Founder's Apex Omni-Panoramic Penthouse Suite.
 * Cozy ultra-luxury walnut & Calacatta marble finishes, fluid titanium command desk,
 * tri-holographic floating HUDs, curved bouclé lounge, zen hearth, VIP bar, and sky balcony.
 */

import * as THREE from "three";
import { OfficeProceduralMaterials } from "../materials/OfficeProceduralMaterials";

export class RingFloor4FounderPenthouse {
  public static readonly PENTHOUSE_ELEVATION = 12.0; // Top Floor (Fl 4)
  private static readonly R_MID = 117.0; // Mid-radius of The Grand Ring (R_in=98, R_out=136)

  /** Builds the complete Founder's Apex Penthouse Suite on Floor 4. */
  public static buildPenthouse(): THREE.Group {
    const penthouse = new THREE.Group();
    penthouse.name = "Ring_Floor4_FounderPenthouse";
    penthouse.position.set(0, this.PENTHOUSE_ELEVATION, 0);

    const walnutMat = new THREE.MeshStandardMaterial({ color: 0x1f130b, roughness: 0.3 });
    const calacattaMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.2, metalness: 0.05 });
    const titaniumMat = OfficeProceduralMaterials.createTitaniumFrameMaterial();

    // 1. Luxury Parquet & Marble Floor Zone (Center sector angle = 0, East)
    const floorCenter = new THREE.Group();
    floorCenter.position.set(this.R_MID, 0.02, 0);

    const rugMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.85 });
    const cashmereRug = new THREE.Mesh(new THREE.CylinderGeometry(7.0, 7.0, 0.03, 32), rugMat);
    cashmereRug.receiveShadow = true;
    floorCenter.add(cashmereRug);

    // 2. Fluid Titanium & Dark Walnut Founder Command Island
    floorCenter.add(this.createFounderCommandIsland(walnutMat, titaniumMat));

    // 3. Tri-Holographic Panoramic Floating Displays
    floorCenter.add(this.createTriHolographicFeed());

    // 4. Cozy Executive Bouclé Lounge & Linear Zen Flame Hearth
    floorCenter.add(this.createCozyLoungeAndHearth(calacattaMat));

    // 5. VIP Private Bar & Espresso Credenza
    floorCenter.add(this.createVipPrivateBar(walnutMat, calacattaMat));

    // Warm Ambient Cove Illumination
    const coveLight = new THREE.PointLight(0xfff7ed, 3.2, 35, 1.2);
    coveLight.position.set(0, 3.2, 0);
    floorCenter.add(coveLight);

    // 6. Private Frameless Glass Sky Balcony overlooking Central Meadow
    penthouse.add(this.createSkyObservationBalcony());
    penthouse.add(floorCenter);

    return penthouse;
  }

  /** Constructs the fluid organic command desk for the Founder. */
  private static createFounderCommandIsland(woodMat: THREE.Material, metalMat: THREE.Material): THREE.Group {
    const island = new THREE.Group();
    island.name = "Founder_Command_Island";
    island.position.set(0, 0, -1.2);

    const deskTop = new THREE.Mesh(new THREE.CylinderGeometry(2.6, 2.8, 0.12, 32, 1, false, -0.9, 1.8), woodMat);
    deskTop.scale.set(1.15, 1.0, 0.55);
    deskTop.position.y = 0.74;
    deskTop.castShadow = true;

    [-1.5, 1.5].forEach((px) => {
      const ped = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.4, 0.74, 16), metalMat);
      ped.position.set(px, 0.37, 0);
      island.add(ped);
    });

    const leatherMat = new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.4 });
    const chair = new THREE.Mesh(new THREE.BoxGeometry(0.75, 1.2, 0.72), leatherMat);
    chair.position.set(0, 0.65, 0.7);
    chair.castShadow = true;

    island.add(deskTop, chair);
    return island;
  }

  /** Constructs 3 curved holographic telemetry displays floating above desk. */
  private static createTriHolographicFeed(): THREE.Group {
    const holo = new THREE.Group();
    holo.position.set(0, 1.45, -1.8);

    const holoMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      emissive: 0x0284c7,
      emissiveIntensity: 0.95,
      transparent: true,
      opacity: 0.7,
      roughness: 0.1,
    });
    const goldHolo = new THREE.MeshStandardMaterial({
      color: 0xfbbf24,
      emissive: 0xd97706,
      emissiveIntensity: 0.95,
      transparent: true,
      opacity: 0.7,
      roughness: 0.1,
    });

    const centerScreen = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.95, 0.02), goldHolo);
    const leftScreen = new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.8, 0.02), holoMat);
    leftScreen.position.set(-1.6, 0, 0.2);
    leftScreen.rotation.y = 0.3;
    const rightScreen = new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.8, 0.02), holoMat);
    rightScreen.position.set(1.6, 0, 0.2);
    rightScreen.rotation.y = -0.3;

    holo.add(centerScreen, leftScreen, rightScreen);
    return holo;
  }

  /** Constructs curved bouclé lounge sofa, Calacatta marble table, and zen flame hearth. */
  private static createCozyLoungeAndHearth(marbleMat: THREE.Material): THREE.Group {
    const lounge = new THREE.Group();
    lounge.position.set(0, 0, 2.8);

    const boucleMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.9 });
    const sofa = new THREE.Mesh(new THREE.CylinderGeometry(2.8, 2.8, 0.48, 24, 1, false, 0.6, 1.9), boucleMat);
    sofa.position.set(0, 0.24, 0);

    const table = new THREE.Mesh(new THREE.CylinderGeometry(0.95, 0.95, 0.32, 24), marbleMat);
    table.position.set(0, 0.16, -1.1);

    const hearthBase = new THREE.Mesh(
      new THREE.BoxGeometry(2.6, 0.38, 0.6),
      new THREE.MeshStandardMaterial({ color: 0x090d16, roughness: 0.4 })
    );
    hearthBase.position.set(0, 0.19, -2.5);

    const flameMesh = new THREE.Mesh(
      new THREE.BoxGeometry(2.0, 0.14, 0.16),
      new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xd97706, emissiveIntensity: 1.5 })
    );
    flameMesh.position.set(0, 0.42, -2.5);

    const fireLight = new THREE.PointLight(0xf59e0b, 2.2, 12, 1.5);
    fireLight.position.set(0, 0.8, -2.5);

    lounge.add(sofa, table, hearthBase, flameMesh, fireLight);
    return lounge;
  }

  /** Constructs VIP private beverage bar and marble credenza. */
  private static createVipPrivateBar(woodMat: THREE.Material, marbleMat: THREE.Material): THREE.Group {
    const bar = new THREE.Group();
    bar.position.set(0, 0, -4.5);

    const counter = new THREE.Mesh(new THREE.BoxGeometry(4.5, 1.05, 0.9), woodMat);
    counter.position.y = 0.525;
    const top = new THREE.Mesh(new THREE.BoxGeometry(4.6, 0.08, 0.95), marbleMat);
    top.position.y = 1.09;

    const espresso = new THREE.Mesh(
      new THREE.BoxGeometry(0.9, 0.55, 0.5),
      new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.9, roughness: 0.2 })
    );
    espresso.position.set(-1.2, 1.4, 0);

    bar.add(counter, top, espresso);
    return bar;
  }

  /** Constructs private sky observation balcony opening towards central meadow. */
  private static createSkyObservationBalcony(): THREE.Group {
    const balcony = new THREE.Group();
    const glassMat = OfficeProceduralMaterials.createAppleGlassMaterial();
    const deckMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.4 });

    const rIn = 98.0;
    const deckGeo = new THREE.RingGeometry(rIn - 3.2, rIn + 0.2, 32, 1, -0.25, 0.5);
    deckGeo.rotateX(-Math.PI / 2);
    const deck = new THREE.Mesh(deckGeo, deckMat);
    deck.position.y = 0.05;
    deck.receiveShadow = true;

    const railGeo = new THREE.CylinderGeometry(rIn - 3.2, rIn - 3.2, 1.25, 32, 1, true, -0.25, 0.5);
    const rail = new THREE.Mesh(railGeo, glassMat);
    rail.position.y = 0.65;

    balcony.add(deck, rail);
    return balcony;
  }
}
