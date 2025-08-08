# VideoMilker User Guide

Welcome to VideoMilker! This guide will help you get started with downloading videos using our intuitive CLI interface.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Install VideoMilker

```bash
# Clone the repository
git clone https://github.com/deadcoast/milkvideo.git
cd milkvideo

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Verify Installation

```bash
python -m videomilker --version
```

## Quick Start

### Interactive Mode (Recommended)

Start VideoMilker in interactive mode:

```bash
python -m videomilker
```

This will launch the main menu where you can:

- Download single videos
- Process batch downloads
- Configure settings
- View download history

### Quick Download Mode

Download a video directly without the menu:

```bash
python -m videomilker --link "https://youtube.com/watch?v=..."
```

Or using the legacy option:

```bash
python -m videomilker --url "https://youtube.com/watch?v=..."
```

### With Custom Configuration

```bash
python -m videomilker --config /path/to/config.json --verbose
```

### Set Custom Download Path

```bash
python -m videomilker --download-path /custom/download/path
```

## Basic Usage

### Main Menu Navigation

When you start VideoMilker, you'll see the main menu:

```bash
VideoMilker v1.0
┌─────────────────────────────────────────┐
│           Welcome to VideoMilker!       │
│─────────────────────────────────────────│
│                                         │
│  [1] Quick Download                     │
│  [2] Batch Download                     │
│  [3] Queue Management                   │
│  [4] Audio Download (Ctrl+A)            │
│  [5] Chapter Download (Ctrl+C)          │
│  [6] Options & Settings                 │
│  [7] Download History                   │
│  [8] File Management (Ctrl+F)           │
│  [9] Help & Info                        │
│                                         │
│  [q] Quit Application                   │
└─────────────────────────────────────────┘

Global Shortcuts:
• Ctrl+Q: Quick Download
• Ctrl+B: Batch Download
• Ctrl+A: Audio Download
• Ctrl+C: Chapter Download
• Ctrl+H: History
• Ctrl+F: File Management
```

### 1. Quick Download

Select option `1` for single video downloads:

1. Enter the video URL when prompted
2. Choose download options (quality, format) with preview
3. Enable auto-download for future downloads (optional)
4. Confirm download or select 'auto' for immediate download
5. Monitor progress with detailed speed and ETA information

**Features:**

- Format preview and selection before download
- Auto-download option (saves preference permanently)
- Real-time progress with speed and ETA
- Download resume for interrupted downloads

### 2. Batch Download

Select option `2` for multiple video downloads:

1. Choose input method:
   - Paste URLs directly
   - Load from batch file
   - Browse for batch file
2. Add URLs to the queue
3. Configure concurrent download limits
4. Start batch download with pause/resume capability
5. Monitor progress for all downloads

**Features:**

- Concurrent download limits with threading
- Memory optimization for large batches
- Progress tracking for individual and overall batch
- Download resume for interrupted downloads
- Chunked processing for better performance

### 3. Queue Management

Select option `3` to manage download queues:

- **Add/Load URLs**: Add individual URLs or load from batch files
- **Pause/Resume/Stop Processing**: Control queue execution
- **View Queue Progress**: Monitor active downloads
- **View Download Results**: Check completed and failed downloads
- **Clear Queue**: Remove all pending downloads

### 4. Audio Download

Select option `4` for audio-only downloads:

- **Audio Format Selection**: Choose from M4A, MP3, OPUS, AAC, FLAC
- **Quality Settings**: Configure audio bitrate and quality
- **Batch Audio Processing**: Download multiple audio files with concurrency
- **Format Preview**: Preview available audio formats before download

### 5. Chapter Download

Select option `5` for videos with chapter information:

- **Chapter Preview**: View available chapters before download
- **Chapter Selection**: Choose specific chapters to download
- **Split by Chapters**: Download each chapter as separate file
- **Chapter Metadata**: Embed chapter information in files

### 6. Options & Settings

Select option `6` to configure VideoMilker:

- **Download Path Settings**: Set custom download location with folder browser
- **Audio/Video Format Settings**: Configure quality and format preferences
- **File Organization Settings**: Set up folder structure and naming
- **Performance Settings**: Configure concurrent download limits
- **Configuration Management**: Export/import, validate, and auto-fix settings
- **Configuration Wizard**: First-time setup guide
- **Advanced yt-dlp Options**: Configure advanced download options
- **View/Edit Config Files**: Direct access to configuration files
- **Reset to Defaults**: Restore default settings

### 7. Download History

Select option `7` to view your download history:

- **View Recent Downloads**: See latest download activity
- **Advanced Search**: Search by title, URL, date, or status
- **Filter by Date Range**: View downloads from specific periods
- **Export History**: Export download logs in various formats
- **Clear History**: Remove old download records
- **Statistics**: View download statistics and trends

### 8. File Management

Select option `8` for file management and cleanup:

- **Duplicate Detection**: Find duplicate files using hash-based, name/size-based, or similar file algorithms
- **File Cleanup**: Remove large files, old files, or empty folders
- **Storage Analysis**: Analyze disk usage and get recommendations
- **Organize Files**: Sort files by type into organized folders
- **Remove Duplicates**: Choose strategy (keep newest, oldest, largest, smallest)

## Advanced Features

### File Organization

VideoMilker automatically organizes downloads:

```plaintext
Downloads/
└── VideoMilker/
    ├── 01/  # January 1st downloads
    ├── 02/  # January 2nd downloads
    ├── 15/  # January 15th downloads (current day)
    │   ├── 20241215_video-title-1.mp4
    │   ├── 20241215_video-title-2.mp4
    │   └── batch_downloads/
    │       └── 20241215_14-30_batch.log
    └── config/
        ├── videomilker.json
        └── download_history.json
