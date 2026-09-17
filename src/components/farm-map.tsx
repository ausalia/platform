"use client";

import type { Plant } from "@/lib/types";
import { STATUS_COLOR, STATUS_LABEL, type Status } from "@/lib/status";
import StatusIcon from "@/components/status-icon";

const LEGEND_ORDER: Status[] = ["good", "warning", "critical", "idle"];

export default function FarmMap({
  plants,
  statusByPlant,
  selectedPlantId,
  onSelect,
}: {
  plants: Plant[];
  statusByPlant: Record<string, Status>;
  selectedPlantId?: string;
  onSelect: (plant: Plant) => void;
}) {
  return (
    <div>
      <div className="grid grid-cols-4 gap-2 sm:grid-cols-5 md:grid-cols-7">
        {plants.map((p) => {
          const status = statusByPlant[p.id] ?? "idle";
          const selected = p.id === selectedPlantId;
          return (
            <button
              key={p.id}
              onClick={() => onSelect(p)}
              className={`flex flex-col items-center justify-center gap-1.5 rounded-lg border px-2 py-3 text-center ${
                selected ? "border-accent" : "border-border"
              }`}
              style={{
                background: `color-mix(in srgb, ${STATUS_COLOR[status]} 22%, var(--surface))`,
              }}
            >
              <span style={{ color: STATUS_COLOR[status] }}>
                <StatusIcon status={status} size={12} />
              </span>
              <span className="font-mono text-[10px] leading-tight text-ink">{p.name}</span>
            </button>
          );
        })}
      </div>
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1.5">
        {LEGEND_ORDER.map((s) => (
          <span
            key={s}
            className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wide text-ink2"
          >
            <span style={{ color: STATUS_COLOR[s] }}>
              <StatusIcon status={s} size={9} />
            </span>
            {STATUS_LABEL[s]}
          </span>
        ))}
      </div>
    </div>
  );
}
