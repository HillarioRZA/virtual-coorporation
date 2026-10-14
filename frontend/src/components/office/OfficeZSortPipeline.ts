/**
 * Multi-Layered Z-Sort Pipeline for 2.5D Depth Ordering.
 * Ensures natural occlusion: Floors -> Chairs -> Characters -> Desks/Monitors -> Speech/Flying Docs.
 */

import { CampusRoom, FurnitureEntity } from "./officeLayoutData";
import { AgentSpatialData, OfficeTheme } from "../../lib/types/office";
import { OfficeTileRenderer } from "./OfficeTileRenderer";
import { OfficeFurnitureRenderer } from "./OfficeFurnitureRenderer";
import { OfficeSpriteEngine } from "./OfficeSpriteEngine";

export class OfficeZSortPipeline {
  public static renderFrame(
    ctx: CanvasRenderingContext2D,
    rooms: CampusRoom[],
    furniture: FurnitureEntity[],
    agents: AgentSpatialData[],
    theme: OfficeTheme,
    width: number,
    height: number,
    floor: number = 1,
    selectedBuilding?: string,
    timestamp: number = Date.now()
  ): void {
    // Filter by current active floor
    const activeRooms = rooms.filter((r) => r.floor === floor && (!selectedBuilding || selectedBuilding === "all" || r.buildingId === selectedBuilding));
    const activeFurniture = furniture.filter((f) => f.floor === floor && (!selectedBuilding || selectedBuilding === "all" || f.buildingId === selectedBuilding));

    // LAYER 0: Ground Grid, Floors & Room Walls
    OfficeTileRenderer.renderCampusGround(ctx, width, height);
    activeRooms.forEach((room) => OfficeTileRenderer.renderRoom(ctx, room));
    OfficeTileRenderer.renderSkybridge(ctx, floor);

    // LAYER 1: Background Furniture (Chairs, Koi Pond, Nap Pods, Tables)
    activeFurniture.forEach((f) => {
      if (f.type === "koi_pond" || f.type === "meeting_table" || f.type === "nap_pod") {
        OfficeFurnitureRenderer.renderEntity(ctx, f, timestamp, false, false);
      }
    });

    // LAYER 2: Characters (Filtered by active visible floor/building)
    agents.forEach((agent) => {
      // In multi-floor mode, check if agent is in this floor/building
      OfficeSpriteEngine.renderAgentSprite(ctx, agent, theme, timestamp);
    });

    // LAYER 3: Foreground Furniture (Desks, Monitors, Arcade Cabinets, Server Racks)
    // Occludes the lower body of sitting agents naturally
    activeFurniture.forEach((f) => {
      if (f.type !== "koi_pond" && f.type !== "meeting_table" && f.type !== "nap_pod") {
        const assignedAgent = agents.find((a) => a.role_id === f.assignedRole);
        const isOccupied = !!assignedAgent;
        const isCoding = assignedAgent?.activity_state === "CODING";
        OfficeFurnitureRenderer.renderEntity(ctx, f, timestamp, isOccupied, isCoding);
      }
    });

    // LAYER 4: Speech Bubbles, Honest File Badges, and Flying Documents
    agents.forEach((agent) => {
      if (agent.speech_bubble) {
        this.renderSpeechBubble(ctx, agent.x, agent.y - 28, agent.speech_bubble, agent.color);
      }
      if (agent.active_file && agent.activity_state === "CODING") {
        this.renderHonestSignal(ctx, agent.x, agent.y - 42, agent.active_file);
      }
    });
  }

  private static renderSpeechBubble(ctx: CanvasRenderingContext2D, x: number, y: number, text: string, color?: string): void {
    ctx.save();
    ctx.font = "bold 9px sans-serif";
    const bw = Math.min(220, ctx.measureText(text).width + 16);
    const bh = 18;
    const bx = x - bw / 2;
    const by = y - bh;

    ctx.fillStyle = "rgba(15, 23, 42, 0.95)";
    ctx.strokeStyle = color || "#06b6d4";
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.roundRect(bx, by, bw, bh, 5);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, x, by + bh / 2);
    ctx.restore();
  }

  private static renderHonestSignal(ctx: CanvasRenderingContext2D, x: number, y: number, fileName: string): void {
    ctx.save();
    ctx.fillStyle = "rgba(30, 41, 59, 0.9)";
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 0.8;
    const text = `📝 ${fileName}`;
    ctx.font = "8px monospace";
    const bw = ctx.measureText(text).width + 10;
    ctx.fillRect(x - bw / 2, y, bw, 14);
    ctx.strokeRect(x - bw / 2, y, bw, 14);

    ctx.fillStyle = "#38bdf8";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, x, y + 7);
    ctx.restore();
  }
}
