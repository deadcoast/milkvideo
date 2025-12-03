# VideoMilker CLI Design Plan - Enhanced

## Overview

An intuitive, tree-structured CLI interface for yt-dlp that eliminates complex command-line arguments and provides standardized workflows with visual feedback using the Rich library.

## Core Design Principles

- **Intuitive Navigation**: Clear menu hierarchy with consistent navigation patterns
- **Visual Feedback**: Rich terminal UI with borders, colors, and progress indicators
- **Smart Defaults**: Automated folder organization and sensible configuration
- **Error Recovery**: Graceful error handling with clear user guidance
- **Workflow Optimization**: Streamlined processes for common download scenarios

## Menu Architecture

### Main Menu Structure

```bash
VideoMilker v1.0

           Welcome to VideoMilker!


  [1] Quick Download
  [2] Batch Download
  [3] Queue Management
  [4] Audio Download (Ctrl+A)
  [5] Chapter Download (Ctrl+C)
  [6] Options & Settings
  [7] Download History
  [8] File Management (Ctrl+F)
  [9] Help & Info

  [q] Quit Application


Global Shortcuts:
• Ctrl+Q: Quick Download  • Ctrl+B: Batch Download
• Ctrl+A: Audio Download  • Ctrl+C: Chapter Download
• Ctrl+H: History         • Ctrl+F: File Management
```

### 1. Quick Download Menu

```bash
Quick Download

  Enter video URL below:


  URL: [_________________________]

  [Enter] Start Download
  [v] Preview Video Info
  [f] Choose Format/Quality

  [0] ← Back to Main Menu

```

### 2. Batch Download Menu

```bash
Batch Download

  Choose batch download method:


  [1] Paste URLs directly
  [2] Load from batch file
  [3] Browse for batch file

  [0] ← Back to Main Menu

```

#### 2.1 Direct URL Input

```bash
Batch Download - Direct Input

  Paste URLs (one per line, Ctrl+D to
  finish):


  1. https://youtube.com/watch?v=...
  2. https://youtube.com/watch?v=...
  3. [Enter URL or Ctrl+D to finish]

  [Enter] Add URL
  [d] Done (start download)
  [c] Clear all URLs

  [0] ← Back to Batch Menu

```

### 3. Options & Settings Menu

```bash
Options & Settings

  Configure VideoMilker settings:


  [1] Download Path Settings
  [2] Audio/Video Format Settings
  [3] File Organization Settings
  [4] Advanced yt-dlp Options
  [5] View/Edit Config Files
  [6] Reset to Defaults

  [0] ← Back to Main Menu

```

#### 3.1 Download Path Settings

```bash
Download Path Settings

  Current Path: /Users/name/Downloads


  [1] Set Custom Download Path
  [2] Use Default Downloads Folder
  [3] Browse for Folder
  [4] Save as Default (Config)

  Folder Structure:
   Downloads/
       VideoMilker/
           DD/ (current day)

  [0] ← Back to Options Menu

```

### 4. Download History Menu

```bash
Download History

  Recent Downloads:


  2024-01-15 (Today)
   Video Title 1.mp4 (25.3 MB)
   Video Title 2.mp4 (48.7 MB)

  2024-01-14
   Video Title 3.mp4 (15.2 MB)

  [1] View Full History
  [2] Clear History
  [3] Open Download Folder

  [0] ← Back to Main Menu

```

## File Organization System

### Directory Structure

```plaintext
Downloads/
 VideoMilker/
     01/  # January 1st downloads
     02/  # January 2nd downloads
     15/  # January 15th downloads (current day)
        YYYY-MM-DD_video-title-1.mp4
        YYYY-MM-DD_video-title-2.mp4
        batch_downloads/
            YYYY-MM-DD_HH-MM_batch.log
     config/
         videomilker.json
         batch_files/
         download_history.json
```

### File Naming Convention

- **Single Downloads**: `YYYY-MM-DD_sanitized-video-title.ext`
- **Batch Downloads**: `YYYY-MM-DD_HH-MM_batch-N_sanitized-title.ext`
- **Config Files**: Standard naming in dedicated config folder

