import type { Status } from "@/lib/status";

// Colorblind rule: status must never be carried by color alone, so each
// status gets a distinct shape too (circle/triangle/diamond/dash), not just
// a differently-colored dot.
export default function StatusIcon({ status, size = 10 }: { status: Status; size?: number }) {
  const common = { width: size, height: size, viewBox: "0 0 10 10", fill: "currentColor" };

  switch (status) {
    case "good":
      return (
        <svg {...common} aria-hidden="true">
          <circle cx="5" cy="5" r="4" />
        </svg>
      );
    case "warning":
      return (
        <svg {...common} aria-hidden="true">
          <polygon points="5,1 9,9 1,9" />
        </svg>
      );
    case "critical":
      return (
        <svg {...common} aria-hidden="true">
          <polygon points="5,0 10,5 5,10 0,5" />
        </svg>
      );
    case "idle":
      return (
        <svg {...common} aria-hidden="true">
          <rect x="1" y="4" width="8" height="2" rx="1" />
        </svg>
      );
  }
}
