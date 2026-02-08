'use client';

import { useState } from 'react';
import SourceCard from './SourceCard';

interface Source {
  episode_title: string;
  speaker: string;
  timestamp: string;
  text_snippet: string;
}

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

export default function ChatMessage({ role, content, sources }: ChatMessageProps) {
  const [showSources, setShowSources] = useState(false);

  const isUser = role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'} rounded-lg px-4 py-3`}>
        <div className="whitespace-pre-wrap">{content}</div>

        {sources && sources.length > 0 && (
          <div className="mt-3">
            <button
              onClick={() => setShowSources(!showSources)}
              className="text-xs font-semibold text-blue-200 hover:text-blue-100 underline"
            >
              {showSources ? 'Hide' : 'Show'} {sources.length} source{sources.length > 1 ? 's' : ''}
            </button>

            {showSources && (
              <div className="mt-3 space-y-2">
                {sources.map((source, idx) => (
                  <SourceCard key={idx} {...source} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
