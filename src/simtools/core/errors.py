"""Domain errors for SimTools."""


class SimToolsError(Exception):
    """Base exception for SimTools."""


class ConfigError(SimToolsError):
    """Raised when config or manifest data is invalid."""


class ToolNotFoundError(SimToolsError):
    """Raised when a requested tool id is not in the registry."""