## Progress & Feedback System

### Download Progress Display

```bash
Downloading: Video Title Here

  Progress:   67%
  Speed: 2.4 MB/s    ETA: 00:45
  Size: 15.3 MB / 22.8 MB

  Status: Downloading video stream...

  [Ctrl+C] Cancel Download

```

### Batch Progress Display

```bash
Batch Download Progress

  Overall:   3/8

  Video 1 - Complete (25.3 MB)
  Video 2 - Complete (18.7 MB)
  Video 3 - Downloading... 45%
  Video 4 - Queued
  Video 5 - Queued

  [p] Pause  [s] Skip Current  [q] Quit

```

## Error Handling & User Guidance

### Error Display Format

```bash
Download Error

  Error: Video unavailable or private

  URL: https://youtube.com/watch?v=...

  Suggestions:
  • Check if video is public
  • Verify URL is correct
  • Try again later

  [r] Retry  [s] Skip  [c] Continue
  [0] ← Back to Main Menu

```

## Configuration Management

### Config File Structure (JSON)

```json
{
  "version": "1.0.0",
  "settings": {
    "download_path": "/Users/name/Downloads/VideoMilker",
    "create_day_folders": true,
    "file_naming": "YYYY-MM-DD_{title}",
    "default_quality": "best",
    "default_format": "mp4",
    "max_concurrent_downloads": 3,
    "auto_subtitle": false,
    "save_thumbnail": false
  },
  "history": {
    "max_entries": 1000,
    "auto_cleanup": true,
    "cleanup_days": 30
  },
  "ui": {
    "theme": "default",
    "show_progress_details": true,
    "confirm_before_quit": true
  }
}
```

## Implementation Specifications

### Required Libraries

- **Rich**: Terminal UI, progress bars, styling
- **Click**: Command-line interface framework
- **yt-dlp**: Video downloading engine
- **pathlib**: Cross-platform path handling
- **json**: Configuration management
- **datetime**: Date/time operations

### Key Features Implementation

#### Smart Folder Management

```python
def ensure_day_folder(base_path: Path) -> Path:
    """Create and return today's folder (DD format)"""
    today = datetime.now()
    day_folder = base_path / f"{today.day:02d}"
    day_folder.mkdir(parents=True, exist_ok=True)
    return day_folder
```

#### Download History Tracking

```python
def log_download(url: str, filename: str, size: int, status: str):
    """Log download to history with metadata"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "url": url,
        "filename": filename,
        "size": size,
        "status": status,
        "path": str(download_path)
    }
    # Append to history.json
```

### Navigation Controls

- **Arrow Keys**: Navigate menu options
- **Enter**: Select/confirm action
- **0**: Go back to previous menu
- **q**: Quit application (with confirmation)
- **Ctrl+C**: Cancel current operation
- **Tab**: Auto-complete where applicable

## User Experience Enhancements

### Quality of Life Features

1. **Auto-detection**: Recognize video platforms and suggest optimal settings
2. **Resume Downloads**: Continue interrupted downloads
3. **Duplicate Detection**: Warn about already downloaded videos
4. **Format Preview**: Show available formats before download
5. **Keyboard Shortcuts**: Quick access to common actions
6. **Search History**: Recent URLs for easy re-download
7. **Export Options**: Save download lists for later use
8. **Auto-Download Mode**: Skip confirmation dialogs permanently
9. **Queue Management**: Pause/resume/stop download queues
10. **Audio-Only Downloads**: Extract audio with format selection
11. **Chapter Splitting**: Download videos with chapter extraction
12. **File Management**: Organize and clean up download directories
13. **Configuration Tools**: Export/import settings with validation
14. **Storage Analysis**: Monitor disk usage and get recommendations

### Accessibility Considerations

- High contrast color schemes
- Clear text descriptions for all visual elements
- Keyboard-only navigation support
- Screen reader compatible output
- Adjustable interface elements

## Testing Scenarios

### Core Functionality Tests

