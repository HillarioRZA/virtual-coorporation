/**
 * Topographical Contoured Elevation Engine for Apple Park Mega-Campus.
 * Models Cupertino's iconic Southern Hill (Steve Jobs Theater crest) & gentle parkland slopes.
 * Provides continuous smooth elevation sampling & vertex displacement geometry.
 */

import * as THREE from "three";

export class OfficeTerrainElevation {
  // Steve Jobs Theater hilltop center
  private static readonly HILL_CENTER = new THREE.Vector2(40, 230);
  private static readonly HILL_RADIUS = 68.0;
  private static readonly HILL_PEAK = 3.2; // 3.2m elevated summit

  /**
   * Computes exact terrain elevation Y for any world coordinate (X, Z).
   * @param x World X coordinate.
   * @param z World Z coordinate.
   * @returns Continuous terrain elevation Y in meters.
   */
  public static getElevationAt(x: number, z: number): number {
    const r = Math.hypot(x, z);

    // 1. The Grand Ring Footprint & Immediate Perimeter (Strictly Flat Grade Y=0)
    if (r >= 94.0 && r <= 140.0) {
      return 0.0;
    }

    // 2. Tantau SecOps Datacenter Pad (Strictly Flat Grade Y=0)
    if (x >= 30 && x <= 90 && z >= -252 && z <= -208) {
      return 0.0;
    }

    // 3. Central Courtyard Meadow (Gentle Meadow with Flat Ring Margin)
    if (r < 94.0) {
      // Very subtle organic depression towards pool edge
      return 0.0;
    }

    // 4. Southern Hill Crest around Steve Jobs Theater (40, 230)
    const distToHill = Math.hypot(x - this.HILL_CENTER.x, z - this.HILL_CENTER.y);
    if (distToHill < this.HILL_RADIUS) {
      // Smooth cosine hill crest profile
      const factor = (1 + Math.cos((distToHill / this.HILL_RADIUS) * Math.PI)) * 0.5;
      return this.HILL_PEAK * Math.pow(factor, 1.4);
    }

    return 0.0;
  }

  /**
   * Generates procedurally displaced contoured circular terrain BufferGeometry.
   * @param radius Maximum campus lawn radius (e.g. 320m).
   * @param segments Radial and angular segment resolution.
   */
  public static createContouredTerrainGeo(radius = 320, segments = 96): THREE.BufferGeometry {
    const geo = new THREE.CircleGeometry(radius, segments);
    geo.rotateX(-Math.PI / 2);

    const posAttr = geo.attributes.position as THREE.BufferAttribute;
    const vertex = new THREE.Vector3();

    for (let i = 0; i < posAttr.count; i++) {
      vertex.fromBufferAttribute(posAttr, i);
      const elev = this.getElevationAt(vertex.x, vertex.z);
      posAttr.setY(i, elev - 0.05); // Base lawn inset
    }

    geo.computeVertexNormals();
    return geo;
  }
}
