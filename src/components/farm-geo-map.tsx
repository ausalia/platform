"use client";

import type { Plant } from "@/lib/types";
import { STATUS_COLOR, STATUS_LABEL, type Status } from "@/lib/status";
import StatusIcon from "@/components/status-icon";
import { FARM_GEO, pathCentroid } from "@/lib/farm-geo";

const LEGEND_ORDER: Status[] = ["good", "warning", "critical", "idle"];

function cuartelNumber(plantName: string): number | null {
  const m = plantName.match(/(\d+)\s*$/);
  return m ? Number(m[1]) : null;
}

export default function FarmGeoMap({
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
  const plantByCuartel = new Map<number, Plant>();
  for (const p of plants) {
    const n = cuartelNumber(p.name);
    if (n !== null) plantByCuartel.set(n, p);
  }

  return (
    <div>
      <svg viewBox={FARM_GEO.viewBox} className="w-full" style={{ maxHeight: 360 }}>
        <path d={FARM_GEO.farmPath} fill="none" stroke="var(--border)" strokeWidth={3} />
        {FARM_GEO.cuarteles.map((c) => {
          const plant = plantByCuartel.get(c.id);
          if (!plant) return null;
          const status = statusByPlant[plant.id] ?? "idle";
          const selected = plant.id === selectedPlantId;
          const [cx, cy] = pathCentroid(c.path);
          return (
            <g key={c.id} onClick={() => onSelect(plant)} style={{ cursor: "pointer" }}>
              <path
                d={c.path}
                fill={`color-mix(in srgb, ${STATUS_COLOR[status]} 30%, var(--surface))`}
                stroke={selected ? "var(--accent)" : "var(--border)"}
                strokeWidth={selected ? 4 : 1.5}
              />
              <g
                transform={`translate(${cx - 8}, ${cy - 8})`}
                style={{ pointerEvents: "none", color: STATUS_COLOR[status] }}
              >
                <StatusIcon status={status} size={16} />
              </g>
            </g>
          );
        })}
      </svg>
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
