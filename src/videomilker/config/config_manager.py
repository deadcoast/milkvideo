"""Configuration management for VideoMilker."""

import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from .settings import Settings
from .defaults import DEFAULT_CONFIG
from ..exceptions.config_errors import ConfigValidationError, ConfigFileError


class ConfigManager:
    """Manages VideoMilker configuration files and settings."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the configuration manager."""
        self.config_dir = config_dir or self._get_default_config_dir()
        self.config_file = self.config_dir / "videomilker.json"
        self.backup_dir = self.config_dir / "backups"
        self.settings: Optional[Settings] = None
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory."""
        if Path.home().exists():
            return Path.home() / ".config" / "videomilker"
        return Path.cwd() / "config"
    
    def load_config(self, config_path: Optional[Path] = None) -> Settings:
        """Load configuration from file or create default."""
        config_file = config_path or self.config_file
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle version migration if needed
                data = self._migrate_config(data)
                
                self.settings = Settings(**data)
                return self.settings
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # Backup corrupted config and create new one
                self._backup_corrupted_config(config_file, str(e))
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Settings:
        """Create and save default configuration."""
        self.settings = Settings(**DEFAULT_CONFIG)
        self.save_config()
        return self.settings
    
    def save_config(self, config_path: Optional[Path] = None) -> None:
        """Save current configuration to file."""
        if not self.settings:
            raise ValueError("No settings to save")
        
        config_file = config_path or self.config_file
        
        # Create backup before saving
        if config_file.exists():
            self._create_backup(config_file)
        
        # Save new configuration
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings.model_dump(), f, indent=2, default=str)
    
    def _create_backup(self, config_file: Path) -> None:
        """Create a backup of the current configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"videomilker_{timestamp}.json"
        shutil.copy2(config_file, backup_file)
    
    def _backup_corrupted_config(self, config_file: Path, error: str) -> None:
        """Backup a corrupted configuration file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"corrupted_{timestamp}.json"
        
        try:
            shutil.copy2(config_file, backup_file)
            # Add error information to backup
            with open(backup_file, 'a', encoding='utf-8') as f:
                f.write(f"\n# Error: {error}\n")
        except Exception:
            pass  # Don't fail if backup fails
    
    def _migrate_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate configuration to current version."""
        current_version = "1.0.0"
        config_version = data.get("version", "0.0.0")
        
        if config_version != current_version:
            # Apply migrations based on version
            if config_version < "1.0.0":
                data = self._migrate_to_v1_0_0(data)
            
            data["version"] = current_version
        
        return data
    
    def _migrate_to_v1_0_0(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate configuration to version 1.0.0."""
        # Add any new fields with defaults
        if "download" not in data:
            data["download"] = DEFAULT_CONFIG["download"]
        if "ui" not in data:
            data["ui"] = DEFAULT_CONFIG["ui"]
        if "history" not in data:
            data["history"] = DEFAULT_CONFIG["history"]
        
        return data
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        if not self.settings:
            self.load_config()
        
        # Support nested keys like "download.path"
        keys = key.split(".")
        value = self.settings
        
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        
        return value
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a specific setting value."""
        if not self.settings:
            self.load_config()
        
        # Support nested keys like "download.path"
        keys = key.split(".")
        obj = self.settings
        
        for k in keys[:-1]:
            if hasattr(obj, k):
                obj = getattr(obj, k)
            else:
                raise KeyError(f"Invalid setting key: {key}")
        
        setattr(obj, keys[-1], value)
    
    def reset_to_defaults(self) -> Settings:
        """Reset configuration to defaults."""
        self.settings = self._create_default_config()
        return self.settings
    
    def export_config(self, export_path: Path) -> None:
        """Export current configuration to a file."""
        if not self.settings:
            self.load_config()
        
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(self.settings.model_dump(), f, indent=2, default=str)
    
    def import_config(self, import_path: Path) -> Settings:
        """Import configuration from a file."""
        if not import_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {import_path}")
        
        with open(import_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate and migrate imported config
        data = self._migrate_config(data)
        self.settings = Settings(**data)
        
        return self.settings
    
    def validate_config(self, settings: Optional[Settings] = None) -> Tuple[bool, List[str]]:
        """Validate configuration and return (is_valid, list_of_errors)."""
        if settings is None:
            settings = self.settings or self.load_config()
        
        errors = []
        
        # Validate download settings
        errors.extend(self._validate_download_settings(settings.download))
        
        # Validate UI settings
        errors.extend(self._validate_ui_settings(settings.ui))
        
        # Validate history settings
        errors.extend(self._validate_history_settings(settings.history))
        
        # Validate advanced settings
        errors.extend(self._validate_advanced_settings(settings.advanced))
        
        # Validate format settings
        errors.extend(self._validate_format_settings(settings.formats))
        
        # Validate post-processing settings
        errors.extend(self._validate_post_processing_settings(settings.post_processing))
        
        return len(errors) == 0, errors
    
    def _validate_download_settings(self, download_settings) -> List[str]:
        """Validate download settings."""
        errors = []
        
        # Validate download path
        try:
            path = Path(download_settings.path).expanduser()
            if not path.exists():
                # Try to create the directory
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"Download path '{path}' cannot be created: {e}")
        except Exception as e:
            errors.append(f"Invalid download path '{download_settings.path}': {e}")
        
        # Validate file naming template
        if not download_settings.file_naming:
            errors.append("File naming template cannot be empty")
        elif "%(ext)s" not in download_settings.file_naming:
            errors.append("File naming template must include %(ext)s for proper file extensions")
        
        # Validate quality settings
        valid_qualities = ["best", "worst", "720p", "1080p", "audio_only", "video_only"]
        if download_settings.default_quality not in valid_qualities:
            errors.append(f"Invalid default quality '{download_settings.default_quality}'. Must be one of: {valid_qualities}")
        
        # Validate format settings
        valid_formats = ["mp4", "mkv", "webm", "avi", "mov"]
        if download_settings.default_format not in valid_formats:
            errors.append(f"Invalid default format '{download_settings.default_format}'. Must be one of: {valid_formats}")
        
        # Validate concurrent downloads
        if download_settings.max_concurrent < 1 or download_settings.max_concurrent > 10:
            errors.append("Max concurrent downloads must be between 1 and 10")
        
        # Validate retry settings
        if download_settings.retries < 0 or download_settings.retries > 50:
            errors.append("Retries must be between 0 and 50")
        
        return errors
    
    def _validate_ui_settings(self, ui_settings) -> List[str]:
        """Validate UI settings."""
        errors = []
        
        # Validate theme
        valid_themes = ["default", "dark", "light", "minimal"]
        if ui_settings.theme not in valid_themes:
            errors.append(f"Invalid theme '{ui_settings.theme}'. Must be one of: {valid_themes}")
        
        # Validate progress bar style
        valid_styles = ["bar", "spinner", "text"]
        if ui_settings.progress_bar_style not in valid_styles:
            errors.append(f"Invalid progress bar style '{ui_settings.progress_bar_style}'. Must be one of: {valid_styles}")
        
        # Validate menu style
        valid_menu_styles = ["rounded", "double", "simple"]
        if ui_settings.menu_style not in valid_menu_styles:
            errors.append(f"Invalid menu style '{ui_settings.menu_style}'. Must be one of: {valid_menu_styles}")
        
        return errors
    
    def _validate_history_settings(self, history_settings) -> List[str]:
        """Validate history settings."""
        errors = []
        
        # Validate max entries
        if history_settings.max_entries < 1 or history_settings.max_entries > 10000:
            errors.append("Max history entries must be between 1 and 10000")
        
        # Validate cleanup days
        if history_settings.cleanup_days < 1 or history_settings.cleanup_days > 365:
            errors.append("Cleanup days must be between 1 and 365")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if history_settings.log_level not in valid_log_levels:
            errors.append(f"Invalid log level '{history_settings.log_level}'. Must be one of: {valid_log_levels}")
        
        # Validate export format
        valid_export_formats = ["json", "csv", "xml"]
        if history_settings.export_format not in valid_export_formats:
            errors.append(f"Invalid export format '{history_settings.export_format}'. Must be one of: {valid_export_formats}")
        
        return errors
    
    def _validate_advanced_settings(self, advanced_settings) -> List[str]:
        """Validate advanced settings."""
        errors = []
        
        # Validate cookies file path if specified
        if advanced_settings.cookies_file:
            try:
                cookies_path = Path(advanced_settings.cookies_file).expanduser()
                if not cookies_path.exists():
                    errors.append(f"Cookies file '{cookies_path}' does not exist")
            except Exception as e:
                errors.append(f"Invalid cookies file path '{advanced_settings.cookies_file}': {e}")
        
        # Validate proxy URL if specified
        if advanced_settings.proxy:
            if not advanced_settings.proxy.startswith(('http://', 'https://', 'socks5://')):
                errors.append("Proxy URL must start with http://, https://, or socks5://")
        
        # Validate XFF header
        valid_xff_values = ["default", "chrome", "firefox", "safari", "edge"]
        if advanced_settings.xff not in valid_xff_values:
            errors.append(f"Invalid XFF header '{advanced_settings.xff}'. Must be one of: {valid_xff_values}")
        
        return errors
    
    def _validate_format_settings(self, format_settings) -> List[str]:
        """Validate format settings."""
        errors = []
        
        # Validate video formats
        valid_video_formats = ["mp4", "mkv", "webm", "avi", "mov", "flv", "wmv"]
        for fmt in format_settings.video_formats:
            if fmt not in valid_video_formats:
                errors.append(f"Invalid video format '{fmt}'. Must be one of: {valid_video_formats}")
        
        # Validate audio formats
        valid_audio_formats = ["m4a", "mp3", "opus", "aac", "flac", "wav", "ogg"]
        for fmt in format_settings.audio_formats:
            if fmt not in valid_audio_formats:
                errors.append(f"Invalid audio format '{fmt}'. Must be one of: {valid_audio_formats}")
        
        # Validate video codec
        valid_video_codecs = ["h264", "h265", "vp8", "vp9", "av1"]
        if format_settings.preferred_video_codec not in valid_video_codecs:
            errors.append(f"Invalid preferred video codec '{format_settings.preferred_video_codec}'. Must be one of: {valid_video_codecs}")
        
        # Validate audio codec
        valid_audio_codecs = ["aac", "mp3", "opus", "flac", "vorbis"]
        if format_settings.preferred_audio_codec not in valid_audio_codecs:
            errors.append(f"Invalid preferred audio codec '{format_settings.preferred_audio_codec}'. Must be one of: {valid_audio_codecs}")
        
        # Validate resolution
        valid_resolutions = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
        if format_settings.max_resolution not in valid_resolutions:
            errors.append(f"Invalid max resolution '{format_settings.max_resolution}'. Must be one of: {valid_resolutions}")
        
        if format_settings.min_resolution not in valid_resolutions:
            errors.append(f"Invalid min resolution '{format_settings.min_resolution}'. Must be one of: {valid_resolutions}")
        
        return errors
    
    def _validate_post_processing_settings(self, post_processing_settings) -> List[str]:
        """Validate post-processing settings."""
        errors = []
        
        # Validate audio format for extraction
        valid_audio_formats = ["m4a", "mp3", "opus", "aac", "flac", "wav"]
        if post_processing_settings.audio_format not in valid_audio_formats:
            errors.append(f"Invalid audio format for extraction '{post_processing_settings.audio_format}'. Must be one of: {valid_audio_formats}")
        
        # Validate audio quality
        if post_processing_settings.audio_quality < 0 or post_processing_settings.audio_quality > 10:
            errors.append("Audio quality must be between 0 and 10")
        
        # Validate subtitle conversion format
        valid_subtitle_formats = ["srt", "vtt", "ass", "ssa"]
        if post_processing_settings.convert_subs not in valid_subtitle_formats:
            errors.append(f"Invalid subtitle conversion format '{post_processing_settings.convert_subs}'. Must be one of: {valid_subtitle_formats}")
        
        return errors
    
    def auto_fix_config(self, settings: Optional[Settings] = None) -> Tuple[bool, List[str]]:
        """Automatically fix common configuration issues."""
        if settings is None:
            settings = self.settings or self.load_config()
        
        fixes_applied = []
        
        # Fix download path if it doesn't exist
        try:
            path = Path(settings.download.path).expanduser()
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                fixes_applied.append(f"Created download directory: {path}")
        except Exception:
            # Reset to default if path is invalid
            settings.download.path = str(Path.home() / "Downloads" / "VideoMilker")
            fixes_applied.append(f"Reset download path to default: {settings.download.path}")
        
        # Fix file naming template if missing extension placeholder
        if "%(ext)s" not in settings.download.file_naming:
            settings.download.file_naming = "%(upload_date)s_%(title)s.%(ext)s"
            fixes_applied.append("Fixed file naming template to include %(ext)s")
        
        # Fix invalid quality settings
        valid_qualities = ["best", "worst", "720p", "1080p", "audio_only", "video_only"]
        if settings.download.default_quality not in valid_qualities:
            settings.download.default_quality = "best"
            fixes_applied.append("Reset default quality to 'best'")
        
        # Fix invalid format settings
        valid_formats = ["mp4", "mkv", "webm", "avi", "mov"]
        if settings.download.default_format not in valid_formats:
            settings.download.default_format = "mp4"
            fixes_applied.append("Reset default format to 'mp4'")
        
        # Fix concurrent downloads limits
        if settings.download.max_concurrent < 1:
            settings.download.max_concurrent = 1
            fixes_applied.append("Set max concurrent downloads to 1")
        elif settings.download.max_concurrent > 10:
            settings.download.max_concurrent = 10
            fixes_applied.append("Set max concurrent downloads to 10")
        
        # Fix retry limits
        if settings.download.retries < 0:
            settings.download.retries = 0
            fixes_applied.append("Set retries to 0")
        elif settings.download.retries > 50:
            settings.download.retries = 50
            fixes_applied.append("Set retries to 50")
        
        # Fix invalid theme
        valid_themes = ["default", "dark", "light", "minimal"]
        if settings.ui.theme not in valid_themes:
            settings.ui.theme = "default"
            fixes_applied.append("Reset theme to 'default'")
        
        # Fix history limits
        if settings.history.max_entries < 1:
            settings.history.max_entries = 1000
            fixes_applied.append("Set max history entries to 1000")
        elif settings.history.max_entries > 10000:
            settings.history.max_entries = 10000
            fixes_applied.append("Set max history entries to 10000")
        
        # Save fixes if any were applied
        if fixes_applied:
            self.save_config()
        
        return len(fixes_applied) > 0, fixes_applied 