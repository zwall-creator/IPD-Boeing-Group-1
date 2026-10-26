-- Persistent scenario history for the simulation workspace.
-- This file is mounted by docker-compose and runs after 01-hello.sql.

create table if not exists public.scenarios (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  topology jsonb not null default '{"nodes": [], "edges": []}'::jsonb,
  created_by uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.simulation_runs (
  id uuid primary key default gen_random_uuid(),
  scenario_id uuid not null references public.scenarios(id) on delete cascade,
  solver text not null check (solver in ('classical', 'quantum')),
  status text not null default 'queued'
    check (status in ('queued', 'running', 'completed', 'failed')),
  started_at timestamptz,
  completed_at timestamptz,
  result jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.logs (
  id bigserial primary key,
  simulation_run_id uuid not null references public.simulation_runs(id) on delete cascade,
  level text not null default 'info'
    check (level in ('debug', 'info', 'warn', 'error')),
  event_type text not null,
  message text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.reports (
  id uuid primary key default gen_random_uuid(),
  simulation_run_id uuid not null unique references public.simulation_runs(id) on delete cascade,
  title text not null,
  summary text,
  metrics jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.solutions (
  id uuid primary key default gen_random_uuid(),
  report_id uuid not null references public.reports(id) on delete cascade,
  name text not null,
  description text,
  payload jsonb not null default '{}'::jsonb,
  selected boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists simulation_runs_scenario_id_idx on public.simulation_runs (scenario_id);
create index if not exists logs_simulation_run_id_idx on public.logs (simulation_run_id, created_at);
create index if not exists solutions_report_id_idx on public.solutions (report_id);
