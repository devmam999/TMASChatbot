/**
 * Message Bubble Component
 * Displays user and AI messages with different styling
 */

import React from 'react';
import type { ChatMessage } from '../types';
import VideoPlayer from './VideoPlayer';

interface MessageBubbleProps {
  message: ChatMessage;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.type === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Avatar */}
        <div className={`flex items-center mb-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${
            isUser ? 'bg-blue-500' : 'bg-green-500'
          }`}>
            {isUser ? 'U' : 'AI'}
          </div>
          <span className={`text-xs text-gray-500 ml-2 ${isUser ? 'mr-2' : 'ml-2'}`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        {/* Message Content */}
        <div className={`rounded-lg p-3 ${
          isUser 
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
        </div>
      </div>
    </div>
  );
};

export default MessageBubble; 