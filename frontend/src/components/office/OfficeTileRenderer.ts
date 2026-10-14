/**
 * Modular Vector Tile & Architectural Floor/Wall Renderer.
 * Procedurally draws rich floor textures, frosted glass partitions, and room walls without flat image assets.
 */

import { CampusRoom } from "./officeLayoutData";

export class OfficeTileRenderer {
  public static renderCampusGround(ctx: CanvasRenderingContext2D, width: number, height: number): void {
    // Void Space Background
    ctx.fillStyle = "#070a12";
    ctx.fillRect(0, 0, width, height);

    // Subtle Ambient Grid
    ctx.strokeStyle = "rgba(30, 41, 59, 0.4)";
    ctx.lineWidth = 1;
    const gridSize = 40;
    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
  }

  public static renderRoom(ctx: CanvasRenderingContext2D, room: CampusRoom): void {
    const { x, y, w, h, floorType, color, name } = room;

    ctx.save();
    // 1. Draw Textured Floors
    this.drawFloorTexture(ctx, x, y, w, h, floorType);

    // 2. Room Border with Soft Ambient Shadow & Frosted Glass Walls
    ctx.shadowColor = "rgba(0, 0, 0, 0.5)";
    ctx.shadowBlur = 12;
    ctx.strokeStyle = "rgba(71, 85, 105, 0.8)";
    ctx.lineWidth = 3;
    ctx.strokeRect(x, y, w, h);
    ctx.shadowBlur = 0;

    // 3. Apple-Style Cyan Accent Frosted Rim
    ctx.strokeStyle = `${color}40`;
    ctx.lineWidth = 1.5;
    ctx.strokeRect(x + 2, y + 2, w - 4, h - 4);

    // 4. Room Architectural Title Banner
    ctx.fillStyle = "rgba(10, 15, 29, 0.9)";
    ctx.strokeStyle = `${color}60`;
    ctx.lineWidth = 1;
    const bannerW = Math.min(240, w - 20);
    ctx.fillRect(x + 10, y + 8, bannerW, 22);
    ctx.strokeRect(x + 10, y + 8, bannerW, 22);

    // Glowing status dot & Room Title
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x + 20, y + 19, 3.5, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#f8fafc";
    ctx.font = "bold 10px monospace";
    ctx.textBaseline = "middle";
    ctx.fillText(name.toUpperCase(), x + 30, y + 19);

    ctx.restore();
  }

  private static drawFloorTexture(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    w: number,
    h: number,
    floorType: CampusRoom["floorType"]
  ): void {
    switch (floorType) {
      case "cherry_wood":
        ctx.fillStyle = "#2a1810";
        ctx.fillRect(x, y, w, h);
        ctx.strokeStyle = "rgba(78, 52, 46, 0.4)";
        ctx.lineWidth = 1;
        for (let py = y; py < y + h; py += 16) {
          ctx.beginPath();
          ctx.moveTo(x, py);
          ctx.lineTo(x + w, py);
          ctx.stroke();
        }
        break;

      case "navy_carpet":
        ctx.fillStyle = "#0f172a";
        ctx.fillRect(x, y, w, h);
        ctx.strokeStyle = "rgba(30, 41, 59, 0.5)";
        ctx.lineWidth = 0.8;
        for (let px = x; px < x + w; px += 24) {
          ctx.strokeRect(px, y, 24, h);
        }
        break;

      case "industrial_slate":
        ctx.fillStyle = "#1e293b";
        ctx.fillRect(x, y, w, h);
        ctx.strokeStyle = "rgba(51, 65, 85, 0.6)";
        ctx.lineWidth = 1;
        for (let px = x; px < x + w; px += 32) {
          for (let py = y; py < y + h; py += 32) {
            ctx.strokeRect(px, py, 32, 32);
          }
        }
        break;

      case "datacenter_raised":
        ctx.fillStyle = "#111827";
        ctx.fillRect(x, y, w, h);
        ctx.strokeStyle = "rgba(16, 185, 129, 0.25)"; // Glowing fiber lines
        ctx.lineWidth = 1;
        for (let px = x; px < x + w; px += 36) {
          ctx.beginPath();
          ctx.moveTo(px, y);
          ctx.lineTo(px, y + h);
          ctx.stroke();
        }
        break;

      case "arcade_neon":
        ctx.fillStyle = "#09090b";
        ctx.fillRect(x, y, w, h);
        ctx.strokeStyle = "rgba(244, 63, 94, 0.2)";
        ctx.lineWidth = 1;
        for (let px = x; px < x + w; px += 28) {
          for (let py = y; py < y + h; py += 28) {
            ctx.strokeRect(px, py, 28, 28);
          }
        }
        break;

      case "music_studio":
        ctx.fillStyle = "#1e1b4b";
        ctx.fillRect(x, y, w, h);
        ctx.strokeStyle = "rgba(168, 85, 247, 0.3)";
        ctx.lineWidth = 1;
        for (let py = y; py < y + h; py += 20) {
          ctx.strokeRect(x, py, w, 20);
        }
        break;

      case "zen_garden":
        ctx.fillStyle = "#064e3b";
        ctx.fillRect(x, y, w, h);
        ctx.fillStyle = "rgba(16, 185, 129, 0.15)";
        for (let i = 0; i < 20; i++) {
          const rx = x + ((i * 37) % (w - 20));
          const ry = y + ((i * 53) % (h - 20));
          ctx.beginPath();
          ctx.arc(rx, ry, 6, 0, Math.PI * 2);
          ctx.fill();
        }
        break;

      default:
        ctx.fillStyle = "#334155";
        ctx.fillRect(x, y, w, h);
        break;
    }
  }

  public static renderSkybridge(ctx: CanvasRenderingContext2D, floor: number): void {
    if (floor !== 2) return;
    // Glass Skybridge connecting Apollo -> Da Vinci -> Olympus at Floor 2
    ctx.save();
    ctx.fillStyle = "rgba(30, 41, 59, 0.85)";
    ctx.fillRect(470, 360, 20, 50); // Bridge 1
    ctx.fillRect(890, 360, 20, 50); // Bridge 2

    ctx.strokeStyle = "rgba(56, 189, 248, 0.6)";
    ctx.lineWidth = 1.5;
    ctx.strokeRect(470, 360, 20, 50);
    ctx.strokeRect(890, 360, 20, 50);

    ctx.fillStyle = "#38bdf8";
    ctx.font = "8px monospace";
    ctx.fillText("SKYBRIDGE", 455, 355);
    ctx.fillText("SKYBRIDGE", 875, 355);
    ctx.restore();
  }
}
