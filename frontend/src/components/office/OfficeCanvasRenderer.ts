/**
 * Procedural Living Vector Canvas Renderer for Corporate Office Simulator.
 * Integrates OfficeZSortPipeline, procedural rooms, living vector furniture, and dynamic depth.
 */

import { CampusRoom, FurnitureEntity, CAMPUS_ROOMS, CAMPUS_FURNITURE } from "./officeLayoutData";
import { AgentSpatialData, OfficeTheme } from "../../lib/types/office";
import { OfficeZSortPipeline } from "./OfficeZSortPipeline";

export class OfficeCanvasRenderer {
  private static customRooms: CampusRoom[] = [];
  private static customFurniture: FurnitureEntity[] = [];

  public static addCustomRoom(room: CampusRoom, furniture: FurnitureEntity[] = []): void {
    this.customRooms.push(room);
    if (furniture.length > 0) {
      this.customFurniture.push(...furniture);
    }
  }

  public static render(
    ctx: CanvasRenderingContext2D,
    agents: AgentSpatialData[],
    theme: OfficeTheme,
    width: number = 1376,
    height: number = 768,
    activeFloor: number = 1,
    selectedBuilding: string = "all",
    timestamp: number = Date.now()
  ): void {
    ctx.clearRect(0, 0, width, height);

    // Combine canonical schema with any custom user-added rooms
    const allRooms = [...CAMPUS_ROOMS, ...this.customRooms];
    const allFurniture = [...CAMPUS_FURNITURE, ...this.customFurniture];

    // Delegate to 5-Layer Z-Sort Pipeline
    OfficeZSortPipeline.renderFrame(
      ctx,
      allRooms,
      allFurniture,
      agents,
      theme,
      width,
      height,
      activeFloor,
      selectedBuilding,
      timestamp
    );
  }

  public static getAgentAtPosition(
    canvasX: number,
    canvasY: number,
    agents: AgentSpatialData[]
  ): AgentSpatialData | null {
    for (const a of agents) {
      const dx = canvasX - a.x;
      const dy = canvasY - a.y;
      if (dx * dx + dy * dy <= 600) return a;
    }
    return null;
  }
}
