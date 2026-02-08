from unittest.mock import patch, MagicMock
from tools.metadata import get_episode_metadata, list_speakers, list_industries


class TestGetEpisodeMetadata:
    @patch("tools.metadata.get_typesense_client")
    def test_returns_metadata(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.collections.__getitem__.return_value.documents.__getitem__.return_value.retrieve.return_value = {
            "id": "ep-1",
            "title": "AI Episode",
            "guest_names": ["Jane"],
            "host_names": ["Host"],
            "industry": "Tech",
            "topic_tags": ["AI"],
            "summary": "Summary",
            "episode_link": "https://example.com",
            "duration_seconds": 3600,
        }
        mock_client_fn.return_value = mock_client

        result = get_episode_metadata("ep-1")
        assert result["title"] == "AI Episode"
        assert result["duration_seconds"] == 3600

    @patch("tools.metadata.get_typesense_client")
    def test_not_found(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.collections.__getitem__.return_value.documents.__getitem__.return_value.retrieve.side_effect = Exception("Not found")
        mock_client_fn.return_value = mock_client

        result = get_episode_metadata("nonexistent")
        assert "error" in result


class TestListSpeakers:
    @patch("tools.metadata.get_typesense_client")
    def test_returns_speakers(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.collections.__getitem__.return_value.documents.search.return_value = {
            "facet_counts": [{
                "field_name": "speaker",
                "counts": [
                    {"value": "Jane Doe", "count": 10},
                    {"value": "Host", "count": 25},
                ],
            }]
        }
        mock_client_fn.return_value = mock_client

        result = list_speakers()
        assert len(result) == 2
        assert result[0]["speaker"] == "Jane Doe"
        assert result[0]["chunk_count"] == 10

    @patch("tools.metadata.get_typesense_client")
    def test_empty_facets(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.collections.__getitem__.return_value.documents.search.return_value = {"facet_counts": []}
        mock_client_fn.return_value = mock_client

        result = list_speakers()
        assert result == []


class TestListIndustries:
    @patch("tools.metadata.get_typesense_client")
    def test_returns_industries(self, mock_client_fn):
        mock_client = MagicMock()
        mock_client.collections.__getitem__.return_value.documents.search.return_value = {
            "facet_counts": [{
                "field_name": "industry",
                "counts": [
                    {"value": "Tech", "count": 5},
                    {"value": "Healthcare", "count": 3},
                ],
            }]
        }
        mock_client_fn.return_value = mock_client

        result = list_industries()
        assert len(result) == 2
        assert result[1]["industry"] == "Healthcare"
        assert result[1]["episode_count"] == 3
