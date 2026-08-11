-- Run ALL of this in Supabase -> SQL Editor -> New query -> Run
-- Fixes: "Could not find the 'lead_source' column of 'leads' in the schema cache"

alter table public.leads
  add column if not exists lead_source text;

alter table public.leads
  add column if not exists lead_source_detail text;

alter table public.leads
  drop constraint if exists leads_lead_source_check;

alter table public.leads
  add constraint leads_lead_source_check
  check (
    lead_source is null
    or lead_source in ('social_media', 'third_party', 'channel_partner')
  );

alter table public.leads
  drop constraint if exists leads_lead_source_detail_check;

alter table public.leads
  add constraint leads_lead_source_detail_check
  check (
    lead_source_detail is null
    or lead_source_detail in ('website', 'social_media', 'reference', 'consultant')
  );

-- Refresh PostgREST schema cache
notify pgrst, 'reload schema';
