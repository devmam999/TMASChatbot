/**
 * Message Bubble Component
 * Displays user and AI messages with different styling
 */

import React from 'react';
import type { ChatMessage } from '../types';
import VideoPlayer from './VideoPlayer';
import { awardBadge } from '../services/achievements';
import { saveMessage } from '../services/history';
import type { QuizQuestion } from './InteractiveQuiz';

interface MessageBubbleProps {
  message: ChatMessage;
  setQuizData: React.Dispatch<React.SetStateAction<{ questions: QuizQuestion[] } | null>>;
  setIsQuizLoading: React.Dispatch<React.SetStateAction<{ [id: string]: boolean }>>;
  isQuizLoading: boolean;
  sessionId?: string | null;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, setQuizData, setIsQuizLoading, isQuizLoading, sessionId }) => {
  const isUser = message.type === 'user';
  const isAI = message.type === 'ai';

  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  const handleGenerateQuizClick = async () => {
    try {
  setIsQuizLoading((prev) => ({ ...prev, [message.id]: true }));
      const response = await fetch(`${backendUrl}/generate-quiz`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ explanation: message.content })
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
  const quiz = await response.json();
      console.log('Quiz response from backend:', quiz);

  // Normalize quiz data for InteractiveQuiz
      const normalizedQuiz = {
        ...quiz,
        questions: Array.isArray(quiz.questions)
          ? quiz.questions.map((q: { options: Record<string, string> | string[]; correctAnswer: string; explanation?: string; hint?: string; question?: string }) => {
              // Convert options to a consistent map
              const optionsMap: Record<string, string> = Array.isArray(q.options)
                ? q.options.reduce((acc: Record<string, string>, opt: string, idx: number) => {
                    acc[String.fromCharCode(65 + idx)] = opt;
                    return acc;
                  }, {})
                : q.options;

              // Determine correct key
              let correctKey = q.correctAnswer;
              if (!(correctKey in optionsMap)) {
                const found = Object.entries(optionsMap).find(([, v]) => v === q.correctAnswer);
                if (found) correctKey = found[0];
              }

              return {
                question: q.question ?? '',
                options: optionsMap,
                correctAnswer: correctKey,
                explanation: q.explanation ?? '',
                hint: q.hint ?? '',
              };
            })
          : [],
      };
  setQuizData(normalizedQuiz);
  // Award first quiz created badge (idempotent on server)
  try { await awardBadge('first_quiz_created'); } catch (e) { console.debug('awardBadge failed', e); }
  // Persist an info message so history shows the quiz event
  if (sessionId) {
    try { await saveMessage(sessionId, 'ai', `Generated a quiz with ${normalizedQuiz.questions.length} questions.`); } catch (e) { console.debug('save quiz-generated msg failed', e); }
  }
    } catch (error) {
      console.error('Failed to generate quiz:', error);
    } finally {
  setIsQuizLoading((prev) => ({ ...prev, [message.id]: false }));
    }
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Avatar */}
        <div className={`flex items-center mb-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${isUser ? 'bg-blue-500' : 'bg-green-500'
            }`}>
            {isUser ? 'U' : 'AI'}
          </div>
          <span className={`text-xs text-gray-500 ml-2 ${isUser ? 'mr-2' : 'ml-2'}`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        {/* Message Content */}
        <div className={`rounded-lg p-3 ${isUser
          ? 'bg-blue-500 text-white'
          : 'bg-white border border-gray-200 text-gray-800'
          }`}>
          {/* Text Content */}
          <div className={`whitespace-pre-wrap ${isUser ? 'text-white' : 'text-gray-800'}`}>
            {message.content}
          </div>

          {/* Animation Video */}
          {message.animation_url && !isUser && (
            <div className="mt-3">
              <VideoPlayer
                src={message.animation_url}
                className="w-full"
                autoplay={true}
                muted={true}
                loop={true}
                controls={false}
                onError={(error) => {
                  console.error('Animation error:', error);
                }}
                onLoad={() => {
                  console.log('Animation loaded successfully');
                }}
              />
            </div>
          )}

          {/* Animation Base64 Video */}
          {message.animation_base64 && !isUser && (
            <div className="mt-3">
              <video
                controls
                autoPlay
                muted
                loop
                style={{ maxWidth: '100%', borderRadius: '8px' }}
                className="w-full"
              >
                <source src={`data:video/mp4;base64,${message.animation_base64}`} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          )}

          {/* Input Type Badge */}
          {message.input_type && !isUser && (
            <div className="mt-2">
              <span className="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
                {message.input_type.replace('_', ' ')}
              </span>
            </div>
          )}

          {/* Generate Quiz Button for AI Messages (but NOT for the welcome message) */}
          {isAI && message.id !== 'welcome' && message.content && message.content.trim().length > 10 && (
            <div className="mt-2">
              {isQuizLoading ? (
                <div className="flex items-center space-x-2 bg-blue-100 text-blue-700 text-xs px-3 py-1 rounded">
                  <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600"></div>
                  <span>Generating Quiz...</span>
                </div>
              ) : (
                <button
                  onClick={handleGenerateQuizClick}
                  className="bg-green-500 text-white text-xs px-3 py-1 rounded hover:bg-green-600 transition cursor-pointer"
                  disabled={isQuizLoading}
                >
                  Generate Quiz
                </button>
              )}
            </div>
          )}
        </div>
      </div>

    </div>
  );
};

export default MessageBubble;