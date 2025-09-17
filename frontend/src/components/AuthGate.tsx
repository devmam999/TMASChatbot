import React, { useEffect, useState } from 'react';
import { supabase } from '../services/supabaseClient';

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState<Awaited<ReturnType<typeof supabase.auth.getSession>>['data']['session'] | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }: { data: { session: typeof session } }) => {
      setSession(data.session);
      setLoading(false);
    });
  const { data: listener } = supabase.auth.onAuthStateChange((_event: unknown, s: typeof session) => {
      setSession(s);
    });
    return () => listener.subscription.unsubscribe();
  }, []);

  if (loading) return <div className="p-6">Loading...</div>;
  if (!session) return <AuthForm />;

  return <>{children}</>;
}

function AuthForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<'login' | 'signup'>('login');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      if (mode === 'signup') {
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        alert('Check your email to confirm your account');
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Auth failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-6 rounded-lg shadow w-full max-w-sm">
        <h2 className="text-xl font-semibold mb-4">{mode === 'login' ? 'Login' : 'Sign up'}</h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input className="w-full border p-2 rounded" type="email" placeholder="Email" value={email} onChange={(e)=>setEmail(e.target.value)} />
          <input className="w-full border p-2 rounded" type="password" placeholder="Password" value={password} onChange={(e)=>setPassword(e.target.value)} />
          {error && <div className="text-red-600 text-sm">{error}</div>}
          <button className="w-full bg-blue-600 text-white py-2 rounded">{mode === 'login' ? 'Login' : 'Create account'}</button>
        </form>
        <button className="text-sm text-blue-600 mt-3" onClick={()=>setMode(mode==='login'?'signup':'login')}>
          {mode==='login' ? "Don't have an account? Sign up" : 'Have an account? Login'}
        </button>
      </div>
    </div>
  );
}
