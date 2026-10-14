/**
 * Steve Jobs Theater Subterranean Keynote Auditorium Interior & All-Hands Amphitheater.
 * 5x Enlarged Scale: 38m acoustic floor, colossal micro-LED backdrop, and tiered seating.
 */

import * as THREE from "three";

export class TheaterKeynoteAuditorium {
  public static readonly AUDITORIUM_POS = new THREE.Vector3(40, -8.0, 230);

  /** Builds the 5x scaled subterranean auditorium stage, backdrop, podium, and 13 agent seats. */
  public static buildAuditoriumInterior(): THREE.Group {
    const group = new THREE.Group();
    group.name = "SteveJobsTheater_Auditorium_Interior_5X";
    group.position.copy(this.AUDITORIUM_POS);

    // 1. Acoustic Slate Base Floor Slab (R = 38m)
    const baseMat = new THREE.MeshStandardMaterial({ color: 0x0b1120, roughness: 0.85 });
    const floor = new THREE.Mesh(new THREE.CylinderGeometry(38.0, 38.0, 0.6, 64), baseMat);
    floor.position.y = -0.3;
    floor.receiveShadow = true;
    group.add(floor);

    // 2. Colossal Curved Keynote Presentation Stage in Rich Dark Walnut Wood
    this.buildPresentationStage(group);

    // 3. Giant Curved Micro-LED Presentation Backdrop Screen
    this.buildCurvedKeynoteBackdrop(group);

    // 4. Tiered Concrete Amphitheater Risers
    this.buildAmphitheaterRisers(group);

    // 5. 13 Ergonomic Cognac Leather Amphitheater Seats for All-Hands Meeting
    this.buildAllHandsSeats(group);

    return group;
  }

  /** Constructs the curved keynote presentation stage and presenter podium. */
  private static buildPresentationStage(group: THREE.Group): void {
    const stageMat = new THREE.MeshStandardMaterial({ color: 0x2e1b0f, roughness: 0.35 });
    const stage = new THREE.Mesh(
      new THREE.CylinderGeometry(14.0, 14.0, 0.85, 48, 1, false, -Math.PI / 2, Math.PI),
      stageMat
    );
    stage.position.set(0, 0.425, -16.0);
    stage.receiveShadow = true;

    // Stage Front Edge LED Halo Strip
    const stripMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.8 });
    const strip = new THREE.Mesh(new THREE.RingGeometry(13.9, 14.15, 48, 1, 0, Math.PI), stripMat);
    strip.rotateX(-Math.PI / 2);
    strip.position.set(0, 0.86, -16.0);

    // Presenter Titanium Podium
    const podMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.4, metalness: 0.7 });
    const podium = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.3, 0.8), podMat);
    podium.position.set(0, 0.9, -15.0);
    podium.castShadow = true;

    // Glowing Retina Control Tablet
    const tabMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, emissive: 0x38bdf8, emissiveIntensity: 0.9 });
    const tablet = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.03, 0.55), tabMat);
    tablet.position.set(0, 1.56, -15.0);
    tablet.rotation.x = -0.3;

    group.add(stage, strip, podium, tablet);
  }

  /** Constructs giant curved micro-LED keynote backdrop display wall. */
  private static buildCurvedKeynoteBackdrop(group: THREE.Group): void {
    const screenMat = new THREE.MeshStandardMaterial({
      color: 0x0284c7,
      emissive: 0x0ea5e9,
      emissiveIntensity: 0.95,
      roughness: 0.2,
    });

    const screen = new THREE.Mesh(
      new THREE.CylinderGeometry(24.0, 24.0, 8.5, 64, 1, true, -Math.PI / 2 - 0.75, 1.5),
      screenMat
    );
    screen.position.set(0, 4.5, -17.0);

    // Top & Bottom Titanium Framing Bezels
    const frameMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.8 });
    [-0.2, 8.8].forEach((yOffset) => {
      const bezel = new THREE.Mesh(
        new THREE.CylinderGeometry(24.1, 24.1, 0.25, 64, 1, true, -Math.PI / 2 - 0.76, 1.52),
        frameMat
      );
      bezel.position.set(0, yOffset, -17.0);
      group.add(bezel);
    });

    group.add(screen);
  }

  /** Constructs tiered amphitheater curved concrete floor risers. */
  private static buildAmphitheaterRisers(group: THREE.Group): void {
    const riserMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6 });
    [
      { r: 16.0, w: 3.2, y: 0.35 },
      { r: 23.0, w: 3.2, y: 1.15 },
      { r: 30.0, w: 3.2, y: 1.95 },
    ].forEach((tier) => {
      const riser = new THREE.Mesh(
        new THREE.RingGeometry(tier.r - tier.w / 2, tier.r + tier.w / 2, 48, 1, 0, Math.PI),
        riserMat
      );
      riser.rotateX(-Math.PI / 2);
      riser.position.set(0, tier.y, -10.0);
      riser.receiveShadow = true;
      group.add(riser);
    });
  }

  /** Constructs 13 ergonomic caramel/cognac leather executive armchairs. */
  private static buildAllHandsSeats(group: THREE.Group): void {
    const leatherMat = new THREE.MeshStandardMaterial({ color: 0x9a3412, roughness: 0.55 });
    const legMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.75 });
    const seatPositions = this.calculateAllHandsSeating();

    seatPositions.forEach((pos, idx) => {
      const chair = new THREE.Group();
      chair.name = `AllHands_Seat_${idx}`;

      const cushion = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.2, 0.9), leatherMat);
      cushion.position.y = 0.65;
      cushion.castShadow = true;

      const back = new THREE.Mesh(new THREE.BoxGeometry(1.0, 1.1, 0.14), leatherMat);
      back.position.set(0, 1.2, 0.4);
      back.castShadow = true;

      const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.65, 8), legMat);
      leg.position.y = 0.325;

      chair.add(cushion, back, leg);
      chair.position.copy(pos.position);
      chair.rotation.y = pos.rotationY;
      group.add(chair);
    });
  }

  /** Calculates precise non-overlapping coordinates for 13 amphitheater seats. */
  public static calculateAllHandsSeating(): { position: THREE.Vector3; rotationY: number }[] {
    const seats: { position: THREE.Vector3; rotationY: number }[] = [];

    // Row 1 (Tier 1: 6 seats, radius 16.0m, Y = 0.35m)
    for (let i = 0; i < 6; i++) {
      const angle = 0.35 + (i / 5) * (Math.PI - 0.7);
      const px = Math.cos(angle) * 16.0;
      const pz = Math.sin(angle) * 14.0 - 10.0;
      seats.push({
        position: new THREE.Vector3(px, 0.35, pz),
        rotationY: -angle + Math.PI / 2,
      });
    }

    // Row 2 (Tier 2: 7 seats, radius 23.0m, Y = 1.15m)
    for (let i = 0; i < 7; i++) {
      const angle = 0.3 + (i / 6) * (Math.PI - 0.6);
      const px = Math.cos(angle) * 23.0;
      const pz = Math.sin(angle) * 20.0 - 10.0;
      seats.push({
        position: new THREE.Vector3(px, 1.15, pz),
        rotationY: -angle + Math.PI / 2,
      });
    }

    return seats;
  }
}
