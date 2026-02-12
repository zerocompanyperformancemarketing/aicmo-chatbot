from unittest.mock import AsyncMock, patch
import pytest

from models.schemas import IngestFileRequest, IngestDirectoryRequest
import routers.ingest as ingest_module


class TestIngestEndpoint:
    @pytest.mark.asyncio
    async def test_ingest_file(self):
        with patch.object(ingest_module, "ingest_file", new_callable=AsyncMock) as mock_ingest:
            mock_ingest.return_value = {
                "status": "ok",
                "episode_id": "ep-1",
                "chunks_created": 25,
            }

            request = IngestFileRequest(file_path="/data/episode.vtt")
            response = await ingest_module.ingest(request)

            mock_ingest.assert_called_once_with("/data/episode.vtt", force=False)
            assert response.status == "ok"
            assert response.episode_id == "ep-1"
            assert response.chunks_created == 25

    @pytest.mark.asyncio
    async def test_ingest_directory(self):
        with patch.object(ingest_module, "ingest_directory", new_callable=AsyncMock) as mock_ingest_dir:
            mock_ingest_dir.return_value = {
                "status": "ok",
                "episodes_processed": 5,
            }

            request = IngestDirectoryRequest(directory_path="/data/episodes/")
            response = await ingest_module.ingest_dir(request)

            mock_ingest_dir.assert_called_once_with("/data/episodes/", force=False)
            assert response.status == "ok"
            assert response.episodes_processed == 5
