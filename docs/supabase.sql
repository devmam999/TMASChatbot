-- Supabase SQL setup for achievements
-- 1) Create user achievements table
create table if not exists public.user_achievements (
  user_id uuid primary key references auth.users(id) on delete cascade,
  quizzes_completed integer not null default 0,
  last_completed_at timestamptz,
  total_correct integer not null default 0,
  total_questions integer not null default 0
);

-- 2) Enable RLS and policies
alter table public.user_achievements enable row level security;

create policy "Users can view own achievements" on public.user_achievements
  for select using (auth.uid() = user_id);

create policy "Users can upsert own achievements" on public.user_achievements
  for insert with check (auth.uid() = user_id);

create policy "Users can update own achievements" on public.user_achievements
  for update using (auth.uid() = user_id);

-- 3) RPC to increment quizzes completed atomically
create or replace function public.increment_quizzes_completed(
  p_user_id uuid,
  p_correct integer default null,
  p_total integer default null,
  p_percentage integer default null
) returns void
language plpgsql
security definer
as $$
begin
  insert into public.user_achievements(user_id, quizzes_completed, last_completed_at, total_correct, total_questions)
  values (p_user_id, 1, now(), coalesce(p_correct,0), coalesce(p_total,0))
  on conflict (user_id)
  do update set quizzes_completed = public.user_achievements.quizzes_completed + 1,
               last_completed_at = now(),
               total_correct = public.user_achievements.total_correct + coalesce(p_correct,0),
               total_questions = public.user_achievements.total_questions + coalesce(p_total,0);
end;
$$;

-- Grant execute to authenticated users (PostgREST)
grant execute on function public.increment_quizzes_completed to authenticated;
