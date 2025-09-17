import { supabase } from './supabaseClient';

export interface ChatSession {
  id: string;
  title: string | null;
  created_at: string;
}

export interface ChatMessageRow {
  id: string;
  session_id: string;
  role: 'user' | 'ai';
  content: string;
  created_at: string;
}

export async function createSession(title?: string) {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) throw new Error('Not authenticated');
  const { data, error } = await supabase
    .from('chat_sessions')
    .insert({ user_id: user.id, title: title ?? null })
    .select('id')
    .single();
  if (error) throw error;
  return data.id as string;
}

export async function listSessions(): Promise<ChatSession[]> {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return [];
  const { data, error } = await supabase
    .from('chat_sessions')
    .select('id, title, created_at')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false });
  if (error) throw error;
  return (data || []) as ChatSession[];
}

export async function saveMessage(sessionId: string, role: 'user'|'ai', content: string) {
  const { error } = await supabase
    .from('chat_messages')
    .insert({ session_id: sessionId, role, content });
  if (error) throw error;
}

export async function loadMessages(sessionId: string): Promise<ChatMessageRow[]> {
  const { data, error } = await supabase
    .from('chat_messages')
    .select('*')
    .eq('session_id', sessionId)
    .order('created_at', { ascending: true });
  if (error) throw error;
  return (data || []) as ChatMessageRow[];
}
