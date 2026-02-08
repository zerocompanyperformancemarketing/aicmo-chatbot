interface SourceCardProps {
  episode_title: string;
  speaker: string;
  timestamp: string;
  text_snippet: string;
}

export default function SourceCard({
  episode_title,
  speaker,
  timestamp,
  text_snippet,
}: SourceCardProps) {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
      <h4 className="font-semibold text-blue-900 mb-2">{episode_title}</h4>
      <div className="flex gap-4 text-gray-600 mb-2">
        <span className="font-medium">{speaker}</span>
        <span>{timestamp}</span>
      </div>
      <p className="text-gray-700 italic">"{text_snippet}"</p>
    </div>
  );
}
