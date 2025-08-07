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
- **Batch Download**: Multiple URL processing with progress tracking
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

## Installation

### Prerequisites

- Python 3.8+
- yt-dlp
- FFmpeg (for audio/video processing)

### Setup

#### Option 1: Global Installation (Recommended)

Clone the repository:

```bash
git clone https://github.com/deadcoast/milkvideo.git
cd milkvideo
```

Run the global installation script:

```bash
./install_global.sh
```

This will:

- Create a virtual environment
- Install all dependencies
- Make `vmx` available globally
- You can then use `vmx` from anywhere in your terminal

#### Option 2: Manual Installation

Clone the repository:

```bash
git clone https://github.com/deadcoast/milkvideo.git
cd milkvideo
```

Create and activate virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install the package in development mode:

```bash
pip install -e .
```

## Usage

### Interactive Mode

Launch the interactive CLI:

```bash
python -m videomilker
```

### Quick Download

Download a single URL directly:

```bash
python -m videomilker --link "https://youtube.com/watch?v=example"
# or
python -m videomilker -l "https://youtube.com/watch?v=example"
```

### Custom Configuration

Use a custom configuration file:

```bash
python -m videomilker -c /path/to/config.json
```

### Set Download Path

Override download path:

```bash
python -m videomilker -d /path/to/downloads
```

### Help and Version

```bash
python -m videomilker --help      # Show help
python -m videomilker --version   # Show version
```

## Menu System

### Main Menu

The main menu is rendered by [MenuRenderer](src/videomilker/cli/menu_renderer.py) and controlled by [MenuSystem](src/videomilker/cli/menu_system.py):

```plaintext
VideoMilker v1.0
┌─────────────────────────────────────────┐
│           Welcome to VideoMilker!       │
│─────────────────────────────────────────│
│                                         │
│  [1] Quick Download                     │
│  [2] Batch Download                     │
│  [3] Options & Settings                 │
│  [4] Download History                   │
│  [5] Help & Info                        │
│                                         │
│  [q] Quit Application                   │
└─────────────────────────────────────────┘
```

### Single URL Download

- Enter video URL (validated by [InputHandler](src/videomilker/cli/input_handler.py))
- Preview video information
- Confirm download
- Real-time progress tracking via [ProgressTracker](src/videomilker/core/progress_tracker.py)

### Batch URL Download

- Direct URL input
- Load from batch file
- Progress tracking for multiple downloads via [BatchProcessor](src/videomilker/core/batch_processor.py)
- Comprehensive error handling

### Options & Settings Menu

- Download path configuration
- Format and quality settings
- File organization options
- Advanced yt-dlp options
- Configuration management via [ConfigManager](src/videomilker/config/config_manager.py)

### Download History Menu

- View recent downloads
- Search and filter history
- Export download data
- Clear history

## Configuration

### Default Configuration

Configuration is stored in `~/.config/videomilker/videomilker.json` and managed by [ConfigManager](src/videomilker/config/config_manager.py):

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
    "confirm_before_quit": true
  },
  "history": {
    "max_entries": 1000,
    "auto_cleanup": true,
    "cleanup_days": 30
  }
}
```

### Themes

UI themes are defined in [styles.py](src/videomilker/cli/styles.py):

- **default**: Blue borders, yellow highlights
- **dark**: Bright colors for dark terminals
- **light**: Black borders for light terminals
- **minimal**: Minimal styling

## Structure and Organization

### Directory Structure

Files are organized by [FileManager](src/videomilker/core/file_manager.py):

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
        ├── batch_files/
        └── download_history.json
```

### File Naming

- **Single Downloads**: `YYYY-MM-DD_sanitized-video-title.ext`
- **Batch Downloads**: `YYYY-MM-DD_HH-MM_batch-N_sanitized-title.ext`
- **Config Files**: Standard naming in dedicated config folder

## Development

### Project Structure

```plaintext
milkvideo/
├── src/videomilker/
│   ├── cli/              # CLI interface components
│   │   ├── menu_system.py      # Main menu controller
│   │   ├── menu_renderer.py    # Rich UI rendering
│   │   ├── input_handler.py    # User input processing
│   │   └── styles.py           # UI themes and styling
│   ├── core/             # Core functionality
│   │   ├── downloader.py       # Main download management
│   │   ├── batch_processor.py  # Batch download logic
│   │   ├── progress_tracker.py # Progress monitoring
│   │   └── file_manager.py     # File operations
│   ├── config/           # Configuration management
│   │   ├── settings.py         # Pydantic settings models
│   │   ├── config_manager.py   # Config file operations
│   │   └── defaults.py         # Default configurations
│   ├── history/          # Download history
│   │   └── history_manager.py  # History operations
│   ├── utils/            # Utility functions
│   └── exceptions/       # Custom exceptions
│       ├── download_errors.py  # Download-related errors
│       ├── config_errors.py    # Configuration errors
│       └── validation_errors.py # Validation errors
├── tests/                # Test suite
├── docs/                 # Documentation
└── requirements.txt      # Dependencies
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

**Permission Errors**: Check file permissions and paths:

```bash
chmod +x src/videomilker/main.py
```

**Files Downloaded Without Extensions**: This issue has been fixed. Ensure your configuration includes the `%(ext)s` placeholder:

```json
{
  "download": {
    "file_naming": "%(upload_date)s_%(title)s.%(ext)s"
  }
}
```

### Getting Help

- Check the configuration file for errors
- Enable verbose logging: `python -m videomilker --verbose`
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
