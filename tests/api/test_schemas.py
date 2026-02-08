import pytest
from pydantic import ValidationError
from models.schemas import (
    ChatRequest,
    ChatResponse,
    Source,
    IngestFileRequest,
    IngestResponse,
    EpisodeMetadata,
    TranscriptChunk,
    ParsedCue,
    MessageResponse,
    ConversationResponse,
)
from datetime import datetime, timezone


class TestChatRequest:
    def test_minimal(self):
        req = ChatRequest(message="Hello")
        assert req.message == "Hello"
        assert req.conversation_id is None

    def test_with_conversation_id(self):
        req = ChatRequest(message="Hi", conversation_id="abc-123")
        assert req.conversation_id == "abc-123"

    def test_missing_message_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest()


class TestChatResponse:
    def test_full(self):
        resp = ChatResponse(response="Answer", sources=[], conversation_id="id-1")
        assert resp.response == "Answer"
        assert resp.sources == []

    def test_with_sources(self):
        src = Source(episode_title="Ep1", speaker="Host", timestamp="00:01:00", text_snippet="snippet")
        resp = ChatResponse(response="Answer", sources=[src], conversation_id="id-1")
        assert len(resp.sources) == 1
        assert resp.sources[0].speaker == "Host"


class TestParsedCue:
    def test_defaults(self):
        cue = ParsedCue(start_time=0.0, end_time=1.0, text="Hello")
        assert cue.speaker == ""

    def test_with_speaker(self):
        cue = ParsedCue(start_time=0.0, end_time=1.0, text="Hello", speaker="Host")
        assert cue.speaker == "Host"


class TestTranscriptChunk:
    def test_defaults(self):
        chunk = TranscriptChunk(
            episode_id="ep-1", text="content", speaker="Host",
            start_time=0.0, end_time=10.0, chunk_index=0,
        )
        assert chunk.guest_names == []
        assert chunk.industry == ""
        assert chunk.topic_tags == []


class TestEpisodeMetadata:
    def test_required_fields(self):
        meta = EpisodeMetadata(
            title="Ep 1",
            guest_names=["Guest"],
            host_names=["Host"],
            industry="Tech",
            topic_tags=["AI"],
            summary="A summary",
        )
        assert meta.title == "Ep 1"
        assert meta.episode_link is None
        assert meta.duration_seconds == 0
        assert meta.source_file == ""


class TestMessageResponse:
    def test_full(self):
        now = datetime.now(timezone.utc)
        msg = MessageResponse(id=1, role="user", content="Hi", created_at=now)
        assert msg.sources is None

    def test_with_sources(self):
        now = datetime.now(timezone.utc)
        msg = MessageResponse(id=1, role="assistant", content="Reply", sources=[{"key": "val"}], created_at=now)
        assert msg.sources == [{"key": "val"}]


class TestConversationResponse:
    def test_defaults(self):
        now = datetime.now(timezone.utc)
        conv = ConversationResponse(id="abc", created_at=now, updated_at=now)
        assert conv.messages == []
