// REPLACE with YOUR computer's local IP address.
export const API_BASE_URL = 'http://172.16.234.107:8000';

export const ENDPOINTS = {
  CHAT: `${API_BASE_URL}/chat`,
  TRANSCRIBE: `${API_BASE_URL}/transcribe`,
  SYNTHESIZE: `${API_BASE_URL}/synthesize`,
  HISTORY: `${API_BASE_URL}/history`,
  CONVERSATIONS: `${API_BASE_URL}/conversations`,
  GET_CHAT: `${API_BASE_URL}/chat`,
  USER_LEVEL: `${API_BASE_URL}/user/level`,
  USER_STREAK: `${API_BASE_URL}/user/streak`,
};