from unittest.mock import patch, MagicMock
from utils.scrape_utils import scrape_website, web_search


class TestScrapeWebsite:
    @patch("utils.scrape_utils.ScrapingBeeClient")
    def test_basic_scrape(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>Hello</html>"
        mock_client_cls.return_value.get.return_value = mock_response

        result = scrape_website("https://example.com")
        assert result["status_code"] == 200
        assert result["content"] == "<html>Hello</html>"
        assert "data" not in result

    @patch("utils.scrape_utils.ScrapingBeeClient")
    def test_with_extract_rules(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "raw"
        mock_response.json.return_value = {"title": "Test"}
        mock_client_cls.return_value.get.return_value = mock_response

        rules = {"title": "h1"}
        result = scrape_website("https://example.com", extract_rules=rules)
        assert result["data"] == {"title": "Test"}

    @patch("utils.scrape_utils.ScrapingBeeClient")
    def test_extract_rules_json_fails(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "not json"
        mock_response.json.side_effect = Exception("bad json")
        mock_client_cls.return_value.get.return_value = mock_response

        rules = {"title": "h1"}
        result = scrape_website("https://example.com", extract_rules=rules)
        assert result["data"] is None

    @patch("utils.scrape_utils.ScrapingBeeClient")
    def test_passes_params(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_client_cls.return_value.get.return_value = mock_response

        scrape_website("https://example.com", render_js=True, wait=5000, premium_proxy=True)
        call_kwargs = mock_client_cls.return_value.get.call_args
        params = call_kwargs[1]["params"]
        assert params["render_js"] is True
        assert params["wait"] == 5000
        assert params["premium_proxy"] is True


class TestWebSearch:
    @patch("utils.scrape_utils.ScrapingBeeClient")
    def test_returns_results(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"title": "Result 1", "url": "https://r1.com", "description": "Desc 1"},
                {"title": "Result 2", "url": "https://r2.com", "description": "Desc 2"},
            ]
        }
        mock_client_cls.return_value.get.return_value = mock_response

        result = web_search("test query", num_results=2)
        assert result["status_code"] == 200
        assert len(result["results"]) == 2

    @patch("utils.scrape_utils.ScrapingBeeClient")
    def test_failed_response(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_client_cls.return_value.get.return_value = mock_response

        result = web_search("test query")
        assert result["results"] == []

    @patch("utils.scrape_utils.ScrapingBeeClient")
    def test_limits_results(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"title": f"R{i}"} for i in range(10)]
        }
        mock_client_cls.return_value.get.return_value = mock_response

        result = web_search("test", num_results=3)
        assert len(result["results"]) == 3
