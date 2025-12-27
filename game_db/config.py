"""Central configuration module for paths and settings.

All paths and magic constants should be defined here instead of being
hardcoded across the codebase.
"""

from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path
from typing import Final, cast

from .types import SettingsINIDict, TokensINIDict, UsersINIDict

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent

# Fallback list of platforms if database is unavailable
# This should match the platforms in platform_dictionary table
DEFAULT_PLATFORMS: Final[list[str]] = [
    "PC GOG",
    "PC Origin",
    "PS Vita",
    "PS4",
    "PS5",
    "Steam",
    "Switch",
]


@dataclass(frozen=True)
class Paths:
    """Filesystem paths used by the application."""

    backup_dir: Path
    update_db_dir: Path
    files_dir: Path
    sql_root: Path
    sqlite_db_file: Path
    games_excel_file: Path


@dataclass(frozen=True)
class DBFilesConfig:
    """Paths to SQL scripts and main SQLite DB file."""

    sql_games: Path
    sql_games_on_platforms: Path
    sql_dictionaries: Path
    sql_drop_tables: Path
    sql_create_tables: Path
    sqlite_db_file: Path


@dataclass(frozen=True)
class SettingsConfig:
    """Configuration values loaded from settings/settings.ini."""

    paths: Paths
    db_files: DBFilesConfig
    owner_name: str


@dataclass(frozen=True)
class TokensConfig:
    """Secrets and external API tokens."""

    telegram_token: str
    steam_key: str
    steam_id: str


@dataclass(frozen=True)
class UsersConfig:
    """Users and admins configuration."""

    users: list[str]
    admins: list[str]


@dataclass(frozen=True)
class SimilarityThresholdsConfig:
    """Similarity search thresholds configuration."""

    # Length thresholds
    short_length_max: int = 5
    medium_length_max: int = 12

    # Distance thresholds
    short_length_distance: int = 1
    medium_length_distance: int = 2
    long_length_distance: int = 3

    # Score thresholds
    medium_length_score: float = 0.80
    long_length_score: float = 0.85

    # Pre-filtering
    length_diff_threshold: int = 3


def load_similarity_thresholds_config() -> SimilarityThresholdsConfig:
    """Load similarity thresholds configuration.

    Returns default values if not configured.
    """
    # For now, return defaults. Can be extended to load from INI file.
    return SimilarityThresholdsConfig()


def _load_ini(relative_path: str) -> configparser.ConfigParser:
    """Load an INI file from the settings directory."""
    parser = configparser.ConfigParser()
    settings_path = PROJECT_ROOT / "settings" / relative_path
    parser.read(settings_path)
    return parser


def load_settings_config() -> SettingsConfig:
    """Load general project settings (paths, DB file, SQL files)."""
    settings = _load_ini("settings.ini")
    files_section = cast(SettingsINIDict, dict(settings["FILES"]))

    backup_dir = PROJECT_ROOT / "backup_db"
    update_db_dir = PROJECT_ROOT / "update_db"
    files_dir = PROJECT_ROOT / "files"
    sql_root = PROJECT_ROOT / "sql_querry"

    sqlite_db_file = PROJECT_ROOT / files_section["sqlite_db_file"]
    games_excel_file = backup_dir / "games.xlsx"

    db_files = DBFilesConfig(
        sql_games=PROJECT_ROOT / files_section["sql_games"],
        sql_games_on_platforms=PROJECT_ROOT / files_section["sql_games_on_platforms"],
        sql_dictionaries=PROJECT_ROOT / files_section["sql_dictionaries"],
        sql_drop_tables=PROJECT_ROOT / files_section["sql_drop_tables"],
        sql_create_tables=PROJECT_ROOT / files_section["sql_create_tables"],
        sqlite_db_file=sqlite_db_file,
    )

    paths = Paths(
        backup_dir=backup_dir,
        update_db_dir=update_db_dir,
        files_dir=files_dir,
        sql_root=sql_root,
        sqlite_db_file=sqlite_db_file,
        games_excel_file=games_excel_file,
    )

    # Load owner name from OWNER section, default to "Alexander"
    owner_name = "Alexander"
    if settings.has_section("OWNER"):
        owner_name = settings.get("OWNER", "owner_name", fallback="Alexander")

    return SettingsConfig(paths=paths, db_files=db_files, owner_name=owner_name)


def load_tokens_config() -> TokensConfig:
    """Load tokens and external API credentials."""
    tokens = _load_ini("t_token.ini")
    token_section = cast(TokensINIDict, dict(tokens["token"]))
    return TokensConfig(
        telegram_token=token_section["token"],
        steam_key=token_section["steam_key"],
        steam_id=token_section["steam_id"],
    )


def load_users_config() -> UsersConfig:
    """Load users and admins configuration."""
    users_cfg = _load_ini("users.ini")
    users_section = cast(UsersINIDict, dict(users_cfg["users"]))
    users_raw = users_section.get("users", "")
    admins_raw = users_section.get("admins", "")
    users = users_raw.split() if users_raw else []
    admins = admins_raw.split() if admins_raw else []
    return UsersConfig(users=users, admins=admins)


def load_table_names_config() -> configparser.ConfigParser:
    """Load table names mapping configuration."""
    return _load_ini("table_names.ini")


def load_column_table_names_config() -> configparser.ConfigParser:
    """Load column-to-table mapping configuration."""
    return _load_ini("column_table_names.ini")


def load_values_dictionaries_config() -> configparser.ConfigParser:
    """Load values dictionaries configuration."""
    return _load_ini("values_dictionaries.ini")
