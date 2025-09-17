import { useEffect, useState } from 'react';
import { supabase } from '../services/supabaseClient';
import { listBadges } from '../services/achievements';
import type { RealtimePostgresChangesPayload } from '@supabase/supabase-js';

interface AchievementStats {
  quizzes_completed: number;
  last_completed_at: string | null;
}

export default function AchievementsPanel() {
  const [stats, setStats] = useState<AchievementStats>({ quizzes_completed: 0, last_completed_at: null });
  const [loading, setLoading] = useState(true);
  const [badges, setBadges] = useState<{ badge_key: string; earned_at: string }[]>([]);

  useEffect(() => {
    const load = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      const { data, error } = await supabase
        .from('user_achievements')
        .select('quizzes_completed, last_completed_at')
        .eq('user_id', user.id)
        .single();
      if (!error && data) setStats(data as AchievementStats);
      try { setBadges(await listBadges()); } catch (e) { console.debug('listBadges failed', e); }
      setLoading(false);
    };
    load();
    // Realtime subscriptions for live updates
    type UA = { user_id: string; quizzes_completed: number; last_completed_at: string | null };
    type UB = { user_id: string; badge_key: string; earned_at: string };
    const channel = supabase
      .channel('achievements_rt')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'user_achievements' }, async (payload: RealtimePostgresChangesPayload<UA>) => {
        const { data: { user } } = await supabase.auth.getUser();
        // only refresh if row pertains to current user
        // payload.new may be null for deletes
        const row = payload.new as UA | null;
        if (user && row && row.user_id === user.id) {
          setStats({ quizzes_completed: row.quizzes_completed, last_completed_at: row.last_completed_at });
        }
      })
      .on('postgres_changes', { event: '*', schema: 'public', table: 'user_badges' }, async (payload: RealtimePostgresChangesPayload<UB>) => {
        const { data: { user } } = await supabase.auth.getUser();
        const row = payload.new as UB | null;
        if (user && row && row.user_id === user.id) {
          try { setBadges(await listBadges()); } catch (e) { console.debug('refresh badges failed', e); }
        }
      })
      .subscribe();
    return () => { supabase.removeChannel(channel); };
  }, []);

  if (loading) return <div className="text-sm text-gray-500">Loading achievements...</div>;

  return (
    <div className="flex items-center space-x-4">
      <div className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
        🏆 {stats.quizzes_completed}
      </div>
      {stats.last_completed_at && (
        <div className="text-xs text-gray-500">Last: {new Date(stats.last_completed_at).toLocaleString()}</div>
      )}
      {badges.length > 0 && (
        <div className="hidden md:flex items-center space-x-1 text-xs">
          {badges.slice(0, 4).map(b => (
            <span key={b.badge_key} className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full">{b.badge_key.replaceAll('_',' ')}</span>
          ))}
        </div>
      )}
    </div>
  );
}

// Optional full achievements dialog (exported for parent to use if needed)
export function AchievementsDialog({ open, onClose }: { open: boolean; onClose: ()=>void }) {
  const [badges, setBadges] = useState<{ badge_key: string; earned_at: string }[]>([]);
  const [catalog, setCatalog] = useState<Record<string, { title: string; description: string; icon: string | null }>>({});
  useEffect(() => {
    if (!open) return;
    (async ()=>{
      try {
        const { listBadges, getBadgeCatalog } = await import('../services/achievements');
        const [b, c] = await Promise.all([listBadges(), getBadgeCatalog()]);
        setBadges(b); setCatalog(c);
      } catch (e) { console.debug('load achievements dialog failed', e); }
    })();
  }, [open]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-lg shadow-lg w-full max-w-lg p-5" onClick={(e)=>e.stopPropagation()}>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold">Your Achievements</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-800">✕</button>
        </div>
        {badges.length === 0 ? (
          <div className="text-sm text-gray-600">No badges yet. Complete a quiz to earn your first badge!</div>
        ) : (
          <ul className="space-y-2 max-h-80 overflow-y-auto">
            {badges.map(b => {
              const meta = catalog[b.badge_key];
              return (
                <li key={b.badge_key} className="border border-gray-200 rounded p-3 flex items-start gap-3">
                  <div className="text-xl" aria-hidden>{meta?.icon ?? '🏅'}</div>
                  <div className="flex-1">
                    <div className="font-medium">{meta?.title ?? b.badge_key.replaceAll('_',' ')}</div>
                    <div className="text-xs text-gray-600">{meta?.description ?? 'Badge earned'}</div>
                  </div>
                  <div className="text-[10px] text-gray-500">{new Date(b.earned_at).toLocaleString()}</div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
