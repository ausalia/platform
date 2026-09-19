import { describe, expect, it } from "vitest";
import type { Reading } from "@/lib/types";
import { buildEnv, lastNonNull } from "./env";

const H = 3600000;
const anchor = Date.parse("2026-09-18T12:00:00Z");
const row = (hoursAgo: number, over: Partial<Reading> = {}): Reading => ({
  id: 1, plant_id: "p", ts: new Date(anchor - hoursAgo * H).toISOString(),
  soil_pct: 50, root_temp_c: 18, air_temp_c: 24, humidity_pct: 40, pressure_hpa: 900, weight_g: 2000,
  ...over,
});

describe("buildEnv", () => {
  it("day keeps raw points from the last 24h only", () => {
    const { dates, env } = buildEnv([row(30), row(20), row(1)], "day", anchor);
    expect(dates).toHaveLength(2);
    expect(env.moisture).toEqual([50, 50]);
  });

  it("converts weight from grams to kg", () => {
    const { env } = buildEnv([row(1)], "day", anchor);
    expect(env.weight).toEqual([2]);
  });

  it("keeps nulls as null instead of turning them into 0", () => {
    const { env } = buildEnv([row(1, { weight_g: null })], "day", anchor);
    expect(env.weight).toEqual([null]);
  });

  it("week averages readings per local day", () => {
    const { dates, env } = buildEnv(
      [row(2, { soil_pct: 40 }), row(3, { soil_pct: 60 }), row(48, { soil_pct: 10 })],
      "week", anchor,
    );
    expect(dates.length).toBeGreaterThanOrEqual(2);
    expect(env.moisture).toContain(50);
    expect(env.moisture).toContain(10);
  });

  it("week skips nulls when averaging a field", () => {
    const { env } = buildEnv(
      [row(2, { humidity_pct: 30 }), row(3, { humidity_pct: null })],
      "week", anchor,
    );
    expect(env.humidity).toEqual([30]);
  });

  it("excludes readings older than the window", () => {
    expect(buildEnv([row(24 * 8)], "week", anchor).dates).toHaveLength(0);
    expect(buildEnv([row(24 * 8)], "month", anchor).dates).toHaveLength(1);
  });

  it("applies the per-sensor jitter multiplier", () => {
    const { env } = buildEnv([row(1)], "day", anchor, 1.1);
    expect(env.moisture![0]).toBeCloseTo(55);
  });
});

describe("lastNonNull", () => {
  it("returns the newest real value", () => {
    expect(lastNonNull([1, 2, null])).toBe(2);
    expect(lastNonNull([null, null])).toBeNull();
    expect(lastNonNull(undefined)).toBeNull();
  });
});
