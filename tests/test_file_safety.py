"""Unit tests for file safety utilities."""

# pylint: disable=redefined-outer-name

from __future__ import annotations

import pathlib
import sys
import tempfile
from pathlib import Path

import pytest

from game_db.utils import (clean_directory_safely, get_allowed_file_extensions,
                           is_file_type_allowed, is_path_safe,
                           safe_delete_directory, safe_delete_file,
                           validate_file_name)

# Ensure project root is on sys.path when running tests directly
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def allowed_dir(temp_dir: Path) -> Path:
    """Create an allowed directory for path safety tests."""
    allowed = temp_dir / "allowed"
    allowed.mkdir()
    return allowed


class TestValidateFileName:
    """Tests for validate_file_name function."""

    def test_valid_file_names(self) -> None:
        """Test that valid file names pass validation."""
        valid_names = [
            "test.txt",
            "game.xlsx",
            "file_name-123.pdf",
            "document.doc",
            "image.jpg",
        ]
        for name in valid_names:
            assert validate_file_name(name) is True, f"{name} should be valid"

    def test_path_traversal_attempts(self) -> None:
        """Test that path traversal attempts are rejected."""
        invalid_names = [
            "../file.txt",
            "../../etc/passwd",
            "..\\file.txt",
            "file/../other.txt",
            "file\\..\\other.txt",
        ]
        for name in invalid_names:
            assert (
                validate_file_name(name) is False
            ), f"{name} should be rejected (path traversal)"

    def test_null_bytes(self) -> None:
        """Test that null bytes are rejected."""
        assert validate_file_name("file\x00.txt") is False

    def test_reserved_characters(self) -> None:
        """Test that reserved characters are rejected."""
        reserved = '<>:"|?*'
        for char in reserved:
            assert (
                validate_file_name(f"file{char}name.txt") is False
            ), f"Character '{char}' should be rejected"

    def test_empty_or_whitespace(self) -> None:
        """Test that empty or whitespace-only names are rejected."""
        assert validate_file_name("") is False
        assert validate_file_name("   ") is False
        assert validate_file_name("\t\n") is False

    def test_control_characters(self) -> None:
        """Test that control characters are rejected."""
        assert validate_file_name("file\x01name.txt") is False
        assert validate_file_name("file\x1fname.txt") is False


