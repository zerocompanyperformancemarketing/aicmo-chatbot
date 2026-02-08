from scrapingbee import ScrapingBeeClient
from config import Config


def scrape_website(
    url: str,
    render_js: bool = False,
    extract_rules: dict | None = None,
    wait: int | None = None,
    premium_proxy: bool = False,
) -> dict:
    """
    Scrape a website using ScrapingBee.
    Args:
        url (str): The URL to scrape.
        render_js (bool): Whether to render JavaScript. Defaults to False (1 credit vs 5).
        extract_rules (dict | None): CSS/XPath extraction rules for structured data.
        wait (int | None): Milliseconds to wait before returning content.
        premium_proxy (bool): Use premium residential proxies for hard-to-scrape sites.
    Returns:
        dict: A dictionary with 'status_code', 'content', and optionally 'data' (if extract_rules provided).
    """
    client = ScrapingBeeClient(api_key=Config.SCRAPINGBEE_API_KEY)

    params = {
        "render_js": render_js,
        "premium_proxy": premium_proxy,
    }

    if wait is not None:
        params["wait"] = wait

    if extract_rules is not None:
        params["extract_rules"] = extract_rules

    response = client.get(url, params=params, retries=3)

    result = {
        "status_code": response.status_code,
        "content": response.text,
    }

    if extract_rules:
        try:
            result["data"] = response.json()
        except Exception:
            result["data"] = None

    return result


def web_search(query: str, num_results: int = 5) -> dict:
    """
    Perform a web search by scraping Google search results using ScrapingBee.
    Args:
        query (str): The search query.
        num_results (int): Number of results to return. Defaults to 5.
    Returns:
        dict: A dictionary with 'status_code' and 'results' (list of title, url, description).
    """
    client = ScrapingBeeClient(api_key=Config.SCRAPINGBEE_API_KEY)

    search_url = f"https://www.google.com/search?q={query}&num={num_results}"

    params = {
        "render_js": False,
        "extract_rules": {
            "results": {
                "selector": "div.g",
                "type": "list",
                "output": {
                    "title": "h3",
                    "url": "a@href",
                    "description": "div.VwiC3b",
                }
            }
        },
    }

    response = client.get(search_url, params=params, retries=3)

    result = {
        "status_code": response.status_code,
        "results": [],
    }

    if response.ok:
        try:
            data = response.json()
            result["results"] = data.get("results", [])[:num_results]
        except Exception:
            result["results"] = []

    return result
