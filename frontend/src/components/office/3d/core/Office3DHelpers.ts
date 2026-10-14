/**
 * Spatial Helpers & Assembly Engine for 3D Apple Park Campus Simulator.
 * Assembles campus landscape, 360-degree The Grand Ring, 4-story interiors, and camera focal points.
 */

import * as THREE from "three";
import { OfficeTerrainPark } from "../environment/OfficeTerrainPark";
import { OfficeNatureInstanced } from "../environment/OfficeNatureInstanced";
import { OfficeRingBuilding } from "../buildings/OfficeRingBuilding";
import { OfficeRingAtriumCaffe } from "../buildings/OfficeRingAtriumCaffe";
import { OfficeTheaterBuilding } from "../buildings/OfficeTheaterBuilding";
import { OfficeTantauBuilding } from "../buildings/OfficeTantauBuilding";
import { OfficeAncientSakura } from "../environment/OfficeAncientSakura";
import { RingFloor1SiliconLab } from "../rooms/RingFloor1SiliconLab";
import { RingFloor2Strategy } from "../rooms/RingFloor2Strategy";
import { RingFloor3Executive } from "../rooms/RingFloor3Executive";
import { RingFloor4FounderPenthouse } from "../rooms/RingFloor4FounderPenthouse";
import { RingModularFuturePods } from "../rooms/RingModularFuturePods";
import { TheaterKeynoteAuditorium } from "../rooms/TheaterKeynoteAuditorium";
import { TantauDatacenterVault } from "../rooms/TantauDatacenterVault";

export class Office3DHelpers {
  /** Assembles the full campus outdoor world: terrain, sakura grove, 360 ring, and satellite pavilions. */
  public static buildCampusWorld(activeFloor: number = 1): THREE.Group {
    const campus = new THREE.Group();
    campus.name = "ApplePark_Campus_World";

    campus.add(OfficeTerrainPark.buildParkland());
    campus.add(OfficeNatureInstanced.buildTreeGrove());
    campus.add(OfficeAncientSakura.buildAncientSakura());
    campus.add(OfficeRingBuilding.buildRing(activeFloor));
    campus.add(OfficeRingAtriumCaffe.buildAtrium());
    campus.add(OfficeTheaterBuilding.buildTheater());
    campus.add(OfficeTantauBuilding.buildTantau());

    return campus;
  }

  /** Assembles all detailed room interiors across all 4 floors and satellite buildings. */
  public static buildCampusInteriors(): THREE.Group {
    const interiors = new THREE.Group();
    interiors.name = "ApplePark_Interiors";

    // The Grand Ring 4-Story Interiors
    interiors.add(RingFloor1SiliconLab.buildLab());
    interiors.add(RingFloor2Strategy.buildStrategyFloor());
    interiors.add(RingFloor3Executive.buildExecutiveFloor());
    interiors.add(RingFloor4FounderPenthouse.buildPenthouse());
    interiors.add(RingModularFuturePods.buildFuturePods());

    // Steve Jobs Theater All-Hands Stage & Seating
    interiors.add(TheaterKeynoteAuditorium.buildAuditoriumInterior());

    // Tantau R&D Datacenter Vault
    interiors.add(TantauDatacenterVault.buildTantauInterior());

    return interiors;
  }

  /** Returns focal point and camera radius for building and floor inspection. */
  public static getBuildingTarget(bldg: string): { pos: THREE.Vector3; dist: number; phi?: number; theta?: number } {
    switch (bldg) {
      case "penthouse":
      case "founder":
        return { pos: new THREE.Vector3(117, 13.0, 0), dist: 12, phi: 1.35, theta: 0 };
      case "ring":
      case "apollo":
        return { pos: new THREE.Vector3(0, 10, 0), dist: 220, phi: 1.15 };
      case "theater":
      case "olympus":
        return { pos: new THREE.Vector3(40, 4.0, 230), dist: 48, phi: 1.32, theta: -Math.PI / 4 };
      case "tantau":
        return { pos: new THREE.Vector3(60, 5, -230), dist: 58, phi: 1.22, theta: Math.PI };
      case "caffe":
      case "davinci":
        return { pos: new THREE.Vector3(-98, 6, 0), dist: 45, phi: 1.32 };
      case "all":
      default:
        return { pos: new THREE.Vector3(0, 0, 0), dist: 380, phi: Math.PI / 3.4 };
    }
  }
}
