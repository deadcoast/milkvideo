# VideoMilker

An intuitive, tree-structured CLI interface for yt-dlp that eliminates complex command-line arguments and provides standardized workflows with visual feedback using the Rich library.

## Overview

VideoMilker transforms the complex yt-dlp experience into user-friendly workflows with:

- **Intuitive Navigation**: Clear menu hierarchy with consistent navigation patterns
- **Visual Feedback**: Rich terminal UI with borders, colors, and progress indicators
- **Smart Defaults**: Automated folder organization and sensible configuration
- **Error Recovery**: Graceful error handling with clear user guidance
- **Workflow Optimization**: Streamlined processes for common download scenarios

## Features

### Core Functionality

- **Quick Download**: Single video downloads with preview and confirmation
- **Audio-Only Download**: Extract audio from videos
- **Chapter Split Download**: Download videos with chapter separation
- **Batch Download**: Multiple URL processing with progress tracking
- **Resume Interrupted Downloads**: Continue failed or interrupted downloads
- **File Management**: Organize and manage downloaded files
- **Format Selection**: Intelligent format and quality selection
- **Progress Tracking**: Real-time download progress with speed and ETA
- **Error Handling**: Comprehensive error handling with user guidance

### File Organization

- **Day-based Folders**: Automatic organization by date (DD format)
- **Smart Naming**: Configurable file naming templates with `%(ext)s` extension support
- **Batch Logs**: Detailed logging of batch operations
- **Duplicate Prevention**: Unique filename generation

### Configuration Management

- **Persistent Settings**: JSON-based configuration storage using [Pydantic models](src/videomilker/config/settings.py)
- **Theme Support**: Multiple UI themes (default, dark, light, minimal)
- **Migration Support**: Automatic configuration version migration
- **Backup System**: Automatic configuration backups

### History & Analytics

- **Download History**: SQLite-based download tracking via [HistoryManager](src/videomilker/history/history_manager.py)
- **Statistics**: Comprehensive download analytics
- **Search & Filter**: Advanced history search capabilities
- **Export Options**: History export in JSON/CSV formats

### Advanced Features

- **yt-dlp Integration**: Full yt-dlp feature support via [VideoDownloader](src/videomilker/core/downloader.py)
- **Format Presets**: Predefined quality and format options
- **Post-processing**: Audio extraction, metadata embedding
- **SponsorBlock**: Sponsor segment handling
- **Proxy Support**: Network proxy configuration

## Quick Start Guide

### 1. Installation

#### Prerequisites

- Python 3.8+
- FFmpeg (for audio/video processing)
- curl (for network operations)

#### Easy Installation

Clone the repository and run the installation script:

```bash
git clone https://github.com/deadcoast/milkvideo.git
cd milkvideo
bash install.sh
```

This will:

- ✅ Check system dependencies (Python, FFmpeg, curl)
- ✅ Create a virtual environment
- ✅ Install all dependencies with correct architecture
- ✅ Install the `vmx` command globally
- ✅ Verify the installation

#### Manual Installation

If you prefer manual installation:

```bash
git clone https://github.com/deadcoast/milkvideo.git
cd milkvideo
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### 2. First Run

Launch VideoMilker:

```bash
vmx
```

You'll see the main menu with options for different download types.

### 3. Quick Download

For a single video download:

```bash
vmx --link "https://youtube.com/watch?v=example"
# or
vmx -l "https://youtube.com/watch?v=example"
```

### 4. Interactive Menu

Use the interactive menu for full functionality:

```bash
vmx
```

Navigate using:

- **Number keys** (1-9) to select options
- **Arrow keys** to navigate
- **Enter** to confirm
- **q** to quit
- **?** for keyboard shortcuts
- **0** to go back

## Installation

### Dependencies

- **Python 3.8+**: Required for the application
- **FFmpeg**: For audio/video processing (warning if not found)
- **curl**: For network operations (required)

### Automated Installation

The `install.sh` script provides an automated installation:

```bash
git clone https://github.com/deadcoast/milkvideo.git
cd milkvideo
bash install.sh
```

#### What the installer does

1. **System Checks**: Verifies Python version, FFmpeg, and curl
2. **Virtual Environment**: Creates and activates a Python virtual environment
3. **Dependencies**: Installs all required packages with architecture compatibility
4. **Package Installation**: Installs VideoMilker in development mode
5. **Global Command**: Creates the `vmx` command available system-wide
6. **Verification**: Tests the installation

#### Installation Output

The installer provides detailed feedback:

```bash
🎬 VideoMilker Installation
===========================
📁 Installing from: /path/to/milkvideo
✅ Python 3.12 found
✅ pip3 found
ℹ️ Checking system dependencies...
✅ ffmpeg found
✅ curl found
✅ Virtual environment already exists
ℹ️ Activating virtual environment...
✅ Virtual environment activated
ℹ️ Installing dependencies...
✅ Dependencies installed successfully
ℹ️ Installing VideoMilker...
✅ VideoMilker package installed
ℹ️ Creating wrapper script...
ℹ️ Installing vmx command...
✅ vmx installed globally at /usr/local/bin/vmx
ℹ️ Verifying installation...
✅ vmx command verified

