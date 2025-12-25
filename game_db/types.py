"""Type definitions for domain models and API responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple, TypedDict


class SteamGame(NamedTuple):
    """Represents a game from Steam API response."""

    appid: int
    name: str
    playtime_forever: int
    img_icon_url: str
    img_logo_url: str
    has_community_visible_stats: bool | None
    playtime_windows_forever: int | None
    playtime_mac_forever: int | None
    playtime_linux_forever: int | None
    rtime_last_played: int | None

    @classmethod
    def from_dict(cls, data: dict[str, object] | SteamGameDict) -> SteamGame:
        """Create SteamGame from Steam API response dictionary."""
        appid_val = data.get("appid", 0)
        playtime_val = data.get("playtime_forever", 0)
        return cls(
            appid=int(appid_val) if isinstance(appid_val, (int, str)) else 0,
            name=str(data.get("name", "")),
            playtime_forever=int(playtime_val) if isinstance(playtime_val, (int, str)) else 0,
            img_icon_url=str(data.get("img_icon_url", "")),
            img_logo_url=str(data.get("img_logo_url", "")),
            has_community_visible_stats=(
                data.get("has_community_visible_stats")
                if isinstance(data.get("has_community_visible_stats"), (bool, type(None)))
                else None
            ),
            playtime_windows_forever=(
                data.get("playtime_windows_forever")
                if isinstance(data.get("playtime_windows_forever"), (int, type(None)))
                else None
            ),
            playtime_mac_forever=(
                data.get("playtime_mac_forever")
                if isinstance(data.get("playtime_mac_forever"), (int, type(None)))
                else None
            ),
            playtime_linux_forever=(
                data.get("playtime_linux_forever")
                if isinstance(data.get("playtime_linux_forever"), (int, type(None)))
                else None
            ),
            rtime_last_played=(
                data.get("rtime_last_played")
                if isinstance(data.get("rtime_last_played"), (int, type(None)))
                else None
            ),
        )


@dataclass(frozen=True)
class GameInfo:
    """Represents a game from database query result."""

    game_name: str
    status: str
    platforms: str
    press_score: str | None
    average_time_beat: str | None
    user_score: str | None
    my_score: str | None
    metacritic_url: str | None
    trailer_url: str | None
    my_time_beat: str | None
    last_launch_date: str | None

    @classmethod
    def from_tuple(cls, row: tuple) -> GameInfo:
        """Create GameInfo from database query tuple."""
        return cls(
            game_name=str(row[0]),
            status=str(row[1]),
            platforms=str(row[2]),
            press_score=str(row[3]) if row[3] is not None else None,
            average_time_beat=str(row[4]) if row[4] is not None else None,
            user_score=str(row[5]) if row[5] is not None else None,
            my_score=str(row[6]) if row[6] is not None else None,
            metacritic_url=str(row[7]) if row[7] is not None else None,
            trailer_url=str(row[8]) if row[8] is not None else None,
            my_time_beat=str(row[9]) if row[9] is not None else None,
            last_launch_date=str(row[10]) if row[10] is not None else None,
        )


@dataclass(frozen=True)
class GameListItem:
    """Represents a game in a list (simplified info)."""

    game_name: str
    press_score: str | None
    average_time_beat: str | None
    trailer_url: str | None

    @classmethod
    def from_tuple(cls, row: tuple) -> GameListItem:
        """Create GameListItem from database query tuple."""
        return cls(
            game_name=str(row[0]),
            press_score=str(row[1]) if row[1] is not None else None,
            average_time_beat=str(row[2]) if row[2] is not None else None,
            trailer_url=str(row[3]) if row[3] is not None else None,
        )


# TypedDict for INI configuration files


class SettingsINIDict(TypedDict):
    """TypedDict for settings.ini [FILES] section."""

    sql_games: str
    sql_games_on_platforms: str
    sql_dictionaries: str
    sql_drop_tables: str
    sql_create_tables: str
    sqlite_db_file: str


class TokensINIDict(TypedDict):
    """TypedDict for t_token.ini [token] section."""

    token: str
    steam_key: str
    steam_id: str


class UsersINIDict(TypedDict):
    """TypedDict for users.ini [users] section."""

    users: str  # Space-separated list
    admins: str  # Space-separated list


# TypedDict for Steam API responses


class SteamGameDict(TypedDict, total=False):
    """TypedDict for a single game in Steam API response.

    All fields except appid and name are optional in the API response.
    Use total=False to make all fields optional except those explicitly
    required.
    """

    appid: int  # Required
    name: str  # Required
    playtime_forever: int
    img_icon_url: str
    img_logo_url: str
    has_community_visible_stats: bool
    playtime_windows_forever: int
    playtime_mac_forever: int
    playtime_linux_forever: int
    rtime_last_played: int


class SteamAPIResponseDict(TypedDict):
    """TypedDict for Steam API GetOwnedGames response structure."""

    response: dict[str, list[SteamGameDict]]


# TypedDict for Excel row data


class ExcelGameRowDict(TypedDict, total=False):
    """TypedDict for a single game row from Excel file.

    This represents the raw data structure when reading from Excel,
    before conversion to GameRow dataclass.
    """

    game_name: str
    platforms: str
    status: str
    release_date: str
    press_score: str | None
    user_score: str | None
    my_score: str | None
    metacritic_url: str | None
    average_time_beat: str | None
    trailer_url: str | None
    my_time_beat: str | None
    last_launch_date: str | None
    additional_time: str | None
