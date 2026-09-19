import { describe, expect, it } from "vitest";
import { DEMO_GEO } from "./demo-geo";
import { bboxOfPoints, buildCircuits, gridGeo, parsePathPoints, polygonCentroid } from "./geo";

describe("gridGeo", () => {
  it("returns a single square for one plant", () => {
    const g = gridGeo(1);
    expect(g.cuarteles).toHaveLength(1);
    expect(g.width).toBe(400);
  });
  it("lays out one cell per plant for several plants", () => {
    for (const n of [2, 5, 9, 14]) expect(gridGeo(n).cuarteles).toHaveLength(n);
  });
  it("keeps every cell inside the viewbox", () => {
    const g = gridGeo(7);
    for (const c of g.cuarteles) {
      const bb = bboxOfPoints(parsePathPoints(c.path));
      expect(bb.minx).toBeGreaterThanOrEqual(0);
      expect(bb.maxx).toBeLessThanOrEqual(g.width);
      expect(bb.maxy).toBeLessThanOrEqual(g.height);
    }
  });
});

describe("DEMO_GEO", () => {
  it("has the 14 surveyed plots, numbered 1 to 14", () => {
    expect(DEMO_GEO.cuarteles.map((c) => c.id)).toEqual(Array.from({ length: 14 }, (_, i) => i + 1));
  });
});

describe("polygon helpers", () => {
  const square = parsePathPoints("M 0,0 L 10,0 L 10,10 L 0,10 Z");
  it("parses a path into points", () => {
    expect(square).toEqual([[0, 0], [10, 0], [10, 10], [0, 10]]);
  });
  it("finds the centroid of a square", () => {
    const [x, y] = polygonCentroid(square);
    expect(x).toBeCloseTo(5);
    expect(y).toBeCloseTo(5);
  });
  it("builds circuits that stay inside the plot", () => {
    for (const cu of DEMO_GEO.cuarteles) {
      const poly = parsePathPoints(cu.path);
      const bb = bboxOfPoints(poly);
      for (const c of buildCircuits(poly, 3)) {
        for (const [x, y] of [[c.x1, c.y1], [c.x2, c.y2]]) {
          expect(x).toBeGreaterThanOrEqual(bb.minx - 1);
          expect(x).toBeLessThanOrEqual(bb.maxx + 1);
          expect(y).toBeGreaterThanOrEqual(bb.miny - 1);
          expect(y).toBeLessThanOrEqual(bb.maxy + 1);
        }
      }
    }
  });
});
