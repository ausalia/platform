"use client";

import { useState, useEffect, useCallback } from "react";
import { createClient } from "@/lib/supabase/client";
import type { Org, Plant, Reading, IrrigationConfig, PlantIngestStatus } from "@/lib/types";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type Status = "good" | "warning" | "critical" | "idle";

function statusFor(soilPct: number | null | undefined): Status {
  if (soilPct === null || soilPct === undefined) return "idle";
  if (soilPct < 20) return "critical";
  if (soilPct < 40) return "warning";
  return "good";
}

const STATUS_COLOR: Record<Status, string> = {
  good: "var(--status-ok)",
  warning: "var(--status-stress)",
  critical: "var(--status-critical)",
  idle: "var(--status-idle)",
};

const STATUS_LABEL: Record<Status, string> = {
  good: "Nominal",
  warning: "Elevated",
  critical: "Critical",
  idle: "No data",
};

function pad2(n: number) {
  return n < 10 ? `0${n}` : `${n}`;
}

function fmt(v: number | null | undefined, digits: number, unit: string) {
  if (v === null || v === undefined) return "—";
  return `${v.toFixed(digits)}${unit}`;
}

function timeAgo(ts: string | null | undefined) {
  if (!ts) return "never";
  const ms = Date.now() - new Date(ts).getTime();
  const mins = Math.round(ms / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.round(hours / 24)}d ago`;
}

export default function DashboardView({
  orgs,
  demoOrg,
  initialOrg,
  initialPlants,
  initialPlant,
  initialIrrigationConfig,
  userEmail,
  logoutAction,
}: {
  orgs: Org[];
  demoOrg: Org | null;
  initialOrg: Org;
  initialPlants: Plant[];
  initialPlant: Plant | null;
  initialIrrigationConfig: IrrigationConfig | null;
  userEmail: string;
  logoutAction: () => void;
}) {
  const supabase = createClient();

  const allOrgs = demoOrg ? [...orgs, demoOrg] : orgs;
  const [selectedOrg, setSelectedOrg] = useState(initialOrg);
  const [plants, setPlants] = useState(initialPlants);
  const [selectedPlant, setSelectedPlant] = useState(initialPlant);
  const [readings, setReadings] = useState<Reading[]>([]);
  const [irrigation, setIrrigation] = useState(initialIrrigationConfig);
  const [irrStatus, setIrrStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [ingestStatus, setIngestStatus] = useState<Record<string, PlantIngestStatus>>({});

  const isDemo = selectedOrg.is_demo;

  useEffect(() => {
    if (isDemo) {
      setIngestStatus({});
      return;
    }
    supabase
      .from("plant_ingest_status")
      .select("*")
      .eq("org_id", selectedOrg.id)
      .then(({ data }) => {
        const map: Record<string, PlantIngestStatus> = {};
        for (const row of (data ?? []) as PlantIngestStatus[]) map[row.plant_id] = row;
        setIngestStatus(map);
      });
  }, [selectedOrg.id, isDemo, supabase]);

  const loadPlantData = useCallback(
    async (plant: Plant) => {
      setLoading(true);
      const [{ data: readingsData }, { data: irrData }] = await Promise.all([
        supabase
          .from("readings")
          .select("*")
          .eq("plant_id", plant.id)
          .order("ts", { ascending: true })
          .limit(200),
        supabase
          .from("irrigation_config")
          .select("*")
          .eq("plant_id", plant.id)
          .maybeSingle(),
      ]);
      setReadings((readingsData ?? []) as Reading[]);
      setIrrigation(irrData as IrrigationConfig | null);
      setLoading(false);
    },
    [supabase],
  );

  useEffect(() => {
    if (selectedPlant) loadPlantData(selectedPlant);
  }, [selectedPlant, loadPlantData]);

  async function handleOrgChange(orgId: string) {
    const org = allOrgs.find((o) => o.id === orgId)!;
    setSelectedOrg(org);
    setLoading(true);
    const { data: plantsData } = await supabase
      .from("plants")
      .select("id, org_id, name, variety")
      .eq("org_id", org.id);
    const newPlants = (plantsData ?? []) as Plant[];
    setPlants(newPlants);
    setSelectedPlant(newPlants[0] ?? null);
  }

  async function saveIrrigation(formData: FormData) {
    if (!selectedPlant) return;
    const t1 = String(formData.get("time1"));
    const t2 = String(formData.get("time2"));
    const duration = Number(formData.get("duration"));
    const enabled = formData.get("enabled") === "on";
    const [h1, m1] = t1.split(":").map(Number);
    const [h2, m2] = t2.split(":").map(Number);

    setIrrStatus("Saving…");
    const { data, error } = await supabase
      .from("irrigation_config")
      .upsert({
        plant_id: selectedPlant.id,
        hour1: h1,
        min1: m1,
        hour2: h2,
        min2: m2,
        duration_min: duration,
        enabled,
        updated_at: new Date().toISOString(),
      })
      .select()
      .single();

    if (error) {
      setIrrStatus("Save failed — try again");
      return;
    }
    setIrrigation(data as IrrigationConfig);
    setIrrStatus("Saved");
  }

  const latest = readings[readings.length - 1];
  const plantIngest = selectedPlant ? ingestStatus[selectedPlant.id] : undefined;
  const status: Status = plantIngest?.is_stale ? "idle" : statusFor(latest?.soil_pct);
  const chartData = readings
    .filter((r) => r.soil_pct !== null)
    .map((r) => ({
      time: new Date(r.ts).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" }),
      soil_pct: r.soil_pct,
    }));

  return (
    <main className="min-h-screen bg-bg px-6 py-6 text-ink">
      <div className="mx-auto max-w-5xl">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="font-[family-name:var(--font-display)] text-lg font-semibold">
            AUSALIA
          </h1>
          <div className="flex items-center gap-3">
            <select
              value={selectedOrg.id}
              onChange={(e) => handleOrgChange(e.target.value)}
              className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-ink"
            >
              {orgs.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.name}
                </option>
              ))}
              {demoOrg && (
                <option value={demoOrg.id}>{demoOrg.name} (demo)</option>
              )}
            </select>
            <span className="text-xs text-ink2">{userEmail}</span>
            <form action={logoutAction}>
              <button className="text-xs text-ink2 underline">Sign out</button>
            </form>
          </div>
        </div>

        {plants.length > 1 && (
          <div className="mt-4 flex gap-2">
            {plants.map((p) => (
              <button
                key={p.id}
                onClick={() => setSelectedPlant(p)}
                className={`rounded-full border px-3 py-1 text-xs font-mono ${
                  selectedPlant?.id === p.id
                    ? "border-accent bg-accent text-accent-ink"
                    : "border-border text-ink2"
                }`}
              >
                {p.name}
                {ingestStatus[p.id]?.is_stale && (
                  <span className="ml-1" style={{ color: "var(--status-stress)" }}>
                    · stale
                  </span>
                )}
              </button>
            ))}
          </div>
        )}

        {!selectedPlant ? (
          <p className="mt-10 text-center text-sm text-ink2">
            No plants in this organization yet.
          </p>
        ) : (
          <div className="mt-6 grid gap-6 md:grid-cols-[1fr_320px]">
            <div className="rounded-2xl border border-border bg-surface p-5">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold">{selectedPlant.name}</h2>
                  <p className="text-sm text-ink2">{selectedPlant.variety}</p>
                </div>
                <span
                  className="flex items-center gap-2 rounded-full px-3 py-1 text-xs font-mono font-bold uppercase tracking-wide"
                  style={{
                    background: `color-mix(in srgb, ${STATUS_COLOR[status]} 16%, var(--surface))`,
                  }}
                >
                  <span
                    className="h-2 w-2 rounded-full"
                    style={{ background: STATUS_COLOR[status] }}
                  />
                  {STATUS_LABEL[status]}
                </span>
              </div>
              {!isDemo && (
                <p className="mt-1 text-xs text-ink2">
                  Last reading {timeAgo(plantIngest?.last_reading_at ?? latest?.ts)}
                </p>
              )}

              <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3">
                <Tile label="Soil moisture" value={fmt(latest?.soil_pct, 0, "%")} />
                <Tile label="Root temp" value={fmt(latest?.root_temp_c, 1, "°C")} />
                <Tile label="Air temp" value={fmt(latest?.air_temp_c, 1, "°C")} />
                <Tile label="Humidity" value={fmt(latest?.humidity_pct, 0, "%")} />
                <Tile label="Pressure" value={fmt(latest?.pressure_hpa, 0, " hPa")} />
                <Tile label="Weight" value={fmt(latest?.weight_g ? latest.weight_g / 1000 : null, 2, "kg")} />
              </div>

              <div className="mt-6 h-56">
                {loading ? (
                  <p className="text-sm text-ink2">Loading…</p>
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
                      />
                      <Line
                        type="monotone"
                        dataKey="soil_pct"
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

            {!isDemo && (
              <div className="rounded-2xl border border-border bg-surface p-5">
                <h3 className="text-xs font-semibold uppercase tracking-wide text-ink2">
                  Irrigation schedule
                </h3>
                <form action={saveIrrigation} className="mt-4 flex flex-col gap-4">
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      name="enabled"
                      defaultChecked={irrigation?.enabled ?? true}
                    />
                    Enabled
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Morning">
                      <input
                        type="time"
                        name="time1"
                        defaultValue={`${pad2(irrigation?.hour1 ?? 8)}:${pad2(irrigation?.min1 ?? 0)}`}
                        className="w-full rounded-lg border border-border bg-bg px-2 py-1.5 text-sm"
                      />
                    </Field>
                    <Field label="Afternoon">
                      <input
                        type="time"
                        name="time2"
                        defaultValue={`${pad2(irrigation?.hour2 ?? 18)}:${pad2(irrigation?.min2 ?? 0)}`}
                        className="w-full rounded-lg border border-border bg-bg px-2 py-1.5 text-sm"
                      />
                    </Field>
                  </div>
                  <Field label="Duration (min)">
                    <input
                      type="number"
                      name="duration"
                      min={0}
                      max={60}
                      defaultValue={irrigation?.duration_min ?? 5}
                      className="w-full rounded-lg border border-border bg-bg px-2 py-1.5 text-sm"
                    />
                  </Field>
                  <div className="flex items-center gap-3">
                    <button
                      type="submit"
                      className="rounded-lg bg-amber px-4 py-2 text-sm font-semibold text-forest"
                    >
                      Save schedule
                    </button>
                    <span className="text-xs text-ink2">{irrStatus}</span>
                  </div>
                </form>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
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

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-[10px] font-medium uppercase tracking-wide text-ink2">{label}</label>
      {children}
    </div>
  );
}
