"""Tests for security module."""

from __future__ import annotations

from game_db.config import UsersConfig
from game_db.security import Security


class TestSecurity:
    """Test Security class functionality."""

    def test_user_check_allowed_user(self) -> None:
        """Test user_check returns True for allowed user."""
        users_cfg = UsersConfig(users=["12345", "67890"], admins=["12345"])
        security = Security(users_cfg)

        assert security.user_check("12345") is True
        assert security.user_check(12345) is True  # int should work too
        assert security.user_check("67890") is True

    def test_user_check_denied_user(self) -> None:
        """Test user_check returns False for denied user."""
        users_cfg = UsersConfig(users=["12345"], admins=["12345"])
        security = Security(users_cfg)

        assert security.user_check("99999") is False
        assert security.user_check(99999) is False

    def test_admin_check_admin_user(self) -> None:
        """Test admin_check returns True for admin user."""
        users_cfg = UsersConfig(users=["12345", "67890"], admins=["12345"])
        security = Security(users_cfg)

        assert security.admin_check("12345") is True
        assert security.admin_check(12345) is True

    def test_admin_check_non_admin_user(self) -> None:
        """Test admin_check returns False for non-admin user."""
        users_cfg = UsersConfig(users=["12345", "67890"], admins=["12345"])
        security = Security(users_cfg)

        assert security.admin_check("67890") is False
        assert security.admin_check(67890) is False

    def test_admin_check_unauthorized_user(self) -> None:
        """Test admin_check returns False for unauthorized user."""
        users_cfg = UsersConfig(users=["12345"], admins=["12345"])
        security = Security(users_cfg)

        assert security.admin_check("99999") is False

    def test_singleton_same_config(self) -> None:
        """Test that Security is singleton for same config."""
        users_cfg1 = UsersConfig(users=["12345"], admins=["12345"])
        users_cfg2 = UsersConfig(users=["12345"], admins=["12345"])

        security1 = Security(users_cfg1)
        security2 = Security(users_cfg2)

        assert security1 is security2

    def test_singleton_different_config(self) -> None:
        """Test that Security creates different instances for different configs."""
        users_cfg1 = UsersConfig(users=["12345"], admins=["12345"])
        users_cfg2 = UsersConfig(users=["67890"], admins=["67890"])

        security1 = Security(users_cfg1)
        security2 = Security(users_cfg2)

        assert security1 is not security2

    def test_singleton_different_users_same_admins(self) -> None:
        """Test that different user lists create different instances."""
        users_cfg1 = UsersConfig(users=["12345"], admins=["admin"])
        users_cfg2 = UsersConfig(users=["67890"], admins=["admin"])

        security1 = Security(users_cfg1)
        security2 = Security(users_cfg2)

        assert security1 is not security2

    def test_clear_instances(self) -> None:
        """Test that clear_instances clears singleton cache."""
        users_cfg = UsersConfig(users=["12345"], admins=["12345"])

        security1 = Security(users_cfg)
        Security.clear_instances()
        security2 = Security(users_cfg)

        # After clearing, should be different instances
        assert security1 is not security2

    def test_empty_users_list(self) -> None:
        """Test Security with empty users list."""
        users_cfg = UsersConfig(users=[], admins=[])
        security = Security(users_cfg)

        assert security.user_check("12345") is False
        assert security.admin_check("12345") is False

    def test_empty_admins_list(self) -> None:
        """Test Security with empty admins list but non-empty users."""
        users_cfg = UsersConfig(users=["12345"], admins=[])
        security = Security(users_cfg)

        assert security.user_check("12345") is True
        assert security.admin_check("12345") is False
