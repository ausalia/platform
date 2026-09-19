// Auselia mark (stem, one leaf, amber node with signal arcs) plus wordmark.
// The stem and leaf follow the text color; the node and arcs are always amber.
export function LogoMark({ size = 24, className }: { size?: number; className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="-4.6 3 64 64"
      width={size}
      height={size}
      aria-hidden="true"
      className={className}
    >
      <path d="M28 58V12" fill="none" stroke="currentColor" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M28 48C28 37 18 31 7 31C7 42 17 50 28 48Z" fill="currentColor" />
      <circle cx="28" cy="24" r="6" style={{ fill: "var(--amber)" }} />
      <path d="M39.5 16A14 14 0 0 1 39.5 32" fill="none" strokeWidth="3.6" strokeLinecap="round" style={{ stroke: "var(--amber)" }} />
      <path d="M46 11.4A22 22 0 0 1 46 36.6" fill="none" strokeWidth="3.6" strokeLinecap="round" style={{ stroke: "var(--amber)" }} />
    </svg>
  );
}

// tone "auto" follows the light/dark theme; "onDark" is for surfaces that are
// always forest green (the auth pages).
export default function Wordmark({
  size = 24,
  tone = "auto",
  className = "",
}: {
  size?: number;
  tone?: "auto" | "onDark";
  className?: string;
}) {
  const aus = tone === "onDark" ? "var(--bone)" : "var(--wm-aus)";
  const alia = tone === "onDark" ? "var(--amber)" : "var(--wm-alia)";
  return (
    <span
      className={`inline-flex items-center gap-2 font-[family-name:var(--font-display)] font-bold tracking-[0.01em] ${className}`}
      style={{ fontSize: size * 0.68 }}
    >
      <span style={{ color: aus, display: "inline-flex" }}>
        <LogoMark size={size} />
      </span>
      <span>
        <span style={{ color: aus }}>AUS</span>
        <span style={{ color: alia }}>ELIA</span>
      </span>
    </span>
  );
}
