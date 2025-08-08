"""Custom exceptions for VideoMilker download operations."""


class VideoMilkerError(Exception):
    """Base exception for all VideoMilker errors."""
    pass


class DownloadError(VideoMilkerError):
    """Raised when a download operation fails."""
    pass


class FormatError(VideoMilkerError):
    """Raised when there are issues with video formats."""
    pass


class NetworkError(VideoMilkerError):
    """Raised when there are network-related issues."""
    pass


class FileError(VideoMilkerError):
    """Raised when there are file system related issues."""
    pass


class ConfigurationError(VideoMilkerError):
    """Raised when there are configuration issues."""
    pass


class ValidationError(VideoMilkerError):
    """Raised when input validation fails."""
    pass


class URLValidationError(ValidationError):
    """Raised when URL validation fails."""
    pass


class FormatSelectionError(FormatError):
    """Raised when format selection fails."""
    pass


class AuthenticationError(VideoMilkerError):
    """Raised when authentication fails."""
    pass


class RateLimitError(NetworkError):
    """Raised when rate limiting is encountered."""
    pass


class GeoRestrictionError(NetworkError):
    """Raised when content is geo-restricted."""
    pass


class AgeRestrictionError(VideoMilkerError):
    """Raised when content has age restrictions."""
    pass


class PrivateContentError(VideoMilkerError):
    """Raised when trying to access private content."""
    pass


class UnavailableContentError(VideoMilkerError):
    """Raised when content is unavailable."""
    pass


class PostProcessingError(VideoMilkerError):
    """Raised when post-processing operations fail."""
    pass


class MetadataError(VideoMilkerError):
    """Raised when metadata operations fail."""
    pass


class HistoryError(VideoMilkerError):
    """Raised when history operations fail."""
    pass


class DatabaseError(VideoMilkerError):
    """Raised when database operations fail."""
    pass


class UIError(VideoMilkerError):
    """Raised when UI operations fail."""
    pass


class CancelledError(VideoMilkerError):
    """Raised when an operation is cancelled by the user."""
    pass


class TimeoutError(VideoMilkerError):
    """Raised when an operation times out."""
    pass


class InsufficientSpaceError(FileError):
    """Raised when there's insufficient disk space."""
    pass


class PermissionError(FileError):
    """Raised when there are permission issues."""
    pass


class CorruptedFileError(FileError):
    """Raised when a downloaded file is corrupted."""
    pass


class UnsupportedFormatError(FormatError):
    """Raised when a format is not supported."""
    pass


class QualityNotAvailableError(FormatError):
    """Raised when requested quality is not available."""
    pass


class SubtitleError(VideoMilkerError):
    """Raised when subtitle operations fail."""
    pass


class ThumbnailError(VideoMilkerError):
    """Raised when thumbnail operations fail."""
    pass


class SponsorBlockError(VideoMilkerError):
    """Raised when SponsorBlock operations fail."""
    pass


class BatchProcessingError(VideoMilkerError):
    """Raised when batch processing fails."""
    pass


class QueueError(VideoMilkerError):
    """Raised when queue operations fail."""
    pass


class ProgressError(VideoMilkerError):
    """Raised when progress tracking fails."""
    pass


# Error mapping for common yt-dlp errors
YT_DLP_ERROR_MAPPING = {
    "Video unavailable": UnavailableContentError,
    "Private video": PrivateContentError,
    "Age-restricted video": AgeRestrictionError,
    "Video is private": PrivateContentError,
    "Video unavailable in your country": GeoRestrictionError,
    "This video is not available": UnavailableContentError,
    "Sign in to confirm your age": AgeRestrictionError,
    "This video is private": PrivateContentError,
    "Video unavailable": UnavailableContentError,
    "HTTP Error 403": AuthenticationError,
    "HTTP Error 404": UnavailableContentError,
    "HTTP Error 429": RateLimitError,
    "HTTP Error 503": NetworkError,
    "Connection timeout": TimeoutError,
    "Network unreachable": NetworkError,
    "No space left on device": InsufficientSpaceError,
    "Permission denied": PermissionError,
    "Access denied": PermissionError,
    "Format not available": QualityNotAvailableError,
    "No formats found": FormatError,
    "No video formats found": FormatError,
    "No audio formats found": FormatError,
}


def map_yt_dlp_error(error_message: str) -> type[VideoMilkerError]:
    """Map yt-dlp error messages to appropriate VideoMilker exceptions."""
    for pattern, exception_class in YT_DLP_ERROR_MAPPING.items():
        if pattern.lower() in error_message.lower():
            return exception_class
    
    # Default to DownloadError if no specific mapping found
    return DownloadError