🎉 Installation Complete!
========================

You can now use VideoMilker with these commands:
  vmx                    - Open the main menu
  vmx --link <URL>       - Quick download
  vmx --help             - Show help
  vmx --version          - Show version
```

### Custom Installation

For advanced users or custom setups:

```bash
# Clone repository
git clone https://github.com/deadcoast/milkvideo.git
cd milkvideo

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install package
pip install -e .

# Create wrapper script (optional)
echo '#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/.venv/bin/activate"
python -m videomilker.main "$@"' > vmx
chmod +x vmx

# Install globally (optional)
sudo cp vmx /usr/local/bin/vmx
```

## Usage

### Command Line Interface

#### Interactive Mode

Launch the interactive CLI:

```bash
vmx
```

#### Quick Download

Download a single URL directly:

```bash
vmx --link "https://youtube.com/watch?v=example"
# or
vmx -l "https://youtube.com/watch?v=example"
```

#### Custom Configuration

Use a custom configuration file:

```bash
vmx -c /path/to/config.json
```

#### Set Download Path

Override download path:

```bash
vmx -d /path/to/downloads
```

#### Help and Version

```bash
vmx --help      # Show help
vmx --version   # Show version
```

### Menu System

#### Main Menu

The main menu provides access to all features:

```plaintext
╭──────────────────── VideoMilker Main Menu ─────────────────────╮
│ 1 -  Quick Download                                            │
│ 2 -  Audio-Only Download                                       │
│ 3 -  Chapter Split Download                                    │
│ 4 -  Batch Download                                            │
│ 5 -  Resume Interrupted Downloads                              │
│ 6 -  File Management                                           │
│ 7 -  Options & Settings                                        │
│ 8 -  Download History                                          │
│ 9 -  Help & Info                                               │
│ q - Quit Application                                           │
│ 0 - ← Back                                                     │
│ Press ? for keyboard shortcuts                                 │
╰────────────────────────────────────────────────────────────────╯
```

#### Keyboard Shortcuts

Press `?` to see all available keyboard shortcuts:

- **Global Navigation**: `q` (quit), `0` (back), `?` (help)
- **Direct Menu Access**: `1-9` (menu options)
- **General Navigation**: Arrow keys, Enter, Tab
- **Input & Editing**: Ctrl+C (cancel), Ctrl+U (clear line)
- **Download Controls**: Space (pause/resume), Ctrl+C (cancel)
- **File Management**: Various shortcuts for file operations
- **History & Search**: Search and filter shortcuts
- **Configuration**: Settings management shortcuts

### Download Types

#### 1. Quick Download

- Single video download with preview
- Format and quality selection
- Real-time progress tracking

#### 2. Audio-Only Download

- Extract audio from videos
- Multiple audio format options
- Quality selection

#### 3. Chapter Split Download

- Download videos with chapter separation
- Individual chapter files
- Metadata preservation

#### 4. Batch Download

- Multiple URL processing
- File loading options (browse, path, recent, templates)
- Queue management with analytics
- Progress tracking for all downloads

#### 5. Resume Interrupted Downloads

- Continue failed downloads
- Resume from last successful point
- Error recovery

#### 6. File Management

- Organize downloaded files
- Duplicate detection
- Storage analysis
- Cleanup utilities

### Options & Settings

Access comprehensive settings:

- **Download Path**: Configure default download location
- **Format Settings**: Video/audio format preferences
- **File Organization**: Naming templates and folder structure
- **Performance**: Concurrent download limits
- **Advanced yt-dlp Options**: Custom yt-dlp parameters
- **Configuration Management**: Import/export settings

### Download History

Manage your download history:

- **Recent Downloads**: View latest downloads
- **Search & Filter**: Find specific downloads
- **Statistics**: Download analytics and metrics
- **Export Options**: Export history in various formats
- **Clear History**: Remove old or failed downloads

## Configuration

### Default Configuration

Configuration is stored in `~/.config/videomilker/videomilker.json`:

```json
{
  "version": "1.0.0",
  "download": {
    "path": "~/Downloads/VideoMilker",
    "create_day_folders": true,
    "file_naming": "%(upload_date)s_%(title)s.%(ext)s",
    "default_quality": "best",
    "default_format": "mp4",
    "max_concurrent": 3
  },
  "ui": {
    "theme": "default",
    "show_progress_details": true,
    "confirm_before_quit": true,
    "clear_screen": true
  },
  "history": {
    "max_entries": 1000,
    "auto_cleanup": true,
    "cleanup_days": 30
  }
}
```

### Themes

Available UI themes:

- **default**: Blue borders, yellow highlights
- **dark**: Bright colors for dark terminals
- **light**: Black borders for light terminals
- **minimal**: Minimal styling

## Structure and Organization

### Directory Structure

Files are organized automatically:

```plaintext
Downloads/
 VideoMilker/
     01/  # January 1st downloads
     02/  # January 2nd downloads
     15/  # January 15th downloads (current day)
        20241215_video-title-1.mp4
        20241215_video-title-2.mp4
        batch_downloads/
            20241215_14-30_batch.log
     config/
         videomilker.json
         batch_files/
         download_history.json
