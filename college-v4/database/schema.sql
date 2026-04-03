-- ============================================================
-- College Asset Management — Supabase Schema
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- ============================================================

-- 1. USERS (stored in session; optional table for audit logs)
create table if not exists public.users (
  id          bigint primary key generated always as identity,
  username    text not null unique,
  role        text not null check (role in ('Admin','User')),
  department  text,
  created_at  timestamptz default now()
);

-- 2. ASSETS (stationary stock per department)
create table if not exists public.assets (
  id          bigint primary key generated always as identity,
  department  text not null,
  item_name   text not null,
  quantity    int  not null default 0 check (quantity >= 0),
  updated_at  timestamptz default now(),
  unique (department, item_name)
);

-- 3. INDENT REQUESTS
create table if not exists public.indent_requests (
  id          bigint primary key generated always as identity,
  indent_no   text not null unique,
  department  text not null,
  ordered_by  text,
  items       jsonb not null default '[]',
  status      text not null default 'Pending'
                check (status in ('Pending','In Progress','Solved','Rejected')),
  created_at  timestamptz default now()
);

-- 4. ITEM REQUESTS (assign/request single items)
create table if not exists public.item_requests (
  id          bigint primary key generated always as identity,
  department  text not null,
  item        text not null,
  quantity    int  not null default 1,
  status      text not null default 'Pending'
                check (status in ('Pending','Approved','Rejected')),
  created_at  timestamptz default now()
);

-- 5. STATIONARY REQUESTS (user requests new stationary types)
create table if not exists public.stationary_requests (
  id          bigint primary key generated always as identity,
  department  text not null,
  name        text not null,
  description text default '',
  quantity    int  not null default 1,
  status      text not null default 'Pending'
                check (status in ('Pending','Approved','Rejected')),
  created_at  timestamptz default now()
);

-- ============================================================
-- Row Level Security (RLS) — disable for service_role key
-- Enable only if you use anon key in production
-- ============================================================
-- alter table public.assets enable row level security;
-- alter table public.indent_requests enable row level security;
-- alter table public.item_requests enable row level security;
-- alter table public.stationary_requests enable row level security;
