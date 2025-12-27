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
            if (
                product_title_div
                and hasattr(product_title_div, "a")
                and product_title_div.a
            ):
                self.game["title"] = product_title_div.a.text.strip()
        except Exception:
            logger.debug("Problem getting title and platform information")
            pass

        # Get publisher and release date
        try:
            publisher_li = self.soup.find("li", class_="summary_detail publisher")
            if publisher_li and hasattr(publisher_li, "a") and publisher_li.a:
                self.game["publisher"] = publisher_li.a.text.strip()

            # Try multiple ways to find release date
            # Method 1: Standard selector
            release_li = self.soup.find("li", class_="summary_detail release_data")
            if release_li and hasattr(release_li, "find"):
                data_span = release_li.find("span", class_="data")
                if data_span and hasattr(data_span, "text"):
                    self.game["release_date"] = data_span.text.strip()
                    logger.info(
                        "[METACRITIC_SCRAPER] Found release_date (method 1): %s",
                        self.game["release_date"],
                    )
                else:
                    # Try getting text directly from release_li
                    release_text = release_li.get_text(strip=True)
                    if release_text:
                        # Extract date part (usually after "Release Date:" or similar)
                        parts = release_text.split(":", 1)
                        if len(parts) > 1:
                            self.game["release_date"] = parts[1].strip()
                            logger.info(
                                "[METACRITIC_SCRAPER] Found release_date (method 1 alt): %s",
                                self.game["release_date"],
                            )

            # Method 2: Look in all summary_detail elements
            if not self.game["release_date"]:
                all_summary_details = self.soup.find_all("li", class_="summary_detail")
                logger.debug(
                    "[METACRITIC_SCRAPER] Found %d summary_detail elements",
                    len(all_summary_details),
                )
                for li in all_summary_details:
                    li_text = li.get_text().lower()
                    li_class = " ".join(li.get("class", []))
                    logger.debug(
                        "[METACRITIC_SCRAPER] summary_detail class: %s, text: %s",
                        li_class,
                        li_text[:100],
                    )
                    if (
                        "release" in li_text
                        or "date" in li_text
                        or "release" in li_class
                    ):
                        data_span = li.find("span", class_="data")
                        if data_span:
                            date_text = data_span.text.strip()
                            # Check if it looks like a date
                            if any(
                                month in date_text.lower()
                                for month in [
                                    "jan",
                                    "feb",
                                    "mar",
                                    "apr",
                                    "may",
                                    "jun",
                                    "jul",
                                    "aug",
                                    "sep",
                                    "oct",
                                    "nov",
                                    "dec",
                                ]
                            ) or any(c.isdigit() for c in date_text):
                                self.game["release_date"] = date_text
                                logger.info(
                                    "[METACRITIC_SCRAPER] Found release_date (method 2): %s",
                                    self.game["release_date"],
                                )
                                break
                        else:
                            # Try getting text directly
                            date_text = li.get_text(strip=True)
                            if date_text and (
                                "release" in date_text.lower()
                                or any(
                                    month in date_text.lower()
                                    for month in [
                                        "jan",
                                        "feb",
                                        "mar",
                                        "apr",
                                        "may",
                                        "jun",
                                        "jul",
                                        "aug",
                                        "sep",
                                        "oct",
                                        "nov",
                                        "dec",
                                    ]
                                )
                            ):
                                # Extract date part
                                parts = date_text.split(":", 1)
                                if len(parts) > 1:
                                    date_text = parts[1].strip()
                                if any(c.isdigit() for c in date_text):
                                    self.game["release_date"] = date_text
                                    logger.info(
                                        "[METACRITIC_SCRAPER] Found release_date (method 2 alt): %s",
                                        self.game["release_date"],
                                    )
                                    break

            # Method 3: Try finding in JSON-LD structured data
            if not self.game["release_date"]:
                try:
                    res = self.soup.find("script", type="application/ld+json")
                    if res and res.string:
                        js = json.loads(res.string)
                        # Check for datePublished or releaseDate
                        if "datePublished" in js:
                            self.game["release_date"] = js["datePublished"]
                            logger.info(
                                "[METACRITIC_SCRAPER] Found release_date (JSON-LD): %s",
                                self.game["release_date"],
                            )
                except Exception:
                    pass

            if not self.game["release_date"]:
                logger.warning(
                    "[METACRITIC_SCRAPER] Could not find release_date with any method"
                )
        except Exception as e:
            logger.warning(
                "Problem getting publisher and release date information: %s",
                str(e),
                exc_info=True,
            )

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
            # Method 0: Try finding in JSON-LD structured data first
            try:
                res = self.soup.find("script", type="application/ld+json")
                if res and res.string:
                    js = json.loads(res.string)
                    # Check for userRating in JSON-LD
                    if "userRating" in js:
                        user_rating = js["userRating"]
                        if isinstance(user_rating, dict):
                            rating_value = user_rating.get("ratingValue")
                            if rating_value:
                                self.game["user_score"] = str(rating_value)
                                logger.info(
                                    "[METACRITIC_SCRAPER] Found user_score (JSON-LD): %s",
                                    self.game["user_score"],
                                )
                    # Also check for aggregateRating with user reviews
                    if "aggregateRating" in js and not self.game["user_score"]:
                        # Sometimes there are multiple aggregateRating entries
                        # or user score is in a different structure
                        pass
            except Exception as e:
                logger.debug("Could not get user_score from JSON-LD: %s", str(e))

            # Method 1: Try finding in details side_details
            if not self.game["user_score"]:
                users = self.soup.find("div", class_="details side_details")
                if users:
                    # Look for metascore_w div (user score)
                    metascore = users.find("div", class_="metascore_w")
                    if metascore:
                        score_text = metascore.text.strip()
                        if score_text and score_text.lower() != "tbd":
                            self.game["user_score"] = score_text
                            logger.info(
                                "[METACRITIC_SCRAPER] Found user_score (method 1): %s",
                                self.game["user_score"],
                            )

                    # If not found, try finding all metascore divs
                    if not self.game["user_score"]:
                        user_score_divs = users.find_all(
                            "div", class_=lambda x: x and "metascore" in str(x).lower()
                        )
                        logger.info(
                            "[METACRITIC_SCRAPER] Found %d metascore divs in side_details",
                            len(user_score_divs),
                        )
                        for div in user_score_divs:
                            div_class = " ".join(div.get("class", []))
                            div_text = div.text.strip()
                            logger.info(
                                "[METACRITIC_SCRAPER] Metascore div class: %s, text: %s",
                                div_class,
                                div_text[:50],
                            )
                            # User score is usually in metascore_w (not metascore)
                            if "metascore_w" in div_class.lower() and div_text:
                                if div_text.lower() != "tbd":
                                    self.game["user_score"] = div_text
                                    logger.info(
                                        "[METACRITIC_SCRAPER] Found user_score (method 1 alt): %s",
                                        self.game["user_score"],
                                    )
                                    break

            # Method 2: Look in the main summary area
            if not self.game["user_score"]:
                summary_section = self.soup.find("div", class_="summary")
                if summary_section:
                    # Look for user score in summary
                    all_metascores = summary_section.find_all(
                        "div", class_=lambda x: x and "metascore" in str(x).lower()
                    )
                    logger.info(
                        "[METACRITIC_SCRAPER] Found %d metascore divs in summary",
                        len(all_metascores),
                    )
                    # Usually: first is critic score, second is user score
                    for i, elem in enumerate(all_metascores):
                        text = elem.text.strip()
                        elem_class = " ".join(elem.get("class", []))
                        logger.info(
                            "[METACRITIC_SCRAPER] Summary metascore[%d] class: %s, text: %s",
                            i,
                            elem_class,
                            text[:50],
                        )
                        # User score is typically in metascore_w or the second metascore
                        if (
                            ("metascore_w" in elem_class.lower() or i == 1)
                            and text
                            and text.lower() != "tbd"
                        ):
                            # Validate it's a number
                            try:
                                float(text)
                                self.game["user_score"] = text
                                logger.info(
                                    "[METACRITIC_SCRAPER] Found user_score (method 2): %s",
                                    self.game["user_score"],
                                )
                                break
                            except ValueError:
                                pass

            # Method 3: Try finding all divs with "score" in class or id
            if not self.game["user_score"]:
                # Try finding divs with "score" in class name
                score_divs = self.soup.find_all(
                    "div", class_=lambda x: x and "score" in str(x).lower()
                )
                logger.info(
                    "[METACRITIC_SCRAPER] Found %d divs with 'score' in class",
                    len(score_divs),
                )
                for elem in score_divs:
                    text = elem.text.strip()
                    elem_class = " ".join(elem.get("class", []))
                    elem_id = elem.get("id", "")
                    logger.info(
                        "[METACRITIC_SCRAPER] Score div class: %s, id: %s, text: %s",
                        elem_class,
                        elem_id,
                        text[:50],
                    )
                    # Look for user score indicators
                    if (
                        ("user" in elem_class.lower() or "user" in elem_id.lower())
                        and text
                        and text.lower() != "tbd"
                    ):
                        try:
                            score_val = float(text)
                            # User scores are typically 0-10, critic scores are 0-100
                            # But we already have critic_score, so this should be user
                            if 0 <= score_val <= 10:
                                self.game["user_score"] = text
                                logger.info(
                                    "[METACRITIC_SCRAPER] Found user_score (method 3): %s",
                                    self.game["user_score"],
                                )
                                break
                        except ValueError:
                            pass

            # Method 4: Try finding by text "User Score" or similar and nearby numbers
            if not self.game["user_score"]:
                # Look for text containing "user" and "score"
                user_score_labels = self.soup.find_all(
                    text=lambda t: t and "user" in t.lower() and "score" in t.lower()
                )
                logger.info(
                    "[METACRITIC_SCRAPER] Found %d elements with 'user score' text",
                    len(user_score_labels),
                )
                for label in user_score_labels:
                    logger.info(
                        "[METACRITIC_SCRAPER] User score label text: %s",
                        label[:100],
                    )
                    # Find parent element and look for nearby score
                    parent = label.parent
                    if parent:
                        # Look for all divs, spans, and other elements nearby
                        nearby_elements = parent.find_all(["div", "span", "a"])
                        logger.info(
                            "[METACRITIC_SCRAPER] Found %d nearby elements",
                            len(nearby_elements),
                        )
                        for elem in nearby_elements:
                            score_text = elem.text.strip()
                            elem_class = " ".join(elem.get("class", []))
                            logger.info(
                                "[METACRITIC_SCRAPER] Nearby elem class: %s, text: %s",
                                elem_class,
                                score_text[:50],
                            )
                            if score_text and score_text.lower() != "tbd":
                                try:
                                    score_val = float(score_text)
                                    # User scores are typically 0-10
                                    if 0 <= score_val <= 10:
                                        self.game["user_score"] = score_text
                                        logger.info(
                                            "[METACRITIC_SCRAPER] Found user_score (method 4): %s (near '%s')",
                                            self.game["user_score"],
                                            label[:50],
                                        )
                                        break
                                except ValueError:
                                    pass

                        # Also check siblings and parent's siblings
                        if not self.game["user_score"] and parent.parent:
                            siblings = parent.parent.find_all(["div", "span"])
                            for sibling in siblings:
                                score_text = sibling.text.strip()
                                if score_text and score_text.lower() != "tbd":
                                    try:
                                        score_val = float(score_text)
                                        if 0 <= score_val <= 10:
                                            self.game["user_score"] = score_text
                                            logger.info(
                                                "[METACRITIC_SCRAPER] Found user_score (method 4 sibling): %s",
                                                self.game["user_score"],
                                            )
                                            break
                                    except ValueError:
                                        pass

                        if self.game["user_score"]:
                            break

            # Method 5: Try finding in spans or other elements with numeric text
            if not self.game["user_score"]:
                # Look for spans with numeric text that might be user score
                all_spans = self.soup.find_all("span")
                logger.info(
                    "[METACRITIC_SCRAPER] Checking %d spans for user score",
                    len(all_spans),
                )
                for span in all_spans:
                    span_text = span.text.strip()
                    span_class = " ".join(span.get("class", []))
                    # Look for spans with "user" in class or nearby text
                    parent_text = ""
                    if span.parent:
                        parent_text = span.parent.get_text().lower()

                    if span_text and (
                        "user" in span_class.lower() or "user" in parent_text
                    ):
                        try:
                            score_val = float(span_text)
                            if 0 <= score_val <= 10:
                                self.game["user_score"] = span_text
                                logger.info(
                                    "[METACRITIC_SCRAPER] Found user_score (method 5): %s",
                                    self.game["user_score"],
                                )
                                break
                        except ValueError:
                            pass

            if not self.game["user_score"]:
                logger.warning(
                    "[METACRITIC_SCRAPER] Could not find user_score with any method"
                )

            count_span = None
            if users:
                count_span = users.find("span", class_="count")
            if count_span and count_span.a:
                raw_users_count = count_span.a.text
                user_count = ""
                for c in raw_users_count:
                    if c.isdigit():
                        user_count += c
                self.game["user_count"] = user_count.strip()
        except Exception as e:
            logger.warning(
                "Problem getting user score information: %s",
                str(e),
                exc_info=True,
            )

        # Get remaining information (developer, genre, rating)
        try:
            product_section = self.soup.find("div", class_="section product_details")
            if product_section:
                product_info = product_section.find(
                    "div", class_="details side_details"
                )
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
