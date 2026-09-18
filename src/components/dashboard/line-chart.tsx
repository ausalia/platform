"use client";

import { useEffect, useRef, useState } from "react";

function niceTicks(min: number, max: number, count: number) {
  if (min === max) { min -= 1; max += 1; }
  const span = max - min;
  let step = Math.pow(10, Math.floor(Math.log10(span / count)));
  const err = span / count / step;
  if (err >= 7.5) step *= 10; else if (err >= 3.5) step *= 5; else if (err >= 1.5) step *= 2;
  const niceMin = Math.floor(min / step) * step;
  const niceMax = Math.ceil(max / step) * step;
  const ticks: number[] = [];
  for (let v = niceMin; v <= niceMax + step * 0.5; v += step) ticks.push(v);
  return ticks;
}

export default function LineChart({
  data, labels, fmt, h = 150,
}: {
  data: number[]; labels: string[]; fmt?: (v: number) => string; h?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [W, setW] = useState(420);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver(() => setW(el.clientWidth || 420));
    ro.observe(el);
    setW(el.clientWidth || 420);
    return () => ro.disconnect();
  }, []);

  const padL = 42, padR = 14, padT = 12, padB = 24;
  const innerW = W - padL - padR, innerH = h - padT - padB;
  const ticks = niceTicks(Math.min(...data), Math.max(...data), 4);
  const vMin = ticks[0], vMax = ticks[ticks.length - 1];
  const n = data.length;
  const x = (i: number) => padL + (i / (n - 1)) * innerW;
  const y = (v: number) => padT + innerH - ((v - vMin) / (vMax - vMin)) * innerH;
  const path = data.map((v, i) => `${i === 0 ? "M" : "L"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const li = n - 1;
  const tickIdx = [0, Math.round((n - 1) * 0.25), Math.round((n - 1) * 0.5), Math.round((n - 1) * 0.75), n - 1];
  const txt = { fill: "var(--ink2)", fontSize: 10 };

  return (
    <div ref={ref}>
      <svg viewBox={`0 0 ${W} ${h}`} width="100%" height={h} className="block">
        {ticks.map((v) => (
          <g key={v}>
            <line x1={padL} x2={W - padR} y1={y(v)} y2={y(v)} style={{ stroke: "var(--border)" }} strokeWidth={1} />
            <text x={padL - 8} y={y(v) + 3} textAnchor="end" style={txt}>
              {Math.abs(v) >= 100 ? Math.round(v) : v % 1 === 0 ? v : v.toFixed(1)}
            </text>
          </g>
        ))}
        {tickIdx.map((i) => (
          <text key={i} x={x(i)} y={h - 6} textAnchor={i === 0 ? "start" : i === n - 1 ? "end" : "middle"} style={txt}>
            {labels[i]}
          </text>
        ))}
        <path d={path} fill="none" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" style={{ stroke: "var(--accent)" }} />
        <circle cx={x(li)} cy={y(data[li])} r={6.5} style={{ fill: "var(--surface)" }} />
        <circle cx={x(li)} cy={y(data[li])} r={4} style={{ fill: "var(--amber)" }} />
        <text x={W - padR + 4} y={y(data[li]) + 3} style={{ ...txt, fontWeight: 600 }}>
          {fmt ? fmt(data[li]) : data[li]}
        </text>
      </svg>
    </div>
  );
}
