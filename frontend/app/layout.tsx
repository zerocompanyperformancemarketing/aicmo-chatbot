import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AICMO Podcast Chatbot',
  description: 'Multi-agent RAG chatbot for podcast transcript knowledge base',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
