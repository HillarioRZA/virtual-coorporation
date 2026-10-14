/**
 * Procedural Web Audio Footstep Synthesizer for Apple Park Simulation.
 * 100% Zero-Asset: Procedural noise bursts & bandpass filters tailored to surfaces.
 * Supports Oak Wood, Italian Travertine Marble, Parkland Grass, and Granite Pavers.
 */

export type SurfaceMaterial = "wood" | "marble" | "grass" | "granite";

export class OfficeProceduralAudio {
  private static ctx: AudioContext | null = null;
  private static isMuted = false;
  private static lastStepTime = 0;

  /** Initializes the Web Audio context on user gesture. */
  private static getContext(): AudioContext | null {
    if (!this.ctx && typeof window !== "undefined") {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume().catch(() => {});
    }
    return this.ctx;
  }

  /**
   * Generates a realistic surface-dependent footstep sound procedurally.
   * @param surface Surface material under the player.
   * @param isSprint Whether player is currently sprinting.
   */
  public static playFootstep(surface: SurfaceMaterial = "wood", isSprint = false): void {
    if (this.isMuted) return;
    const now = performance.now();
    if (now - this.lastStepTime < 180) return; // Debounce
    this.lastStepTime = now;

    const ctx = this.getContext();
    if (!ctx) return;

    try {
      const duration = isSprint ? 0.08 : 0.095;
      const bufferSize = Math.floor(ctx.sampleRate * duration);
      const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
      const data = buffer.getChannelData(0);

      // Procedural decaying noise with acoustic body resonance
      for (let i = 0; i < bufferSize; i++) {
        const decay = Math.exp(-i / (bufferSize * 0.28));
        data[i] = (Math.random() * 2 - 1) * decay;
      }

      const noiseSource = ctx.createBufferSource();
      noiseSource.buffer = buffer;

      // Surface-specific biquad resonant filter
      const filter = ctx.createBiquadFilter();
      const gain = ctx.createGain();

      switch (surface) {
        case "marble":
          filter.type = "bandpass";
          filter.frequency.value = isSprint ? 2200 : 1800;
          filter.Q.value = 3.2;
          gain.gain.setValueAtTime(0.09, ctx.currentTime);
          break;
        case "granite":
          filter.type = "bandpass";
          filter.frequency.value = isSprint ? 1400 : 1100;
          filter.Q.value = 1.8;
          gain.gain.setValueAtTime(0.08, ctx.currentTime);
          break;
        case "grass":
          filter.type = "lowpass";
          filter.frequency.value = isSprint ? 550 : 420;
          gain.gain.setValueAtTime(0.065, ctx.currentTime);
          break;
        case "wood":
        default:
          filter.type = "bandpass";
          filter.frequency.value = isSprint ? 720 : 580;
          filter.Q.value = 2.4;
          gain.gain.setValueAtTime(0.1, ctx.currentTime);
          break;
      }

      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);

      noiseSource.connect(filter);
      filter.connect(gain);
      gain.connect(ctx.destination);

      noiseSource.start();
    } catch {}
  }

  /**
   * Determines the surface material based on player coordinates.
   * @param x Player X coordinate.
   * @param z Player Z coordinate.
   * @param floorLevel Player current floor level.
   */
  public static detectSurface(x: number, z: number, floorLevel: number): SurfaceMaterial {
    const r = Math.hypot(x, z);

    // Inside The Grand Ring 4 floors
    if (r >= 98.0 && r <= 136.0) {
      if (floorLevel >= 12.0) return "marble"; // Penthouse luxury marble hearth
      return "wood"; // Blonde oak planking
    }

    // Steve Jobs Theater Pavilion
    if (Math.hypot(x - 40, z - 230) < 28.0) return "marble";

    // Tantau SecOps
    if (x >= 34 && x <= 86 && z >= -248 && z <= -212) return "marble";

    // Promenade Granit Loops (R=48-54, R=148-154, Avenues)
    if ((r >= 48 && r <= 54) || (r >= 148 && r <= 154)) return "granite";
    if (Math.abs(x - 40) < 6.0 && z > 140 && z < 210) return "granite";
    if (Math.abs(x - 60) < 6.0 && z < -140 && z > -210) return "granite";

    // Default Parkland Lawn
    return "grass";
  }
}
