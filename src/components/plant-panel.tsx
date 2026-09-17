"use client";

import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { Reading } from "@/lib/types";
import { statusFor, STATUS_COLOR, STATUS_LABEL, type Status } from "@/lib/status";
import StatusIcon from "@/components/status-icon";

function fmt(v: number | null | undefined, digits: number, unit: string) {
  if (v === null || v === undefined) return "-";
  return `${v.toFixed(digits)}${unit}`;
}

export function timeAgo(ts: string | null | undefined) {
  if (!ts) return "never";
  const ms = Date.now() - new Date(ts).getTime();
  const mins = Math.round(ms / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.round(hours / 24)}d ago`;
}

const METRICS = [
  { key: "soil_pct", label: "Soil", unit: "%", digits: 0 },
  { key: "root_temp_c", label: "Root", unit: "°C", digits: 1 },
  { key: "air_temp_c", label: "Air", unit: "°C", digits: 1 },
  { key: "humidity_pct", label: "Humidity", unit: "%", digits: 0 },
  { key: "pressure_hpa", label: "Pressure", unit: " hPa", digits: 0 },
  { key: "weight_g", label: "Weight", unit: "kg", digits: 2, scale: 1 / 1000 },
] as const;

type MetricKey = (typeof METRICS)[number]["key"];

export default function PlantPanel({
  name,
  variety,
  readings,
  loading,
  lastReadingLabel,
  stale,
}: {
  name: string;
  variety?: string | null;
  readings: Reading[];
  loading: boolean;
  lastReadingLabel?: string | null;
  stale?: boolean;
}) {
  const [metric, setMetric] = useState<MetricKey>("soil_pct");
  const metricDef = METRICS.find((m) => m.key === metric)!;

  const latest = readings[readings.length - 1];
  const status: Status = stale ? "idle" : statusFor(latest?.soil_pct);

  const chartData = readings
    .filter((r) => r[metric] !== null)
    .map((r) => ({
      time: new Date(r.ts).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" }),
      value: "scale" in metricDef ? r[metric]! * metricDef.scale : r[metric],
    }));

  return (
    <div className="rounded-2xl border border-border bg-surface p-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">{name}</h2>
          {variety && <p className="text-sm text-ink2">{variety}</p>}
        </div>
        <span
          className="flex items-center gap-2 rounded-full px-3 py-1 text-xs font-mono font-bold uppercase tracking-wide"
          style={{
            background: `color-mix(in srgb, ${STATUS_COLOR[status]} 16%, var(--surface))`,
          }}
        >
          <span style={{ color: STATUS_COLOR[status] }}>
            <StatusIcon status={status} size={10} />
          </span>
          {STATUS_LABEL[status]}
        </span>
      </div>
      {lastReadingLabel && (
        <p className="mt-1 text-xs text-ink2">Last reading {lastReadingLabel}</p>
      )}

      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3">
        <Tile label="Soil moisture" value={fmt(latest?.soil_pct, 0, "%")} />
        <Tile label="Root temp" value={fmt(latest?.root_temp_c, 1, "°C")} />
        <Tile label="Air temp" value={fmt(latest?.air_temp_c, 1, "°C")} />
        <Tile label="Humidity" value={fmt(latest?.humidity_pct, 0, "%")} />
        <Tile label="Pressure" value={fmt(latest?.pressure_hpa, 0, " hPa")} />
        <Tile
          label="Weight"
          value={fmt(latest?.weight_g ? latest.weight_g / 1000 : null, 2, "kg")}
        />
      </div>

      <div className="mt-6 flex flex-wrap gap-1.5">
        {METRICS.map((m) => (
          <button
            key={m.key}
            onClick={() => setMetric(m.key)}
            className={`rounded-full border px-2.5 py-1 font-mono text-[10px] uppercase tracking-wide ${
              metric === m.key
                ? "border-accent bg-accent text-accent-ink"
                : "border-border text-ink2"
            }`}
          >
            {m.label}
          </button>
        ))}
      </div>

      <div className="mt-3 h-56">
        {loading ? (
          <p className="text-sm text-ink2">Loading.</p>
        ) : chartData.length < 2 ? (
          <p className="text-sm text-ink2">Not enough data yet for a trend.</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid stroke="var(--border)" vertical={false} />
              <XAxis dataKey="time" stroke="var(--ink2)" fontSize={11} />
              <YAxis stroke="var(--ink2)" fontSize={11} width={32} />
              <Tooltip
                contentStyle={{
                  background: "var(--surface)",
                  border: "1px solid var(--border)",
                  borderRadius: 8,
                  fontSize: 12,
                }}
                formatter={(value) => [`${Number(value).toFixed(metricDef.digits)}${metricDef.unit}`, metricDef.label]}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="var(--canopy)"
                strokeWidth={2}
                dot={{ r: 3, fill: "var(--canopy)" }}
                activeDot={{ r: 5, fill: "var(--amber)" }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

function Tile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-bg px-3 py-2.5">
      <div className="text-[10px] font-medium uppercase tracking-wide text-ink2">{label}</div>
      <div className="mt-0.5 font-mono text-sm font-semibold">{value}</div>
    </div>
  );
}
