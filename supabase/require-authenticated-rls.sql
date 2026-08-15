-- Lock leads/notes to signed-in users only
-- Paste THIS ENTIRE file into Supabase → SQL Editor → Run
-- Do not type the filename as SQL

-- 1) Drop every existing policy on these tables
do $$
declare
  r record;
begin
  for r in (
    select policyname
    from pg_policies
    where schemaname = 'public' and tablename = 'leads'
  ) loop
    execute format('drop policy if exists %I on public.leads', r.policyname);
  end loop;

  for r in (
    select policyname
    from pg_policies
    where schemaname = 'public' and tablename = 'notes'
  ) loop
    execute format('drop policy if exists %I on public.notes', r.policyname);
  end loop;
end $$;

-- 2) Make sure RLS is on
alter table public.leads enable row level security;
alter table public.notes enable row level security;

-- 3) Allow only authenticated (logged-in) users
create policy "authenticated_leads_select"
  on public.leads for select to authenticated
  using (true);

create policy "authenticated_leads_insert"
  on public.leads for insert to authenticated
  with check (true);

create policy "authenticated_leads_update"
  on public.leads for update to authenticated
  using (true)
  with check (true);

create policy "authenticated_leads_delete"
  on public.leads for delete to authenticated
  using (true);

create policy "authenticated_notes_select"
  on public.notes for select to authenticated
  using (true);

create policy "authenticated_notes_insert"
  on public.notes for insert to authenticated
  with check (true);

create policy "authenticated_notes_update"
  on public.notes for update to authenticated
  using (true)
  with check (true);

create policy "authenticated_notes_delete"
  on public.notes for delete to authenticated
  using (true);
