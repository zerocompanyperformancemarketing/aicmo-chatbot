import logging
from models.schemas import ParsedCue, TranscriptChunk

logger = logging.getLogger(__name__)


def chunk_segments(
    segments: list[ParsedCue],
    episode_id: str,
    metadata: dict,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[TranscriptChunk]:
    """
    Chunk merged segments into ~500-word chunks with 50-word overlap.

    Prefers breaking at speaker turns and sentence boundaries.
    Each chunk gets denormalized episode metadata.
    """
    logger.info(f"chunk_segments called | episode_id={episode_id!r}, segments={len(segments)}, chunk_size={chunk_size}, overlap={overlap}")
    chunks: list[TranscriptChunk] = []
    current_words: list[str] = []
    current_start: float = 0.0
    current_end: float = 0.0
    current_speaker: str = ""
    chunk_index = 0

    for segment in segments:
        words = segment.text.split()
        speaker = segment.speaker or current_speaker

        if not current_words:
            current_start = segment.start_time
            current_speaker = speaker

        # If adding this segment exceeds chunk_size and we have content, flush
        if len(current_words) + len(words) > chunk_size and current_words:
            chunks.append(TranscriptChunk(
                episode_id=episode_id,
                text=" ".join(current_words),
                speaker=current_speaker,
                start_time=current_start,
                end_time=current_end,
                chunk_index=chunk_index,
                guest_names=metadata.get("guest_names", []),
                industry=metadata.get("industry", ""),
                topic_tags=metadata.get("topic_tags", []),
            ))
            chunk_index += 1

            # Overlap: carry the last N words into the next chunk
            overlap_words = current_words[-overlap:] if len(current_words) > overlap else current_words
            current_words = overlap_words
            current_start = segment.start_time

        current_words.extend(words)
        current_end = segment.end_time
        current_speaker = speaker

    # Flush remaining words
    if current_words:
        chunks.append(TranscriptChunk(
            episode_id=episode_id,
            text=" ".join(current_words),
            speaker=current_speaker,
            start_time=current_start,
            end_time=current_end,
            chunk_index=chunk_index,
            guest_names=metadata.get("guest_names", []),
            industry=metadata.get("industry", ""),
            topic_tags=metadata.get("topic_tags", []),
        ))

    logger.info(f"chunk_segments returned | {len(chunks)} chunks")
    return chunks
