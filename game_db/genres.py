"""Metacritic genres extraction utilities (moved from parse_genres.py)."""

import logging
import time

import pandas as pd

from .config import PROJECT_ROOT
from .logging_config import configure_logging
from .MetaCriticScraper import MetaCriticScraper

logger = logging.getLogger("game_db.genres")


def extract_genre_from_metacritic(url: str) -> str | None:
    """Extract genre string from Metacritic game page using MetaCriticScraper.

    Args:
        url: URL of the Metacritic game page

    Returns:
        Genre string if found, None otherwise
    """
    try:
        scraper = MetaCriticScraper(url)
        # MetaCriticScraper stores data in scraper.game dictionary
        if scraper.game and scraper.game.get("genre"):
            genre = scraper.game["genre"].strip()
            if genre:
                return genre
        logger.warning(
            "Genre not found for URL: %s",
            url,
        )
        return None
    except Exception as e:
        logger.exception("Ошибка при обработке %s: %s", url, str(e))
        return None


def main() -> None:
    """CLI entrypoint: enrich Excel with genres from Metacritic."""
    configure_logging()
    backup_dir = PROJECT_ROOT / "backup_db"
    input_path = backup_dir / "games.xlsx"
    output_path = backup_dir / "games_with_genres.xlsx"

    logger.info("Loading Excel file: %s", input_path)
    df = pd.read_excel(str(input_path), sheet_name=0)

    completed = df[df["Завершение"] == "Пройдена"]
    completed = completed[
        completed["Metacritic"].notna()
        & completed["Metacritic"].str.contains("metacritic.com/game")
    ]

    genres: list[str | None] = []
    for i, url in enumerate(completed["Metacritic"]):
        logger.info("[%s/%s] Обработка: %s", i + 1, len(completed), url)
        genre = extract_genre_from_metacritic(url)
        genres.append(genre)
        time.sleep(1.5)

    df.loc[completed.index, "Жанр"] = genres

    df.to_excel(str(output_path), index=False)
    logger.info("Готово! Результат сохранён в %s", output_path)


if __name__ == "__main__":
    main()
