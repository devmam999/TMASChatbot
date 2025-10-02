/**
 * API Service for communicating with the FastAPI backend
 * Handles chat requests, file uploads, and health checks
 */

import type { ChatRequest, ChatResponse, HealthResponse, ApiConfig } from '../types';

// Default API configuration
const defaultConfig: ApiConfig = {
  baseUrl: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
};

export interface VideoChatResponse {
  videoUrl: string;
  explanation?: string;
  input_type?: string;
}

class ApiService {
  private config: ApiConfig;

  constructor(config: Partial<ApiConfig> = {}) {
    this.config = { ...defaultConfig, ...config };
  }

  /**
   * Send a chat request to the backend
   * Supports text-only, image-only, or both
   */
  async sendChatRequest(request: ChatRequest): Promise<ChatResponse | VideoChatResponse> {
    try {
      const formData = new FormData();
      formData.append('text', request.text);
      const response = await fetch(`${this.config.baseUrl}/chat`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const contentType = response.headers.get('Content-Type');
        if (contentType && contentType.includes('text/html')) {
          // Server returned an HTML error page
          const errorText = await response.text();
          throw new Error(`Server error (${response.status}): ${errorText.substring(0, 200)}...`);
        } else {
          // Try to parse as JSON for structured error
          try {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
          } catch {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
        }
      }
      const contentType = response.headers.get('Content-Type');
      if (contentType && contentType.startsWith('video/')) {
        // It's a video stream!
        const videoBlob = await response.blob();
        const videoUrl = URL.createObjectURL(videoBlob);
        // Optionally, you could parse explanation from a custom header if you want
        return { videoUrl };
      } else {
        // It's a JSON response (explanation only or error)
        return await response.json();
      }
    } catch (error) {
      console.error('Chat request failed:', error);
      throw new Error(`Failed to send chat request: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Send a chat request using JSON format (alternative endpoint)
   */
  async sendChatRequestJson(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.config.baseUrl}/chat-json`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Chat request failed:', error);
      throw new Error(`Failed to send chat request: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Check if the backend is healthy
   */
  async healthCheck(): Promise<HealthResponse> {
    try {
      const response = await fetch(`${this.config.baseUrl}/health`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw new Error(`Backend health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Convert a File to base64 string
   * Used for JSON endpoint
   */
  async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        if (typeof reader.result === 'string') {
          resolve(reader.result);
        } else {
          reject(new Error('Failed to convert file to base64'));
        }
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsDataURL(file);
    });
  }

  /**
   * Get the full URL for a media file
   */
  getMediaUrl(filename: string): string {
    return `${this.config.baseUrl}/media/${filename}`;
  }
}

export async function streamChatText(
  request: ChatRequest,
  onText: (text: string) => void
) {
  const formData = new FormData();
  formData.append('text', request.text);
  const response = await fetch(`${defaultConfig.baseUrl}/chat/stream`, {
    method: 'POST',
    body: formData,
  });
  console.log('[streamChatText] response meta status:', response.status, 'ok:', response.ok, 'content-type:', response.headers.get('Content-Type'));
  
  // Check if response is ok
  if (!response.ok) {
    const contentType = response.headers.get('Content-Type');
    if (contentType && contentType.includes('text/html')) {
      // Server returned an HTML error page
      const errorText = await response.text();
      throw new Error(`Server error (${response.status}): ${errorText.substring(0, 200)}...`);
    } else {
      // Try to parse as JSON for structured error
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      } catch {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    }
  }
  
  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let result = '';
  let chunks = 0;
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value);
    result += chunk;
    chunks++;
    onText(result); // Update UI with new text
  }
}

export async function pollForVideo(requestId: string, onVideo: (videoUrl: string) => void) {
  const url = `${defaultConfig.baseUrl}/chat/video/${requestId}`;
  let attempts = 0;
  while (attempts < 60) { // Try for up to 60 seconds
    const response = await fetch(url);
    if (response.status === 200) {
      const videoBlob = await response.blob();
      const videoUrl = URL.createObjectURL(videoBlob);
      onVideo(videoUrl);
      break;
    }
    await new Promise(res => setTimeout(res, 2000)); // Wait 2 seconds
    attempts++;
  }
}

// Export a singleton instance
export const apiService = {
  fileToBase64: (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data URL prefix if you want only base64
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  },

  streamChatText: async (
    data: { text: string },
    onChunk: (chunk: string) => void
  ) => {
    const formData = new FormData();
    formData.append('text', data.text);

    const response = await fetch(`${defaultConfig.baseUrl}/chat/stream`, {
      method: 'POST',
      body: formData,
    });

    // Check if response is ok
    if (!response.ok) {
      const contentType = response.headers.get('Content-Type');
      if (contentType && contentType.includes('text/html')) {
        // Server returned an HTML error page
        const errorText = await response.text();
        throw new Error(`Server error (${response.status}): ${errorText.substring(0, 200)}...`);
      } else {
        // Try to parse as JSON for structured error
        try {
          const errorData = await response.json();
          throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        } catch {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }
    }

    if (!response.body) throw new Error('No response body');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let done = false;
    let text = '';
    let chunks = 0;
    while (!done) {
      const { value, done: doneReading } = await reader.read();
      done = doneReading;
      if (value) {
        const chunk = decoder.decode(value);
        text += chunk;
        chunks++;
        onChunk(text);
      }
    }
  },

  getVideoBase64: async (requestId: string) => {
    // Poll until the video is ready
    for (let i = 0; i < 60; i++) {
      try {
        const res = await fetch(`${defaultConfig.baseUrl}/chat/video_base64/${requestId}`);
        if (res.status === 202) {
          await new Promise(r => setTimeout(r, 2000));
          continue;
        }
        if (res.status === 404) {
          console.log('No video will be created for this request');
          return null;
        }
        if (res.ok) {
          const data = await res.json();
          return data.video_base64;
        }
      } catch (error) {
        console.error(`Error polling for video (attempt ${i + 1}):`, error);
      }
      await new Promise(r => setTimeout(r, 2000));
    }
    return null;
  },

};
export default ApiService; 