"""Input handling for VideoMilker CLI."""

import re
from pathlib import Path
from typing import List
from typing import Optional


class InputHandler:
    """Handles user input processing and validation."""

    def __init__(self):
        """Initialize the input handler."""
        pass

    def validate_url(self, url: str) -> bool:
        """Validate if a URL is properly formatted."""
        if not url or not url.strip():
            return False

        # Basic URL validation
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        return bool(url_pattern.match(url))

    def validate_path(self, path: str) -> bool:
        """Validate if a path is valid."""
        try:
            Path(path).expanduser()
            return True
        except Exception:
            return False

    def validate_filename(self, filename: str) -> bool:
        """Validate if a filename is valid."""
        if not filename or not filename.strip():
            return False

        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        return all(char not in filename for char in invalid_chars)

    def parse_urls_from_text(self, text: str) -> List[str]:
        """Parse URLs from text input."""
        urls = []

        # Split by lines and extract URLs
        lines = text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):  # Skip comments
                # Extract URLs from the line
                url_matches = re.findall(r"https?://[^\s]+", line)
                urls.extend(url_matches)

        return list(set(urls))  # Remove duplicates

    def parse_batch_file(self, file_path: Path) -> List[str]:
        """Parse URLs from a batch file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return self.parse_urls_from_text(content)

        except Exception as e:
            raise ValueError(f"Failed to read batch file: {e}") from e

    def sanitize_input(self, input_text: str) -> str:
        """Sanitize user input."""
        if not input_text:
            return ""

        # Remove control characters
        sanitized = re.sub(r"[\x00-\x1f\x7f]", "", input_text)

        # Trim whitespace
        sanitized = sanitized.strip()

        return sanitized

    def parse_quality_setting(self, quality: str) -> Optional[str]:
        """Parse and validate quality setting."""
        valid_qualities = [
            "best",
            "worst",
            "720p",
            "1080p",
            "480p",
            "360p",
            "audio_only",
            "video_only",
            "bestvideo",
            "bestaudio",
        ]

        quality_lower = quality.lower()
        return quality_lower if quality_lower in valid_qualities else None

    def parse_format_setting(self, format_str: str) -> Optional[str]:
        """Parse and validate format setting."""
        valid_formats = ["mp4", "mkv", "webm", "avi", "mov", "m4a", "mp3", "opus", "aac", "flac"]

        format_lower = format_str.lower()
        return format_lower if format_lower in valid_formats else None

    def parse_number_input(
        self, input_text: str, min_value: Optional[int] = None, max_value: Optional[int] = None
    ) -> Optional[int]:
        """Parse and validate numeric input."""
        try:
            value = int(input_text.strip())

            if min_value is not None and value < min_value:
                return None

            return None if max_value is not None and value > max_value else value
        except ValueError:
            return None

    def parse_boolean_input(self, input_text: str) -> Optional[bool]:
        """Parse boolean input."""
        input_lower = input_text.lower().strip()

        true_values = ["yes", "y", "true", "1", "on"]
        false_values = ["no", "n", "false", "0", "off"]

        if input_lower in true_values:
            return True
        elif input_lower in false_values:
            return False

        return None

    def parse_list_input(self, input_text: str, separator: str = ",") -> List[str]:
        """Parse list input separated by a delimiter."""
        if not input_text:
            return []

        items = [item.strip() for item in input_text.split(separator)]
        return [item for item in items if item]  # Remove empty items

    def validate_file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        try:
            return Path(file_path).expanduser().exists()
        except Exception:
            return False

    def validate_directory_exists(self, dir_path: str) -> bool:
        """Check if a directory exists."""
        try:
            path = Path(dir_path).expanduser()
            return path.exists() and path.is_dir()
        except Exception:
            return False

    def suggest_filename(self, title: str, extension: str = "mp4") -> str:
        """Suggest a filename based on title."""
        if not title:
            return f"video.{extension}"

        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', "_", title)

        # Limit length
        if len(filename) > 100:
            filename = filename[:100]

        # Add extension if not present
        if not filename.endswith(f".{extension}"):
            filename = f"{filename}.{extension}"

        return filename

    def parse_time_input(self, time_input: str) -> Optional[int]:
        """Parse time input (e.g., '1h 30m 45s' or '5400') into seconds."""
        if not time_input:
            return None

        time_input = time_input.strip().lower()

        # Try to parse as seconds first
        try:
            return int(time_input)
        except ValueError:
            pass

        # Parse time format (e.g., "1h 30m 45s")
        total_seconds = 0

        if hour_match := re.search(r"(\d+)h", time_input):
            total_seconds += int(hour_match[1]) * 3600

        if minute_match := re.search(r"(\d+)m", time_input):
            total_seconds += int(minute_match[1]) * 60

        if second_match := re.search(r"(\d+)s", time_input):
            total_seconds += int(second_match[1])

        return total_seconds if total_seconds > 0 else None

    def format_time(self, seconds: int) -> str:
        """Format seconds into a human-readable time string."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes, remaining_seconds = divmod(seconds, 60)
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            remaining_seconds = seconds % 60
            return f"{hours}h {remaining_minutes}m {remaining_seconds}s"

    def format_file_size(self, bytes_size: int) -> str:
        """Format bytes into a human-readable file size."""
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"
