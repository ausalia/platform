import { createClient } from "@/lib/supabase/server";
import DemoView from "./demo-view";
import type { Plant, Reading } from "@/lib/types";

// Public, unauthenticated page - the demo org is readable by anyone per its
// RLS policy (is_demo = true bypasses the membership check), so this needs
// no login at all. Lets someone try the product before creating an account.
export default async function DemoPage() {
  const supabase = await createClient();

  const { data: org } = await supabase
    .from("organizations")
    .select("id, name")
    .eq("is_demo", true)
    .maybeSingle();

  if (!org) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-bg px-4 text-ink">
        <p className="text-sm text-ink2">Demo isn&apos;t set up yet.</p>
      </main>
    );
  }

  const { data: plants } = await supabase
    .from("plants")
    .select("id, org_id, name, variety")
    .eq("org_id", org.id)
    .order("name");

  const firstPlant = (plants ?? [])[0] as Plant | undefined;
  let readings: Reading[] = [];
  if (firstPlant) {
    const { data } = await supabase
      .from("readings")
      .select("*")
      .eq("plant_id", firstPlant.id)
      .order("ts", { ascending: true })
      .limit(200);
    readings = (data ?? []) as Reading[];
  }

  return (
    <DemoView
      orgName={org.name}
      plants={(plants ?? []) as Plant[]}
      initialPlant={firstPlant ?? null}
      initialReadings={readings}
    />
  );
}
