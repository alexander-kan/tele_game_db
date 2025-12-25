"""User and admin security checks (moved from security_user.py)."""

from __future__ import annotations

from typing import Union

from .config import UsersConfig


class Security:
    """Check if user is allowed to use the bot and/or is admin.

    This class implements the Singleton pattern to ensure only one
    instance exists per UsersConfig, preventing redundant configuration
    loading and object creation.
    """

    _instances: dict[tuple[tuple[str, ...], tuple[str, ...]], "Security"] = {}

    def __new__(cls, users_cfg: UsersConfig) -> "Security":
        """Create or return existing Security instance for given config.

        Args:
            users_cfg: Users configuration to use

        Returns:
            Security instance (singleton per UsersConfig)
        """
        # Use tuple of (users tuple, admins tuple) as key for singleton lookup
        # This allows different Security instances for different configs
        key = (tuple(users_cfg.users), tuple(users_cfg.admins))
        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance
        return cls._instances[key]

    def __init__(self, users_cfg: UsersConfig) -> None:
        """Initialize Security with users configuration.

        Args:
            users_cfg: Users configuration to use
        """
        # Only set users_cfg if not already initialized
        if not hasattr(self, "users_cfg"):
            self.users_cfg = users_cfg

    def user_check(self, user_id: Union[int, str]) -> bool:
        """Return True if user is allowed to use bot."""
        return str(user_id) in self.users_cfg.users

    def admin_check(self, user_id: Union[int, str]) -> bool:
        """Return True if user is admin."""
        return str(user_id) in self.users_cfg.admins

    @classmethod
    def clear_instances(cls) -> None:
        """Clear all cached Security instances.

        Useful for testing or when configuration changes.
        """
        cls._instances.clear()
