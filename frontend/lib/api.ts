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


// --- Admin API Functions ---

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_verified: boolean;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
}

export interface AdminUserListResponse {
  users: AdminUser[];
}

export interface AdminMessageResponse {
  message: string;
}

export async function fetchAllUsers(): Promise<AdminUser[]> {
  const data = await apiRequest<AdminUserListResponse>('/api/admin/users');
  return data.users;
}

export async function fetchPendingUsers(): Promise<AdminUser[]> {
  const data = await apiRequest<AdminUserListResponse>('/api/admin/users/pending');
  return data.users;
}

export async function verifyUser(userId: number): Promise<AdminMessageResponse> {
  return apiRequest<AdminMessageResponse>(`/api/admin/users/${userId}/verify`, {
    method: 'POST',
  });
}

export async function revokeUser(userId: number): Promise<AdminMessageResponse> {
  return apiRequest<AdminMessageResponse>(`/api/admin/users/${userId}/revoke`, {
    method: 'POST',
  });
}

export async function reactivateUser(userId: number): Promise<AdminMessageResponse> {
  return apiRequest<AdminMessageResponse>(`/api/admin/users/${userId}/reactivate`, {
    method: 'POST',
  });
}

export async function deleteUser(userId: number): Promise<AdminMessageResponse> {
  return apiRequest<AdminMessageResponse>(`/api/admin/users/${userId}`, {
    method: 'DELETE',
  });
}
