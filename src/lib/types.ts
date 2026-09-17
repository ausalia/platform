export type Org = { id: string; name: string; is_demo: boolean };

export type Plant = {
  id: string;
  org_id: string;
  name: string;
  variety: string | null;
};

export type Reading = {
  id: number;
  plant_id: string;
  ts: string;
  soil_pct: number | null;
  root_temp_c: number | null;
  air_temp_c: number | null;
  humidity_pct: number | null;
  pressure_hpa: number | null;
  weight_g: number | null;
};

export type IrrigationConfig = {
  plant_id: string;
  hour1: number;
  min1: number;
  hour2: number;
  min2: number;
  duration_min: number;
  enabled: boolean;
  updated_at: string;
};
