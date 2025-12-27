"""Metacritic search functionality for finding games by name."""

from __future__ import annotations

import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("game_db.metacritic_search")


def search_metacritic_game_url(game_name: str) -> str | None:
    """Search for game on Metacritic by name and return first result URL.

    Args:
        game_name: Name of the game to search for

    Returns:
        URL of the first search result, or None if not found
    """
    try:
        # Build search URL - Metacritic uses hyphens instead of spaces
        # and lowercase for search terms
        search_term = game_name.lower().replace(" ", "-")
        # Remove special characters that might break URL
        search_term = "".join(c if c.isalnum() or c in "-" else "" for c in search_term)
        # Remove multiple consecutive hyphens
        while "--" in search_term:
            search_term = search_term.replace("--", "-")
        search_term = search_term.strip("-")

        search_url = f"https://www.metacritic.com/search/game/{search_term}/results"

        # Use realistic browser headers
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/webp,image/apng,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "DNT": "1",
        }

        session = requests.Session()
        session.headers.update(headers)

        response = session.get(search_url, timeout=10, allow_redirects=True)
        response.raise_for_status()

        logger.debug(
            "Search response status: %d, URL: %s", response.status_code, response.url
        )

        soup = BeautifulSoup(response.content, "html.parser")

        # Try multiple selectors for search results
        # Metacritic search results can be in different structures
        result_url = None

        # Method 1: Look for <li class="result"> or similar list items
        result_items = soup.find_all(
            "li", class_=lambda x: x and "result" in str(x).lower()
        )
        for result in result_items:
            link = result.find("a", href=True)
            if link:
                href = link.get("href", "")
                if href and "/game/" in href and len(href) > len("/game/"):
                    # Skip incomplete URLs
                    if href.count("/") >= 3:  # /game/platform/name format
                        if href.startswith("/"):
                            result_url = f"https://www.metacritic.com{href}"
                        elif href.startswith("http"):
                            result_url = href
                        if result_url and "/search/" not in result_url:
                            break

        # Method 2: Look for all links with /game/ in href, prioritize first valid one
        if not result_url:
            game_links = soup.find_all("a", href=True)
            logger.debug("Found %d links on search page", len(game_links))
            for link in game_links:
                href = link.get("href", "")
                if href and "/game/" in href:
                    # Skip if it's a search URL, category page, or incomplete
                    if (
                        "/search/" in href
                        or "/browse/" in href
                        or href == "/game/"
                        or href.endswith("/game/")
                    ):
                        continue
                    # Must have platform and game name: /game/platform/name
                    parts = [p for p in href.split("/") if p]  # Remove empty parts
                    if len(parts) >= 3 and parts[-1]:  # Has game name
                        # Reconstruct href from parts
                        clean_href = "/" + "/".join(parts)
                        if clean_href.startswith("/game/"):
                            result_url = f"https://www.metacritic.com{clean_href}"
                        elif href.startswith("http") and "metacritic.com/game/" in href:
                            result_url = href
                        if result_url:
                            logger.debug("Found game URL via method 2: %s", result_url)
                            break

        # Method 3: Look for divs or sections with game information
        if not result_url:
            game_containers = soup.find_all(
                ["div", "section", "article"],
                class_=lambda x: x
                and ("game" in str(x).lower() or "result" in str(x).lower()),
            )
            for container in game_containers:
                link = container.find("a", href=True)
                if link:
                    href = link.get("href", "")
                    if href and "/game/" in href and len(href) > len("/game/"):
                        parts = href.split("/")
                        if len(parts) >= 4 and parts[-1]:
                            if href.startswith("/"):
                                result_url = f"https://www.metacritic.com{href}"
                            elif href.startswith("http"):
                                result_url = href
                            if result_url and "/search/" not in result_url:
                                break

        if result_url:
            logger.info("Found Metacritic URL for '%s': %s", game_name, result_url)
            return result_url

        logger.warning(
            "No Metacritic URL found for game: %s (searched: %s)",
            game_name,
            search_url,
        )
        return None

    except requests.RequestException as e:
        logger.warning(
            "Error searching Metacritic for game '%s': %s",
            game_name,
            str(e),
        )
        return None
    except Exception as e:
        logger.warning(
            "Unexpected error searching Metacritic for game '%s': %s",
            game_name,
            str(e),
        )
        return None
