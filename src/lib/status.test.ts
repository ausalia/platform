import { describe, expect, it } from "vitest";
import { statusFor } from "./status";

describe("statusFor", () => {
  it("is idle without a reading", () => {
    expect(statusFor(null)).toBe("idle");
    expect(statusFor(undefined)).toBe("idle");
  });
  it("is critical below 20%", () => {
    expect(statusFor(0)).toBe("critical");
    expect(statusFor(19.9)).toBe("critical");
  });
  it("is warning from 20% up to 40%", () => {
    expect(statusFor(20)).toBe("warning");
    expect(statusFor(39.9)).toBe("warning");
  });
  it("is good from 40%", () => {
    expect(statusFor(40)).toBe("good");
    expect(statusFor(100)).toBe("good");
  });
});
