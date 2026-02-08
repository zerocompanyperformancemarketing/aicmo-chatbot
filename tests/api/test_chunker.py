from models.schemas import ParsedCue, TranscriptChunk
from ingestion.chunker import chunk_segments


def _make_segment(text: str, speaker: str = "Host", start: float = 0.0, end: float = 1.0) -> ParsedCue:
    return ParsedCue(start_time=start, end_time=end, text=text, speaker=speaker)


METADATA = {
    "guest_names": ["Jane Doe"],
    "industry": "Tech",
    "topic_tags": ["AI", "Startups"],
}


class TestChunkSegments:
    def test_empty_segments(self):
        result = chunk_segments([], "ep-1", METADATA)
        assert result == []

    def test_single_small_segment(self):
        segments = [_make_segment("Hello world", start=0.0, end=1.0)]
        result = chunk_segments(segments, "ep-1", METADATA)
        assert len(result) == 1
        assert result[0].text == "Hello world"
        assert result[0].episode_id == "ep-1"
        assert result[0].chunk_index == 0

    def test_metadata_attached_to_chunks(self):
        segments = [_make_segment("Hello world")]
        result = chunk_segments(segments, "ep-1", METADATA)
        assert result[0].guest_names == ["Jane Doe"]
        assert result[0].industry == "Tech"
        assert result[0].topic_tags == ["AI", "Startups"]

    def test_chunking_splits_at_size(self):
        # Two segments that together exceed chunk_size trigger a flush
        seg1 = _make_segment(" ".join(["word"] * 400), start=0.0, end=40.0)
        seg2 = _make_segment(" ".join(["word"] * 200), start=40.0, end=60.0)
        result = chunk_segments([seg1, seg2], "ep-1", METADATA, chunk_size=500, overlap=50)
        assert len(result) == 2

    def test_overlap_words_carry_over(self):
        # Two segments that together exceed chunk_size
        seg1 = _make_segment(" ".join(["alpha"] * 300), start=0.0, end=30.0)
        seg2 = _make_segment(" ".join(["beta"] * 300), start=30.0, end=60.0)
        result = chunk_segments([seg1, seg2], "ep-1", METADATA, chunk_size=500, overlap=50)
        assert len(result) == 2
        # Second chunk should start with overlap words from the first
        second_words = result[1].text.split()
        assert "alpha" in second_words  # overlap carried from first chunk

    def test_chunk_indices_sequential(self):
        text = " ".join(["word"] * 1500)
        segments = [_make_segment(text, start=0.0, end=150.0)]
        result = chunk_segments(segments, "ep-1", METADATA, chunk_size=500, overlap=50)
        indices = [c.chunk_index for c in result]
        assert indices == list(range(len(result)))

    def test_speaker_attribution(self):
        # When segments fit in one chunk, speaker is the last segment's speaker
        segments = [
            _make_segment("Hello from host", speaker="Host", start=0.0, end=1.0),
            _make_segment("Hello from guest", speaker="Guest", start=1.0, end=2.0),
        ]
        result = chunk_segments(segments, "ep-1", METADATA, chunk_size=500)
        assert result[0].speaker == "Guest"

    def test_empty_metadata_defaults(self):
        segments = [_make_segment("Hello")]
        result = chunk_segments(segments, "ep-1", {})
        assert result[0].guest_names == []
        assert result[0].industry == ""
        assert result[0].topic_tags == []
