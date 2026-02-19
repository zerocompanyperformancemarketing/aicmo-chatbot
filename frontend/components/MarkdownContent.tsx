'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Components } from 'react-markdown';

interface MarkdownContentProps {
  content: string;
  variant: 'user' | 'assistant';
}

export default function MarkdownContent({ content, variant }: MarkdownContentProps) {
  const isUser = variant === 'user';

  const components: Components = {
    a: ({ href, children }) => (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="underline hover:no-underline"
      >
        {children}
      </a>
    ),
    pre: ({ children }) => (
      <pre className="overflow-x-auto max-w-full">
        {children}
      </pre>
    ),
  };

  return (
    <div
      className={`prose prose-chat max-w-none ${
        isUser ? 'prose-chat-invert' : ''
      }`}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
