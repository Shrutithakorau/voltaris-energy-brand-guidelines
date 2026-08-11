-- Voltaris Energy Lead Manager schema for Supabase
-- Run this in: Supabase Dashboard -> SQL Editor -> New query -> Run

create extension if not exists "pgcrypto";

create table if not exists public.leads (
  id text primary key,
  customer_name text not null,
  mobile text not null,
  email text not null,
  address text not null,
  product_type text not null check (product_type in ('solar', 'battery', 'solar-battery')),
  nmi text,
  lead_source text check (lead_source is null or lead_source in ('social_media', 'third_party', 'channel_partner')),
  lead_source_detail text check (lead_source_detail is null or lead_source_detail in ('website', 'social_media', 'reference', 'consultant')),
  phase text not null check (phase in ('single', 'three')),
  status text not null default 'lead' check (
    status in ('lead', 'opportunity', 'quoted', 'closed_won', 'closed_lost', 'installation')
  ),
  created_at timestamptz not null default now(),
  updated_at timestamptz default now()
);

create table if not exists public.notes (
  id text primary key,
  lead_id text not null references public.leads(id) on delete cascade,
  body text not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_leads_created_at on public.leads (created_at desc);
create index if not exists idx_leads_status on public.leads (status);
create index if not exists idx_notes_lead_id on public.notes (lead_id, created_at desc);

alter table public.leads enable row level security;
alter table public.notes enable row level security;

-- MVP: allow anon key access from the static web app.
-- Tighten later with Supabase Auth (recommended before production).
drop policy if exists "anon_leads_all" on public.leads;
create policy "anon_leads_all"
  on public.leads
  for all
  to anon, authenticated
  using (true)
  with check (true);

drop policy if exists "anon_notes_all" on public.notes;
create policy "anon_notes_all"
  on public.notes
  for all
  to anon, authenticated
  using (true)
  with check (true);

