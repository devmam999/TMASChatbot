/**
 * Chat Input Component
 * Combines text input and file upload for sending messages
 */

import React, { useState, useRef, useEffect } from 'react';
import type { FileUploadState } from '../types';
import FileUpload from './FileUpload';

interface ChatInputProps {
  onSendMessage: (text: string, file?: File) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading = false,
  disabled = false,
}) => {
  const [text, setText] = useState('');
  const [uploadState, setUploadState] = useState<FileUploadState>({
    file: null,
    preview: null,
    uploading: false,
    error: null,
  });
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [text]);

  const handleFileSelect = (file: File) => {
    // Create preview URL
    const preview = URL.createObjectURL(file);
    setUploadState({
      file,
      preview,
      uploading: false,
      error: null,
    });
  };

  const handleFileRemove = () => {
    // Clean up preview URL
    if (uploadState.preview) {
      URL.revokeObjectURL(uploadState.preview);
    }
    setUploadState({
      file: null,
      preview: null,
      uploading: false,
      error: null,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (disabled || isLoading) return;
    
    const trimmedText = text.trim();
    if (!trimmedText && !uploadState.file) return;

    // Send message
    onSendMessage(trimmedText, uploadState.file || undefined);
    
    // Reset form
    setText('');
    handleFileRemove();
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 bg-white p-4">
      {/* File Upload */}
      {uploadState.file && (
        <div className="mb-3">
          <FileUpload
            onFileSelect={handleFileSelect}
            onFileRemove={handleFileRemove}
            uploadState={uploadState}
            maxSize={10}
          />
        </div>
      )}

      {/* Input Area */}
      <div className="flex items-end space-x-3">
        {/* Text Input */}
        <div className="flex-1">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here... (Shift+Enter for new line)"
            className="w-full resize-none border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={1}
            maxLength={1000}
            disabled={disabled || isLoading}
          />
        </div>

        {/* File Upload Button */}
        <button
          type="button"
          onClick={() => {
            if (!uploadState.file) {
              // Trigger file upload
              const input = document.createElement('input');
              input.type = 'file';
              input.accept = 'image/*';
              input.onchange = (e) => {
                const file = (e.target as HTMLInputElement).files?.[0];
                if (file) handleFileSelect(file);
              };
              input.click();
            }
          }}
          disabled={disabled || isLoading}
          className={`p-2 rounded-lg ${
            uploadState.file
              ? 'bg-red-100 text-red-600 hover:bg-red-200'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          title={uploadState.file ? 'Remove image' : 'Add image'}
        >
          {uploadState.file ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          )}
        </button>

        {/* Send Button */}
        <button
          type="submit"
          disabled={disabled || isLoading || (!text.trim() && !uploadState.file)}
          className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Processing...</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              <span>Send</span>
            </>
          )}
        </button>
      </div>

      {/* Character count */}
      <div className="text-xs text-gray-500 mt-1 text-right">
        {text.length}/1000
      </div>
    </form>
  );
};

export default ChatInput; 