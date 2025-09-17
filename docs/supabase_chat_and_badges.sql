-- Chat history tables
create table if not exists public.chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text,
  created_at timestamptz not null default now()
);

create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.chat_sessions(id) on delete cascade,
  role text not null check (role in ('user','ai')),
  content text not null,
  created_at timestamptz not null default now()
);

alter table public.chat_sessions enable row level security;
alter table public.chat_messages enable row level security;

create policy "own sessions" on public.chat_sessions for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "own messages" on public.chat_messages for all
  using (exists(select 1 from public.chat_sessions s where s.id = session_id and s.user_id = auth.uid()))
  with check (exists(select 1 from public.chat_sessions s where s.id = session_id and s.user_id = auth.uid()));

-- Badges/achievements
create table if not exists public.user_badges (
  user_id uuid not null references auth.users(id) on delete cascade,
  badge_key text not null,
  earned_at timestamptz not null default now(),
  primary key (user_id, badge_key)
);

-- A catalog of badges (optional, for metadata)
create table if not exists public.badge_catalog (
  badge_key text primary key,
  title text not null,
  description text not null,
  icon text
);

alter table public.user_badges enable row level security;
create policy "own badges" on public.user_badges for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Helper function to award a badge
create or replace function public.award_badge(p_user_id uuid, p_badge_key text)
returns void language plpgsql security definer as $$
begin
  insert into public.user_badges(user_id, badge_key)
  values (p_user_id, p_badge_key)
  on conflict do nothing;
end;$$;

grant execute on function public.award_badge to authenticated;

-- Seed some badge ideas (feel free to modify in dashboard)
insert into public.badge_catalog (badge_key, title, description, icon) values
  ('first_quiz_created','First Quiz Created','Generated your first quiz','🎯'),
  ('first_quiz_completed','First Quiz Completed','Completed your first quiz','🏁'),
  ('five_quizzes_completed','5 Quizzes Completed','You are on a roll!','🏆'),
  ('ten_quizzes_completed','10 Quizzes Completed','Double digits!','🥇'),
  ('fifty_quizzes_completed','50 Quizzes Completed','Serious grinder!','💪')
  on conflict (badge_key) do nothing;