```

### File Naming

Files are named using the template: `%(upload_date)s_%(title)s.%(ext)s`

Available placeholders:

- `%(title)s` - Video title
- `%(upload_date)s` - Upload date (YYYYMMDD)
- `%(uploader)s` - Channel/uploader name
- `%(id)s` - Video ID
- `%(ext)s` - File extension
- `%(resolution)s` - Video resolution
- `%(duration)s` - Video duration

### Progress Tracking

Real-time progress display:

```bash
Downloading: Video Title Here
┌─────────────────────────────────────────┐
│  Progress: ████████████░░░░░░░  67%     │
│  Speed: 2.4 MB/s    ETA: 00:45          │
│  Size: 15.3 MB / 22.8 MB                │
│                                         │
│  Status: Downloading video stream...    │
│                                         │
│  [Ctrl+C] Cancel Download               │
└─────────────────────────────────────────┘
```

### Batch Processing

Monitor multiple downloads:

```bash
Batch Download Progress
┌─────────────────────────────────────────┐
│  Overall: ██████░░░░░░░░░░░░░░░  3/8    │
│                                         │
│  Video 1 - Complete (25.3 MB)           │
│  Video 2 - Complete (18.7 MB)           │
│  Video 3 - Downloading... 45%           │
│  Video 4 - Queued                       │
│  Video 5 - Queued                       │
│                                         │
│  [p] Pause  [s] Skip Current  [q] Quit  │
└─────────────────────────────────────────┘
```

## Configuration

### Configuration Files

VideoMilker uses JSON configuration files:

- **User Config**: `~/.config/videomilker/videomilker.json`
- **Default Config**: `config/default_config.json`

### Key Settings

#### Download Settings

```json
{
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
    "write_info_json": true,
    "restrict_filenames": true,
    "continue_download": true,
    "retries": 10
  }
}
```

#### UI Settings

```json
{
  "ui": {
    "theme": "default",
    "show_progress_details": true,
    "confirm_before_quit": true,
    "clear_screen": true,
    "color_output": true,
    "show_eta": true,
    "show_speed": true,
    "show_size": true
  }
}
```

#### History Settings

```json
{
  "history": {
    "max_entries": 1000,
    "auto_cleanup": true,
    "cleanup_days": 30,
    "save_download_logs": true,
    "log_level": "INFO"
  }
}
```

### Available Themes

- **default**: Standard blue/yellow theme
- **dark**: Dark mode with bright colors
- **light**: Light mode with dark text
- **minimal**: Minimal styling

### Quality Presets

- **best**: Best available quality
- **worst**: Lowest quality
- **720p**: Maximum 720p resolution
- **1080p**: Maximum 1080p resolution
- **audio_only**: Audio only
- **video_only**: Video only

### Format Presets

- **mp4**: MP4 format with H.264 video and AAC audio
- **mkv**: MKV container with best available streams
- **webm**: WebM format for web compatibility

## Troubleshooting

### Common Issues

#### "Command not found: videomilker"

- Ensure installation completed successfully
- Check that Python scripts directory is in your PATH
- Try running: `python -m videomilker`

#### "Permission denied" errors

- On macOS/Linux, you may need to run: `chmod +x ~/.local/bin/videomilker`
- Or install with: `pip install --user videomilker`

#### Download fails with "Video unavailable"

- Check if the video is public and accessible
- Verify the URL is correct
- Try again later (video might be temporarily unavailable)
- Check if the video has age restrictions

#### Files downloaded without extensions

- This was a configuration issue that has been fixed
- Ensure your config has: `"file_naming": "%(upload_date)s_%(title)s.%(ext)s"`
- The `%(ext)s` placeholder is required for proper file extensions

#### Network errors

- Check your internet connection
- Try using a different network
- Configure proxy settings if needed
- Increase retry settings in configuration

### Getting Help

#### Verbose Mode

Run with verbose logging for detailed information:

```bash
python -m videomilker --verbose
```

#### Check Logs

Logs are stored in:

- **macOS/Linux**: `~/.config/videomilker/logs/`
- **Windows**: `%APPDATA%\videomilker\logs\`

#### Report Issues

When reporting issues, include:

1. VideoMilker version: `python -m videomilker --version`
2. Python version: `python --version`
3. Operating system
4. Error message or log output
5. Steps to reproduce the issue

### Performance Tips

#### Optimize Download Speed

- Use wired internet connection when possible
- Close other bandwidth-intensive applications
- Configure appropriate concurrent download limits
- Use quality presets instead of "best" for faster downloads

#### Manage Storage

- Regularly clean up download history
- Use day-based folder organization
- Configure auto-cleanup for old history entries
- Monitor download folder size

#### Batch Downloads

- Use batch files for multiple downloads
- Monitor system resources during batch processing
- Consider pausing/resuming large batches
- Use appropriate quality settings for batch downloads

## Keyboard Shortcuts

### Global Shortcuts (Available from Main Menu)

- **Ctrl+Q**: Quick Download
- **Ctrl+B**: Batch Download
- **Ctrl+A**: Audio Download
- **Ctrl+C**: Chapter Download
- **Ctrl+H**: Download History
- **Ctrl+F**: File Management

### Navigation

- **Arrow Keys**: Navigate menu options
- **Enter**: Select/confirm action
- **0**: Go back to previous menu
- **q**: Quit application (with confirmation)

### During Downloads

- **Ctrl+C**: Cancel current download
- **p**: Pause batch processing
- **s**: Skip current download in batch
- **r**: Resume paused downloads
- **q**: Quit application (with confirmation for active downloads)

### Input

- **Tab**: Auto-complete where applicable
- **Ctrl+D**: Finish URL input (batch mode)
- **Ctrl+C**: Cancel input

### File Management

- **d**: Delete selected files
- **o**: Organize files by type
- **c**: Clean up empty folders
- **a**: Analyze storage usage

## Examples

### Download a YouTube Video

```bash
# Interactive mode
python -m videomilker
# Select "Quick Download" and enter URL

