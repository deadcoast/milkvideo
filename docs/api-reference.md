# VideoMilker API Reference

This document provides a comprehensive reference for the VideoMilker codebase, including all major classes, methods, and their usage.

## Table of Contents

- [Main Entry Point](#main-entry-point)
- [CLI Components](#cli-components)
- [Core Functionality](#core-functionality)
- [Configuration Management](#configuration-management)
- [History Management](#history-management)
- [Exception Handling](#exception-handling)

## Main Entry Point

### `src/videomilker/main.py`

The main entry point for the VideoMilker CLI application.

#### `main()`

**Function**: Main CLI entry point using Click framework

**Parameters**:

- `config` (str, optional): Path to configuration file
- `verbose` (bool): Enable verbose logging
- `download_path` (str, optional): Set download path
- `link` (str, optional): Quick download URL
- `url` (str, optional): Legacy download URL option

**Usage**:

```bash
# Interactive mode
videomilker

# Quick download
videomilker --link "https://youtube.com/watch?v=..."

# With custom config
videomilker --config /path/to/config.json --verbose

# Set download path
videomilker --download-path /custom/path
```

## CLI Components

### `src/videomilker/cli/menu_system.py`

#### `MenuSystem`

**Class**: Main menu controller and state management

**Key Methods**:

- `__init__(settings, verbose=False)`: Initialize menu system
- `run()`: Start the main menu loop
- `show_main_menu()`: Display main menu with keyboard shortcuts
- `handle_quick_download()`: Handle single URL downloads with format selection
- `handle_batch_download()`: Handle batch downloads with concurrency
- `handle_queue_management()`: Manage download queues with pause/resume
- `handle_audio_download()`: Handle audio-only downloads
- `handle_chapter_download()`: Handle chapter splitting downloads
- `show_settings_menu()`: Display settings menu with new options
- `show_history_menu()`: Display download history with advanced search
- `handle_file_management()`: Manage files and duplicates
- `show_download_confirmation()`: Show confirmation with auto-download option
- `_handle_global_shortcuts()`: Process global keyboard shortcuts
- `_show_format_selection()`: Display format preview and selection
- `_handle_configuration_wizard()`: Run first-time setup wizard
- `_handle_advanced_search()`: Advanced history search functionality
- `_handle_performance_settings()`: Configure concurrent download limits
- `_export_configuration()`: Export settings to file
- `_import_configuration()`: Import settings from file

**Usage**:

```python
from videomilker.cli.menu_system import MenuSystem
from videomilker.config.config_manager import ConfigManager

config_manager = ConfigManager()
settings = config_manager.load_config()
menu_system = MenuSystem(settings=settings, verbose=True)
menu_system.run()
```

### `src/videomilker/cli/menu_renderer.py`

#### `MenuRenderer`

**Class**: Rich-based UI rendering and display components

**Key Methods**:

- `render_main_menu()`: Render main menu interface with shortcuts
- `render_quick_download_menu()`: Render quick download interface
- `render_batch_download_menu()`: Render batch download interface
- `render_settings_menu()`: Render settings interface with new options
- `render_progress_display()`: Render download progress with detailed stats
- `render_error_display()`: Render user-friendly error messages
- `show_download_confirmation()`: Show confirmation dialog with auto option
- `show_progress()`: Display enhanced progress with speed and ETA
- `show_download_progress()`: Show detailed download progress
- `show_error()`: Display formatted error messages with suggestions
- `show_warning()`: Display confirmation dialogs for destructive actions
- `show_menu()`: Display menu with keyboard shortcut information

**Usage**:

```python
from videomilker.cli.menu_renderer import MenuRenderer
from rich.console import Console

console = Console()
renderer = MenuRenderer(console)
renderer.render_main_menu()
```

### `src/videomilker/cli/input_handler.py`

#### `InputHandler`

**Class**: User input processing and validation

**Key Methods**:

- `get_user_input(prompt, validator=None)`: Get validated user input
- `get_url_input()`: Get and validate URL input
- `get_choice_input(options, default=None)`: Get choice from options
- `get_confirm_input(prompt, default=True)`: Get yes/no confirmation
- `get_path_input(prompt, must_exist=False)`: Get file/path input

**Usage**:

```python
from videomilker.cli.input_handler import InputHandler

handler = InputHandler()
url = handler.get_url_input()
choice = handler.get_choice_input(['option1', 'option2'], default='option1')
```

### `src/videomilker/cli/styles.py`

#### Style Definitions

**Module**: UI styling and theme definitions

**Key Components**:

- `DEFAULT_THEME`: Default color theme
- `DARK_THEME`: Dark mode theme
- `LIGHT_THEME`: Light mode theme
- `MINIMAL_THEME`: Minimal theme

**Usage**:

```python
from videomilker.cli.styles import DEFAULT_THEME, DARK_THEME
from rich.theme import Theme

# Apply theme to console
console = Console(theme=Theme(DEFAULT_THEME))
```

## Core Functionality

### `src/videomilker/core/downloader.py`

#### `VideoDownloader`

**Class**: Main download management with yt-dlp integration

**Key Methods**:

- `__init__(settings, console=None)`: Initialize downloader
- `download_single(url, options=None)`: Download single video with resume support
- `download_batch(urls, options=None)`: Download multiple videos
- `add_to_queue(url, options=None)`: Add URL to download queue
- `get_queue_status()`: Get current queue status
- `validate_url(url)`: Validate URL format
- `get_video_info(url)`: Get video information without downloading
- `list_formats(url)`: List available formats
- `get_formatted_formats(url)`: Get detailed format information with preview
- `get_best_formats(url, format_type='video')`: Get best available formats
- `get_chapters(url)`: Get chapter information for videos
- `download_with_chapters(url, options=None)`: Download with chapter splitting
- `find_interrupted_downloads(download_path)`: Find incomplete downloads
- `resume_download(url, partial_file, options=None)`: Resume interrupted download
- `cleanup_partial_files(download_path)`: Clean up incomplete download files

**Usage**:

```python
from videomilker.core.downloader import VideoDownloader
from videomilker.config.config_manager import ConfigManager

config_manager = ConfigManager()
settings = config_manager.load_config()
downloader = VideoDownloader(settings)

# Download single video
result = downloader.download_single("https://youtube.com/watch?v=...")

# Download batch
urls = ["url1", "url2", "url3"]
results = downloader.download_batch(urls)
```

#### `AsyncVideoDownloader`

**Class**: Asynchronous version of VideoDownloader

**Key Methods**:

- `download_single_async(url, options=None)`: Async single download
- `download_batch_async(urls, options=None)`: Async batch download
- `get_video_info_async(url)`: Async video info retrieval

### `src/videomilker/core/batch_processor.py`

#### `DownloadQueue`

**Class**: Thread-safe download queue management

**Key Methods**:

- `__init__()`: Initialize empty queue
- `add_url(url, options=None)`: Add URL to queue
- `get_next()`: Get next URL from queue
- `pause()`: Pause queue processing
- `resume()`: Resume queue processing
- `stop()`: Stop all processing
- `clear()`: Clear all items from queue
- `get_status()`: Get current queue status
- `get_progress()`: Get processing progress

#### `BatchProcessor`

**Class**: Batch download logic and queue management

**Key Methods**:

- `__init__(settings, console=None)`: Initialize batch processor
- `process_batch(urls, options=None)`: Process batch of URLs with chunking
- `process_batch_with_limits(urls, options=None, max_concurrent=3)`: Process with concurrency
- `process_audio_batch(urls, options=None)`: Process audio-only batch
- `process_audio_batch_with_limits(urls, options=None, max_concurrent=3)`: Audio batch with concurrency
- `add_to_queue(url, options=None)`: Add to processing queue
- `get_queue_status()`: Get queue status
- `clear_queue()`: Clear processing queue
- `pause_processing()`: Pause batch processing
- `resume_processing()`: Resume batch processing
- `estimate_memory_usage(num_urls, avg_size_mb=50)`: Estimate memory requirements

**Usage**:

```python
from videomilker.core.batch_processor import BatchProcessor

processor = BatchProcessor(settings)
processor.process_batch(urls)
```

### `src/videomilker/core/progress_tracker.py`

#### `ProgressTracker`

**Class**: Progress monitoring and display

**Key Methods**:

- `__init__(console=None)`: Initialize progress tracker
- `start_tracking(download_id, total_size=None)`: Start tracking download
- `update_progress(progress, speed=None, eta=None)`: Update progress
- `complete_tracking(download_id)`: Mark download as complete
- `error_tracking(download_id, error)`: Mark download as failed
- `get_progress_display()`: Get formatted progress display

**Usage**:

```python
from videomilker.core.progress_tracker import ProgressTracker

tracker = ProgressTracker()
tracker.start_tracking("download_1", total_size=1024000)
tracker.update_progress(50.0, speed=1024, eta=30)
```

### `src/videomilker/core/file_manager.py`

#### `FileManager`

**Class**: File operations and organization

**Key Methods**:

- `__init__(settings)`: Initialize file manager
- `ensure_download_path()`: Ensure download directory exists
- `get_download_path()`: Get current download path
- `organize_file(filename, category=None)`: Organize downloaded file
- `cleanup_temp_files()`: Clean up temporary files
- `get_file_info(filepath)`: Get file information
- `validate_file(filepath)`: Validate downloaded file
- `calculate_file_hash(filepath, algorithm='sha256')`: Calculate file hash for duplicate detection
- `find_duplicates_by_hash(directory)`: Find duplicate files using content hash
- `find_duplicates_by_name_size(directory)`: Find duplicates by name and size
- `find_similar_files(directory, similarity_threshold=0.8)`: Find similar files using fuzzy matching
- `remove_duplicates(duplicates, keep_strategy='newest')`: Remove duplicate files with strategy
- `get_large_files(directory, size_threshold_mb=100)`: Find files larger than threshold
- `get_old_files(directory, age_days=30)`: Find files older than specified days
- `cleanup_empty_folders(directory)`: Remove empty directories
- `move_files_by_extension(directory, create_folders=True)`: Organize files by type
- `analyze_storage_usage(directory)`: Analyze disk usage and provide recommendations

**Usage**:

```python
from videomilker.core.file_manager import FileManager

file_manager = FileManager(settings)
download_path = file_manager.get_download_path()
file_manager.organize_file("video.mp4", category="music")
```

## Configuration Management

### `src/videomilker/config/settings.py`

#### `Settings`

**Class**: Main application settings using Pydantic

**Key Components**:

- `DownloadSettings`: Download configuration
- `UISettings`: UI configuration
- `HistorySettings`: History configuration
- `AdvancedSettings`: Advanced options
- `FormatSettings`: Format preferences
- `PostProcessingSettings`: Post-processing options

**Usage**:

```python
from videomilker.config.settings import Settings

settings = Settings()
settings.download.path = "/custom/download/path"
settings.download.file_naming = "%(title)s.%(ext)s"
```

#### `DownloadSettings`

**Class**: Download-specific configuration

**Key Fields**:

- `path`: Download directory path
- `create_day_folders`: Create day-based folders
- `file_naming`: File naming template
- `default_quality`: Default video quality
- `default_format`: Default video format
- `max_concurrent`: Maximum concurrent downloads

### `src/videomilker/config/config_manager.py`

#### `ConfigManager`

**Class**: Configuration file operations and migration

**Key Methods**:

- `__init__(config_dir=None)`: Initialize config manager
- `load_config(config_path=None)`: Load configuration with validation
- `save_config(config_path=None)`: Save configuration
- `get_setting(key, default=None)`: Get specific setting
- `set_setting(key, value)`: Set specific setting
- `reset_to_defaults()`: Reset to default configuration
- `export_config(export_path)`: Export configuration with metadata
- `import_config(import_path)`: Import configuration with validation
- `validate_config(settings)`: Validate configuration settings
- `auto_fix_config(settings)`: Automatically fix common configuration issues

**Usage**:

```python
from videomilker.config.config_manager import ConfigManager

config_manager = ConfigManager()
settings = config_manager.load_config()
config_manager.set_setting("download.path", "/new/path")
config_manager.save_config()
```

### `src/videomilker/config/defaults.py`

#### Default Configurations

**Module**: Default settings and presets

**Key Components**:

- `DEFAULT_CONFIG`: Default configuration structure
- `THEMES`: Available UI themes
- `FILE_NAMING_TEMPLATES`: File naming templates
- `QUALITY_PRESETS`: Quality presets
- `FORMAT_PRESETS`: Format presets

**Usage**:

```python
from videomilker.config.defaults import DEFAULT_CONFIG, THEMES

# Use default config
settings = Settings(**DEFAULT_CONFIG)

# Apply theme
theme = THEMES["dark"]
```

## History Management

### `src/videomilker/history/history_manager.py`

#### `HistoryManager`

**Class**: History operations and database management

**Key Methods**:

- `__init__(settings)`: Initialize history manager
- `add_download(url, filename, size, status)`: Add download to history
- `get_recent_downloads(limit=10)`: Get recent downloads
- `get_downloads_by_date(date)`: Get downloads by date
- `clear_history()`: Clear download history
- `export_history(format='json')`: Export history
- `search_history(query)`: Search download history

**Usage**:

```python
from videomilker.history.history_manager import HistoryManager

history_manager = HistoryManager(settings)
history_manager.add_download("https://youtube.com/watch?v=...", "video.mp4", 1024000, "completed")
recent = history_manager.get_recent_downloads(limit=5)
```

## Exception Handling

### `src/videomilker/exceptions/download_errors.py`

#### Download Exceptions

**Module**: Download-related errors and mappings

**Key Exception Classes**:

- `VideoMilkerError`: Base exception class
- `DownloadError`: General download errors
- `FormatError`: Format-related errors
- `NetworkError`: Network-related errors
- `FileError`: File system errors
- `ValidationError`: Validation errors
- `AuthenticationError`: Authentication errors
- `RateLimitError`: Rate limiting errors

**Key Functions**:

- `map_yt_dlp_error(error_message)`: Map yt-dlp errors to custom exceptions
- `create_error_with_context(error, url, additional_info=None)`: Create detailed error with context
- `get_user_friendly_error_message(error_type, error_message)`: Get user-friendly error descriptions
- `format_error_for_display(error, show_suggestions=True)`: Format errors for UI display

**Error Mapping**:

- `USER_FRIENDLY_ERRORS`: Dictionary mapping error types to user-friendly messages and suggestions

**Usage**:

```python
from videomilker.exceptions.download_errors import DownloadError, NetworkError

try:
    downloader.download_single(url)
except DownloadError as e:
    console.print(f"[red]Download failed: {e}[/red]")
except NetworkError as e:
    console.print(f"[yellow]Network error: {e}[/yellow]")
```

### `src/videomilker/exceptions/config_errors.py`

#### Configuration Exceptions

**Module**: Configuration-related errors

**Key Exception Classes**:

- `ConfigError`: Base configuration error
- `ConfigFileError`: Base class for configuration file errors
- `ConfigFileNotFoundError`: Configuration file not found
- `ConfigFileCorruptedError`: Configuration file corrupted
- `ConfigValidationError`: Configuration validation errors
- `ConfigMigrationError`: Configuration migration errors

### `src/videomilker/exceptions/validation_errors.py`

#### Validation Exceptions

**Module**: Input validation errors

**Key Exception Classes**:

- `ValidationError`: Base validation error
- `URLValidationError`: URL validation errors
- `PathValidationError`: Path validation errors
- `FormatValidationError`: Format validation errors

## Utility Functions

### `src/remove_emojis.py`

#### `remove_emojis(text)`

**Function**: Remove emojis from text for filename compatibility

**Parameters**:

- `text` (str): Text to clean

**Returns**:

- `str`: Text with emojis removed

**Usage**:

```python
from src.remove_emojis import remove_emojis

clean_title = remove_emojis("Video Title 🎵🎬")
# Result: "Video Title "
```

## Configuration File Structure

### User Configuration Location

- **macOS/Linux**: `~/.config/videomilker/videomilker.json`
- **Windows**: `%APPDATA%\videomilker\videomilker.json`

### Configuration Schema

```json
{
  "version": "1.0.0",
  "download": {
    "path": "/Users/username/Downloads/VideoMilker",
    "create_day_folders": true,
    "file_naming": "%(upload_date)s_%(title)s.%(ext)s",
    "default_quality": "best",
    "default_format": "mp4",
    "max_concurrent": 3,
    "auto_subtitle": false,
    "save_thumbnail": false,
    "embed_metadata": true,
    "write_description": false,
    "write_info_json": true,
    "restrict_filenames": true,
    "continue_download": true,
    "retries": 10,
    "fragment_retries": 10,
    "socket_timeout": 30,
    "retry_sleep": 1,
    "max_sleep_interval": 10,
    "sleep_interval": 1,
    "sleep_requests": 0.75,
    "sleep_subtitles": 5,
    "resume": true,
    "fragment_retries": 10,
    "retry_sleep": 1
  },
  "ui": {
    "theme": "default",
    "show_progress_details": true,
    "confirm_before_quit": true,
    "clear_screen": true,
    "color_output": true,
    "show_eta": true,
    "show_speed": true,
    "show_size": true,
    "progress_bar_style": "bar",
    "menu_style": "rounded",
    "border_style": "blue",
    "highlight_style": "yellow",
    "error_style": "red",
    "success_style": "green",
    "warning_style": "yellow",
    "auto_download": false
  },
  "history": {
    "max_entries": 1000,
    "auto_cleanup": true,
    "cleanup_days": 30,
    "save_download_logs": true,
    "log_level": "INFO",
    "database_path": "history.db",
    "export_format": "json"
  },
  "advanced": {
    "use_cookies": false,
    "cookies_file": "",
    "proxy": "",
    "geo_verification_proxy": "",
    "xff": "default",
    "impersonate": "",
    "force_ipv4": false,
    "force_ipv6": false,
    "prefer_insecure": false,
    "no_check_certificates": false,
    "legacy_server_connect": false,
    "add_headers": []
  },
  "formats": {
    "video_formats": ["mp4", "mkv", "webm", "avi", "mov"],
    "audio_formats": ["m4a", "mp3", "opus", "aac", "flac"],
    "preferred_video_codec": "h264",
    "preferred_audio_codec": "aac",
    "max_resolution": "1080p",
    "min_resolution": "360p",
    "prefer_free_formats": true,
    "check_formats": true
  },
  "post_processing": {
    "extract_audio": false,
    "audio_format": "m4a",
    "audio_quality": 5,
    "embed_thumbnail": false,
    "embed_subs": false,
    "convert_subs": "srt",
    "split_chapters": false,
    "remove_chapters": [],
    "sponsorblock_mark": [],
    "sponsorblock_remove": [],
    "sponsorblock_chapter_title": "[SponsorBlock]: %(category_names)l"
  }
}
```

## Testing

### Test Structure

- **Main Tests**: `tests/test_videomilker.py`
- **Auto Download Tests**: `tests/test_auto_download.py`
- **Batch Functionality Tests**: `tests/test_batch_functionality.py`
- **CLI Tests**: `tests/test_cli/`
- **Config Tests**: `tests/test_config/`
- **Core Tests**: `tests/test_core/`
- **Utils Tests**: `tests/test_utils/`

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/videomilker

# Run specific test file
pytest tests/test_videomilker.py

# Run with verbose output
pytest -v
```

This API reference provides a comprehensive overview of the VideoMilker codebase structure and usage patterns.
