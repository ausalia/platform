// Device readings ingest. A plant/device POSTs its sensor snapshot here.
//
// Auth: apikey header = project publishable key (platform gate, checked by
// withSupabase before this code runs). X-Api-Key header = this specific
// plant's own key (see _shared/device.ts) - that's what ties the reading
// to a plant_id.

import "@supabase/functions-js/edge-runtime.d.ts";
import { withSupabase } from "@supabase/server";
import { authenticateDevice, jsonResponse } from "../_shared/device.ts";

function num(v: unknown): number | null {
  if (v === null || v === undefined) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

export default {
  fetch: withSupabase({ auth: ["publishable", "secret"] }, async (req, ctx) => {
    if (req.method !== "POST") {
      return jsonResponse({ error: "method not allowed" }, 405);
    }

    const device = await authenticateDevice(req, ctx.supabaseAdmin);
    if (!device) {
      return jsonResponse({ error: "invalid or missing X-Api-Key" }, 401);
    }

    let payload: Record<string, unknown>;
    try {
      payload = await req.json();
    } catch {
      return jsonResponse({ error: "invalid JSON" }, 400);
    }

    const record = {
      plant_id: device.plantId,
      soil_pct: num(payload.soil_pct),
      root_temp_c: num(payload.root_temp_c),
      air_temp_c: num(payload.air_temp_c),
      humidity_pct: num(payload.humidity_pct),
      pressure_hpa: num(payload.pressure_hpa),
      weight_g: num(payload.weight_g),
    };

    const { data, error } = await ctx.supabaseAdmin
      .from("readings")
      .insert(record)
      .select()
      .single();

    if (error) {
      console.error("ingest insert failed", error);
      return jsonResponse({ error: "insert failed" }, 500);
    }

    return jsonResponse({ ok: true, stored: data }, 201);
  }),
};
