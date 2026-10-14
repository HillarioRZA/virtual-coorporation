/**
 * Smart Universal Elevator Manager for Multi-Floor Tech Campus.
 * Coordinates 2-way vertical transit between Floors 1, 2, and 3 across Apollo, Da Vinci, and Olympus.
 */

import { officeSound } from "./OfficeSoundManager";

export interface ElevatorBay {
  buildingId: "apollo" | "davinci" | "olympus";
  x: number;
  y: number;
}

export class OfficeElevatorManager {
  public static readonly ELEVATOR_BAYS: Record<string, ElevatorBay> = {
    apollo: { buildingId: "apollo", x: 410, y: 230 },
    davinci: { buildingId: "davinci", x: 830, y: 230 },
    olympus: { buildingId: "olympus", x: 1260, y: 230 },
  };

  public static getElevatorForBuilding(buildingId: string): ElevatorBay {
    return this.ELEVATOR_BAYS[buildingId] || this.ELEVATOR_BAYS.apollo;
  }

  public static executeTransit(
    roleId: string,
    fromFloor: number,
    toFloor: number,
    buildingId: "apollo" | "davinci" | "olympus",
    onFloorChange: (targetFloor: number) => void,
    onComplete: () => void
  ): void {
    if (fromFloor === toFloor) {
      onComplete();
      return;
    }

    // Play elevator chime
    try {
      officeSound.playMeetingChime();
    } catch {
      // Audio optional
    }

    // Transit duration simulation
    setTimeout(() => {
      onFloorChange(toFloor);
      setTimeout(() => {
        onComplete();
      }, 500);
    }, 800);
  }
}
