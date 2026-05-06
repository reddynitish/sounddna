-- SoundDNA Database Schema
-- Run this in your Supabase SQL editor

create table if not exists song_fingerprints (
  id uuid default gen_random_uuid() primary key,
  spotify_id text unique not null,
  title text,
  artist text,
  year text,
  image_url text,
  external_url text,
  fingerprint_hash text,
  key text,
  tempo numeric,
  era text,
  mode text,
  genres text[] default '{}',
  instruments text[] default '{}',
  vocal_style text,
  audio_features jsonb default '{}',
  analyzed_count integer default 1,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Index for fast similarity lookups by audio features
create index if not exists idx_fingerprints_era on song_fingerprints(era);
create index if not exists idx_fingerprints_key on song_fingerprints(key);
create index if not exists idx_fingerprints_spotify_id on song_fingerprints(spotify_id);

-- Auto-update updated_at
create or replace function update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger song_fingerprints_updated_at
  before update on song_fingerprints
  for each row execute function update_updated_at();

-- Increment analyzed_count on conflict (tracks usage)
-- The upsert in code handles on_conflict="spotify_id"
