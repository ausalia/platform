"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

export async function signup(formData: FormData) {
  const email = String(formData.get("email") ?? "");
  const password = String(formData.get("password") ?? "");
  const orgName = String(formData.get("orgName") ?? "").trim();

  const supabase = await createClient();
  const { data, error } = await supabase.auth.signUp({ email, password });

  if (error) {
    redirect(`/signup?error=${encodeURIComponent(error.message)}`);
  }

  // No session yet means this project requires email confirmation - there's
  // no authenticated request to safely create their org from yet. The
  // dashboard page itself handles "logged in but no org" as an onboarding
  // step, so this resolves itself on their first real login.
  if (!data.session) {
    redirect("/signup/check-email");
  }

  const { data: org, error: orgError } = await supabase
    .from("organizations")
    .insert({ name: orgName || `${email}'s workspace` })
    .select("id")
    .single();

  if (orgError) {
    redirect(`/signup?error=${encodeURIComponent(orgError.message)}`);
  }

  await supabase.from("memberships").insert({
    user_id: data.session!.user.id,
    org_id: org!.id,
    role: "owner",
  });

  redirect("/dashboard");
}
