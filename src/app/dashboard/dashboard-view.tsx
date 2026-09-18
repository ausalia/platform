"use client";

import { useState, useEffect, useCallback } from "react";
import { createClient } from "@/lib/supabase/client";
import type { Org, Plant, Reading, IrrigationConfig, PlantIngestStatus } from "@/lib/types";
import PlantPanel, { timeAgo } from "@/components/plant-panel";
import ThemeToggle from "@/components/theme-toggle";
import FarmMap from "@/components/farm-map";
import FarmGeoMap from "@/components/farm-geo-map";
import { statusFor, type Status } from "@/lib/status";

function pad2(n: number) {
  return n < 10 ? `0${n}` : `${n}`;
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
    supabase
      .from("plant_ingest_status")
      .select("*")
      .eq("org_id", selectedOrg.id)
      .then(({ data }) => {
        const map: Record<string, PlantIngestStatus> = {};
        for (const row of (data ?? []) as PlantIngestStatus[]) map[row.plant_id] = row;
        setIngestStatus(map);
      });
  }, [selectedOrg.id, supabase]);

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
      setIrrStatus("Save failed, try again");
      return;
    }
    setIrrigation(data as IrrigationConfig);
    setIrrStatus("Saved");
  }

  const plantIngest = selectedPlant ? ingestStatus[selectedPlant.id] : undefined;

  const statusByPlant: Record<string, Status> = {};
  for (const p of plants) {
    const ingest = ingestStatus[p.id];
    statusByPlant[p.id] =
      !isDemo && ingest?.is_stale ? "idle" : statusFor(ingest?.latest_soil_pct);
  }

  return (
    <main className="min-h-screen bg-bg px-6 py-6 text-ink">
      <div className="mx-auto max-w-5xl">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="font-[family-name:var(--font-display)] text-lg font-semibold">
            AUSELIA
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
            <ThemeToggle />
            <form action={logoutAction}>
              <button className="text-xs text-ink2 underline">Sign out</button>
            </form>
          </div>
        </div>

        {plants.length > 1 && (
          <div className="mt-4 rounded-2xl border border-border bg-surface p-4">
            {isDemo ? (
              <FarmGeoMap
                plants={plants}
                statusByPlant={statusByPlant}
                selectedPlantId={selectedPlant?.id}
                onSelect={setSelectedPlant}
              />
            ) : (
              <FarmMap
                plants={plants}
                statusByPlant={statusByPlant}
                selectedPlantId={selectedPlant?.id}
                onSelect={setSelectedPlant}
              />
            )}
          </div>
        )}

        {!selectedPlant ? (
          <p className="mt-10 text-center text-sm text-ink2">
            No plants in this organization yet.
          </p>
        ) : (
          <div className="mt-6 grid gap-6 md:grid-cols-[1fr_320px]">
            <PlantPanel
              name={selectedPlant.name}
              variety={selectedPlant.variety}
              readings={readings}
              loading={loading}
              stale={plantIngest?.is_stale}
              lastReadingLabel={
                isDemo ? null : timeAgo(plantIngest?.last_reading_at ?? readings[readings.length - 1]?.ts)
              }
            />

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

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-[10px] font-medium uppercase tracking-wide text-ink2">{label}</label>
      {children}
    </div>
  );
}
