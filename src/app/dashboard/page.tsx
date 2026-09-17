import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { createOrganization, logout } from "./actions";
import DashboardView from "./dashboard-view";
import type { Org, Plant, IrrigationConfig } from "@/lib/types";

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>;
}) {
  const { error } = await searchParams;
  const supabase = await createClient();

  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  // RLS does the filtering here: this returns exactly the orgs the user is
  // a member of, plus the demo org - no manual union needed.
  const { data: orgs } = await supabase
    .from("organizations")
    .select("id, name, is_demo")
    .order("is_demo", { ascending: true });

  const realOrgs = (orgs ?? []).filter((o) => !o.is_demo) as Org[];
  const demoOrg = (orgs ?? []).find((o) => o.is_demo) as Org | undefined;

  if (realOrgs.length === 0) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-bg px-4">
        <div className="w-full max-w-sm rounded-2xl border border-border bg-surface p-8">
          <h1 className="font-[family-name:var(--font-display)] text-xl font-semibold text-ink">
            Name your organization
          </h1>
          <p className="mt-1 text-sm text-ink2">
            One more step before you see your dashboard.
          </p>
          {error && (
            <p className="mt-4 rounded-lg border border-status-critical/40 bg-status-critical/10 px-3 py-2 text-sm text-ink">
              {error}
            </p>
          )}
          <form action={createOrganization} className="mt-6 flex flex-col gap-3">
            <input
              name="orgName"
              type="text"
              placeholder="Organization name"
              required
              className="rounded-lg border border-border bg-bg px-3 py-2 text-sm text-ink outline-none focus:border-accent"
            />
            <button
              type="submit"
              className="rounded-lg bg-amber px-4 py-2 text-sm font-semibold text-forest"
            >
              Create
            </button>
          </form>
        </div>
      </main>
    );
  }

  const defaultOrg = realOrgs[0];
  const { data: plants } = await supabase
    .from("plants")
    .select("id, org_id, name, variety")
    .eq("org_id", defaultOrg.id);

  const defaultPlant = (plants ?? [])[0] as Plant | undefined;

  let irrigationConfig: IrrigationConfig | null = null;
  if (defaultPlant) {
    const { data } = await supabase
      .from("irrigation_config")
      .select("*")
      .eq("plant_id", defaultPlant.id)
      .maybeSingle();
    irrigationConfig = data as IrrigationConfig | null;
  }

  return (
    <DashboardView
      orgs={realOrgs}
      demoOrg={demoOrg ?? null}
      initialOrg={defaultOrg as Org}
      initialPlants={(plants ?? []) as Plant[]}
      initialPlant={defaultPlant ?? null}
      initialIrrigationConfig={irrigationConfig}
      userEmail={user.email ?? ""}
      logoutAction={logout}
    />
  );
}
