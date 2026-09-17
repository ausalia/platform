-- Seed the demo org "Agrícola Punto Azul" with 14 plants (one per cuartel in
-- the old farm-map demo) and a day of simulated hourly readings each, so the
-- dashboard's demo-org path has real data to render against.

insert into organizations (id, name, is_demo)
values ('00000000-0000-0000-0000-000000000001', 'Agrícola Punto Azul', true)
on conflict (id) do nothing;

insert into plants (id, org_id, name, variety, api_key_hash)
select
  gen_random_uuid(),
  '00000000-0000-0000-0000-000000000001',
  'Cuartel ' || n,
  (array['Kee Crisp', 'Endura', 'Arcadia', 'Emerald'])[((n - 1) % 4) + 1],
  encode(gen_random_bytes(32), 'hex')
from generate_series(1, 14) as n
where not exists (
  select 1 from plants where org_id = '00000000-0000-0000-0000-000000000001'
);

do $$
declare
  demo_org_id uuid := '00000000-0000-0000-0000-000000000001';
  p record;
  status text;
  roll numeric;
  moist_start numeric;
  moist_drop numeric;
  hum_start numeric;
  hum_drop numeric;
  weight_start numeric;
  weight_drop numeric;
  h int;
  frac numeric;
begin
  for p in select id from plants where org_id = demo_org_id loop
    roll := random();
    status := case
      when roll < 0.10 then 'critical'
      when roll < 0.28 then 'warning'
      else 'good'
    end;

    if status = 'critical' then
      moist_start := 52 + random() * 8;
      moist_drop := 30 + random() * 12;
      hum_start := 58 + random() * 6;
      hum_drop := 20 + random() * 8;
      weight_start := 3 + random() * 0.4;
      weight_drop := 0.5 + random() * 0.3;
    elsif status = 'warning' then
      moist_start := 54 + random() * 6;
      moist_drop := 14 + random() * 10;
      hum_start := 58 + random() * 4;
      hum_drop := 8 + random() * 7;
      weight_start := 3 + random() * 0.3;
      weight_drop := 0.2 + random() * 0.15;
    else
      moist_start := 54 + random() * 6;
      moist_drop := 2 + random() * 6;
      hum_start := 58 + random() * 5;
      hum_drop := 1 + random() * 4;
      weight_start := 3 + random() * 0.3;
      weight_drop := random() * 0.1;
    end if;

    for h in 0..23 loop
      frac := h / 23.0;
      insert into readings (plant_id, ts, soil_pct, root_temp_c, air_temp_c, humidity_pct, pressure_hpa, weight_g)
      values (
        p.id,
        now() - ((23 - h) || ' hours')::interval,
        greatest(0, round((moist_start - (frac ^ 1.3) * moist_drop + (random() - 0.5) * 1.4)::numeric, 1)),
        round((15 + moist_start * 0.12 + sin(frac * 4) * 1.5 + (random() - 0.5) * 0.5)::numeric, 1),
        round((23 + frac * 3 + sin(frac * 10) * 0.6 + (random() - 0.5) * 0.5)::numeric, 1),
        greatest(0, round((hum_start - frac * hum_drop + (random() - 0.5) * 2)::numeric, 1)),
        round((1013 + sin(frac * 6) * 4 + (random() - 0.5) * 1.5)::numeric, 1),
        round(((weight_start - frac * weight_drop + (random() - 0.5) * 0.04) * 1000)::numeric, 0)
      );
    end loop;
  end loop;
end $$;
