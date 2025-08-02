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
- **Smart Naming**: Configurable file naming templates
- **Batch Logs**: Detailed logging of batch operations
- **Duplicate Prevention**: Unique filename generation

### Configuration Management

- **Persistent Settings**: JSON-based configuration storage
- **Theme Support**: Multiple UI themes (default, dark, light, minimal)
- **Migration Support**: Automatic configuration version migration
- **Backup System**: Automatic configuration backups

### History & Analytics

- **Download History**: SQLite-based download tracking
- **Statistics**: Comprehensive download analytics
- **Search & Filter**: Advanced history search capabilities
- **Export Options**: History export in JSON/CSV formats

### Advanced Features

- **yt-dlp Integration**: Full yt-dlp feature support
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
./scripts/install_global.sh
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

1. Install the package in development mode:

```bash
pip install -e .
```

## Usage

### Interactive Mode

Launch the interactive CLI:

```bash
vmx
```

### Quick Download

Download a single URL directly:

```bash
vmx --link "https://youtube.com/watch?v=example"
# or
vmx -l "https://youtube.com/watch?v=example"
```

### Custom Configuration

Use a custom configuration file:

```bash
vmx -c /path/to/config.json
```

### Set Download Path

Override download path:

```bash
vmx -d /path/to/downloads
```

### Help and Version

```bash
vmx --help      # Show help
vmx --version   # Show version
```

## Menu System

### Main Menu

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

- Enter video URL
- Preview video information
- Confirm download
- Real-time progress tracking

### Batch URL Download

- Direct URL input
- Load from batch file
- Progress tracking for multiple downloads
- Comprehensive error handling

### Options & Settings Menu

- Download path configuration
- Format and quality settings
- File organization options
- Advanced yt-dlp options
- Configuration management

### Download History Menu

- View recent downloads
- Search and filter history
- Export download data
- Clear history

## Configuration Menu

### Default Configuration

Configuration is stored in `~/.config/videomilker/videomilker.json`:

```json
{
  "version": "1.0.0",
  "download": {
    "path": "~/Downloads/VideoMilker",
    "create_day_folders": true,
    "file_naming": "%(upload_date)s_%(title)s",
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

- **default**: Blue borders, yellow highlights
- **dark**: Bright colors for dark terminals
- **light**: Black borders for light terminals
- **minimal**: Minimal styling

## File Organization Menu

### Directory Structure

```plaintext
Downloads/
└── VideoMilker/
    ├── 01/  # January 1st downloads
    ├── 02/  # January 2nd downloads
    ├── 15/  # January 15th downloads (current day)
    │   ├── YYYY-MM-DD_video-title-1.mp4
    │   ├── YYYY-MM-DD_video-title-2.mp4
    │   └── batch_downloads/
    │       └── YYYY-MM-DD_HH-MM_batch.log
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
│   ├── core/             # Core functionality
│   ├── config/           # Configuration management
│   ├── history/          # Download history
│   ├── utils/            # Utility functions
│   └── exceptions/       # Custom exceptions
├── tests/                # Test suite
├── docs/                 # Documentation
└── requirements.txt      # Dependencies
```

### Running Tests

```bash
python test_videomilker.py
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

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

### Getting Help

- Check the configuration file for errors
- Enable verbose logging: `python -m src.videomilker.main -v`
- Review the download history for failed downloads
- Check the batch logs for detailed error information

## Roadmap

- [ ] GUI version using Tkinter/PyQt
- [ ] Web interface
- [ ] Plugin system
- [ ] Advanced format selection
- [ ] Download scheduling
- [ ] Cloud storage integration
- [ ] Mobile app companion

---