class TestIsPathSafe:
    """Tests for is_path_safe function."""

    def test_path_within_allowed_dir(self, allowed_dir: Path) -> None:
        """Test that paths within allowed directory are safe."""
        safe_path = allowed_dir / "subdir" / "file.txt"
        safe_path.parent.mkdir()
        safe_path.touch()

        assert is_path_safe(safe_path, allowed_dir) is True

    def test_path_outside_allowed_dir(self, allowed_dir: Path, temp_dir: Path) -> None:
        """Test that paths outside allowed directory are unsafe."""
        outside_path = temp_dir / "outside" / "file.txt"
        outside_path.parent.mkdir()
        outside_path.touch()

        assert is_path_safe(outside_path, allowed_dir) is False

    def test_path_traversal_attempt(self, allowed_dir: Path) -> None:
        """Test that path traversal attempts are detected."""
        # Create a file in allowed_dir
        safe_file = allowed_dir / "file.txt"
        safe_file.touch()

        # Try to access parent directory
        parent_file = allowed_dir.parent / "sensitive.txt"
        parent_file.touch()

        assert is_path_safe(parent_file, allowed_dir) is False

    def test_symlink_handling(self, allowed_dir: Path) -> None:
        """Test that symlinks are resolved correctly."""
        # Create a file in allowed_dir
        safe_file = allowed_dir / "file.txt"
        safe_file.touch()

        # Create a symlink (if supported)
        try:
            symlink = allowed_dir / "link.txt"
            symlink.symlink_to(safe_file)
            assert is_path_safe(symlink, allowed_dir) is True
        except (OSError, NotImplementedError):
            # Symlinks not supported on this platform
            pytest.skip("Symlinks not supported on this platform")

    def test_nonexistent_path(self, allowed_dir: Path) -> None:
        """Test that nonexistent paths are handled."""
        nonexistent = allowed_dir / "nonexistent" / "file.txt"
        # Should not raise, but may return False
        result = is_path_safe(nonexistent, allowed_dir)
        assert isinstance(result, bool)

    def test_is_path_safe_handles_os_error(
        self, allowed_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that is_path_safe returns False on OS errors."""
        target = allowed_dir / "file.txt"

        def raise_oserror(self: Path) -> Path:  # type: ignore[override]
            raise OSError("resolve failed")

        monkeypatch.setattr(Path, "resolve", raise_oserror)

        result = is_path_safe(target, allowed_dir)
        assert result is False


class TestSafeDeleteFile:
    """Tests for safe_delete_file function."""

    def test_delete_file_success(self, allowed_dir: Path) -> None:
        """Test successful file deletion."""
        test_file = allowed_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()

        result = safe_delete_file(test_file, allowed_dir)
        assert result is True
        assert not test_file.exists()

    def test_delete_file_outside_allowed_dir(
        self, allowed_dir: Path, temp_dir: Path
    ) -> None:
        """Test that files outside allowed directory cannot be deleted."""
        outside_file = temp_dir / "outside.txt"
        outside_file.write_text("content")
        assert outside_file.exists()

        result = safe_delete_file(outside_file, allowed_dir)
        assert result is False
        # File should still exist
        assert outside_file.exists()

    def test_delete_nonexistent_file(self, allowed_dir: Path) -> None:
        """Test deleting nonexistent file."""
        nonexistent = allowed_dir / "nonexistent.txt"
        result = safe_delete_file(nonexistent, allowed_dir)
        assert result is False

    def test_delete_directory_as_file(self, allowed_dir: Path) -> None:
        """Test that directories cannot be deleted as files."""
        subdir = allowed_dir / "subdir"
        subdir.mkdir()

        result = safe_delete_file(subdir, allowed_dir)
        assert result is False
        assert subdir.exists()

    def test_safe_delete_file_handles_os_error(
        self, allowed_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that safe_delete_file handles unlink errors."""
        test_file = allowed_dir / "test_error.txt"
        test_file.write_text("content")

        def raise_oserror(self: Path) -> None:  # type: ignore[override]
            raise OSError("unlink failed")

        monkeypatch.setattr(Path, "unlink", raise_oserror)

        result = safe_delete_file(test_file, allowed_dir)
        assert result is False


class TestSafeDeleteDirectory:
    """Tests for safe_delete_directory function."""

    def test_delete_directory_success(self, allowed_dir: Path) -> None:
        """Test successful directory deletion."""
        subdir = allowed_dir / "subdir"
        subdir.mkdir()
        (subdir / "file.txt").write_text("content")
        assert subdir.exists()

        result = safe_delete_directory(subdir, allowed_dir)
        assert result is True
        assert not subdir.exists()

    def test_delete_directory_outside_allowed_dir(
        self, allowed_dir: Path, temp_dir: Path
    ) -> None:
        """Test that directories outside allowed directory cannot be deleted."""
        outside_dir = temp_dir / "outside"
        outside_dir.mkdir()
        assert outside_dir.exists()

        result = safe_delete_directory(outside_dir, allowed_dir)
        assert result is False
        assert outside_dir.exists()  # Directory should still exist

    def test_delete_nonexistent_directory(self, allowed_dir: Path) -> None:
        """Test deleting nonexistent directory."""
        nonexistent = allowed_dir / "nonexistent"
        result = safe_delete_directory(nonexistent, allowed_dir)
        assert result is False

    def test_delete_directory_with_files(self, allowed_dir: Path) -> None:
        """Test deleting directory with multiple files."""
        subdir = allowed_dir / "subdir"
        subdir.mkdir()
        (subdir / "file1.txt").write_text("content1")
        (subdir / "file2.txt").write_text("content2")
        nested = subdir / "nested"
        nested.mkdir()
        (nested / "file3.txt").write_text("content3")

        result = safe_delete_directory(subdir, allowed_dir)
        assert result is True
        assert not subdir.exists()

    def test_delete_directory_path_is_file(self, allowed_dir: Path) -> None:
        """Test that safe_delete_directory returns False when path is a file."""
        file_path = allowed_dir / "file.txt"
        file_path.write_text("content")

        result = safe_delete_directory(file_path, allowed_dir)
        assert result is False

    def test_safe_delete_directory_handles_os_error(
        self, allowed_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that safe_delete_directory handles rmdir errors."""
        subdir = allowed_dir / "subdir_err"
        subdir.mkdir()

        def raise_oserror(self: Path) -> None:  # type: ignore[override]
            raise OSError("rmdir failed")

        monkeypatch.setattr(Path, "rmdir", raise_oserror)

        result = safe_delete_directory(subdir, allowed_dir)
        assert result is False


class TestCleanDirectorySafely:
    """Tests for clean_directory_safely function."""

    def test_clean_directory_removes_files(self, allowed_dir: Path) -> None:
        """Test that cleaning directory removes all files."""
        (allowed_dir / "file1.txt").write_text("content1")
        (allowed_dir / "file2.txt").write_text("content2")
        assert len(list(allowed_dir.iterdir())) == 2

        clean_directory_safely(allowed_dir, allowed_dir, keep_dirs=False)
        assert len(list(allowed_dir.iterdir())) == 0

    def test_clean_directory_removes_subdirectories(self, allowed_dir: Path) -> None:
        """Test that cleaning directory removes subdirectories."""
        subdir = allowed_dir / "subdir"
        subdir.mkdir()
        (subdir / "file.txt").write_text("content")
        assert subdir.exists()

        clean_directory_safely(allowed_dir, allowed_dir, keep_dirs=False)
        assert not subdir.exists()

    def test_clean_directory_keeps_dirs(self, allowed_dir: Path) -> None:
        """Test that cleaning with keep_dirs=True keeps subdirectories."""
        (allowed_dir / "file.txt").write_text("content")
        subdir = allowed_dir / "subdir"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("nested")

        clean_directory_safely(allowed_dir, allowed_dir, keep_dirs=True)
        assert not (allowed_dir / "file.txt").exists()  # File removed
        assert subdir.exists()  # Directory kept
        assert (subdir / "nested.txt").exists()  # Nested file kept

    def test_clean_directory_outside_allowed_dir(
        self, allowed_dir: Path, temp_dir: Path
    ) -> None:
        """Test that cleaning directory outside allowed dir does nothing."""
        outside_dir = temp_dir / "outside"
        outside_dir.mkdir()
        (outside_dir / "file.txt").write_text("content")
        assert (outside_dir / "file.txt").exists()

        clean_directory_safely(outside_dir, allowed_dir, keep_dirs=False)
        assert (outside_dir / "file.txt").exists()  # File should still exist

    def test_clean_directory_path_is_file(self, allowed_dir: Path) -> None:
        """Test that clean_directory_safely returns early when path is file."""
        file_path = allowed_dir / "file.txt"
        file_path.write_text("content")

        clean_directory_safely(file_path, allowed_dir, keep_dirs=False)
        # File should remain untouched
        assert file_path.exists()

    def test_clean_directory_handles_os_error(
        self, allowed_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that clean_directory_safely handles iteration errors."""
        subdir = allowed_dir / "subdir_err"
        subdir.mkdir()

        def raise_oserror(self: Path):  # type: ignore[override]
            raise OSError("iterdir failed")

        monkeypatch.setattr(Path, "iterdir", raise_oserror)

        # Should not raise, even though iterdir fails
        clean_directory_safely(allowed_dir, allowed_dir, keep_dirs=False)


class TestFileTypeValidation:
    """Tests for file type validation functions."""

    def test_get_allowed_extensions(self) -> None:
        """Test that allowed extensions are returned."""
        extensions = get_allowed_file_extensions()
        assert isinstance(extensions, set)
        assert ".xlsx" in extensions
        assert ".txt" in extensions
        assert ".pdf" in extensions

    def test_allowed_file_types(self) -> None:
        """Test that allowed file types pass validation."""
        allowed_files = [
            "document.xlsx",
            "file.txt",
            "image.jpg",
            "doc.pdf",
            "file.doc",
        ]
        for filename in allowed_files:
            assert (
                is_file_type_allowed(filename) is True
            ), f"{filename} should be allowed"

    def test_disallowed_file_types(self) -> None:
        """Test that disallowed file types are rejected."""
        disallowed_files = [
            "script.exe",
            "malware.bat",
            "virus.sh",
            "file.unknown",
        ]
        for filename in disallowed_files:
            assert (
                is_file_type_allowed(filename) is False
            ), f"{filename} should be rejected"

    def test_file_without_extension(self) -> None:
        """Test that files without extension are rejected."""
        assert is_file_type_allowed("file") is False
        assert is_file_type_allowed("") is False

    def test_case_insensitive_extension(self) -> None:
        """Test that extension checking is case insensitive."""
        assert is_file_type_allowed("file.XLSX") is True
        assert is_file_type_allowed("file.TXT") is True
        assert is_file_type_allowed("file.JPG") is True
