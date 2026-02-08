import json
from unittest.mock import AsyncMock, patch, MagicMock
import pytest

from models.schemas import ParsedCue


@pytest.fixture
def sample_segments():
    return [
        ParsedCue(start_time=0.0, end_time=5.0, text="Welcome to the show."),
        ParsedCue(start_time=5.0, end_time=10.0, text="Thank you for having me."),
    ]


class TestDetectSpeakers:
    @pytest.mark.asyncio
    @patch("ingestion.speaker_detector.get_llm")
    async def test_assigns_speakers(self, mock_get_llm, sample_segments):
        from ingestion.speaker_detector import detect_speakers

        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = json.dumps([
            {"index": 0, "speaker": "Steven Sikash", "confidence": 0.9},
            {"index": 1, "speaker": "Jane Doe", "confidence": 0.85},
        ])
        mock_llm.ainvoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = await detect_speakers(sample_segments, "Jane Doe")
        assert len(result) == 2
        assert result[0].speaker == "Steven Sikash"
        assert result[1].speaker == "Jane Doe"

    @pytest.mark.asyncio
    @patch("ingestion.speaker_detector.get_llm")
    async def test_handles_json_parse_failure(self, mock_get_llm, sample_segments):
        from ingestion.speaker_detector import detect_speakers

        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "not valid json"
        mock_llm.ainvoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = await detect_speakers(sample_segments, "Jane Doe")
        assert len(result) == 2
        # Speakers should be empty when parsing fails
        assert result[0].speaker == ""
        assert result[1].speaker == ""

    @pytest.mark.asyncio
    @patch("ingestion.speaker_detector.get_llm")
    async def test_handles_markdown_fences(self, mock_get_llm, sample_segments):
        from ingestion.speaker_detector import detect_speakers

        mock_llm = AsyncMock()
        mock_response = MagicMock()
        data = [
            {"index": 0, "speaker": "Host", "confidence": 0.9},
            {"index": 1, "speaker": "Guest", "confidence": 0.8},
        ]
        mock_response.content = f"```json\n{json.dumps(data)}\n```"
        mock_llm.ainvoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = await detect_speakers(sample_segments, "Guest")
        assert result[0].speaker == "Host"
        assert result[1].speaker == "Guest"

    @pytest.mark.asyncio
    @patch("ingestion.speaker_detector.get_llm")
    async def test_batching(self, mock_get_llm):
        from ingestion.speaker_detector import detect_speakers

        # Create 5 segments, batch_size=2 → 3 LLM calls
        segments = [
            ParsedCue(start_time=float(i), end_time=float(i + 1), text=f"Segment {i}")
            for i in range(5)
        ]

        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "[]"
        mock_llm.ainvoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = await detect_speakers(segments, "Guest", batch_size=2)
        assert len(result) == 5
        assert mock_llm.ainvoke.call_count == 3
