"use server";

import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { headers } from "next/headers";

export async function requestPasswordReset(formData: FormData) {
  const email = String(formData.get("email") ?? "");
  const supabase = await createClient();
  const origin = (await headers()).get("origin");

  // Supabase intentionally doesn't error for an unknown email here, to
  // avoid leaking which addresses have accounts.
  const { error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${origin}/auth/callback?next=/reset-password`,
  });

  if (error) {
    redirect(`/forgot-password?error=${encodeURIComponent(error.message)}`);
  }

  redirect("/forgot-password/check-email");
}
