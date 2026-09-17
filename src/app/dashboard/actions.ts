"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";

export async function createOrganization(formData: FormData) {
  const orgName = String(formData.get("orgName") ?? "").trim();
  const supabase = await createClient();

  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: org, error: orgError } = await supabase
    .from("organizations")
    .insert({ name: orgName || `${user!.email}'s workspace` })
    .select("id")
    .single();

  if (orgError) {
    redirect(`/dashboard?error=${encodeURIComponent(orgError.message)}`);
  }

  await supabase.from("memberships").insert({
    user_id: user!.id,
    org_id: org!.id,
    role: "owner",
  });

  revalidatePath("/dashboard");
}

export async function logout() {
  const supabase = await createClient();
  await supabase.auth.signOut();
  redirect("/login");
}
