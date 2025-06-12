import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  response: string;
  sources?: string[];
  status: string;
}

export interface AvatarResponse {
  status: string;
  video_url?: string;
  error?: string;
}

export const chatService = {
  sendMessage: async (message: string): Promise<ChatResponse> => {
    const response = await api.post('/chat', { message });
    return response.data;
  },

  getChatHistory: async (): Promise<{ history: ChatMessage[] }> => {
    const response = await api.get('/chat/history');
    return response.data;
  },

  clearChatHistory: async (): Promise<void> => {
    await api.delete('/chat/history');
  },

  speechToText: async (audioFile: File): Promise<{ transcript: string; status: string }> => {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    
    const response = await api.post('/speech-to-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },  createAvatar: async (text: string): Promise<AvatarResponse> => {
    const response = await api.post('/create-avatar', { text }, {
      timeout: 300000, // 5 minutes timeout (longer than the backend's 4.5-minute processing time)
    });
    return response.data;
  },

  checkHealth: async (): Promise<{ status: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
