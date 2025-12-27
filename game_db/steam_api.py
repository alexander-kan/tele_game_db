"""Steam Web API wrapper.

This module contains a small helper class for retrieving owned games
from Steam Web API. All credentials are taken from the project
configuration (see :mod:`game_db.config`).
"""

from __future__ import annotations

import json
import logging
from typing import Optional, cast

import requests

from .config import load_tokens_config
from .types import SteamAPIResponseDict, SteamGame

logger = logging.getLogger("game_db.http")
_tokens_cfg = load_tokens_config()


class SteamAPI:
    """Small wrapper around Steam Web API to get owned games."""

    def get_all_games(self, steamid: Optional[str] = None) -> list[SteamGame]:
        """Return list of games for given SteamID.

        Args:
            steamid: Optional SteamID64 of the account. If not provided,
                the value from configuration is used.

        Returns:
            A list of SteamGame objects. On any error, an empty list is
            returned.
        """
        steam_id = steamid or _tokens_cfg.steam_id
        key = _tokens_cfg.steam_key
        host = "https://api.steampowered.com"
        path = "/IPlayerService/GetOwnedGames/v0001/?"

        url = f"{host}{path}key={key}&steamid={steam_id}&include_appinfo=true"
        try:
            logger.info("Requesting owned games for SteamID %s", steam_id)
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = cast(SteamAPIResponseDict, json.loads(response.text))
            response_data = data.get("response", {})
            games_data = response_data.get("games", [])
            game_count = response_data.get("game_count", len(games_data))

            # Log warning if API returns fewer games than reported count
            # This is a known Steam API limitation - some games (DLC, hidden games, etc.)
            # may not be returned even though they exist in the account
            if len(games_data) < game_count:
                logger.warning(
                    "[STEAM_API] API reports %d games but returned only %d. "
                    "Some games (DLC, hidden games, removed from store) may not be included.",
                    game_count,
                    len(games_data),
                )

            return [SteamGame.from_dict(game) for game in games_data]
        except requests.RequestException:
            logger.exception(
                "HTTP error while requesting Steam API for SteamID %s",
                steam_id,
            )
            return []
        except (ValueError, KeyError, TypeError):
            logger.exception(
                "Failed to parse Steam API response for SteamID %s", steam_id
            )
            return []
