"""Default configuration values for VideoMilker."""

from pathlib import Path

# Default configuration structure
DEFAULT_CONFIG = {
    "version": "1.0.0",
    "download": {
        "path": str(Path.home() / "Downloads" / "VideoMilker"),
        "create_day_folders": True,
        "file_naming": "%(upload_date)s_%(title)s",
        "default_quality": "best",
        "default_format": "mp4",
        "max_concurrent": 3,
        "auto_subtitle": False,
        "save_thumbnail": False,
        "embed_metadata": True,
        "write_description": False,
        "write_info_json": True,
        "restrict_filenames": True,
        "continue_download": True,
        "retries": 10,
        "fragment_retries": 10,
        "socket_timeout": 30,
        "retry_sleep": 1,
        "max_sleep_interval": 10,
        "sleep_interval": 1,
        "sleep_requests": 0.75,
        "sleep_subtitles": 5
    },
    "ui": {
        "theme": "default",
        "show_progress_details": True,
        "confirm_before_quit": True,
        "clear_screen": True,
        "color_output": True,
        "show_eta": True,
        "show_speed": True,
        "show_size": True,
        "progress_bar_style": "bar",
        "menu_style": "rounded",
        "border_style": "blue",
        "highlight_style": "yellow",
        "error_style": "red",
        "success_style": "green",
        "warning_style": "yellow",
        "auto_download": False
    },
    "history": {
        "max_entries": 1000,
        "auto_cleanup": True,
        "cleanup_days": 30,
        "save_download_logs": True,
        "log_level": "INFO",
        "database_path": "history.db",
        "export_format": "json"
    },
    "advanced": {
        "use_cookies": False,
        "cookies_file": "",
        "proxy": "",
        "geo_verification_proxy": "",
        "xff": "default",
        "impersonate": "",
        "force_ipv4": False,
        "force_ipv6": False,
        "prefer_insecure": False,
        "no_check_certificates": False,
        "legacy_server_connect": False,
        "add_headers": [],
        "sleep_requests": 0.75,
        "sleep_interval": 1,
        "max_sleep_interval": 10,
        "sleep_subtitles": 5
    },
    "formats": {
        "video_formats": ["mp4", "mkv", "webm", "avi", "mov"],
        "audio_formats": ["m4a", "mp3", "opus", "aac", "flac"],
        "preferred_video_codec": "h264",
        "preferred_audio_codec": "aac",
        "max_resolution": "1080p",
        "min_resolution": "360p",
        "prefer_free_formats": True,
        "check_formats": True
    },
    "post_processing": {
        "extract_audio": False,
        "audio_format": "m4a",
        "audio_quality": 5,
        "embed_thumbnail": False,
        "embed_subs": False,
        "convert_subs": "srt",
        "split_chapters": False,
        "remove_chapters": [],
        "sponsorblock_mark": [],
        "sponsorblock_remove": [],
        "sponsorblock_chapter_title": "[SponsorBlock]: %(category_names)l"
    }
}

# Platform-specific defaults
def get_platform_defaults():
    """Get platform-specific default settings."""
    import platform
    
    system = platform.system().lower()
    
    if system == "windows":
        return {
            "download": {
                "path": str(Path.home() / "Downloads" / "VideoMilker"),
                "restrict_filenames": True,
                "windows_filenames": True
            }
        }
    elif system == "darwin":  # macOS
        return {
            "download": {
                "path": str(Path.home() / "Downloads" / "VideoMilker"),
                "restrict_filenames": False
            }
        }
    else:  # Linux/Unix
        return {
            "download": {
                "path": str(Path.home() / "Downloads" / "VideoMilker"),
                "restrict_filenames": False
            }
        }

# Theme configurations
THEMES = {
    "default": {
        "border_style": "blue",
        "highlight_style": "yellow",
        "error_style": "red",
        "success_style": "green",
        "warning_style": "yellow",
        "info_style": "cyan",
        "menu_style": "rounded"
    },
    "dark": {
        "border_style": "bright_blue",
        "highlight_style": "bright_yellow",
        "error_style": "bright_red",
        "success_style": "bright_green",
        "warning_style": "bright_yellow",
        "info_style": "bright_cyan",
        "menu_style": "double"
    },
    "light": {
        "border_style": "black",
        "highlight_style": "black",
        "error_style": "red",
        "success_style": "green",
        "warning_style": "yellow",
        "info_style": "blue",
        "menu_style": "single"
    },
    "minimal": {
        "border_style": "dim",
        "highlight_style": "white",
        "error_style": "red",
        "success_style": "green",
        "warning_style": "yellow",
        "info_style": "dim",
        "menu_style": "none"
    }
}

# File naming templates
FILE_NAMING_TEMPLATES = {
    "simple": "%(title)s.%(ext)s",
    "with_date": "%(upload_date)s_%(title)s.%(ext)s",
    "with_id": "%(title)s [%(id)s].%(ext)s",
    "full_info": "%(upload_date)s_%(uploader)s_%(title)s [%(id)s].%(ext)s",
    "playlist": "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s",
    "channel": "%(uploader)s/%(upload_date)s_%(title)s.%(ext)s"
}

# Quality presets
QUALITY_PRESETS = {
    "best": "bestvideo+bestaudio/best",
    "worst": "worstvideo+worstaudio/worst",
    "720p": "best[height<=720]/best",
    "1080p": "best[height<=1080]/best",
    "audio_only": "bestaudio/best",
    "video_only": "bestvideo/best"
}

# Format presets
FORMAT_PRESETS = {
    "mp4": {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_format": "mp4"
    },
    "mkv": {
        "format": "bestvideo+bestaudio/best",
        "merge_format": "mkv"
    },
    "webm": {
        "format": "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best",
        "merge_format": "webm"
    }
} 