"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";

export async function createOrganization(formData: FormData) {
  const orgName = String(formData.get("orgName") ?? "").trim();
  const supabase = await createClient();

  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  // Insert without .select(): reading the new row back would require the
  // organizations SELECT policy (is_org_member) to pass, but no membership
  // exists yet at this point in the transaction - RLS would reject the
  // RETURNING and roll back the whole insert. Generating the id ourselves
  // avoids needing it read back at all.
  const orgId = crypto.randomUUID();

  const { error: orgError } = await supabase
    .from("organizations")
    .insert({ id: orgId, name: orgName || `${user!.email}'s workspace` });

  if (orgError) {
    redirect(`/dashboard?error=${encodeURIComponent(orgError.message)}`);
  }

  const { error: memberError } = await supabase.from("memberships").insert({
    user_id: user!.id,
    org_id: orgId,
    role: "owner",
  });

  if (memberError) {
    redirect(`/dashboard?error=${encodeURIComponent(memberError.message)}`);
  }

  revalidatePath("/dashboard");
}

export async function logout() {
  const supabase = await createClient();
  await supabase.auth.signOut();
  redirect("/login");
}