# Direct download
python -m videomilker --link "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

### Batch Download from File

```bash
# Create batch file
echo "https://youtube.com/watch?v=video1" > batch.txt
echo "https://youtube.com/watch?v=video2" >> batch.txt

# Use batch file
python -m videomilker
# Select "Batch Download" → "Load from batch file" → select batch.txt
```

### Custom Configuration

```bash
# Set custom download path
python -m videomilker --download-path /Volumes/External/Downloads

# Use custom config file
python -m videomilker --config /path/to/custom_config.json
```

### Audio-Only Download

```bash
# Interactive mode
python -m videomilker
# Select "Audio Download" → Choose format (M4A, MP3, etc.) → Enter URL

# Quick audio download (using best audio format)
python -m videomilker --link "https://youtube.com/watch?v=..." --audio
```

### Chapter Download

```bash
# Interactive mode
python -m videomilker
# Select "Chapter Download" → Preview chapters → Select chapters → Download

# For videos with chapters, use chapter splitting
python -m videomilker --link "https://youtube.com/watch?v=..." --split-chapters
```

### File Management Operations

```bash
# Interactive mode for file management
python -m videomilker
# Select "File Management" → Choose operation:
# - Find duplicates
# - Clean up large/old files
# - Organize files by type
# - Analyze storage usage
```

### Configuration Management

```bash
# Export current configuration
python -m videomilker
# Select "Options & Settings" → "Configuration Management" → "Export Configuration"

# Import configuration from backup
python -m videomilker
# Select "Options & Settings" → "Configuration Management" → "Import Configuration"

# Run configuration wizard for first-time setup
python -m videomilker
# Select "Options & Settings" → "Configuration Management" → "Run Configuration Wizard"
```

### Verbose Mode for Debugging

```bash
python -m videomilker --verbose --link "https://youtube.com/watch?v=..."
```

## New Features Guide

### Auto-Download Mode

Enable auto-download to skip confirmation dialogs:

1. Go to Quick Download
2. Enter a URL
3. When prompted for confirmation, type 'auto'
4. This permanently enables auto-download for future downloads

### Queue Management

Manage multiple downloads efficiently:

1. Add URLs to queue via "Queue Management" menu
2. Configure concurrent download limits in "Performance Settings"
3. Use pause/resume/stop controls during processing
4. Monitor individual download progress

### Duplicate Detection

Keep your downloads organized:

1. Use "File Management" → "Find Duplicates"
2. Choose detection method:
   - Hash-based (most accurate)
   - Name and size based (faster)
   - Similar files (fuzzy matching)
3. Select removal strategy (newest, oldest, largest, smallest)

### Storage Analysis

Monitor disk usage:

1. Go to "File Management" → "Analyze Storage"
2. View breakdown by file type and size
3. Get recommendations for cleanup
4. Identify large files and old downloads

This user guide covers all the essential features and usage patterns for VideoMilker. For more detailed information, refer to the [API Reference](api-reference.md) or [Project Architecture](project-architecture.md) documentation.
