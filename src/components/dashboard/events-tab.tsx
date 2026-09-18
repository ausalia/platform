"use client";

import { useState } from "react";
import type { Lang, Strings } from "@/lib/dashboard/i18n";
import { DAYS, aeDates, eventsForDay, type AeEvent } from "@/lib/dashboard/sim";
import { Segmented } from "./ui";

function Waveform({ decay }: { decay: number }) {
  const W = 280, H = 110, mid = H / 2, cycles = 18;
  const pts: string[] = [];
  for (let i = 0; i <= 200; i++) {
    const tt = i / 200, env = Math.exp(-decay * tt * 6);
    pts.push(`${(tt * W).toFixed(1)},${(mid - env * Math.sin(tt * cycles * Math.PI * 2) * (mid - 8)).toFixed(1)}`);
  }
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height={H}>
      <line x1={0} y1={mid} x2={W} y2={mid} strokeWidth={1} style={{ stroke: "var(--border)" }} />
      <path d={"M" + pts.join(" L")} fill="none" strokeWidth={1.6} strokeLinecap="round" style={{ stroke: "var(--amber)" }} />
    </svg>
  );
}

export default function EventsTab({
  t, lang, nodeLabel, ae, sensorCount, fixedSensor,
}: {
  t: Strings; lang: Lang; nodeLabel: string; ae: number[]; sensorCount: number; fixedSensor?: string;
}) {
  const [view, setView] = useState<"list" | "calendar">("list");
  const [openKey, setOpenKey] = useState<string | null>(null);
  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const dates = aeDates();
  const locale = lang === "es" ? "es-CL" : undefined;
  const fmtDate = (d: Date) => d.toLocaleDateString(locale, { month: "short", day: "numeric" });
  const evs = (d: number) => eventsForDay(ae, d, sensorCount, fixedSensor);

  function row(ev: AeEvent, key: string) {
    const open = openKey === key;
    const feats: [string, string][] = [
      [t.featAmp, `${ev.amp} mV`], [t.featFreq, `${ev.freq} kHz`], [t.featRise, `${ev.rise} µs`],
      [t.featDur, `${ev.dur} µs`], [t.featEnergy, `${ev.energy} aJ`], [t.featCounts, String(ev.counts)],
      [t.featRms, `${ev.rms} mV`], [t.featLocation, `${nodeLabel} · ${ev.sensorLabel}`],
    ];
    return (
      <div key={key} className="border-b border-border last:border-b-0">
        <button
          onClick={() => setOpenKey(open ? null : key)}
          className="flex w-full items-center gap-3 px-1 py-3 text-left hover:bg-surface-2"
        >
          <span className={`w-3.5 text-[11px] text-ink2 transition-transform ${open ? "rotate-90" : ""}`}>▸</span>
          <span className="flex-none font-mono text-xs text-ink2">{fmtDate(dates[ev.dayIdx])}, {ev.time}</span>
          <span className="flex-1 text-[13px] text-ink2">{ev.amp} mV · {ev.freq} kHz</span>
          <span className="flex-none rounded-[5px] bg-surface-2 px-[7px] py-0.5 font-mono text-[10px] font-semibold text-ink2">
            {ev.sensorLabel}
          </span>
          <span
            className="flex-none rounded-[5px] border px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-[0.04em] text-ink"
            style={{
              borderColor: ev.cls === "confirmed" ? "var(--status-critical)" : "var(--status-stress)",
              background: `color-mix(in srgb, ${ev.cls === "confirmed" ? "var(--status-critical) 20%" : "var(--status-stress) 24%"}, var(--surface))`,
            }}
          >
            {t[ev.cls]}
          </span>
        </button>
        {open && (
          <div className="grid gap-3 pb-4 pl-5 pr-1 pt-1.5">
            <div className="rounded-[10px] bg-surface-2 p-3.5">
              <div className="mb-2 text-[11px] uppercase tracking-[0.04em] text-ink2">{t.waveformCap}</div>
              <Waveform decay={1 / (ev.dur / 120)} />
            </div>
            <div className="grid grid-cols-2 content-start gap-x-[18px] gap-y-2.5">
              {feats.map(([k, v]) => (
                <div key={k} className="flex justify-between gap-2 border-b border-dashed border-border pb-1.5 text-[12.5px]">
                  <span className="flex-none text-ink2">{k}</span>
                  <span className="min-w-0 text-right font-mono font-semibold">{v}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  const recent: number[] = [];
  for (let d = DAYS - 1; d >= 0 && recent.length < 6; d--) if (ae[d] > 0) recent.push(d);

  const maxCount = Math.max(1, ...ae);
  const heat = (c: number) =>
    c === 0 ? "transparent" : `color-mix(in srgb, var(--accent) ${Math.round(15 + Math.min(1, c / maxCount) * 70)}%, var(--surface))`;
  const monthLabel = dates[0].toLocaleDateString(locale, { month: "long", year: "numeric" });
  const firstDow = (dates[0].getDay() + 6) % 7;

  return (
    <>
      <Segmented
        value={view}
        onChange={(v) => { setView(v); setOpenKey(null); setSelectedDay(null); }}
        options={[{ value: "list", label: t.listView }, { value: "calendar", label: t.calView }]}
      />
      {view === "list" ? (
        <div>
          <div className="px-1 pt-2.5 text-xs text-ink2">{t.tapInspect}</div>
          {recent.flatMap((d) => evs(d).map((ev, i) => row(ev, `${d}-${i}`)))}
        </div>
      ) : (
        <div>
          <div className="rounded-[14px] border border-border bg-surface p-4">
            <div className="mb-2.5 font-[family-name:var(--font-display)] text-sm font-bold capitalize">{monthLabel}</div>
            <div className="grid grid-cols-7 gap-[5px]">
              {t.dow.map((d) => (
                <div key={d} className="pb-1 text-center text-[10px] uppercase tracking-[0.04em] text-ink2">{d}</div>
              ))}
              {Array.from({ length: firstDow }, (_, i) => <div key={"e" + i} className="invisible" />)}
              {dates.map((d, idx) => (
                <button
                  key={idx}
                  onClick={() => { setSelectedDay(selectedDay === idx ? null : idx); setOpenKey(null); }}
                  className={`relative flex aspect-square flex-col items-center justify-center rounded-lg font-mono ${
                    selectedDay === idx ? "border-2 border-accent" : "border-[1.5px] border-border"
                  }`}
                  style={{ background: heat(ae[idx]) }}
                >
                  <span className="absolute left-1.5 top-1 text-[11px] text-ink2">{d.getDate()}</span>
                  <span className="text-[15px] font-bold">{ae[idx] > 0 ? ae[idx] : ""}</span>
                </button>
              ))}
            </div>
          </div>
          {selectedDay !== null && (
            <div className="mt-3.5 rounded-[14px] border border-border bg-surface px-4 pb-3 pt-1.5">
              {evs(selectedDay).length === 0 ? (
                <div className="p-[30px] text-center text-[13px] text-ink2">
                  {fmtDate(dates[selectedDay])} · {t.events0}
                </div>
              ) : (
                evs(selectedDay).map((ev, i) => row(ev, `${selectedDay}-${i}`))
              )}
            </div>
          )}
        </div>
      )}
    </>
  );
}
