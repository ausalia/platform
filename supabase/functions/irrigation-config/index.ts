// Device-facing irrigation schedule poll (GET only - the dashboard writes
// directly via the Supabase client + RLS, no function needed for that side).
//
// Same two-layer auth as ingest: apikey = project publishable key (platform
// gate), X-Api-Key = this plant's own key (see _shared/device.ts).

import "@supabase/functions-js/edge-runtime.d.ts";
import { withSupabase } from "@supabase/server";
import { authenticateDevice, jsonResponse } from "../_shared/device.ts";

const DEFAULTS = { hour1: 8, min1: 0, hour2: 18, min2: 0, durationMin: 5, enabled: true };

export default {
  fetch: withSupabase({ auth: ["publishable", "secret"] }, async (req, ctx) => {
    if (req.method !== "GET") {
      return jsonResponse({ error: "method not allowed" }, 405);
    }

    const device = await authenticateDevice(req, ctx.supabaseAdmin);
    if (!device) {
      return jsonResponse({ error: "invalid or missing X-Api-Key" }, 401);
    }

    const { data, error } = await ctx.supabaseAdmin
      .from("irrigation_config")
      .select("hour1, min1, hour2, min2, duration_min, enabled")
      .eq("plant_id", device.plantId)
      .maybeSingle();

    if (error) {
      console.error("irrigation-config lookup failed", error);
      return jsonResponse({ error: "lookup failed" }, 500);
    }

    if (!data) {
      // No row yet for this plant (e.g. freshly provisioned) - fall back to
      // the same defaults the schema itself uses, so the device always gets
      // a sane schedule rather than an error.
      return jsonResponse(DEFAULTS);
    }

    return jsonResponse({
      hour1: data.hour1,
      min1: data.min1,
      hour2: data.hour2,
      min2: data.min2,
      durationMin: data.duration_min,
      enabled: data.enabled,
    });
  }),
};
