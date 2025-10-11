/**
 * Main Chat Interface Component
 * Combines all chat components and handles the chat logic
 */

import React, { useState, useEffect, useRef } from 'react';
import type { ChatMessage } from '../types';
import { apiService } from '../services/api';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import InteractiveQuiz, { type QuizQuestion } from './InteractiveQuiz';
import AchievementsPanel, { AchievementsDialog } from './AchievementsPanel';
import { supabase } from '../services/supabaseClient';
import { incrementQuizzesCompleted, awardBadge, getAchievements } from '../services/achievements';
import { createSession, listSessions, loadMessages, saveMessage, type ChatSession } from '../services/history';

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [quizData, setQuizData] = useState<{ questions: QuizQuestion[] } | null>(null);
  // Track quiz loading state per message ID
  const [isQuizLoading, setIsQuizLoading] = useState<{ [id: string]: boolean }>({});
  // Track animation loading state per message ID
  const [isAnimationLoading, setIsAnimationLoading] = useState<{ [id: string]: boolean }>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [achievementsOpen, setAchievementsOpen] = useState(false);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add welcome message
  useEffect(() => {
  const welcomeMessage: ChatMessage = {
      id: 'welcome',
      type: 'ai',
              content: `👋 Welcome to the TMAS Chatbot!

I can help you understand concepts with text explanations and animated visualizations using Manim.

You can:
• 💬 Ask questions with text
• 📚 Generate practice quizzes to test your understanding

Try asking me something like "Explain how a binary search tree works". Afterward, click "Generate Quiz" to practice with questions!`,
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
    // Load sessions list
    (async () => {
      try { setSessions(await listSessions()); } catch (e) { console.debug('List sessions failed', e); }
    })();
  }, []);

  // Handler for when animation is generated
  const handleAnimationGenerated = (messageId: string, animationBase64: string) => {
    setMessages(prev => prev.map(message => 
      message.id === messageId 
        ? { ...message, animation_base64: animationBase64 }
        : message
    ));
  };
  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;

    // Clear previous quiz when asking new questions
    setQuizData(null);
    setIsQuizLoading({});
    setIsAnimationLoading({});    // Generate a unique ID for this message

    // Generate a unique ID for this message
    const uniqueId = Date.now().toString() + Math.random().toString(36).substr(2, 5);

    // Create user message
    const userMessage: ChatMessage = {
      id: uniqueId + '-user',
      type: 'user',
      content: text,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    // Ensure we have a session
    let sessionId = activeSessionId;
    if (!sessionId) {
      sessionId = await createSession(text.slice(0, 60));
      setActiveSessionId(sessionId);
      try { setSessions(await listSessions()); } catch (e) { console.debug('Refresh sessions failed', e); }
    }
    // Persist user message
    try { await saveMessage(sessionId, 'user', userMessage.content); } catch (e) { console.debug('Save user msg failed', e); }
    setIsLoading(true);
    setError(null);

  // Will hold the latest streamed text
  let streamedText = '';
  try {
      const request: { text: string } = { text: text.trim() };

      // Create a single AI message that will be updated
      const aiMessageId = uniqueId + '-ai';
  setMessages(prev => [
        ...prev,
        {
          id: aiMessageId,
          type: 'ai',
          content: '',
          timestamp: new Date(),
        }
      ]);

      // Stream the explanation text
  await apiService.streamChatText(request, (chunk) => {
  streamedText = chunk;
        
        // Update the AI message with the current text
  setMessages(prev => prev.map(m => 
          m.id === aiMessageId 
            ? { ...m, content: chunk.trim() }
            : m
  ));
      });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      // Update the existing AI message with the error
      setMessages(prev => prev.map(m => 
        m.type === 'ai' && m.content === ''
          ? { ...m, content: `Sorry, I encountered an error: ${err instanceof Error ? err.message : 'Unknown error'}. Please try again.` }
          : m
      ));
    } finally {
      setIsLoading(false);
      // Persist latest AI message using the aiMessageId we created
      const finalContent = streamedText.trim();
      if (sessionId) {
        try { await saveMessage(sessionId, 'ai', finalContent); } catch (e) { console.debug('Save ai msg failed', e); }
      }
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar: sessions */}
      <div className="w-64 border-r border-gray-200 bg-white hidden md:flex md:flex-col">
        <div className="p-4 border-b">
          <div className="text-sm font-semibold">Chats</div>
          <button
            className="mt-2 text-xs bg-blue-600 text-white px-3 py-1 rounded"
            onClick={async ()=>{
              const id = await createSession('New chat');
              setActiveSessionId(id);
              setMessages([]);
              try { setSessions(await listSessions()); } catch (e) { console.debug('Refresh sessions failed', e); }
            }}
          >New Chat</button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {sessions.map(s => (
            <button key={s.id} className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-50 ${activeSessionId===s.id?'bg-gray-100':''}`}
              onClick={async ()=>{
                setActiveSessionId(s.id);
                const rows = await loadMessages(s.id);
                setMessages(rows.map(r=>({ id: r.id, type: r.role, content: r.content, timestamp: new Date(r.created_at) })));
              }}
            >{s.title ?? 'Untitled'}
              <div className="text-[10px] text-gray-500">{new Date(s.created_at).toLocaleString()}</div>
            </button>
          ))}
        </div>
      </div>
      {/* Main column */}
      <div className="flex-1 flex flex-col">
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">
              TMAS Chatbot
            </h1>
            <p className="text-sm text-gray-500">
              AI-powered explanations with Manim animations
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <AchievementsPanel />
            <button onClick={()=>setAchievementsOpen(true)} className="text-xs bg-purple-600 text-white px-3 py-1 rounded">Achievements</button>
            <button onClick={()=>supabase.auth.signOut()} className="text-xs text-gray-600 hover:text-gray-900">Sign out</button>
            <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`}></div>
            <span className="text-xs text-gray-500">
              {isLoading ? 'Processing...' : 'Ready'}
            </span>
          </div>
        </div>
      </div>

  {/* Messages Area */}
  <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <MessageBubble 
            key={message.id} 
            message={message} 
            setQuizData={setQuizData}
            setIsQuizLoading={setIsQuizLoading}
            isQuizLoading={!!isQuizLoading[message.id]}
            setIsAnimationLoading={setIsAnimationLoading}
            isAnimationLoading={!!isAnimationLoading[message.id]}
            onAnimationGenerated={handleAnimationGenerated}
            sessionId={activeSessionId}
          />
        ))}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="max-w-xs lg:max-w-md xl:max-w-lg">
              <div className="flex items-center mb-2">
                <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white text-sm font-medium">
                  AI
                </div>
                <span className="text-xs text-gray-500 ml-2">
                  {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              <div className="bg-white border border-gray-200 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                  <span className="text-sm text-gray-600">Generating response...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <span className="text-sm text-red-800">{error}</span>
            </div>
          </div>
        )}

        {/* Interactive Quiz Display */}
        {quizData && (
          <InteractiveQuiz 
            questions={quizData.questions} 
            onClose={() => {
              setQuizData(null);
              setIsQuizLoading({});
            }}
            onComplete={async (summary) => {
              try {
                await incrementQuizzesCompleted(summary);
                // Re-fetch to get new count, then award badges
                const ach = await getAchievements();
                const count = ach?.quizzes_completed ?? 0;
                if (count === 1) {
                  try { await awardBadge('first_quiz_completed'); } catch (e) { console.debug('award first completed failed', e); }
                }
                if (count >= 5) { try { await awardBadge('five_quizzes_completed'); } catch (e) { console.debug('award 5 failed', e); } }
                if (count >= 10) { try { await awardBadge('ten_quizzes_completed'); } catch (e) { console.debug('award 10 failed', e); } }
                if (count >= 50) { try { await awardBadge('fifty_quizzes_completed'); } catch (e) { console.debug('award 50 failed', e); } }
              } catch (e) {
                console.error('Failed to record achievement', e);
              }
            }}
          />
        )}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        disabled={isLoading}
      />
  <AchievementsDialog open={achievementsOpen} onClose={()=>setAchievementsOpen(false)} />
  </div>
    </div>
  );
};

export default ChatInterface; 