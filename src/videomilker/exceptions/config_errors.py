"""Configuration-related exceptions for VideoMilker."""

from .download_errors import VideoMilkerError


class ConfigError(VideoMilkerError):
    """Base exception for configuration errors."""


class ConfigFileError(ConfigError):
    """Base exception for configuration file errors."""


class ConfigFileNotFoundError(ConfigFileError):
    """Raised when a configuration file is not found."""


class ConfigFileCorruptedError(ConfigFileError):
    """Raised when a configuration file is corrupted."""


class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails."""


class ConfigMigrationError(ConfigError):
    """Raised when configuration migration fails."""


class ConfigBackupError(ConfigError):
    """Raised when configuration backup operations fail."""


class ConfigExportError(ConfigError):
    """Raised when configuration export fails."""


class ConfigImportError(ConfigError):
    """Raised when configuration import fails."""


class ConfigPermissionError(ConfigError):
    """Raised when there are permission issues with configuration files."""


class ConfigVersionError(ConfigError):
    """Raised when there are version compatibility issues."""


class ConfigDefaultError(ConfigError):
    """Raised when default configuration creation fails."""
