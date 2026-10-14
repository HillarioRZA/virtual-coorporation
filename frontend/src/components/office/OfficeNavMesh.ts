/**
 * Collision Grid & Corridor Waypoint NavMesh for Virtual Office.
 * Implements obstacle collision maps and door-to-corridor routing (adapted from eliautobot).
 */

import { CampusRoom, FurnitureEntity } from "./officeLayoutData";

export interface Point {
  x: number;
  y: number;
}

export class OfficeNavMesh {
  private static readonly CELL_SIZE = 32;

  public static buildCollisionGrid(
    width: number,
    height: number,
    rooms: CampusRoom[],
    furniture: FurnitureEntity[]
  ): Uint8Array {
    const cols = Math.ceil(width / this.CELL_SIZE);
    const rows = Math.ceil(height / this.CELL_SIZE);
    const grid = new Uint8Array(cols * rows); // 0 = Passable, 1 = Solid

    // Mark furniture boundaries as solid
    furniture.forEach((f) => {
      const startCol = Math.floor(f.x / this.CELL_SIZE);
      const endCol = Math.min(cols - 1, Math.floor((f.x + f.w) / this.CELL_SIZE));
      const startRow = Math.floor(f.y / this.CELL_SIZE);
      const endRow = Math.min(rows - 1, Math.floor((f.y + f.h) / this.CELL_SIZE));

      for (let r = startRow; r <= endRow; r++) {
        for (let c = startCol; c <= endCol; c++) {
          grid[r * cols + c] = 1;
        }
      }
    });

    return grid;
  }

  public static getDoorwayForRoom(roomId: string): Point {
    switch (roomId) {
      case "apollo_lab":
        return { x: 260, y: 390 };
      case "apollo_auditorium":
        return { x: 260, y: 410 };
      case "davinci_canteen":
      case "davinci_media":
        return { x: 690, y: 370 };
      case "olympus_boardroom":
      case "olympus_penthouse":
        return { x: 910, y: 370 };
      default:
        return { x: 470, y: 380 };
    }
  }

  public static findPath(start: Point, target: Point): Point[] {
    // Waypoint routing: Desk -> Room Doorway -> Main Corridor -> Target Doorway -> Target
    const dx = target.x - start.x;
    const dy = target.y - start.y;
    const distSq = dx * dx + dy * dy;

    // If close by in the same room, direct line is fine
    if (distSq < 20000) {
      return [start, target];
    }

    // Determine doorway navigation waypoints
    const midCorridorY = 380; // Central campus spine walkway
    const wp1: Point = { x: start.x, y: midCorridorY };
    const wp2: Point = { x: target.x, y: midCorridorY };

    return [start, wp1, wp2, target];
  }
}
