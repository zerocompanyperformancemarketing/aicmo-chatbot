'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import ConversationHistory from '@/components/ConversationHistory';
import { getToken, getFullName, getIsAdmin, isAuthenticated, logout } from '@/lib/auth';
import Link from 'next/link';
import { fetchConversation } from '@/lib/api';

interface Source {
  episode_title: string;
  speaker: string;
  timestamp: string;
  text_snippet: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [displayName, setDisplayName] = useState<string | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auth guard + load conversation ID from sessionStorage on mount
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    setDisplayName(getFullName());
    setIsAdmin(getIsAdmin());
    const savedConversationId = sessionStorage.getItem('conversationId');
    if (savedConversationId) {
      setConversationId(savedConversationId);
    }
  }, [router]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (message: string) => {
    setError(null);
    setIsLoading(true);

    // Add user message immediately
    const userMessage: Message = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? '';
      const token = getToken();
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
        }),
      });

      if (response.status === 401) {
        logout();
        router.push('/login');
        return;
      }

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      // Save conversation ID
      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
        sessionStorage.setItem('conversationId', data.conversation_id);
      }

      // Add assistant message
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        sources: data.sources || [],
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    sessionStorage.removeItem('conversationId');
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const handleSelectConversation = async (selectedConversationId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const conversation = await fetchConversation(selectedConversationId);
      setConversationId(selectedConversationId);
      sessionStorage.setItem('conversationId', selectedConversationId);
      setMessages(
        conversation.messages.map((msg) => ({
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          sources: msg.sources as Source[] | undefined,
        }))
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">AICMO Podcast Chat</h1>
        <div className="flex items-center gap-4">
          {displayName && (
            <span className="text-sm text-gray-600">{displayName}</span>
          )}
          {isAdmin && (
            <Link
              href="/admin"
              className="px-4 py-2 bg-purple-50 text-purple-700 rounded-lg font-medium hover:bg-purple-100 transition-colors"
            >
              Admin
            </Link>
          )}
          <button
            onClick={() => setIsHistoryOpen(true)}
            className="px-4 py-2 bg-blue-50 text-blue-700 rounded-lg font-medium hover:bg-blue-100 transition-colors"
          >
            History
          </button>
          <button
            onClick={handleNewChat}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors"
          >
            New Chat
          </button>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-50 text-red-700 rounded-lg font-medium hover:bg-red-100 transition-colors"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <p className="text-lg mb-2">Welcome to AICMO Podcast Chat!</p>
              <p className="text-sm">Ask a question to get started.</p>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <ChatMessage key={idx} {...msg} />
        ))}

        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <p className="text-red-800 font-medium">Error: {error}</p>
            <p className="text-red-600 text-sm mt-1">
              Please check that the API server is running and try again.
            </p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={isLoading} />

      {/* Conversation History Panel */}
      <ConversationHistory
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectConversation={handleSelectConversation}
        currentConversationId={conversationId}
        onDeleteCurrentConversation={handleNewChat}
      />
    </div>
  );
}
