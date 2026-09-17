-- Extends plant_ingest_status with the latest soil_pct reading, so the
-- farm map can color each plot by status without each client fetching full
-- reading history for every plant just to know its current state.
create or replace view plant_ingest_status
with (security_invoker = true) as
select
  p.id as plant_id,
  p.org_id,
  p.name,
  latest.ts as last_reading_at,
  now() - latest.ts as since_last_reading,
  (latest.ts is null or now() - latest.ts > interval '90 minutes') as is_stale,
  latest.soil_pct as latest_soil_pct
from plants p
left join lateral (
  select ts, soil_pct
  from readings r
  where r.plant_id = p.id
  order by r.ts desc
  limit 1
) latest on true;
