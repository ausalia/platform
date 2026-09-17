"use client";

import { useState, useCallback, useEffect } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";
import PlantPanel from "@/components/plant-panel";
import ThemeToggle from "@/components/theme-toggle";
import FarmGeoMap from "@/components/farm-geo-map";
import { statusFor, type Status } from "@/lib/status";
import type { Plant, Reading, PlantIngestStatus } from "@/lib/types";

export default function DemoView({
  orgName,
  plants,
  initialPlant,
  initialReadings,
}: {
  orgName: string;
  plants: Plant[];
  initialPlant: Plant | null;
  initialReadings: Reading[];
}) {
  const supabase = createClient();
  const [selectedPlant, setSelectedPlant] = useState(initialPlant);
  const [readings, setReadings] = useState<Reading[]>(initialReadings);
  const [loading, setLoading] = useState(false);
  const [ingestStatus, setIngestStatus] = useState<Record<string, PlantIngestStatus>>({});

  useEffect(() => {
    if (!initialPlant) return;
    supabase
      .from("plant_ingest_status")
      .select("*")
      .eq("org_id", initialPlant.org_id)
      .then(({ data }) => {
        const map: Record<string, PlantIngestStatus> = {};
        for (const row of (data ?? []) as PlantIngestStatus[]) map[row.plant_id] = row;
        setIngestStatus(map);
      });
    // Only needs to run once - this page has a single fixed org.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadReadings = useCallback(
    async (plant: Plant) => {
      setLoading(true);
      const { data } = await supabase
        .from("readings")
        .select("*")
        .eq("plant_id", plant.id)
        .order("ts", { ascending: true })
        .limit(200);
      setReadings((data ?? []) as Reading[]);
      setLoading(false);
    },
    [supabase],
  );

  useEffect(() => {
    if (selectedPlant && selectedPlant.id !== initialPlant?.id) loadReadings(selectedPlant);
    // Only re-fetch on a real plant switch - the initial plant's readings
    // already arrived from the server render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedPlant]);

  const statusByPlant: Record<string, Status> = {};
  for (const p of plants) {
    statusByPlant[p.id] = statusFor(ingestStatus[p.id]?.latest_soil_pct);
  }

  return (
    <main className="min-h-screen bg-bg px-6 py-6 text-ink">
      <div className="mx-auto max-w-5xl">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link href="/" className="font-[family-name:var(--font-display)] text-lg font-semibold">
            AUSALIA
          </Link>
          <div className="flex items-center gap-3">
            <span className="text-xs text-ink2">{orgName} · demo</span>
            <ThemeToggle />
            <Link
              href="/login"
              className="rounded-full border border-border px-3 py-1.5 text-xs font-mono uppercase tracking-wide text-ink2"
            >
              Partner sign in
            </Link>
          </div>
        </div>

        {plants.length > 1 && (
          <div className="mt-4 rounded-2xl border border-border bg-surface p-4">
            <FarmGeoMap
              plants={plants}
              statusByPlant={statusByPlant}
              selectedPlantId={selectedPlant?.id}
              onSelect={setSelectedPlant}
            />
          </div>
        )}

        {!selectedPlant ? (
          <p className="mt-10 text-center text-sm text-ink2">No plants in the demo yet.</p>
        ) : (
          <div className="mt-6 max-w-2xl">
            <PlantPanel
              name={selectedPlant.name}
              variety={selectedPlant.variety}
              readings={readings}
              loading={loading}
            />
          </div>
        )}
      </div>
    </main>
  );
}
