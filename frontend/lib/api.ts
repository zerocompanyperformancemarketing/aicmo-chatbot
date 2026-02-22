import { getToken } from './auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

export interface ConversationSummary {
  id: string;
  preview: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  sources?: Record<string, unknown>[];
  created_at: string;
}

export interface ConversationDetail {
  id: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface ConversationListResponse {
  conversations: ConversationSummary[];
}

async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getToken();
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function fetchConversations(): Promise<ConversationSummary[]> {
  const data = await apiRequest<ConversationListResponse>('/conversations');
  return data.conversations;
}

export async function fetchConversation(id: string): Promise<ConversationDetail> {
  return apiRequest<ConversationDetail>(`/conversations/${id}`);
}

export async function deleteConversation(id: string): Promise<void> {
  await apiRequest(`/conversations/${id}`, { method: 'DELETE' });
}
