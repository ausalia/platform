-- Found by scripts/db-tests.mjs: insert_own_membership only checked
-- user_id = auth.uid(), so any signed-in user could add themselves to ANY org
-- (including another tenant's, or the demo org) and read its data.
--
-- Self-insert is only needed during onboarding, when a brand-new org has no
-- members yet. Restrict it to exactly that, and never allow joining the demo
-- org. The helper is security definer so it can see all memberships, not just
-- the caller's own (which is all RLS would let a plain subquery see).

create or replace function org_has_members(check_org_id uuid)
returns boolean
language sql
security definer
set search_path = public
stable
as $$
  select exists (select 1 from memberships where org_id = check_org_id);
$$;

drop policy insert_own_membership on memberships;

create policy insert_first_membership on memberships for insert
  with check (
    user_id = auth.uid()
    and not is_demo_org(org_id)
    and not org_has_members(org_id)
  );
