/**
 * API Service for communicating with the FastAPI backend
 * Handles chat requests, file uploads, and health checks
 */

import type { ChatRequest, ChatResponse, HealthResponse, ApiConfig, AnimationResponse } from '../types';

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
      // Add text if provided
      if (request.text) {
        formData.append('text', request.text);
      }
      // Add image if provided
      if (request.image_base64) {
        const base64Response = await fetch(request.image_base64);
        const blob = await base64Response.blob();
        formData.append('image', blob, 'image.png');
      }
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

  /**
   * Generate animation from explanation text
   */
  async generateAnimation(explanation: string): Promise<AnimationResponse> {
    try {
      const response = await fetch(`${this.config.baseUrl}/generate-animation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ explanation }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Animation generation failed:', error);
      throw new Error(`Failed to generate animation: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}

export async function streamChatText(
  request: ChatRequest,
  onText: (text: string) => void
) {
  const formData = new FormData();
  if (request.text) formData.append('text', request.text);
  if (request.image_base64) {
    const base64Response = await fetch(request.image_base64);
    const blob = await base64Response.blob();
    formData.append('image', blob, 'image.png');
  }
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
  
  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let result = '';
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value);
    result += chunk;
    onText(result); // Update UI with new text
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
    data: { text?: string; image_base64?: string },
    onChunk: (chunk: string) => void
  ) => {
    const formData = new FormData();
    if (data.text) formData.append('text', data.text);
    if (data.image_base64) formData.append('image', data.image_base64);

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
    while (!done) {
      const { value, done: doneReading } = await reader.read();
      done = doneReading;
      if (value) {
        const chunk = decoder.decode(value);
        text += chunk;
        onChunk(text);
      }
    }
  },
};
export default ApiService; 