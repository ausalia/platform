import type { Status } from "@/lib/status";
import { buildCircuits, parsePathPoints, polygonCentroid, type Circuit } from "./geo";

// The demo org's acoustic events, circuits and sensor layout are simulated
// (there is no acoustic hardware yet). Everything is seeded from the plant id
// so it stays stable across renders and reloads.

export function hashSeed(s: string) {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
export function rng(seed: number) {
  let a = seed;
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const range = (r: () => number, a: number, b: number) => a + r() * (b - a);
const int = (r: () => number, a: number, b: number) => a + Math.floor(r() * (b - a + 1));

export const DAYS = 31;

function aeProfile(status: Status, r: () => number) {
  if (status === "critical") return { scale: range(r, 0.8, 1.1), rise: range(r, 4, 9) };
  if (status === "warning") return { scale: range(r, 0.3, 0.55), rise: range(r, 12, 20) };
  return { scale: range(r, 0.05, 0.2), rise: range(r, 24, 30) };
}

function aeSeries(r: () => number, n: number, scale: number, riseStart: number) {
  riseStart = Math.min(riseStart, n - 2);
  const a: number[] = [];
  for (let i = 0; i < n; i++) {
    const f = Math.max(0, (i - riseStart) / (n - 1 - riseStart));
    const base = Math.pow(f, 2.3) * 40 * scale;
    let mult = 1;
    const x = r();
    if (x < 0.15) mult = 0.35; else if (x > 0.88) mult = 1.5;
    a.push(Math.max(0, Math.round(base * mult + (r() - 0.5) * base * 0.3)));
  }
  return a;
}

export type SimNode = {
  stress: number; sensorCount: number; mmPlan: number; mmDelta: number; ae: number[];
};

export function simNode(seed: string, status: Status): SimNode {
  const r = rng(hashSeed("node:" + seed));
  const p = aeProfile(status, r);
  const stress = status === "critical" ? range(r, 65, 90) : status === "warning" ? range(r, 30, 55) : range(r, 3, 22);
  return {
    stress: Math.round(stress),
    sensorCount: int(r, 1, 3),
    mmPlan: Math.round(range(r, 8, 22) * 10) / 10,
    mmDelta: status === "critical" ? int(r, 3, 6) : status === "warning" ? int(r, 1, 3) : 0,
    ae: aeSeries(r, DAYS, p.scale, Math.round(p.rise)),
  };
}

export type SensorDot = {
  id: string; label: string; x: number; y: number; status: Status;
  circuitIdx: number; jitter: number; ae: number[];
};

function sensorStatusFor(cuartel: Status, r: () => number): Status {
  const x = r();
  if (cuartel === "critical") return x < 0.55 ? "critical" : x < 0.85 ? "warning" : "good";
  if (cuartel === "warning") return x < 0.5 ? "warning" : x < 0.75 ? "good" : "critical";
  return x < 0.82 ? "good" : "warning";
}

export function buildSensorLayout(
  seed: string, path: string, status: Status, sensorCount: number,
): { dots: SensorDot[]; circuits: Circuit[] } {
  const poly = parsePathPoints(path);
  const circuits = buildCircuits(poly, sensorCount);
  const assign: number[] = [];
  for (let i = 0; i < sensorCount; i++) assign.push(i % circuits.length);
  const per: Record<number, number> = {};
  assign.forEach((ci) => { per[ci] = (per[ci] ?? 0) + 1; });
  const seen: Record<number, number> = {};
  const dots = assign.map((ci, i) => {
    const c = circuits[ci];
    seen[ci] = (seen[ci] ?? 0) + 1;
    const frac = seen[ci] / (per[ci] + 1);
    const r = rng(hashSeed(`sensor:${seed}:${i}`));
    const st = sensorStatusFor(status, r);
    const p = aeProfile(st, r);
    return {
      id: `Sensor ${i + 1}`, label: `Sensor ${i + 1}`,
      x: c.x1 + frac * (c.x2 - c.x1), y: c.y1 + frac * (c.y2 - c.y1),
      status: st, circuitIdx: ci,
      jitter: 0.94 + r() * 0.12,
      ae: aeSeries(r, DAYS, p.scale, Math.round(p.rise)),
    };
  });
  return { dots, circuits };
}

export function liveSensor(label: string, path: string, status: Status): SensorDot {
  const c = polygonCentroid(parsePathPoints(path));
  return { id: label, label, x: c[0], y: c[1], status, circuitIdx: 0, jitter: 1, ae: [] };
}

const TEMPLATES = [
  { amp: 118, freq: 672, rise: 2.4, dur: 340, energy: 812, counts: 47, rms: 31, cls: "confirmed" },
  { amp: 74, freq: 398, rise: 3.1, dur: 410, energy: 530, counts: 33, rms: 22, cls: "confirmed" },
  { amp: 131, freq: 679, rise: 2.1, dur: 355, energy: 890, counts: 52, rms: 34, cls: "confirmed" },
  { amp: 41, freq: 214, rise: 5.6, dur: 520, energy: 210, counts: 14, rms: 12, cls: "candidate" },
  { amp: 96, freq: 668, rise: 2.8, dur: 330, energy: 690, counts: 41, rms: 27, cls: "confirmed" },
  { amp: 37, freq: 211, rise: 6.0, dur: 540, energy: 190, counts: 12, rms: 10, cls: "candidate" },
] as const;

export type AeEvent = (typeof TEMPLATES)[number] & { time: string; dayIdx: number; sensorLabel: string };

export function eventsForDay(ae: number[], dayIdx: number, sensorCount: number, fixedSensor?: string): AeEvent[] {
  const count = Math.min(ae[dayIdx] ?? 0, 5);
  const out: AeEvent[] = [];
  for (let i = 0; i < count; i++) {
    const tmpl = TEMPLATES[(dayIdx + i) % TEMPLATES.length];
    const hh = (3 + i * 4) % 24, mm = (dayIdx * 7 + i * 13) % 60;
    out.push({
      ...tmpl,
      time: `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}`,
      dayIdx,
      sensorLabel: fixedSensor ?? `Sensor ${((dayIdx + i) % Math.max(1, sensorCount)) + 1}`,
    });
  }
  return out;
}

// The last DAYS calendar days ending today, for the AE trend and calendar.
export function aeDates(): Date[] {
  const now = new Date();
  const base = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  return Array.from({ length: DAYS }, (_, i) => new Date(base.getTime() - (DAYS - 1 - i) * 86400000));
}
