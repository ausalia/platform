-- Ausalia platform - initial schema
-- org -> plants -> readings / irrigation_config, RLS-scoped by membership.
-- One exception: any authenticated user can read the seeded demo org's data,
-- so it works as an always-visible sales demo without needing an invite.

create extension if not exists pgcrypto;

create table organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  is_demo boolean not null default false,
  created_at timestamptz not null default now()
);

create table memberships (
  user_id uuid references auth.users(id) not null,
  org_id uuid references organizations(id) not null,
  role text not null default 'member',
  created_at timestamptz not null default now(),
  primary key (user_id, org_id)
);

create table plants (
  id uuid primary key default gen_random_uuid(),
  org_id uuid references organizations(id) not null,
  name text not null,
  variety text,
  api_key_hash text not null,
  created_at timestamptz not null default now()
);
create unique index idx_plants_api_key_hash on plants(api_key_hash);

create table readings (
  id bigint generated always as identity primary key,
  plant_id uuid references plants(id) not null,
  ts timestamptz not null default now(),
  soil_pct real,
  root_temp_c real,
  air_temp_c real,
  humidity_pct real,
  pressure_hpa real,
  weight_g real
);
create index idx_readings_plant_ts on readings(plant_id, ts);

create table irrigation_config (
  plant_id uuid primary key references plants(id),
  hour1 int not null default 8,
  min1 int not null default 0,
  hour2 int not null default 18,
  min2 int not null default 0,
  duration_min int not null default 5 check (duration_min between 0 and 60),
  enabled boolean not null default true,
  updated_at timestamptz not null default now()
);

-- ============ helper: is the current user a member of this org? ============
create or replace function is_org_member(check_org_id uuid)
returns boolean
language sql
security definer
set search_path = public
stable
as $$
  select exists (
    select 1 from memberships
    where org_id = check_org_id and user_id = auth.uid()
  );
$$;

create or replace function is_demo_org(check_org_id uuid)
returns boolean
language sql
security definer
set search_path = public
stable
as $$
  select exists (
    select 1 from organizations
    where id = check_org_id and is_demo = true
  );
$$;

-- ============ organizations ============
alter table organizations enable row level security;

create policy select_own_or_demo_orgs on organizations for select
  using (is_demo = true or is_org_member(id));

create policy insert_own_org on organizations for insert
  with check (auth.uid() is not null);

-- ============ memberships ============
alter table memberships enable row level security;

create policy select_own_memberships on memberships for select
  using (user_id = auth.uid());

create policy insert_own_membership on memberships for insert
  with check (user_id = auth.uid());

-- ============ plants ============
alter table plants enable row level security;

create policy select_plants_in_scope on plants for select
  using (is_demo_org(org_id) or is_org_member(org_id));

create policy write_plants_as_member on plants for insert
  with check (is_org_member(org_id));

create policy update_plants_as_member on plants for update
  using (is_org_member(org_id));

-- ============ readings ============
alter table readings enable row level security;

create policy select_readings_in_scope on readings for select
  using (
    plant_id in (
      select id from plants
      where is_demo_org(org_id) or is_org_member(org_id)
    )
  );
-- No insert/update/delete policy for readings from the client on purpose -
-- rows only ever arrive via the ingest Edge Function, using the service-role
-- key server-side, which bypasses RLS entirely.

-- ============ irrigation_config ============
alter table irrigation_config enable row level security;

create policy select_irrigation_config_in_scope on irrigation_config for select
  using (
    plant_id in (
      select id from plants
      where is_demo_org(org_id) or is_org_member(org_id)
    )
  );

create policy write_irrigation_config_as_member on irrigation_config for insert
  with check (plant_id in (select id from plants where is_org_member(org_id)));

create policy update_irrigation_config_as_member on irrigation_config for update
  using (plant_id in (select id from plants where is_org_member(org_id)));
