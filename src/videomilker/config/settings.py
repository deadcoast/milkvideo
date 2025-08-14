"""Configuration settings for VideoMilker."""

import json
from pathlib import Path
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class DownloadSettings(BaseModel):
    """Download configuration settings."""

    path: str = Field(default="~/Downloads/VideoMilker", description="Download directory")
    create_day_folders: bool = Field(default=True, description="Organize files by date")
    file_naming: str = Field(default="%(upload_date)s_%(title)s.%(ext)s", description="File naming pattern")
    default_quality: str = Field(default="best", description="Default video quality")
    default_format: str = Field(default="mp4", description="Default video format")
    max_concurrent: int = Field(default=3, description="Maximum concurrent downloads")
    auto_subtitle: bool = Field(default=False, description="Automatically download subtitles")
    save_thumbnail: bool = Field(default=False, description="Save video thumbnails")
    embed_metadata: bool = Field(default=True, description="Embed metadata in files")
    write_description: bool = Field(default=False, description="Write video description to file")
    write_info_json: bool = Field(default=True, description="Write video metadata to JSON")
    restrict_filenames: bool = Field(default=True, description="Restrict filenames to ASCII")
    continue_download: bool = Field(default=True, description="Continue partial downloads")
    retries: int = Field(default=10, description="Number of retries")
    fragment_retries: int = Field(default=10, description="Fragment retries")
    socket_timeout: int = Field(default=30, description="Socket timeout in seconds")
    retry_sleep: int = Field(default=1, description="Sleep between retries")
    max_sleep_interval: int = Field(default=10, description="Maximum sleep interval")
    sleep_interval: int = Field(default=1, description="Sleep interval")
    sleep_requests: float = Field(default=0.75, description="Sleep between requests")
    sleep_subtitles: int = Field(default=5, description="Sleep before subtitle download")


class UISettings(BaseModel):
    """UI configuration settings."""

    theme: str = Field(default="default", description="UI theme")
    show_progress_details: bool = Field(default=True, description="Show detailed progress")
    confirm_before_quit: bool = Field(default=True, description="Confirm before quitting")
    clear_screen: bool = Field(default=True, description="Clear screen on startup")
    color_output: bool = Field(default=True, description="Enable colored output")
    show_eta: bool = Field(default=True, description="Show estimated time remaining")
    show_speed: bool = Field(default=True, description="Show download speed")
    show_size: bool = Field(default=True, description="Show file size")
    progress_bar_style: str = Field(default="bar", description="Progress bar style")
    menu_style: str = Field(default="rounded", description="Menu border style")
    border_style: str = Field(default="blue", description="Border color")
    highlight_style: str = Field(default="yellow", description="Highlight color")
    error_style: str = Field(default="red", description="Error color")
    success_style: str = Field(default="green", description="Success color")
    warning_style: str = Field(default="yellow", description="Warning color")
    auto_download: bool = Field(default=False, description="Automatically start downloads without confirmation")


class HistorySettings(BaseModel):
    """History configuration settings."""

    max_entries: int = Field(default=1000, description="Maximum history entries")
    auto_cleanup: bool = Field(default=True, description="Auto-cleanup old entries")
    cleanup_days: int = Field(default=30, description="Days to keep history")
    save_download_logs: bool = Field(default=True, description="Save download logs")
    log_level: str = Field(default="INFO", description="Logging level")
    database_path: str = Field(default="history.db", description="Database file path")
    export_format: str = Field(default="json", description="Export format")


class AdvancedSettings(BaseModel):
    """Advanced configuration settings."""

    use_cookies: bool = Field(default=False, description="Use cookies for authentication")
    cookies_file: str = Field(default="", description="Path to cookies file")
    proxy: str = Field(default="", description="Proxy URL")
    geo_verification_proxy: str = Field(default="", description="Geo verification proxy")
    xff: str = Field(default="default", description="X-Forwarded-For header")
    impersonate: str = Field(default="", description="Browser impersonation")
    force_ipv4: bool = Field(default=False, description="Force IPv4 connections")
    force_ipv6: bool = Field(default=False, description="Force IPv6 connections")
    prefer_insecure: bool = Field(default=False, description="Prefer insecure connections")
    no_check_certificates: bool = Field(default=False, description="Skip certificate validation")
    legacy_server_connect: bool = Field(default=False, description="Allow legacy server connections")
    add_headers: List[str] = Field(default_factory=list, description="Additional HTTP headers")

    # Authentication settings for age-restricted content
    twitter_auth: bool = Field(default=False, description="Enable Twitter authentication")
    twitter_cookies_file: str = Field(default="", description="Path to Twitter cookies file")
    youtube_auth: bool = Field(default=False, description="Enable YouTube authentication")
    youtube_cookies_file: str = Field(default="", description="Path to YouTube cookies file")
    instagram_auth: bool = Field(default=False, description="Enable Instagram authentication")
    instagram_cookies_file: str = Field(default="", description="Path to Instagram cookies file")

    # Age verification settings
    age_verification: bool = Field(default=False, description="Enable age verification")
    age_verification_method: str = Field(default="cookies", description="Age verification method")

    # Browser impersonation for authentication
    browser_impersonation: str = Field(default="chrome", description="Browser to impersonate")
    user_agent: str = Field(default="", description="Custom user agent string")


