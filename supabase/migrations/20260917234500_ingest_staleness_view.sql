-- Ground rule 6: a basic "is data still arriving" check on the ingest path.
-- The ESP32 uploads hourly (UPLOAD_MS in firmware/src/main.cpp), so a plant
-- with no reading in the last 90 minutes (1.5x the expected cadence, to
-- absorb a missed/retried upload) is worth flagging. This view is the
-- reusable building block; for now the dashboard reads it to show a
-- last-seen indicator, and it's also queryable directly for a future
-- scheduled alert (pg_cron/email) once that's actually needed.

create view plant_ingest_status
with (security_invoker = true) as
select
  p.id as plant_id,
  p.org_id,
  p.name,
  max(r.ts) as last_reading_at,
  now() - max(r.ts) as since_last_reading,
  (max(r.ts) is null or now() - max(r.ts) > interval '90 minutes') as is_stale
from plants p
left join readings r on r.plant_id = p.id
group by p.id, p.org_id, p.name;
