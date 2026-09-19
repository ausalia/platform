import { describe, expect, it } from "vitest";
import { STR } from "./i18n";

const flat = (o: unknown): string[] =>
  Array.isArray(o) ? o.flatMap(flat) : typeof o === "string" ? [o] : [];

describe("i18n", () => {
  it("has the same keys in English and Spanish", () => {
    expect(Object.keys(STR.es).sort()).toEqual(Object.keys(STR.en).sort());
  });
  it("has no empty strings", () => {
    for (const lang of [STR.en, STR.es]) {
      for (const v of Object.values(lang)) expect(flat(v).every((s) => s.length > 0)).toBe(true);
    }
  });
});
