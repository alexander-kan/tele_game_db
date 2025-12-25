"""MetaCriticScraper - extract game data from Metacritic pages.

This module is based on Metacritic-Python-API by JaeguKim.
Source: https://github.com/JaeguKim/Metacritic-Python-API
"""

from __future__ import annotations

import json
import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("game_db.MetaCriticScraper")


class MetaCriticScraper:
    """Scrape game data from Metacritic game pages."""

    def __init__(self, url: str) -> None:
        """Initialize scraper with Metacritic game URL.

        Args:
            url: URL of the Metacritic game page
        """
        self.game = {
            "url": "",
            "image": "",
            "title": "",
            "description": "",
            "platform": "",
            "publisher": "",
            "release_date": "",
            "critic_score": "",
            "critic_outof": "",
            "critic_count": "",
            "user_score": "",
            "user_count": "",
            "developer": "",
            "genre": "",
            "rating": "",
        }

        try:
            # Use requests with realistic browser headers to avoid 403 Forbidden
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

            # Use session to maintain cookies
            session = requests.Session()
            session.headers.update(headers)

            response = session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()  # Raise exception for bad status codes

            self.game["url"] = response.url
            self.soup = BeautifulSoup(response.content, "html.parser")
            self.scrape()
        except requests.RequestException as e:
            logger.warning(
                "Failed to scrape Metacritic page %s: %s",
                url,
                str(e),
            )
        except (ValueError, Exception) as e:
            logger.warning(
                "Failed to scrape Metacritic page %s: %s",
                url,
                str(e),
            )

    def scrape(self) -> None:
        """Scrape game data from parsed HTML."""
        # Get Title and Platform
        try:
            product_title_div = self.soup.find("div", class_="product_title")
            if product_title_div and product_title_div.a:
                self.game["title"] = product_title_div.a.text.strip()
        except Exception:
            logger.debug("Problem getting title and platform information")
            pass

        # Get publisher and release date
        try:
            publisher_li = self.soup.find("li", class_="summary_detail publisher")
            if publisher_li and publisher_li.a:
                self.game["publisher"] = publisher_li.a.text.strip()

            release_li = self.soup.find(
                "li", class_="summary_detail release_data"
            )
            if release_li:
                data_span = release_li.find("span", class_="data")
                if data_span:
                    self.game["release_date"] = data_span.text.strip()
        except Exception:
            logger.debug("Problem getting publisher and release date information")
            pass

        # Get critic information from JSON-LD
        try:
            res = self.soup.find("script", type="application/ld+json")
            if res and res.string:
                js = json.loads(res.string)
                self.game["image"] = js.get("image", "")
                self.game["platform"] = js.get("gamePlatform", "")
                self.game["description"] = js.get("description", "")
                if "aggregateRating" in js:
                    self.game["critic_score"] = js["aggregateRating"].get(
                        "ratingValue", ""
                    )
                    self.game["critic_count"] = js["aggregateRating"].get(
                        "ratingCount", ""
                    )
        except Exception as e:
            logger.debug(
                "Problem getting critic score information: %s",
                str(e),
            )
            pass

        # Get user information
        try:
            users = self.soup.find("div", class_="details side_details")
            if users:
                metascore = users.find("div", class_="metascore_w")
                if metascore:
                    self.game["user_score"] = metascore.text.strip()

                count_span = users.find("span", class_="count")
                if count_span and count_span.a:
                    raw_users_count = count_span.a.text
                    user_count = ""
                    for c in raw_users_count:
                        if c.isdigit():
                            user_count += c
                    self.game["user_count"] = user_count.strip()
        except Exception:
            logger.debug("Problem getting user score information")
            pass

        # Get remaining information (developer, genre, rating)
        try:
            product_section = self.soup.find("div", class_="section product_details")
            if product_section:
                product_info = product_section.find("div", class_="details side_details")
                if product_info:
                    developer_li = product_info.find(
                        "li", class_="summary_detail developer"
                    )
                    if developer_li:
                        data_span = developer_li.find("span", class_="data")
                        if data_span:
                            self.game["developer"] = data_span.text.strip()

                    genre_li = product_info.find(
                        "li", class_="summary_detail product_genre"
                    )
                    if genre_li:
                        data_span = genre_li.find("span", class_="data")
                        if data_span:
                            self.game["genre"] = data_span.text.strip()

                    rating_li = product_info.find(
                        "li", class_="summary_detail product_rating"
                    )
                    if rating_li:
                        data_span = rating_li.find("span", class_="data")
                        if data_span:
                            self.game["rating"] = data_span.text.strip()
        except Exception:
            logger.debug("Problem getting miscellaneous game information")
            pass
