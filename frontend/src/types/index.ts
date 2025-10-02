/**
 * TypeScript types for the TMAS Chatbot
 * These match the backend models for type safety
 */

// Input types that match backend enum
export type InputType = 'text_only';

// Chat request - what we send to the backend
export interface ChatRequest {
  text: string;
}

// Chat response - what we receive from the backend
export interface ChatResponse {
  success: boolean;
  explanation: string;
  animation_url?: string;
  error_message?: string;
  input_type: InputType;
}

// Health check response
export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
}

// Message types for the chat interface
export interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  animation_url?: string;
  input_type?: InputType;
  animation_base64?: string;
}


// API service configuration
export interface ApiConfig {
  baseUrl: string;
  timeout: number;
} 