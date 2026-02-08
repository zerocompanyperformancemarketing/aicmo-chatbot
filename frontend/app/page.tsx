import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-white">
      <main className="flex flex-col gap-8 items-center">
        <h1 className="text-5xl font-bold text-gray-900">
          AICMO Podcast Chatbot
        </h1>
        <p className="text-xl text-gray-600 text-center max-w-2xl">
          Multi-agent RAG chatbot that turns your podcast transcript library
          into a searchable knowledge platform.
        </p>
        <Link
          href="/chat"
          className="px-8 py-4 bg-blue-600 text-white rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Start Chatting
        </Link>
      </main>
    </div>
  );
}
