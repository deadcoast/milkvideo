"""Validation-related exceptions for VideoMilker."""

from .download_errors import VideoMilkerError


class ValidationError(VideoMilkerError):
    """Base exception for validation errors."""
    pass


class URLValidationError(ValidationError):
    """Raised when URL validation fails."""
    pass


class FormatValidationError(ValidationError):
    """Raised when format validation fails."""
    pass


class PathValidationError(ValidationError):
    """Raised when path validation fails."""
    pass


class SettingsValidationError(ValidationError):
    """Raised when settings validation fails."""
    pass


class InputValidationError(ValidationError):
    """Raised when user input validation fails."""
    pass


class QualityValidationError(ValidationError):
    """Raised when quality settings validation fails."""
    pass


class TemplateValidationError(ValidationError):
    """Raised when template validation fails."""
    pass


class MetadataValidationError(ValidationError):
    """Raised when metadata validation fails."""
    pass


class BatchValidationError(ValidationError):
    """Raised when batch file validation fails."""
    pass


class FilterValidationError(ValidationError):
    """Raised when filter validation fails."""
    pass


class PostProcessingValidationError(ValidationError):
    """Raised when post-processing settings validation fails."""
    pass 