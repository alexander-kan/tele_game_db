"""Small utility helpers shared across the project."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger("game_db.utils")


def float_to_time(hours_float: float | str) -> str:
    """Convert hours (as float or string) to human-readable format.

    Converts a decimal number of hours to English format "X hours Y minutes".

    Args:
        hours_float: Number of hours as float or string representation.
            Examples of valid inputs:
            - Float: 1.5, 2.25, 10.75
            - String: "1.5", "2.25", "10.75", "0", "0.0"
            The function accepts any positive number (including 0).
            Negative numbers are treated as 0.

    Returns:
        String in format "X hours Y minutes" where:
        - X is the integer part (hours)
        - Y is the fractional part converted to minutes (0-59)

    Examples:
        >>> float_to_time(1.0)
        '1 hours 0 minutes'
        >>> float_to_time(1.5)
        '1 hours 30 minutes'
        >>> float_to_time(2.25)
        '2 hours 15 minutes'
        >>> float_to_time(0)
        '0 hours 0 minutes'
        >>> float_to_time("10.75")
        '10 hours 45 minutes'

    Note:
        The function uses mathematical conversion:
        - Hours = integer part of input
        - Minutes = (fractional part) * 60, rounded down
        This ensures correct conversion regardless of decimal precision.
    """
    # Convert string to float if needed
    try:
        hours_value = float(hours_float)
    except (ValueError, TypeError):
        # If conversion fails, default to 0
        hours_value = 0.0

    # Handle negative numbers by treating as 0
    if hours_value < 0:
        hours_value = 0.0

    # Extract integer hours and fractional part
    hours = int(hours_value)
    fractional_hours = hours_value - hours

    # Convert fractional hours to minutes (0-59)
    # Round down to avoid exceeding 59 minutes
    minutes = int(fractional_hours * 60)

    return f"{hours} hours {minutes} minutes"


def is_path_safe(target_path: Path, allowed_dir: Path) -> bool:
    """Check if target path is within allowed directory.

    Prevents path traversal attacks by ensuring the target path
    is a subdirectory or file within the allowed directory.

    Args:
        target_path: Path to check
        allowed_dir: Allowed base directory

    Returns:
        True if path is safe, False otherwise
    """
    try:
        # Resolve both paths to handle symlinks and relative paths
        target_resolved = target_path.resolve()
        allowed_resolved = allowed_dir.resolve()

        # Check if target is within allowed directory
        # Use commonpath to handle edge cases
        try:
            common = Path(target_resolved).relative_to(allowed_resolved)
            # Check that we don't have path traversal (no .. in resolved path)
            return ".." not in str(common)
        except ValueError:
            # Path is not relative to allowed_dir
            return False
    except (OSError, RuntimeError) as e:
        logger.warning(
            "Error checking path safety: %s -> %s: %s",
            target_path,
            allowed_dir,
            str(e),
        )
        return False


def validate_file_name(file_name: str) -> bool:
    """Validate file name for security.

    Checks for:
    - Path traversal attempts (../, ..\\)
    - Null bytes
    - Reserved characters on Windows
    - Empty or whitespace-only names

    Args:
        file_name: File name to validate

    Returns:
        True if file name is valid, False otherwise
    """
    if not file_name or not file_name.strip():
        return False

    # Check for path traversal
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        return False

    # Check for null bytes
    if "\x00" in file_name:
        return False

    # Check for reserved characters (Windows)
    reserved_chars = '<>:"|?*'
    if any(char in file_name for char in reserved_chars):
        return False

    # Check for control characters
    if any(ord(char) < 32 for char in file_name):
        return False

    return True


def safe_delete_file(file_path: Path, allowed_dir: Path) -> bool:
    """Safely delete a file after validation.

    Args:
        file_path: Path to file to delete
        allowed_dir: Directory where file must be located

    Returns:
        True if file was deleted, False otherwise
    """
    if not is_path_safe(file_path, allowed_dir):
        logger.warning(
            "Attempted to delete file outside allowed directory: %s (allowed: %s)",
            file_path,
            allowed_dir,
        )
        return False

    if not file_path.exists():
        logger.debug("File does not exist: %s", file_path)
        return False

    if not file_path.is_file():
        logger.warning("Path is not a file: %s", file_path)
        return False

    try:
        file_path.unlink()
        logger.info("Successfully deleted file: %s", file_path)
        return True
    except OSError as e:
        logger.error(
            "Failed to delete file %s: %s",
            file_path,
            str(e),
            exc_info=True,
        )
        return False


def safe_delete_directory(dir_path: Path, allowed_dir: Path) -> bool:
    """Safely delete a directory and its contents after validation.

    Args:
        dir_path: Path to directory to delete
        allowed_dir: Directory where target directory must be located

    Returns:
        True if directory was deleted, False otherwise
    """
    if not is_path_safe(dir_path, allowed_dir):
        logger.warning(
            "Attempted to delete directory outside allowed directory: %s (allowed: %s)",
            dir_path,
            allowed_dir,
        )
        return False

    if not dir_path.exists():
        logger.debug("Directory does not exist: %s", dir_path)
        return False

    if not dir_path.is_dir():
        logger.warning("Path is not a directory: %s", dir_path)
        return False

    try:
        # Delete all files and subdirectories
        for item in dir_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                # Recursively delete subdirectories
                safe_delete_directory(item, allowed_dir)

        # Remove the directory itself
        dir_path.rmdir()
        logger.info("Successfully deleted directory: %s", dir_path)
        return True
    except OSError as e:
        logger.error(
            "Failed to delete directory %s: %s",
            dir_path,
            str(e),
            exc_info=True,
        )
        return False


def clean_directory_safely(
    target_dir: Path, allowed_dir: Path, keep_dirs: bool = False
) -> None:
    """Safely clean a directory by removing all files and optionally subdirectories.

    Args:
        target_dir: Directory to clean
        allowed_dir: Directory where target_dir must be located
        keep_dirs: If True, only remove files, keep subdirectories
    """
    if not is_path_safe(target_dir, allowed_dir):
        logger.warning(
            "Attempted to clean directory outside allowed directory: %s (allowed: %s)",
            target_dir,
            allowed_dir,
        )
        return

    if not target_dir.exists():
        logger.debug("Directory does not exist: %s", target_dir)
        return

    if not target_dir.is_dir():
        logger.warning("Path is not a directory: %s", target_dir)
        return

    try:
        for item in target_dir.iterdir():
            if item.is_file():
                safe_delete_file(item, allowed_dir)
            elif item.is_dir() and not keep_dirs:
                safe_delete_directory(item, allowed_dir)
    except OSError as e:
        logger.error(
            "Failed to clean directory %s: %s",
            target_dir,
            str(e),
            exc_info=True,
        )


def get_allowed_file_extensions() -> set[str]:
    """Get set of allowed file extensions for uploads.

    Returns:
        Set of allowed file extensions (lowercase, with dot)
    """
    return {".xlsx", ".xls", ".txt", ".pdf", ".doc", ".docx", ".jpg", ".png"}


def is_file_type_allowed(file_name: str) -> bool:
    """Check if file extension is allowed.

    Args:
        file_name: Name of the file to check

    Returns:
        True if file extension is allowed, False otherwise
    """
    if not file_name:
        return False

    file_path = Path(file_name)
    extension = file_path.suffix.lower()

    if not extension:
        return False

    allowed = get_allowed_file_extensions()
    return extension in allowed
