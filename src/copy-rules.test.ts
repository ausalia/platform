import { describe, expect, it } from "vitest";
import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";

function files(dir: string): string[] {
  return readdirSync(dir).flatMap((f) => {
    const p = path.join(dir, f);
    return statSync(p).isDirectory() ? files(p) : /\.(ts|tsx|css)$/.test(p) ? [p] : [];
  });
}
const all = files(path.resolve(__dirname));
const self = path.resolve(__dirname, "copy-rules.test.ts");
const read = (p: string) => readFileSync(p, "utf8");

describe("house copy rules", () => {
  it("uses no em dashes", () => {
    const bad = all.filter((p) => p !== self && read(p).includes("—"));
    expect(bad).toEqual([]);
  });
  it("never names the real company behind the demo survey", () => {
    const bad = all.filter((p) => p !== self && /punto azul/i.test(read(p)));
    expect(bad).toEqual([]);
  });
  it("uses the Auselia spelling in visible brand text", () => {
    const bad = all.filter((p) => p !== self && /\bAUSALIA\b|Ausalia is/.test(read(p)));
    expect(bad).toEqual([]);
  });
});
