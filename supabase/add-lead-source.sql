-- Run this in Supabase SQL Editor (for existing projects)
alter table public.leads
  add column if not exists lead_source text;

alter table public.leads
  drop constraint if exists leads_lead_source_check;

alter table public.leads
  add constraint leads_lead_source_check
  check (
    lead_source is null
    or lead_source in ('social_media', 'third_party', 'channel_partner')
  );