def create_error_with_context(error_class: type[VideoMilkerError], message: str, 
                            url: str = "", context: dict = None) -> VideoMilkerError:
    """Create an error with additional context."""
    error = error_class(message)
    error.url = url
    error.context = context or {}
    return error


# User-friendly error messages and suggestions
USER_FRIENDLY_ERRORS = {
    UnavailableContentError: {
        "message": "This video is not available for download.",
        "suggestions": [
            "The video may have been removed or made private",
            "Check if the URL is correct",
            "Try a different video or source"
        ]
    },
    PrivateContentError: {
        "message": "This video is private and cannot be downloaded.",
        "suggestions": [
            "Private videos require authentication",
            "You may need to log in with appropriate credentials",
            "Try a public video instead"
        ]
    },
    AgeRestrictionError: {
        "message": "This video has age restrictions.",
        "suggestions": [
            "Age-restricted content requires authentication",
            "Log in with an account that meets the age requirements",
            "Try a different video without age restrictions"
        ]
    },
    GeoRestrictionError: {
        "message": "This video is not available in your region.",
        "suggestions": [
            "The content may be geo-blocked in your country",
            "Try using a VPN (if legal in your region)",
            "Look for alternative sources of the same content"
        ]
    },
    AuthenticationError: {
        "message": "Authentication failed. You may need to log in.",
        "suggestions": [
            "Check your login credentials",
            "Ensure your account has access to this content",
            "Try logging in again or use a different account"
        ]
    },
    RateLimitError: {
        "message": "Too many requests. Please wait before trying again.",
        "suggestions": [
            "Wait a few minutes before trying again",
            "Reduce the number of concurrent downloads",
            "Check your internet connection"
        ]
    },
    NetworkError: {
        "message": "Network connection failed.",
        "suggestions": [
            "Check your internet connection",
            "Try again in a few moments",
            "Verify the URL is accessible"
        ]
    },
    TimeoutError: {
        "message": "The download timed out.",
        "suggestions": [
            "Check your internet connection speed",
            "Try downloading during off-peak hours",
            "Consider downloading a lower quality version"
        ]
    },
    InsufficientSpaceError: {
        "message": "Not enough disk space for the download.",
        "suggestions": [
            "Free up space on your download drive",
            "Choose a different download location",
            "Consider downloading a lower quality version"
        ]
    },
    PermissionError: {
        "message": "Permission denied. Cannot write to the download location.",
        "suggestions": [
            "Check folder permissions",
            "Try a different download location",
            "Run the application with appropriate permissions"
        ]
    },
    QualityNotAvailableError: {
        "message": "The requested quality is not available for this video.",
        "suggestions": [
            "Try a different quality setting",
            "Use 'best' quality to get the highest available",
            "Check what formats are available for this video"
        ]
    },
    FormatError: {
        "message": "No suitable video format found.",
        "suggestions": [
            "The video may not be available in the requested format",
            "Try downloading audio only",
            "Check if the video is still available"
        ]
    },
    CorruptedFileError: {
        "message": "The downloaded file appears to be corrupted.",
        "suggestions": [
            "Try downloading again",
            "Check your internet connection",
            "Try a different quality setting"
        ]
    },
    CancelledError: {
        "message": "Download was cancelled.",
        "suggestions": [
            "You can restart the download anytime",
            "Check your settings before trying again"
        ]
    }
}


def get_user_friendly_error_message(error: VideoMilkerError) -> dict:
    """Get user-friendly error message and suggestions for an error."""
    error_type = type(error)
    
    if error_type in USER_FRIENDLY_ERRORS:
        return USER_FRIENDLY_ERRORS[error_type]
    
    # Default error message
    return {
        "message": str(error),
        "suggestions": [
            "Check the URL and try again",
            "Verify your internet connection",
            "Try a different video or source"
        ]
    }


def format_error_for_display(error: VideoMilkerError) -> str:
    """Format an error for display in the UI."""
    friendly_error = get_user_friendly_error_message(error)
    
    # Build the error message
    lines = [
        f"[bold red]Error:[/bold red] {friendly_error['message']}"
    ]
    
    if hasattr(error, 'url') and error.url:
        lines.append(f"[dim]URL: {error.url}[/dim]")
    
    if friendly_error['suggestions']:
        lines.append("")
        lines.append("[bold yellow]Suggestions:[/bold yellow]")
        for suggestion in friendly_error['suggestions']:
            lines.append(f"• {suggestion}")
    
    return "\n".join(lines) 