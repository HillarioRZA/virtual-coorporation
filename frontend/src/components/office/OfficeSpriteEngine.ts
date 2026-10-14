/**
 * Procedural 2D Pixel / Tactical Sprite Engine for Corporate Office Simulator.
 * Renders full-body animated RPG characters, walk cycles, typing hands, and monitor glows.
 */

import { AgentSpatialData, OfficeTheme } from "../../lib/types/office";

export class OfficeSpriteEngine {
  public static renderAgentSprite(
    ctx: CanvasRenderingContext2D,
    agent: AgentSpatialData,
    theme: OfficeTheme,
    timestamp: number = Date.now()
  ): void {
    const { x, y, color = "#06b6d4", activity_state, tier } = agent;
    const isChibi = theme.avatarStyle === "chibi";
    const isWalking = activity_state === "WALKING";
    const isCoding = activity_state === "CODING";
    const isMeeting = activity_state === "MEETING";
    const isBlocked = activity_state === "BLOCKED";

    // 1. Walk cycle bobbing & leg swing
    const stepFreq = (timestamp / 140) % (Math.PI * 2);
    const bobY = isWalking ? Math.sin(stepFreq) * 2 : 0;
    const legOffset = isWalking ? Math.sin(stepFreq) * 3.5 : 0;

    ctx.save();
    ctx.translate(x, y + bobY);

    // 2. Base Floor Shadow
    ctx.beginPath();
    ctx.ellipse(0, 16, 12, 5, 0, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(0, 0, 0, 0.45)";
    ctx.fill();

    // 3. Monitor Glow Reflection if Coding
    if (isCoding) {
      const glowGrad = ctx.createRadialGradient(0, -6, 2, 0, -6, 26);
      glowGrad.addColorStop(0, "rgba(56, 189, 248, 0.35)");
      glowGrad.addColorStop(1, "rgba(56, 189, 248, 0)");
      ctx.fillStyle = glowGrad;
      ctx.beginPath();
      ctx.arc(0, -6, 26, 0, Math.PI * 2);
      ctx.fill();
    }

    // 4. Feet & Shoes
    ctx.fillStyle = "#0f172a";
    ctx.fillRect(-6 + legOffset, 12, 4, 4); // Left foot
    ctx.fillRect(2 - legOffset, 12, 4, 4);  // Right foot

    // 5. Torso & Clothing based on Hierarchy Tier
    ctx.fillStyle = this.getTierOutfitColor(tier, color);
    ctx.fillRect(-7, 2, 14, 11);

    // Lapel / Tie / Tech Stripe
    ctx.fillStyle = tier === "EXECUTIVE" ? "#facc15" : "#f8fafc";
    ctx.fillRect(-1, 3, 2, 7);

    // Hands / Typing animation at desk
    if (isCoding) {
      const typeSwing = Math.sin(timestamp / 80) * 1.5;
      ctx.fillStyle = "#fdba74";
      ctx.fillRect(-8, 8 + typeSwing, 3, 3);
      ctx.fillRect(5, 8 - typeSwing, 3, 3);
      // Mini mechanical keyboard
      ctx.fillStyle = "#334155";
      ctx.fillRect(-6, 10, 12, 3);
    } else {
      ctx.fillStyle = "#fdba74";
      ctx.fillRect(-8, 5, 2.5, 4);
      ctx.fillRect(5.5, 5, 2.5, 4);
    }

    // 6. Head & Hair
    ctx.fillStyle = "#fdba74"; // Skin tone
    ctx.beginPath();
    ctx.arc(0, -5, isChibi ? 9.5 : 8, 0, Math.PI * 2);
    ctx.fill();

    // Hairstyle / Tech Cap
    ctx.fillStyle = this.getHairStyleColor(agent.role_id);
    ctx.beginPath();
    ctx.arc(0, -7, isChibi ? 9.5 : 8, Math.PI, Math.PI * 2);
    ctx.fill();
    ctx.fillRect(-8, -8, 16, 4); // Bangs

    // 7. Visor / Eyes
    if (isBlocked) {
      ctx.fillStyle = "#f43f5e";
      ctx.font = "bold 11px monospace";
      ctx.textAlign = "center";
      ctx.fillText("!", 0, -3);
    } else {
      ctx.fillStyle = tier === "EXECUTIVE" ? "#eab308" : "#38bdf8";
      ctx.fillRect(-4, -6, 8, 2.5); // Glowing tech visor
    }

    // 8. Glowing Headset
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(0, -5, isChibi ? 10.5 : 9, Math.PI * 0.8, Math.PI * 1.2);
    ctx.stroke();

    // 9. Role Pill Label below avatar
    const shortName = agent.name.split(" ")[0];
    ctx.font = "bold 9px sans-serif";
    const nw = ctx.measureText(shortName).width + 8;
    ctx.fillStyle = "rgba(10, 15, 29, 0.9)";
    ctx.strokeStyle = `${color}90`;
    ctx.lineWidth = 1;
    ctx.fillRect(-nw / 2, 18, nw, 13);
    ctx.strokeRect(-nw / 2, 18, nw, 13);
    ctx.fillStyle = "#f8fafc";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(shortName, 0, 24.5);

    // 10. Status Indicator Ring
    if (isMeeting) {
      ctx.strokeStyle = "rgba(234, 179, 8, 0.7)";
      ctx.lineWidth = 1.5;
      ctx.strokeRect(-nw / 2 - 2, 16, nw + 4, 17);
    }

    ctx.restore();
  }

  private static getTierOutfitColor(tier: string, roleColor: string): string {
    switch (tier) {
      case "EXECUTIVE":
        return "#1e1b4b"; // Deep midnight luxury navy
      case "LEAD_MANAGEMENT":
        return "#3b0764"; // Royal purple
      case "COMMONS":
        return "#064e3b"; // Courtyard emerald
      default:
        return "#0f172a"; // Cyber dark coat with role accent
    }
  }

  private static getHairStyleColor(roleId: string): string {
    if (roleId.includes("founder")) return "#451a03"; // Dark Auburn
    if (roleId.includes("cto")) return "#172554";    // Deep Navy
    if (roleId.includes("fe")) return "#065f46";     // Forest Cyber
    if (roleId.includes("be")) return "#1e293b";     // Slate Black
    if (roleId.includes("qa")) return "#701a75";     // Magenta
    if (roleId.includes("devsecops")) return "#0e7490"; // Deep Cyan
    return "#334155";
  }
}
