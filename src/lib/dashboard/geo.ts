export type Pt = [number, number];
export type Cuartel = { id: number; area_ha: number | null; path: string };
export type Geo = {
  viewBox: string;
  width: number;
  height: number;
  farmArea: number | null;
  farmPath: string;
  farmPoints: Pt[];
  cuarteles: Cuartel[];
};
export type Circuit = { x1: number; y1: number; x2: number; y2: number };

const polyPath = (pts: Pt[]) => "M " + pts.map((p) => `${p[0]},${p[1]}`).join(" L ") + " Z";

// Plain schematic layout for a real org: a single square for one pot, or a
// grid of squares when an org has several plants and no survey geometry.
export function gridGeo(n: number): Geo {
  if (n <= 1) {
    return {
      viewBox: "0 0 400 400", width: 400, height: 400, farmArea: null,
      farmPath: "M 40,40 L 360,40 L 360,360 L 40,360 Z",
      farmPoints: [[40, 40], [360, 40], [360, 360], [40, 360]],
      cuarteles: [{ id: 1, area_ha: null, path: "M 90,90 L 310,90 L 310,310 L 90,310 Z" }],
    };
  }
  const cols = Math.ceil(Math.sqrt(n));
  const rows = Math.ceil(n / cols);
  const cell = 220, gap = 30, pad = 50;
  const width = pad * 2 + cols * cell + (cols - 1) * gap;
  const height = pad * 2 + rows * cell + (rows - 1) * gap;
  const cuarteles: Cuartel[] = [];
  for (let i = 0; i < n; i++) {
    const x = pad + (i % cols) * (cell + gap);
    const y = pad + Math.floor(i / cols) * (cell + gap);
    cuarteles.push({
      id: i + 1, area_ha: null,
      path: polyPath([[x, y], [x + cell, y], [x + cell, y + cell], [x, y + cell]]),
    });
  }
  const outline: Pt[] = [[20, 20], [width - 20, 20], [width - 20, height - 20], [20, height - 20]];
  return {
    viewBox: `0 0 ${width} ${height}`, width, height, farmArea: null,
    farmPath: polyPath(outline), farmPoints: outline, cuarteles,
  };
}

export function parsePathPoints(d: string): Pt[] {
  const nums = (d.match(/-?\d+\.?\d*/g) ?? []).map(Number);
  const pts: Pt[] = [];
  for (let i = 0; i + 1 < nums.length; i += 2) pts.push([nums[i], nums[i + 1]]);
  return pts;
}

export function polygonCentroid(poly: Pt[]): Pt {
  let x = 0, y = 0, a = 0;
  for (let i = 0; i < poly.length; i++) {
    const p0 = poly[i], p1 = poly[(i + 1) % poly.length];
    const cross = p0[0] * p1[1] - p1[0] * p0[1];
    a += cross;
    x += (p0[0] + p1[0]) * cross;
    y += (p0[1] + p1[1]) * cross;
  }
  a *= 0.5;
  if (Math.abs(a) < 1e-9) {
    let sx = 0, sy = 0;
    poly.forEach((p) => { sx += p[0]; sy += p[1]; });
    return [sx / poly.length, sy / poly.length];
  }
  return [x / (6 * a), y / (6 * a)];
}

function principalAngle(poly: Pt[]) {
  const c = polygonCentroid(poly);
  let sxx = 0, syy = 0, sxy = 0;
  poly.forEach((p) => {
    const dx = p[0] - c[0], dy = p[1] - c[1];
    sxx += dx * dx; syy += dy * dy; sxy += dx * dy;
  });
  return 0.5 * Math.atan2(2 * sxy, sxx - syy);
}

function rotatePoint(p: Pt, angle: number, cx: number, cy: number): Pt {
  const dx = p[0] - cx, dy = p[1] - cy;
  const c = Math.cos(angle), s = Math.sin(angle);
  return [cx + dx * c - dy * s, cy + dx * s + dy * c];
}

function clipScanlineAt(poly: Pt[], yPos: number): [number, number] | null {
  const crossings: number[] = [];
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i], b = poly[(i + 1) % poly.length];
    if ((a[1] <= yPos && b[1] > yPos) || (b[1] <= yPos && a[1] > yPos)) {
      const t = (yPos - a[1]) / (b[1] - a[1]);
      crossings.push(a[0] + t * (b[0] - a[0]));
    }
  }
  crossings.sort((p, q) => p - q);
  const segs: [number, number][] = [];
  for (let i = 0; i + 1 < crossings.length; i += 2) segs.push([crossings[i], crossings[i + 1]]);
  if (!segs.length) return null;
  segs.sort((p, q) => q[1] - q[0] - (p[1] - p[0]));
  return segs[0];
}

export function bboxOfPoints(pts: Pt[]) {
  const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
  return { minx: Math.min(...xs), maxx: Math.max(...xs), miny: Math.min(...ys), maxy: Math.max(...ys) };
}

export function buildCircuits(poly: Pt[], sensorCount: number): Circuit[] {
  const centroid = polygonCentroid(poly);
  const angle = principalAngle(poly);
  const rot = poly.map((p) => rotatePoint(p, -angle, centroid[0], centroid[1]));
  const ys = rot.map((p) => p[1]);
  const yMin = Math.min(...ys), yMax = Math.max(...ys);
  const count = sensorCount <= 1 ? 1 : Math.min(2, Math.ceil(sensorCount / 2));
  const circuits: Circuit[] = [];
  for (let i = 0; i < count; i++) {
    const yPos = yMin + ((i + 1) / (count + 1)) * (yMax - yMin);
    const seg = clipScanlineAt(rot, yPos);
    if (!seg) continue;
    const inset = (seg[1] - seg[0]) * 0.06;
    const p1 = rotatePoint([seg[0] + inset, yPos], angle, centroid[0], centroid[1]);
    const p2 = rotatePoint([seg[1] - inset, yPos], angle, centroid[0], centroid[1]);
    circuits.push({ x1: p1[0], y1: p1[1], x2: p2[0], y2: p2[1] });
  }
  if (!circuits.length) {
    const bb = bboxOfPoints(poly);
    const my = (bb.miny + bb.maxy) / 2;
    circuits.push({ x1: bb.minx, y1: my, x2: bb.maxx, y2: my });
  }
  return circuits;
}
