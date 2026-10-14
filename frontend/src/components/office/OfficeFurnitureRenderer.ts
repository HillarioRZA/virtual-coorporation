/**
 * Procedural Vector Living Furniture & Workstation Renderer.
 * Draws interactive desks, glowing server racks, meeting tables, podiums, and elevators.
 */

import { FurnitureEntity } from "./officeLayoutData";
import { OfficeLeisureRenderer } from "./OfficeLeisureRenderer";

export class OfficeFurnitureRenderer {
  public static renderEntity(
    ctx: CanvasRenderingContext2D,
    entity: FurnitureEntity,
    timestamp: number = Date.now(),
    isOccupied: boolean = false,
    isCoding: boolean = false
  ): void {
    const { x, y, w, h, type } = entity;
    ctx.save();

    switch (type) {
      case "desk":
        this.drawDesk(ctx, x, y, w, h, isOccupied, isCoding, timestamp);
        break;
      case "server_rack":
        this.drawServerRack(ctx, x, y, w, h, timestamp);
        break;
      case "meeting_table":
        this.drawMeetingTable(ctx, x, y, w, h);
        break;
      case "podium":
        this.drawPodium(ctx, x, y, w, h);
        break;
      case "elevator":
        this.drawElevator(ctx, x, y, w, h);
        break;
      case "arcade_machine":
        OfficeLeisureRenderer.drawArcadeMachine(ctx, x, y, w, h, timestamp);
        break;
      case "ping_pong":
        OfficeLeisureRenderer.drawPingPong(ctx, x, y, w, h, timestamp);
        break;
      case "music_instruments":
        OfficeLeisureRenderer.drawMusicInstruments(ctx, x, y, w, h, timestamp);
        break;
      case "nap_pod":
        OfficeLeisureRenderer.drawNapPod(ctx, x, y, w, h, isOccupied, timestamp);
        break;
      case "ramen_bar":
        OfficeLeisureRenderer.drawRamenBar(ctx, x, y, w, h, timestamp);
        break;
      case "koi_pond":
        OfficeLeisureRenderer.drawKoiPond(ctx, x, y, w, h, timestamp);
        break;
    }

    ctx.restore();
  }

  public static drawDesk(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    w: number,
    h: number,
    _isOccupied: boolean,
    isCoding: boolean,
    timestamp: number
  ): void {
    // 1. Desk Surface (Dark Slate Oak)
    ctx.fillStyle = "#334155";
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 1.5;
    ctx.fillRect(x, y, w, h);
    ctx.strokeRect(x, y, w, h);

    // 2. Dual Monitors
    ctx.fillStyle = "#0f172a";
    ctx.fillRect(x + 10, y + 6, 22, 14);
    ctx.fillRect(x + 36, y + 6, 22, 14);

    // Code Glow on Screens if Coding
    if (isCoding) {
      ctx.fillStyle = "#38bdf8";
      const tick = Math.floor(timestamp / 200) % 3;
      ctx.fillRect(x + 12, y + 9 + tick * 3, 16, 2);
      ctx.fillRect(x + 38, y + 9 + ((tick + 1) % 3) * 3, 16, 2);
    }

    // 3. Keyboard
    ctx.fillStyle = "#1e293b";
    ctx.fillRect(x + 22, y + 26, 26, 8);

    // 4. Coffee Cup with Animated Steam
    ctx.fillStyle = "#f8fafc";
    ctx.beginPath();
    ctx.arc(x + 58, y + 30, 3.5, 0, Math.PI * 2);
    ctx.fill();

    const steamY = y + 25 - ((timestamp / 100) % 8);
    ctx.strokeStyle = "rgba(226, 232, 240, 0.4)";
    ctx.beginPath();
    ctx.moveTo(x + 58, y + 27);
    ctx.lineTo(x + 59, steamY);
    ctx.stroke();
  }

  private static drawServerRack(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, ts: number): void {
    ctx.fillStyle = "#090d16";
    ctx.strokeStyle = "#1e293b";
    ctx.lineWidth = 2;
    ctx.fillRect(x, y, w, h);
    ctx.strokeRect(x, y, w, h);

    const rows = 5;
    for (let r = 0; r < rows; r++) {
      const ledY = y + 16 + r * 20;
      ctx.fillStyle = "#1e293b";
      ctx.fillRect(x + 8, ledY - 4, w - 16, 12);

      const isBlink = ((ts + r * 300) / 400) % 2 > 1;
      ctx.fillStyle = isBlink ? "#10b981" : "#047857";
      ctx.beginPath();
      ctx.arc(x + 16, ledY + 2, 2.5, 0, Math.PI * 2);
      ctx.arc(x + 26, ledY + 2, 2.5, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  private static drawMeetingTable(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number): void {
    ctx.fillStyle = "#451a03";
    ctx.strokeStyle = "#78350f";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, 14);
    ctx.fill();
    ctx.stroke();
  }

  private static drawPodium(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number): void {
    ctx.fillStyle = "#1e293b";
    ctx.strokeStyle = "#6366f1";
    ctx.lineWidth = 1.5;
    ctx.fillRect(x, y, w, h);
    ctx.strokeRect(x, y, w, h);

    ctx.fillStyle = "#6366f1";
    ctx.fillRect(x + 10, y + 6, w - 20, 8);
  }

  private static drawElevator(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number): void {
    ctx.fillStyle = "#0f172a";
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 2;
    ctx.fillRect(x, y, w, h);
    ctx.strokeRect(x, y, w, h);

    ctx.strokeStyle = "rgba(56, 189, 248, 0.4)";
    ctx.beginPath();
    ctx.moveTo(x + w / 2, y);
    ctx.lineTo(x + w / 2, y + h);
    ctx.stroke();

    ctx.fillStyle = "#38bdf8";
    ctx.font = "bold 8px monospace";
    ctx.fillText("▲ LIFT", x + 6, y + 14);
  }
}
