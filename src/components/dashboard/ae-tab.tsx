"use client";

import type { Lang, Strings } from "@/lib/dashboard/i18n";
import { DAYS, aeDates } from "@/lib/dashboard/sim";
import LineChart from "./line-chart";

export default function AeTab({
  t, lang, ae, sourceLabel,
}: {
  t: Strings; lang: Lang; ae: number[]; sourceLabel: string;
}) {
  const dates = aeDates();
  const locale = lang === "es" ? "es-CL" : undefined;
  const fmtDate = (d: Date) => d.toLocaleDateString(locale, { month: "short", day: "numeric" });
  const last14 = ae.slice(DAYS - 14);
  const sum7 = ae.slice(DAYS - 7).reduce((a, b) => a + b, 0);
  let peakIdx = 0;
  ae.forEach((v, i) => { if (v > ae[peakIdx]) peakIdx = i; });

  const stats = [
    [t.eventsToday, String(ae[DAYS - 1])],
    [t.sevenDayTotal, String(sum7)],
    [t.peakDay, fmtDate(dates[peakIdx])],
    [t.confirmedRate, "68%"],
  ];

  return (
    <>
      <div className="flex items-center gap-1.5 text-xs font-semibold text-ink2">
        <span className="h-0.5 w-3 rounded-[1px] bg-accent" />
        {sourceLabel}
      </div>
      <LineChart data={last14} labels={dates.slice(DAYS - 14).map(fmtDate)} />
      <div className="grid grid-cols-2 gap-2">
        {stats.map(([k, v]) => (
          <div key={k} className="rounded-[10px] border border-border px-3.5 py-2.5">
            <div className="text-[10px] uppercase tracking-[0.04em] text-ink2">{k}</div>
            <div className="mt-[3px] font-mono text-[17px] font-semibold">{v}</div>
          </div>
        ))}
      </div>
    </>
  );
}
