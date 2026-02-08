import json
from unittest.mock import AsyncMock, patch, MagicMock
import pytest

from models.schemas import ParsedCue


@pytest.fixture
def sample_segments():
    words = " ".join(["word"] * 2500)
    return [ParsedCue(start_time=0.0, end_time=300.0, text=words)]


class TestExtractMetadata:
    @pytest.mark.asyncio
    @patch("ingestion.metadata_extractor.get_llm")
    async def test_extracts_metadata(self, mock_get_llm, sample_segments):
        from ingestion.metadata_extractor import extract_metadata

        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "title": "Great Episode",
            "guest_names": ["Jane Doe"],
            "host_names": ["Steven Sikash"],
            "industry": "Tech",
            "topic_tags": ["AI", "Leadership"],
            "summary": "A great episode about AI.",
        })
        mock_llm.ainvoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = await extract_metadata("Great Episode with Jane Doe _unedited_.vtt", sample_segments)
        assert result.title == "Great Episode"
        assert result.guest_names == ["Jane Doe"]
        assert result.industry == "Tech"
        assert result.source_file == "Great Episode with Jane Doe _unedited_.vtt"

    @pytest.mark.asyncio
    @patch("ingestion.metadata_extractor.get_llm")
    async def test_handles_json_failure(self, mock_get_llm, sample_segments):
        from ingestion.metadata_extractor import extract_metadata

        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "invalid json"
        mock_llm.ainvoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = await extract_metadata("My Episode with Guest.vtt", sample_segments)
        # Should fall back to filename-parsed values
        assert result.title == "My Episode"
        assert result.source_file == "My Episode with Guest.vtt"

    @pytest.mark.asyncio
    @patch("ingestion.metadata_extractor.get_llm")
    async def test_handles_markdown_fences(self, mock_get_llm, sample_segments):
        from ingestion.metadata_extractor import extract_metadata

        mock_llm = AsyncMock()
        data = {
            "title": "Fenced",
            "guest_names": [],
            "host_names": [],
            "industry": "Finance",
            "topic_tags": ["Money"],
            "summary": "Summary.",
        }
        mock_response = MagicMock()
        mock_response.content = f"```json\n{json.dumps(data)}\n```"
        mock_llm.ainvoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = await extract_metadata("Test.vtt", sample_segments)
        assert result.title == "Fenced"
        assert result.industry == "Finance"

    @pytest.mark.asyncio
    @patch("ingestion.metadata_extractor.get_llm")
    async def test_duration_from_segments(self, mock_get_llm):
        from ingestion.metadata_extractor import extract_metadata

        segments = [
            ParsedCue(start_time=0.0, end_time=100.0, text=" ".join(["w"] * 2500)),
            ParsedCue(start_time=100.0, end_time=600.0, text="end"),
        ]

        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            "title": "T", "guest_names": [], "host_names": [],
            "industry": "", "topic_tags": [], "summary": "",
        })
        mock_llm.ainvoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm

        result = await extract_metadata("Test.vtt", segments)
        assert result.duration_seconds == 600
