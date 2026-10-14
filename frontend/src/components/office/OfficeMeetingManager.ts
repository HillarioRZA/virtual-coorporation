/**
 * Dynamic Parent-Relative Meeting Room & Auditorium Seat Manager.
 * Computes individual collision-free theater and boardroom slots relative to room bounds.
 */

export interface SeatSlot {
  x: number;
  y: number;
  isSpeaker?: boolean;
}

export class OfficeMeetingManager {
  // Apollo Hall Floor 1 Briefing Auditorium Bounds: x: 50, y: 410, w: 420, h: 290
  private static readonly AUDITORIUM_PODIUM: SeatSlot = { x: 235, y: 450, isSpeaker: true };

  // 12 Auditorium Theater Seats strictly within y: 500..640, x: 100..380
  private static readonly AUDITORIUM_ROLES: string[] = [
    "role_cos", "role_cfo", "role_cto", "role_pm",
    "role_fe", "role_be", "role_qa", "role_devsecops",
    "role_uiux", "role_copywriter", "role_seo", "role_growth"
  ];

  // Olympus Pavilion Floor 2 Boardroom Center: x: 1065, y: 300
  private static readonly BOARDROOM_CENTER = { x: 1065, y: 300, rx: 95, ry: 55 };

  public static getSeatForAgent(
    roleId: string,
    type: "ALL_HANDS" | "BOARDROOM" = "ALL_HANDS"
  ): SeatSlot {
    if (type === "BOARDROOM") {
      return this.computeBoardroomSeat(roleId);
    }
    return this.computeAuditoriumSeat(roleId);
  }

  private static computeAuditoriumSeat(roleId: string): SeatSlot {
    if (roleId === "role_founder") {
      return this.AUDITORIUM_PODIUM;
    }

    const index = this.AUDITORIUM_ROLES.indexOf(roleId);
    const validIndex = index >= 0 ? index : Math.abs(roleId.split("").reduce((a, c) => a + c.charCodeAt(0), 0)) % 12;

    const row = Math.floor(validIndex / 4); // 0, 1, 2
    const col = validIndex % 4; // 0, 1, 2, 3

    return {
      x: 120 + col * 75,
      y: 520 + row * 50,
      isSpeaker: false,
    };
  }

  private static computeBoardroomSeat(roleId: string): SeatSlot {
    const boardroomRoles = [
      "role_founder", "role_cos", "role_cfo", "role_cto", "role_pm",
      "role_growth", "role_fe", "role_be", "role_qa", "role_devsecops"
    ];
    const index = boardroomRoles.indexOf(roleId);
    const validIndex = index >= 0 ? index : 0;
    const total = boardroomRoles.length;

    // Elliptical distribution around Boardroom table
    const angle = (2 * Math.PI * validIndex) / total - Math.PI / 2;
    const { x, y, rx, ry } = this.BOARDROOM_CENTER;

    return {
      x: Math.round(x + rx * Math.cos(angle)),
      y: Math.round(y + ry * Math.sin(angle)),
      isSpeaker: roleId === "role_founder",
    };
  }

  public static getSpeechBubbleYOffset(roleId: string, isMeeting: boolean): number {
    if (!isMeeting) return -24;
    if (roleId === "role_founder") return -32;
    const idx = this.AUDITORIUM_ROLES.indexOf(roleId);
    const row = idx >= 0 ? Math.floor(idx / 4) : 0;
    return -28 - row * 4;
  }
}
