from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from models.schemas import ParsedCue, EpisodeMetadata, TranscriptChunk


@pytest.fixture
def sample_segments():
    return [
        ParsedCue(start_time=0.0, end_time=5.0, text="Hello world.", speaker=""),
        ParsedCue(start_time=5.0, end_time=10.0, text="Welcome to the show.", speaker=""),
    ]


@pytest.fixture
def labeled_segments():
    return [
        ParsedCue(start_time=0.0, end_time=5.0, text="Hello world.", speaker="Host"),
        ParsedCue(start_time=5.0, end_time=10.0, text="Welcome to the show.", speaker="Guest"),
    ]


@pytest.fixture
def sample_metadata():
    return EpisodeMetadata(
        title="Test Episode",
        guest_names=["Jane Doe"],
        host_names=["Steven Sikash"],
        industry="Tech",
        topic_tags=["AI"],
        summary="A test episode.",
        source_file="Test Episode with Jane Doe.vtt",
        duration_seconds=10,
    )


@pytest.fixture
def sample_chunks():
    return [
        TranscriptChunk(
            episode_id="test_episode_with_jane_doe",
            text="Hello world. Welcome to the show.",
            speaker="Host",
            start_time=0.0,
            end_time=10.0,
            chunk_index=0,
            guest_names=["Jane Doe"],
            industry="Tech",
            topic_tags=["AI"],
        )
    ]


class TestIngestFile:
    @pytest.mark.asyncio
    @patch("ingestion.pipeline._get_typesense_client")
    @patch("ingestion.pipeline.chunk_segments")
    @patch("ingestion.pipeline.detect_speakers", new_callable=AsyncMock)
    @patch("ingestion.pipeline.extract_metadata", new_callable=AsyncMock)
    @patch("ingestion.pipeline.parse_vtt")
    async def test_full_pipeline(
        self, mock_parse, mock_extract, mock_detect, mock_chunk, mock_ts,
        sample_segments, labeled_segments, sample_metadata, sample_chunks,
    ):
        from ingestion.pipeline import ingest_file

        mock_parse.return_value = sample_segments
        mock_extract.return_value = sample_metadata
        mock_detect.return_value = labeled_segments
        mock_chunk.return_value = sample_chunks

        # Use separate mocks per collection so upsert calls don't merge
        episodes_col = MagicMock()
        chunks_col = MagicMock()
        mock_client = MagicMock()
        mock_client.collections.__getitem__ = lambda self, key: {"episodes": episodes_col, "transcript_chunks": chunks_col}[key]
        mock_ts.return_value = mock_client

        result = await ingest_file("/data/Test Episode with Jane Doe.vtt")

        assert result["status"] == "success"
        assert result["episode_id"] == "test_episode_with_jane_doe"
        assert result["chunks_created"] == 1

        # Verify pipeline steps called in order
        mock_parse.assert_called_once_with("/data/Test Episode with Jane Doe.vtt")
        mock_extract.assert_called_once_with("Test Episode with Jane Doe.vtt", sample_segments)
        mock_detect.assert_called_once_with(sample_segments, "Jane Doe")
        mock_chunk.assert_called_once()

        # Verify Typesense upserts
        episodes_col.documents.upsert.assert_called_once()
        chunks_col.documents.upsert.assert_called_once()

    @pytest.mark.asyncio
    @patch("ingestion.pipeline._get_typesense_client")
    @patch("ingestion.pipeline.chunk_segments")
    @patch("ingestion.pipeline.detect_speakers", new_callable=AsyncMock)
    @patch("ingestion.pipeline.extract_metadata", new_callable=AsyncMock)
    @patch("ingestion.pipeline.parse_vtt")
    async def test_episode_id_from_filename(
        self, mock_parse, mock_extract, mock_detect, mock_chunk, mock_ts,
        sample_segments, labeled_segments, sample_metadata, sample_chunks,
    ):
        from ingestion.pipeline import ingest_file

        mock_parse.return_value = sample_segments
        mock_extract.return_value = sample_metadata
        mock_detect.return_value = labeled_segments
        mock_chunk.return_value = sample_chunks
        mock_ts.return_value = MagicMock()

        result = await ingest_file("/data/My Great Episode.vtt")
        assert result["episode_id"] == "my_great_episode"

    @pytest.mark.asyncio
    @patch("ingestion.pipeline._get_typesense_client")
    @patch("ingestion.pipeline.chunk_segments")
    @patch("ingestion.pipeline.detect_speakers", new_callable=AsyncMock)
    @patch("ingestion.pipeline.extract_metadata", new_callable=AsyncMock)
    @patch("ingestion.pipeline.parse_vtt")
    async def test_guest_fallback_to_filename(
        self, mock_parse, mock_extract, mock_detect, mock_chunk, mock_ts,
        sample_segments, labeled_segments, sample_chunks,
    ):
        from ingestion.pipeline import ingest_file

        # Metadata with no guest names → should fall back to filename parsing
        no_guest_meta = EpisodeMetadata(
            title="Episode", guest_names=[], host_names=["Host"],
            industry="", topic_tags=[], summary="",
        )
        mock_parse.return_value = sample_segments
        mock_extract.return_value = no_guest_meta
        mock_detect.return_value = labeled_segments
        mock_chunk.return_value = sample_chunks
        mock_ts.return_value = MagicMock()

        await ingest_file("/data/Episode with John Smith.vtt")
        mock_detect.assert_called_once_with(sample_segments, "John Smith")

    @pytest.mark.asyncio
    @patch("ingestion.pipeline._get_typesense_client")
    @patch("ingestion.pipeline.chunk_segments", return_value=[])
    @patch("ingestion.pipeline.detect_speakers", new_callable=AsyncMock)
    @patch("ingestion.pipeline.extract_metadata", new_callable=AsyncMock)
    @patch("ingestion.pipeline.parse_vtt", return_value=[])
    async def test_empty_file(self, mock_parse, mock_extract, mock_detect, mock_chunk, mock_ts):
        from ingestion.pipeline import ingest_file

        mock_extract.return_value = EpisodeMetadata(
            title="Empty", guest_names=[], host_names=[],
            industry="", topic_tags=[], summary="",
        )
        mock_detect.return_value = []
        mock_ts.return_value = MagicMock()

        result = await ingest_file("/data/empty.vtt")
        assert result["chunks_created"] == 0


class TestIngestDirectory:
    @pytest.mark.asyncio
    @patch("ingestion.pipeline.ingest_file", new_callable=AsyncMock)
    @patch("ingestion.pipeline.os.listdir")
    async def test_processes_vtt_files_only(self, mock_listdir, mock_ingest):
        from ingestion.pipeline import ingest_directory

        mock_listdir.return_value = ["ep1.vtt", "ep2.vtt", "notes.txt", "ep3.vtt"]
        mock_ingest.return_value = {"status": "success", "episode_id": "ep", "chunks_created": 5}

        result = await ingest_directory("/data/episodes")
        assert result["episodes_processed"] == 3
        assert mock_ingest.call_count == 3

    @pytest.mark.asyncio
    @patch("ingestion.pipeline.ingest_file", new_callable=AsyncMock)
    @patch("ingestion.pipeline.os.listdir")
    async def test_empty_directory(self, mock_listdir, mock_ingest):
        from ingestion.pipeline import ingest_directory

        mock_listdir.return_value = []

        result = await ingest_directory("/data/empty")
        assert result["episodes_processed"] == 0
        mock_ingest.assert_not_called()
