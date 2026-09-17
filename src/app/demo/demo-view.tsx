"use client";

import { useState, useCallback, useEffect } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";
import PlantPanel from "@/components/plant-panel";
import ThemeToggle from "@/components/theme-toggle";
import type { Plant, Reading } from "@/lib/types";

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
          <div className="mt-4 flex flex-wrap gap-2">
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
              </button>
            ))}
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