- [x] Single video download with progress tracking
- [x] Batch download with mixed success/failure
- [x] Folder creation and organization
- [x] Config file read/write operations
- [x] Error handling and recovery
- [x] Menu navigation and state management
- [x] History logging and retrieval
- [x] Audio-only downloads with format selection
- [x] Chapter splitting and extraction
- [x] Queue management with pause/resume
- [x] Duplicate detection and file cleanup
- [x] Configuration validation and auto-fix
- [x] File organization and storage analysis

### Edge Cases

- [x] Invalid URLs handling
- [x] Network interruption recovery
- [x] Disk space warnings
- [x] Permission errors
- [x] Large batch file processing
- [x] Special characters in video titles
- [x] Concurrent download limits
- [x] Memory optimization for large batches
- [x] Download resume after interruption
- [x] Configuration file corruption handling
- [x] User-friendly error messages with suggestions

## New Architecture Components

### Queue Management System

The `DownloadQueue` class provides thread-safe queue management for batch operations:

- **Thread Safety**: Uses `threading.Lock` for concurrent access
- **State Management**: Tracks queue status (paused, stopped, processing)
- **Progress Tracking**: Monitors individual and overall progress
- **Memory Efficiency**: Processes items in chunks to manage memory usage

### File Management System

Enhanced file operations with intelligent organization:

- **Duplicate Detection**: Multiple algorithms (hash-based, name/size, similarity)
- **Storage Analysis**: Disk usage monitoring with recommendations
- **Cleanup Utilities**: Automated removal of large/old files and empty folders
- **Organization**: Type-based file sorting and folder structure

### Configuration System

Configuration system with validation and auto-fix:

- **Validation Engine**: Comprehensive setting validation on startup
- **Auto-Fix**: Automatic correction of common configuration issues
- **Export/Import**: Backup and restore configuration with metadata
- **Migration**: Version-aware configuration migration
- **Wizard**: First-time user setup guide

### Error Handling Framework

User-friendly error management system:

- **Error Mapping**: Translates technical yt-dlp errors to user-friendly messages
- **Context Enrichment**: Adds helpful context and suggestions to errors
- **Display Formatting**: Rich formatting for error presentation
- **Recovery Suggestions**: Actionable suggestions for error resolution

### Enhanced Progress System

Detailed progress tracking and display:

- **Real-time Metrics**: Speed, ETA, and detailed progress information
- **Batch Progress**: Individual and overall batch progress tracking
- **Memory Monitoring**: Track memory usage during large batch operations
- **Resume Support**: Seamless continuation of interrupted downloads

### Audio Processing Pipeline

Specialized audio download and processing:

- **Format Selection**: Multiple audio format support (M4A, MP3, OPUS, AAC, FLAC)
- **Quality Configuration**: Bitrate and quality settings
- **Batch Processing**: Concurrent audio processing with limits
- **Metadata Preservation**: Maintain audio metadata and tags

### Chapter Management System

Video chapter extraction and processing:

- **Chapter Detection**: Automatic chapter information extraction
- **Preview Interface**: User-friendly chapter preview and selection
- **Split Processing**: Download individual chapters as separate files
- **Metadata Integration**: Embed chapter information in output files

## Performance Optimizations

### Memory Management

- **Chunked Processing**: Process large batches in memory-efficient chunks
- **Garbage Collection**: Explicit memory cleanup after operations
- **Memory Monitoring**: Track and log memory usage patterns
- **Resource Limits**: Configurable concurrent download limits

### Threading Architecture

- **Thread Pool**: Managed thread pool for concurrent downloads
- **Thread Safety**: All shared resources protected with appropriate locks
- **Graceful Shutdown**: Clean termination of active threads
- **Error Isolation**: Thread-level error handling without affecting other operations

### Caching Strategy

- **Configuration Cache**: In-memory configuration caching
- **Format Cache**: Cache video format information to reduce API calls
- **History Cache**: Efficient history lookup and search
- **Metadata Cache**: Cache video metadata for quick access

This enhanced design provides a comprehensive foundation for building an intuitive, robust CLI interface that transforms the complex yt-dlp experience into user-friendly workflows.
