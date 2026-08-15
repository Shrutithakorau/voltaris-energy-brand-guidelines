# Google SSO setup (Supabase Auth)

The Lead Manager now requires Google sign-in before the dashboard.

## 1. Enable Google provider in Supabase

1. Open https://supabase.com/dashboard/project/avfsnumtwnxeskwgtyxj/auth/providers
2. Enable **Google**
3. Add your Google OAuth **Client ID** and **Client Secret** from Google Cloud Console

### Google Cloud Console

1. https://console.cloud.google.com/apis/credentials
2. Create OAuth client ID → Web application
3. Authorized JavaScript origins:
   - `https://shrutithakorau.github.io`
   - `http://127.0.0.1:8787`
   - `http://localhost:8787`
4. Authorized redirect URIs (important):
   - `https://avfsnumtwnxeskwgtyxj.supabase.co/auth/v1/callback`
5. Copy Client ID + Secret into Supabase Google provider settings → Save

## 2. Add redirect URLs in Supabase Auth

Supabase → **Authentication** → **URL Configuration**:

- Site URL: `https://shrutithakorau.github.io/voltaris-energy-brand-guidelines/leads.html`
- Redirect URLs (add all):
  - `https://shrutithakorau.github.io/voltaris-energy-brand-guidelines/leads.html`
  - `http://127.0.0.1:8787/leads.html`
  - `http://localhost:8787/leads.html`

## 3. Lock data to logged-in users

Do **not** type the filename into SQL Editor. Paste the SQL contents:

1. Open the file `supabase/require-authenticated-rls.sql` on your computer (or copy the block below)
2. Supabase Dashboard → **SQL Editor** → **New query**
3. Paste everything → click **Run**
4. You should see **Success**. If you see an error, copy the red error text and share it

```sql
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

create policy "authenticated_leads_select"
  on public.leads for select to authenticated using (true);
create policy "authenticated_leads_insert"
  on public.leads for insert to authenticated with check (true);
create policy "authenticated_leads_update"
  on public.leads for update to authenticated using (true) with check (true);
create policy "authenticated_leads_delete"
  on public.leads for delete to authenticated using (true);

create policy "authenticated_notes_select"
  on public.notes for select to authenticated using (true);
create policy "authenticated_notes_insert"
  on public.notes for insert to authenticated with check (true);
create policy "authenticated_notes_update"
  on public.notes for update to authenticated using (true) with check (true);
create policy "authenticated_notes_delete"
  on public.notes for delete to authenticated using (true);
```

**Important:** Finish Google Auth (steps 1–2) first. After this SQL, the app only loads leads when you are signed in.

## 4. Test

Open the app → **Continue with Google** → you should land on the dashboard.
