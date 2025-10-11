import React, { useState } from 'react';

export default function APIKeyRequest({ children }: { children: React.ReactNode }) {
    const [session] = useState(null);
    
    if (!session) return <APIKeyForm />;
    return <>{children}</>;
}

function APIKeyForm() {

    const [anthAPI, setAnthAPI] = useState('');
    const [gemAPI, setGemAPI] = useState('');
    const [supURL, setSupURL] = useState('');
    const [supAnon, setSupAnon] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
    }


    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="bg-white p-6 rounded-lg shadow w-full max-w-sm">
                <h2 className="text-xl font-semibold mb-4">API Keys</h2>
                <form onSubmit={handleSubmit} className="space-y-3">
                    <input className="w-full border p-2 rounded" type="email" placeholder="Anthropic (Claude) API Key" value={anthAPI} onChange={(e)=>setAnthAPI(e.target.value)} />
                    <input className="w-full border p-2 rounded" type="password" placeholder="Google Gemini API Key" value={gemAPI} onChange={(e)=>setGemAPI(e.target.value)} />
                    <input className="w-full border p-2 rounded" type="email" placeholder="Supabase URL" value={supURL} onChange={(e)=>setSupURL(e.target.value)} />
                    <input className="w-full border p-2 rounded" type="password" placeholder="Supabase Anon Key" value={supAnon} onChange={(e)=>setSupAnon(e.target.value)} />
                    <button className="w-full bg-blue-600 text-white py-2 rounded">Submit</button>
                </form>
            </div>
        </div>
    );
};