```

### File Naming

- **Single Downloads**: `YYYY-MM-DD_sanitized-video-title.ext`
- **Batch Downloads**: `YYYY-MM-DD_HH-MM_batch-N_sanitized-title.ext`
- **Config Files**: Standard naming in dedicated config folder

## Development

### Project Structure

```plaintext
milkvideo/
 src/videomilker/
    cli/              # CLI interface components
       menu_system.py      # Main menu controller
       menu_renderer.py    # Rich UI rendering
       input_handler.py    # User input processing
       styles.py           # UI themes and styling
    core/             # Core functionality
       downloader.py       # Main download management
       batch_processor.py  # Batch download logic
       progress_tracker.py # Progress monitoring
       file_manager.py     # File operations
    config/           # Configuration management
       settings.py         # Pydantic settings models
       config_manager.py   # Config file operations
       defaults.py         # Default configurations
    history/          # Download history
       history_manager.py  # History operations
    utils/            # Utility functions
    exceptions/       # Custom exceptions
        download_errors.py  # Download-related errors
        config_errors.py    # Configuration errors
        validation_errors.py # Validation errors
 tests/                # Test suite
 docs/                 # Documentation
 requirements.txt      # Dependencies
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/videomilker

# Run specific test file
pytest tests/test_videomilker.py
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Run tests with coverage
pytest --cov=src/
```

## Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- **[Installation Guide](docs/installation.md)** - Setup and installation instructions
- **[User Guide](docs/user-guide.md)** - Complete user manual with examples
- **[API Reference](docs/api-reference.md)** - Developer API documentation
- **[Directory Structure](docs/directory-structure.md)** - Project structure overview
- **[Project Architecture](docs/project-architecture.md)** - Design and architecture
- **[TODO](docs/TODO.md)** - Development tasks and improvements

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the [code style guidelines](docs/TODO.md#development-guidelines)
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Development Guidelines

- Follow Black code formatting
- Use type hints throughout
- Write comprehensive docstrings
- Add tests for new features
- Follow the established project structure

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **yt-dlp**: The powerful video downloader that makes this possible
- **Rich**: Beautiful terminal UI library
- **Click**: Command-line interface framework
- **Pydantic**: Data validation and settings management

## Troubleshooting

### Common Issues

#### Installation Issues

**Architecture Compatibility**: If you encounter `pydantic_core` architecture errors:

```bash
# Remove corrupted virtual environment
rm -rf .venv

# Recreate with correct architecture
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

**Permission Errors**: Check file permissions:

```bash
chmod +x install.sh
chmod +x vmx
```

#### Runtime Issues

**Import Errors**: Ensure you're using the virtual environment:

```bash
source .venv/bin/activate
```

**yt-dlp Not Found**: Install yt-dlp:

```bash
pip install yt-dlp
```

**FFmpeg Missing**: Install FFmpeg for audio/video processing:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

**Files Downloaded Without Extensions**: Ensure your configuration includes the `%(ext)s` placeholder:

```json
{
  "download": {
    "file_naming": "%(upload_date)s_%(title)s.%(ext)s"
  }
}
```

#### Menu Navigation Issues

**`?` Key Not Working**: The `?` key should show keyboard shortcuts. If it doesn't work:

1. Ensure you're in the main menu
2. Press `?` directly (not as part of another input)
3. Check that the menu system is properly initialized

**Clear History Not Working**: The clear history functionality has been fixed. If issues persist:

1. Check that the database file exists: `~/.config/videomilker/download_history.db`
2. Ensure proper permissions on the config directory
3. Try clearing specific types (all, old, failed) from the history menu

### Getting Help

- Check the configuration file for errors
- Enable verbose logging: `vmx --verbose`
- Review the download history for failed downloads
- Check the batch logs for detailed error information
- Consult the [User Guide](docs/user-guide.md#troubleshooting) for common solutions

## Roadmap

- [ ] Enhanced batch processing with pause/resume functionality
- [ ] Additional UI themes and customization options
- [ ] Advanced format selection interface
- [ ] Plugin system for extensibility
- [ ] Web interface
- [ ] Advanced post-processing options
- [ ] Integration with external media libraries
- [ ] Cloud storage integration
- [ ] Mobile app companion

For detailed development plans, see the [TODO](docs/TODO.md) document.
