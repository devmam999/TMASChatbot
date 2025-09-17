import { supabase } from './supabaseClient';

export async function incrementQuizzesCompleted(summary?: { correct: number; total: number; percentage: number }) {
  const { data: { user }, error: userErr } = await supabase.auth.getUser();
  if (userErr || !user) throw new Error(userErr?.message || 'No user');

  // Ensure a row exists; then increment
  const { error: upsertErr } = await supabase
    .from('user_achievements')
    .upsert({ user_id: user.id }, { onConflict: 'user_id', ignoreDuplicates: false });
  if (upsertErr) throw upsertErr;

  const { error } = await supabase.rpc('increment_quizzes_completed', {
    p_user_id: user.id,
    p_correct: summary?.correct ?? null,
    p_total: summary?.total ?? null,
    p_percentage: summary?.percentage ?? null,
  });
  if (error) throw error;
}

export async function getAchievements() {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return null;
  const { data } = await supabase
    .from('user_achievements')
    .select('*')
    .eq('user_id', user.id)
    .single();
  return data;
}

export async function awardBadge(badgeKey: string) {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) throw new Error('Not authenticated');
  const { error } = await supabase.rpc('award_badge', {
    p_user_id: user.id,
    p_badge_key: badgeKey,
  });
  if (error) throw error;
}

export async function listBadges(): Promise<{ badge_key: string; earned_at: string }[]> {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return [];
  const { data, error } = await supabase
    .from('user_badges')
    .select('badge_key, earned_at')
    .eq('user_id', user.id)
    .order('earned_at', { ascending: false });
  if (error) throw error;
  return (data || []) as { badge_key: string; earned_at: string }[];
}

type BadgeCatalogRow = { badge_key: string; title: string; description: string; icon: string | null };
export async function getBadgeCatalog(): Promise<Record<string, { title: string; description: string; icon: string | null }>> {
  const { data, error } = await supabase
    .from('badge_catalog')
    .select('badge_key, title, description, icon');
  if (error) throw error;
  const map: Record<string, { title: string; description: string; icon: string | null }> = {};
  (data as BadgeCatalogRow[] | null || []).forEach((row) => {
    map[row.badge_key] = { title: row.title, description: row.description, icon: row.icon ?? null };
  });
  return map;
}
