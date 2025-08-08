"""Configuration-related exceptions for VideoMilker."""

from .download_errors import VideoMilkerError


class ConfigError(VideoMilkerError):
    """Base exception for configuration errors."""
    pass


class ConfigFileError(ConfigError):
    """Base exception for configuration file errors."""
    pass


class ConfigFileNotFoundError(ConfigFileError):
    """Raised when a configuration file is not found."""
    pass


class ConfigFileCorruptedError(ConfigFileError):
    """Raised when a configuration file is corrupted."""
    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails."""
    pass


class ConfigMigrationError(ConfigError):
    """Raised when configuration migration fails."""
    pass


class ConfigBackupError(ConfigError):
    """Raised when configuration backup operations fail."""
    pass


class ConfigExportError(ConfigError):
    """Raised when configuration export fails."""
    pass


class ConfigImportError(ConfigError):
    """Raised when configuration import fails."""
    pass


class ConfigPermissionError(ConfigError):
    """Raised when there are permission issues with configuration files."""
    pass


class ConfigVersionError(ConfigError):
    """Raised when there are version compatibility issues."""
    pass


class ConfigDefaultError(ConfigError):
    """Raised when default configuration creation fails."""
    pass 