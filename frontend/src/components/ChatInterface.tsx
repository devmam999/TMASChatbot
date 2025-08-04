/**
 * Main Chat Interface Component
 * Combines all chat components and handles the chat logic
 */

import React, { useState, useEffect, useRef } from 'react';
import type { ChatMessage, InputType } from '../types';
import { apiService, streamChatText, pollForVideo } from '../services/api';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

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
• Ask questions with text
• Upload images for analysis
• Combine both text and images

Try asking me something like "Explain how a binary search tree works" or upload an image of a mathematical concept!`,
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  }, []);

  const handleSendMessage = async (text: string, file?: File) => {
    if (!text.trim() && !file) return;

    // Generate a unique ID for this message
    const uniqueId = Date.now().toString() + Math.random().toString(36).substr(2, 5);

    // Create user message
    const userMessage: ChatMessage = {
      id: uniqueId + '-user',
      type: 'user',
      content: text || 'Image uploaded',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      let request: any = {};
      if (text.trim()) request.text = text.trim();
      if (file) {
        const base64 = await apiService.fileToBase64(file);
        request.image_base64 = base64;
      }

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
      let streamedText = '';
      let requestId: string | null = null;
      await apiService.streamChatText(request, (chunk) => {
        streamedText = chunk;
        // Extract request ID if present
        const match = chunk.match(/\[REQUEST_ID:([a-f0-9\-]+)\]/i);
        if (match) requestId = match[1];
        
        // Update the AI message with the current text (without request ID)
        const displayText = chunk.replace(/\[REQUEST_ID:[a-f0-9\-]+\]/i, '').trim();
        setMessages(prev => prev.map(m => 
          m.id === aiMessageId 
            ? { ...m, content: displayText }
            : m
        ));
      });

      // If there is a requestId, update the same message with animation
      if (requestId) {
        // Update the message to show "Generating animation..."
        setMessages(prev => prev.map(m => 
          m.id === aiMessageId 
            ? { ...m, content: streamedText.replace(/\[REQUEST_ID:[a-f0-9\-]+\]/i, '').trim() + '\n\nGenerating animation...' }
            : m
        ));

        try {
          const videoBase64 = await apiService.getVideoBase64(requestId);
          if (videoBase64) {
            // Update the same message with the animation
            setMessages(prev => prev.map(m => 
              m.id === aiMessageId 
                ? { 
                    ...m, 
                    content: streamedText.replace(/\[REQUEST_ID:[a-f0-9\-]+\]/i, '').trim(),
                    animation_base64: videoBase64 
                  }
                : m
            ));
          } else {
            // Remove the "Generating animation..." text if no video
            setMessages(prev => prev.map(m => 
              m.id === aiMessageId 
                ? { ...m, content: streamedText.replace(/\[REQUEST_ID:[a-f0-9\-]+\]/i, '').trim() }
                : m
            ));
          }
        } catch (videoError) {
          console.error('Error fetching video:', videoError);
          // Remove the "Generating animation..." text on error
          setMessages(prev => prev.map(m => 
            m.id === aiMessageId 
              ? { ...m, content: streamedText.replace(/\[REQUEST_ID:[a-f0-9\-]+\]/i, '').trim() }
              : m
          ));
        }
      }
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
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
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
          <div className="flex items-center space-x-2">
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
          <MessageBubble key={message.id} message={message} />
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

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        disabled={isLoading}
      />
    </div>
  );
};

export default ChatInterface; 