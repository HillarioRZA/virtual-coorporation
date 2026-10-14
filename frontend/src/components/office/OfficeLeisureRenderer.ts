/**
 * Procedural Leisure & Lifestyle Facility Vector Renderer.
 * Draws arcade machines, ping-pong tables, music studios, nap pods, ramen bars, and koi ponds.
 */

export class OfficeLeisureRenderer {
  public static drawArcadeMachine(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    w: number,
    h: number,
    ts: number
  ): void {
    ctx.fillStyle = "#1e1b4b";
    ctx.strokeStyle = "#f43f5e";
    ctx.lineWidth = 1.5;
    ctx.fillRect(x, y, w, h);
    ctx.strokeRect(x, y, w, h);

    const neonColor = (ts / 500) % 2 > 1 ? "#38bdf8" : "#ec4899";
    ctx.fillStyle = neonColor;
    ctx.fillRect(x + 8, y + 8, w - 16, 18);

    ctx.fillStyle = "#f43f5e";
    ctx.beginPath();
    ctx.arc(x + 16, y + 36, 3, 0, Math.PI * 2);
    ctx.fill();
  }

  public static drawPingPong(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    w: number,
    h: number,
    ts: number
  ): void {
    ctx.fillStyle = "#047857";
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 1;
    ctx.fillRect(x, y, w, h);
    ctx.strokeRect(x, y, w, h);

    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x + w / 2, y);
    ctx.lineTo(x + w / 2, y + h);
    ctx.stroke();

    const bx = x + 10 + (Math.sin(ts / 300) * 0.5 + 0.5) * (w - 20);
    ctx.fillStyle = "#facc15";
    ctx.beginPath();
    ctx.arc(bx, y + h / 2, 3, 0, Math.PI * 2);
    ctx.fill();
  }

  public static drawMusicInstruments(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    w: number,
    h: number,
    ts: number
  ): void {
    ctx.fillStyle = "#1e1b4b";
    ctx.fillRect(x, y, w, h);

    ctx.fillStyle = "#ffffff";
    ctx.fillRect(x + 10, y + 15, 60, 16);
    ctx.fillStyle = "#000000";
    for (let i = 0; i < 7; i++) {
      ctx.fillRect(x + 15 + i * 7, y + 15, 4, 10);
    }

    ctx.fillStyle = "#a855f7";
    ctx.font = "12px sans-serif";
    const floatY = y + 10 - ((ts / 150) % 15);
    ctx.fillText("♪", x + 80, floatY);
    ctx.fillText("♫", x + 95, floatY + 6);
  }

  public static drawNapPod(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    w: number,
    h: number,
    isOcc: boolean,
    _ts: number
  ): void {
    ctx.fillStyle = "#1e293b";
    ctx.strokeStyle = isOcc ? "#8b5cf6" : "#475569";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.ellipse(x + w / 2, y + h / 2, w / 2, h / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    if (isOcc) {
      ctx.fillStyle = "rgba(139, 92, 246, 0.4)";
      ctx.fill();
      ctx.fillStyle = "#c084fc";
      ctx.font = "bold 9px monospace";
      ctx.fillText("zzz", x + w / 2 - 8, y + h / 2 + 3);
    }
  }

  public static drawRamenBar(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    w: number,
    h: number,
    _ts: number
  ): void {
    ctx.fillStyle = "#78350f";
    ctx.fillRect(x, y, w, h);
    ctx.strokeStyle = "#92400e";
    ctx.strokeRect(x, y, w, h);

    for (let i = 0; i < 3; i++) {
      const bx = x + 25 + i * 45;
      ctx.fillStyle = "#dc2626";
      ctx.beginPath();
      ctx.arc(bx, y + 25, 8, 0, Math.PI);
      ctx.fill();
    }
  }

  public static drawKoiPond(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    w: number,
    h: number,
    ts: number
  ): void {
    ctx.fillStyle = "#0284c7";
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.ellipse(x + w / 2, y + h / 2, w / 2 - 4, h / 2 - 4, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    const kx = x + w / 2 + Math.cos(ts / 800) * (w / 3);
    const ky = y + h / 2 + Math.sin(ts / 800) * (h / 3);
    ctx.fillStyle = "#f97316";
    ctx.beginPath();
    ctx.ellipse(kx, ky, 6, 2.5, ts / 800, 0, Math.PI * 2);
    ctx.fill();
  }
}
