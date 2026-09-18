"use client";

import type { Lang, Strings } from "@/lib/dashboard/i18n";
import { ENV_KEYS, lastNonNull, type EnvKey, type EnvSeries, type Range } from "@/lib/dashboard/env";
import LineChart from "./line-chart";
import { Segmented } from "./ui";

export default function EnvTab({
  t, lang, isLive, dates, env, sourceLabel, envVar, onEnvVar, range, onRange, loading,
}: {
  t: Strings; lang: Lang; isLive: boolean;
  dates: Date[]; env: EnvSeries; sourceLabel: string;
  envVar: EnvKey; onEnvVar: (k: EnvKey) => void;
  range: Range; onRange: (r: Range) => void; loading: boolean;
}) {
  const locale = lang === "es" ? "es-CL" : undefined;
  const meta = ENV_KEYS.find((v) => v.key === envVar)!;

  const pairs: { d: Date; v: number }[] = [];
  const series = env[envVar] ?? [];
  series.forEach((v, i) => {
    if (v !== null && v !== undefined && !Number.isNaN(v) && dates[i]) pairs.push({ d: dates[i], v });
  });

  return (
    <>
      <Segmented
        value={range}
        onChange={onRange}
        options={[
          { value: "day", label: t.rangeDay },
          { value: "week", label: t.rangeWeek },
          { value: "month", label: t.rangeMonth },
        ]}
      />
      <div className="grid grid-cols-2 gap-2">
        {ENV_KEYS.map((v) => {
          const unavailable = v.never || (v.liveOff && isLive);
          const last = unavailable ? null : lastNonNull(env[v.key]);
          const base = "rounded-[10px] border-[1.5px] px-[11px] py-[9px] text-left";
          if (unavailable || last === null) {
            return (
              <button key={v.key} disabled className={`${base} cursor-not-allowed border-border bg-surface opacity-50`}>
                <div className="mb-[3px] text-[9.5px] uppercase tracking-[0.03em] text-ink2">{t[v.key]}</div>
                <div className="text-[11px] font-medium italic text-ink2">
                  {unavailable ? t.noSensor : loading ? `${t.loading}…` : t.waitingForData}
                </div>
              </button>
            );
          }
          return (
            <button
              key={v.key}
              onClick={() => onEnvVar(v.key)}
              className={`${base} bg-surface ${v.key === envVar ? "border-accent bg-accent-soft" : "border-border hover:border-accent/50"}`}
            >
              <div className="mb-[3px] text-[9.5px] uppercase tracking-[0.03em] text-ink2">{t[v.key]}</div>
              <div className="font-mono text-sm font-semibold">{v.fmt(last)}</div>
            </button>
          );
        })}
      </div>
      <div className="flex items-center gap-1.5 text-xs font-semibold text-ink2">
        <span className="h-0.5 w-3 rounded-[1px] bg-accent" />
        {t[envVar]} · {sourceLabel}
      </div>
      {pairs.length < 2 ? (
        <div className="p-[30px] text-center text-[13px] text-ink2">
          {range === "day" ? `${t.waitingForData}…` : t.needsMoreDays}
        </div>
      ) : (
        <LineChart
          data={pairs.map((p) => p.v)}
          labels={pairs.map((p) =>
            range === "day"
              ? p.d.toLocaleString(locale, { hour: "2-digit", minute: "2-digit" })
              : p.d.toLocaleDateString(locale, { month: "short", day: "numeric" }),
          )}
          fmt={meta.fmt}
        />
      )}
    </>
  );
}