class FormatSettings(BaseModel):
    """Format configuration settings."""

    video_formats: List[str] = Field(default_factory=lambda: ["mp4", "mkv", "webm", "avi", "mov"])
    audio_formats: List[str] = Field(default_factory=lambda: ["m4a", "mp3", "opus", "aac", "flac"])
    preferred_video_codec: str = Field(default="h264", description="Preferred video codec")
    preferred_audio_codec: str = Field(default="aac", description="Preferred audio codec")
    max_resolution: str = Field(default="1080p", description="Maximum resolution")
    min_resolution: str = Field(default="360p", description="Minimum resolution")
    prefer_free_formats: bool = Field(default=True, description="Prefer free formats")
    check_formats: bool = Field(default=True, description="Check format availability")


class PostProcessingSettings(BaseModel):
    """Post-processing configuration settings."""

    extract_audio: bool = Field(default=False, description="Extract audio from video")
    audio_format: str = Field(default="m4a", description="Audio format for extraction")
    audio_quality: int = Field(default=5, description="Audio quality (0-10)")
    embed_thumbnail: bool = Field(default=False, description="Embed thumbnail in file")
    embed_subs: bool = Field(default=False, description="Embed subtitles in file")
    convert_subs: str = Field(default="srt", description="Subtitle conversion format")
    split_chapters: bool = Field(default=False, description="Split video by chapters")
    remove_chapters: List[str] = Field(default_factory=list, description="Chapters to remove")
    sponsorblock_mark: List[str] = Field(default_factory=list, description="SponsorBlock categories to mark")
    sponsorblock_remove: List[str] = Field(default_factory=list, description="SponsorBlock categories to remove")
    sponsorblock_chapter_title: str = Field(
        default="[SponsorBlock]: %(category_names)l", description="SponsorBlock chapter title template"
    )


class Settings(BaseModel):
    """Main application settings."""

    version: str = Field(default="1.0.0", description="Settings version")
    download: DownloadSettings = Field(default_factory=DownloadSettings)
    ui: UISettings = Field(default_factory=UISettings)
    history: HistorySettings = Field(default_factory=HistorySettings)
    advanced: AdvancedSettings = Field(default_factory=AdvancedSettings)
    formats: FormatSettings = Field(default_factory=FormatSettings)
    post_processing: PostProcessingSettings = Field(default_factory=PostProcessingSettings)

    @classmethod
    def load_from_file(cls, file_path: Path) -> "Settings":
        """Load settings from a JSON file."""
        if file_path.exists():
            with open(file_path, "r") as f:
                data = json.load(f)
            return cls(**data)
        return cls()

    def save_to_file(self, file_path: Path) -> None:
        """Save settings to a JSON file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(self.model_dump(), f, indent=2, default=str)

    def get_download_path(self) -> Path:
        """Get the resolved download path."""
        path = Path(self.download.path).expanduser()
        if self.download.create_day_folders:
            from datetime import datetime

            today = datetime.now()
            path = path / f"{today.day:02d}"
        return path

    def get_yt_dlp_options(self) -> dict:
        """Get yt-dlp options from settings."""
        options = {
            "outtmpl": self.download.file_naming,
            "format": self.download.default_quality,
            "retries": self.download.retries,
            "fragment_retries": self.download.fragment_retries,
            "socket_timeout": self.download.socket_timeout,
            "retry_sleep": self.download.retry_sleep,
            "max_sleep_interval": self.download.max_sleep_interval,
            "sleep_interval": self.download.sleep_interval,
            "sleep_requests": self.download.sleep_requests,
            "sleep_subtitles": self.download.sleep_subtitles,
            "continue": self.download.continue_download,
            "restrictfilenames": self.download.restrict_filenames,
            "writethumbnail": self.download.save_thumbnail,
            "writedescription": self.download.write_description,
            "writeinfojson": self.download.write_info_json,
            "embedsubtitles": self.post_processing.embed_subs,
            "embedthumbnail": self.post_processing.embed_thumbnail,
            "extractaudio": self.post_processing.extract_audio,
            "audioformat": self.post_processing.audio_format,
            "audioquality": self.post_processing.audio_quality,
            "convertsubtitles": self.post_processing.convert_subs,
            "splitchapters": self.post_processing.split_chapters,
        }

        # Add advanced options
        if self.advanced.proxy:
            options["proxy"] = self.advanced.proxy
        if self.advanced.geo_verification_proxy:
            options["geo_verification_proxy"] = self.advanced.geo_verification_proxy
        if self.advanced.cookies_file:
            options["cookiefile"] = self.advanced.cookies_file
        if self.advanced.impersonate:
            options["impersonate"] = self.advanced.impersonate
        if self.advanced.force_ipv4:
            options["force_ipv4"] = True
        if self.advanced.force_ipv6:
            options["force_ipv6"] = True
        if self.advanced.prefer_insecure:
            options["prefer_insecure"] = True
        if self.advanced.no_check_certificates:
            options["no_check_certificates"] = True
        if self.advanced.legacy_server_connect:
            options["legacy_server_connect"] = True

        # Add headers
        if self.advanced.add_headers:
            options["addheaders"] = self.advanced.add_headers

        # Add SponsorBlock options
        if self.post_processing.sponsorblock_mark:
            options["sponsorblock_mark"] = ",".join(self.post_processing.sponsorblock_mark)
        if self.post_processing.sponsorblock_remove:
            options["sponsorblock_remove"] = ",".join(self.post_processing.sponsorblock_remove)
        if self.post_processing.sponsorblock_chapter_title:
            options["sponsorblock_chapter_title"] = self.post_processing.sponsorblock_chapter_title

        return options


def load_config(config_path: Optional[Path] = None) -> Settings:
    """Load configuration from file or create default."""
    from .config_manager import ConfigManager

    config_manager = ConfigManager()
    return config_manager.load_config(config_path)
