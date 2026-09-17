export type Status = "good" | "warning" | "critical" | "idle";

export function statusFor(soilPct: number | null | undefined): Status {
  if (soilPct === null || soilPct === undefined) return "idle";
  if (soilPct < 20) return "critical";
  if (soilPct < 40) return "warning";
  return "good";
}

export const STATUS_COLOR: Record<Status, string> = {
  good: "var(--status-ok)",
  warning: "var(--status-stress)",
  critical: "var(--status-critical)",
  idle: "var(--status-idle)",
};

export const STATUS_LABEL: Record<Status, string> = {
  good: "Nominal",
  warning: "Elevated",
  critical: "Critical",
  idle: "No data",
};
