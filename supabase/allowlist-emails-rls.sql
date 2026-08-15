-- Restrict leads/notes to allowed Voltaris emails only
-- Paste into Supabase → SQL Editor → Run

create or replace function public.is_allowed_voltaris_user()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select coalesce(
    lower(auth.jwt() ->> 'email') = any (array[
      'rathod.shruti8@gmail.com',
      'jaythakor1985@gmail.com'
    ]::text[])
    or lower(auth.jwt() ->> 'email') like '%@voltarisenergy.com.au',
    false
  );
$$;

revoke all on function public.is_allowed_voltaris_user() from public;
grant execute on function public.is_allowed_voltaris_user() to authenticated, anon;

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

alter table public.leads enable row level security;
alter table public.notes enable row level security;

create policy "allowed_leads_select"
  on public.leads for select to authenticated
  using (public.is_allowed_voltaris_user());

create policy "allowed_leads_insert"
  on public.leads for insert to authenticated
  with check (public.is_allowed_voltaris_user());

create policy "allowed_leads_update"
  on public.leads for update to authenticated
  using (public.is_allowed_voltaris_user())
  with check (public.is_allowed_voltaris_user());

create policy "allowed_leads_delete"
  on public.leads for delete to authenticated
  using (public.is_allowed_voltaris_user());

create policy "allowed_notes_select"
  on public.notes for select to authenticated
  using (public.is_allowed_voltaris_user());

create policy "allowed_notes_insert"
  on public.notes for insert to authenticated
  with check (public.is_allowed_voltaris_user());

create policy "allowed_notes_update"
  on public.notes for update to authenticated
  using (public.is_allowed_voltaris_user())
  with check (public.is_allowed_voltaris_user());

create policy "allowed_notes_delete"
  on public.notes for delete to authenticated
  using (public.is_allowed_voltaris_user());
