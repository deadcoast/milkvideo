"""Custom exceptions for VideoMilker."""

from .config_errors import ConfigBackupError
from .config_errors import ConfigDefaultError
from .config_errors import ConfigError
from .config_errors import ConfigExportError
from .config_errors import ConfigFileCorruptedError
from .config_errors import ConfigFileNotFoundError
from .config_errors import ConfigImportError
from .config_errors import ConfigMigrationError
from .config_errors import ConfigPermissionError
from .config_errors import ConfigValidationError
from .config_errors import ConfigVersionError
from .download_errors import AgeRestrictionError
from .download_errors import AuthenticationError
from .download_errors import BatchProcessingError
from .download_errors import CancelledError
from .download_errors import ConfigurationError
from .download_errors import CorruptedFileError
from .download_errors import DatabaseError
from .download_errors import DownloadError
from .download_errors import FileError
from .download_errors import FormatError
from .download_errors import FormatSelectionError
from .download_errors import GeoRestrictionError
from .download_errors import HistoryError
from .download_errors import InsufficientSpaceError
from .download_errors import MetadataError
from .download_errors import NetworkError
from .download_errors import PermissionError
from .download_errors import PostProcessingError
from .download_errors import PrivateContentError
from .download_errors import ProgressError
from .download_errors import QualityNotAvailableError
from .download_errors import QueueError
from .download_errors import RateLimitError
from .download_errors import SponsorBlockError
from .download_errors import SubtitleError
from .download_errors import ThumbnailError
from .download_errors import TimeoutError
from .download_errors import UIError
from .download_errors import UnavailableContentError
from .download_errors import UnsupportedFormatError
from .download_errors import URLValidationError
from .download_errors import ValidationError
from .download_errors import VideoMilkerError
from .validation_errors import BatchValidationError
from .validation_errors import FilterValidationError
from .validation_errors import FormatValidationError
from .validation_errors import InputValidationError
from .validation_errors import MetadataValidationError
from .validation_errors import PathValidationError
from .validation_errors import PostProcessingValidationError
from .validation_errors import QualityValidationError
from .validation_errors import SettingsValidationError
from .validation_errors import TemplateValidationError
from .validation_errors import URLValidationError as URLValidationErrorBase
from .validation_errors import ValidationError as ValidationErrorBase


__all__ = [
    "AgeRestrictionError",
    "AuthenticationError",
    "BatchProcessingError",
    "BatchValidationError",
    "CancelledError",
    "ConfigBackupError",
    "ConfigDefaultError",
    "ConfigError",
    "ConfigExportError",
    "ConfigFileCorruptedError",
    "ConfigFileNotFoundError",
    "ConfigImportError",
    "ConfigMigrationError",
    "ConfigPermissionError",
    "ConfigValidationError",
    "ConfigVersionError",
    "ConfigurationError",
    "CorruptedFileError",
    "DatabaseError",
    "DownloadError",
    "FileError",
    "FilterValidationError",
    "FormatError",
    "FormatSelectionError",
    "FormatValidationError",
    "GeoRestrictionError",
    "HistoryError",
    "InputValidationError",
    "InsufficientSpaceError",
    "MetadataError",
    "MetadataValidationError",
    "NetworkError",
    "PathValidationError",
    "PermissionError",
    "PostProcessingError",
    "PostProcessingValidationError",
    "PrivateContentError",
    "ProgressError",
    "QualityNotAvailableError",
    "QualityValidationError",
    "QueueError",
    "RateLimitError",
    "SettingsValidationError",
    "SponsorBlockError",
    "SubtitleError",
    "TemplateValidationError",
    "ThumbnailError",
    "TimeoutError",
    "UIError",
    "URLValidationError",
    "URLValidationErrorBase",
    "UnavailableContentError",
    "UnsupportedFormatError",
    "ValidationError",
    "ValidationErrorBase",
    "VideoMilkerError",
]
