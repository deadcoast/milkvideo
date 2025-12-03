# VideoMilker Documentation

Welcome to the VideoMilker documentation. This directory contains comprehensive guides and references for using and developing VideoMilker.

## Documentation Structure

- **[Installation Guide](installation.md)** - How to install and set up VideoMilker
- **[User Guide](user-guide.md)** - Complete user manual with examples and troubleshooting
- **[API Reference](api-reference.md)** - Comprehensive developer API documentation
- **[Directory Structure](directory-structure.md)** - Complete project structure overview
- **[Project Architecture](project-architecture.md)** - Design and architecture overview
- **[TODO](TODO.md)** - Development tasks and improvements

## Quick Links

### For Users

- [Getting Started](installation.md#quick-start)
- [Basic Usage](user-guide.md#basic-usage)
- [Configuration](user-guide.md#configuration)
- [Troubleshooting](user-guide.md#troubleshooting)

### For Developers

- [Project Structure](directory-structure.md)
- [API Documentation](api-reference.md)
- [Architecture Overview](project-architecture.md)
- [Development Tasks](TODO.md)

## What is VideoMilker?

VideoMilker is an intuitive, tree-structured CLI interface for yt-dlp that eliminates complex command-line arguments and provides standardized workflows with visual feedback using the Rich library.

### Key Features

- **Rich Terminal UI**: Beautiful, interactive interface with progress bars and colorized output
- **Click-based CLI**: Command-line interface with options for direct downloads
- **Batch Processing**: Download multiple videos with queue management and pause/resume
- **Smart File Organization**: Automatic day-based folder structure with duplicate detection
- **Configuration Management**: Type-safe settings with Pydantic models, validation, and auto-fix
- **Download History**: Track and manage download history with advanced search
- **Error Handling**: Comprehensive error handling with user-friendly messages and suggestions
- **Audio Downloads**: Audio-only downloads with multiple format support
- **Chapter Splitting**: Download videos with chapter extraction and preview
- **Format Selection**: Preview and select video/audio formats before download
- **File Management**: Duplicate detection, cleanup utilities, and storage analysis
- **Keyboard Shortcuts**: Quick access to common actions and global shortcuts
- **Queue Management**: Advanced download queue with pause/resume/stop functionality
- **Download Resume**: Resume interrupted downloads automatically
- **Configuration Tools**: Export/import settings, validation, and first-time setup wizard

### Technology Stack

- **Python 3.8+**: Core language
- **Click**: CLI framework
- **Rich**: Terminal UI library
- **yt-dlp**: Video downloading engine
- **Pydantic**: Configuration and data validation
- **pytest**: Testing framework

## Quick Start

### Installation

```bash
git clone https://github.com/deadcoast/milkvideo.git
cd milkvideo
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Basic Usage

```bash
# Interactive mode
python -m videomilker

# Quick download
python -m videomilker --link "https://youtube.com/watch?v=..."

# With custom config
python -m videomilker --config /path/to/config.json --verbose
```

## Project Status

### Completed Features

- Rich-based terminal UI with menu system and keyboard shortcuts
- Click CLI with command-line options and direct download support
- yt-dlp integration for video downloading with format selection
- Configuration management with JSON files, validation, and auto-fix
- Download history tracking with advanced search functionality
- Batch download processing with queue management and pause/resume
- Progress tracking and display with detailed speed and ETA information
- File organization and naming with day-based folders
- Error handling and recovery with user-friendly messages
- Type-safe configuration with Pydantic models
- Auto-download option with permanent setting capability
- Enhanced download path configuration with folder browser
- Format preview and selection before download
- Configuration export/import functionality
- Configuration wizard for first-time users
- Confirmation dialogs for destructive actions
- Audio-only download option with multiple format support
- Chapter splitting functionality with preview
- Concurrent download limits with threading support
- Memory optimization for large batch downloads
- Download resume for interrupted downloads
- Duplicate detection with multiple algorithms (hash-based, name/size-based, similar files)
- Comprehensive file cleanup utilities (large files, old files, empty folders)
- Storage analysis and recommendations
- File organization by type with extension-based sorting

### In Development

- Additional UI themes and customization options
- Advanced format selection interface improvements
- Plugin system for extensibility

### Planned Features

- Web interface (optional)
- Advanced post-processing options
- Integration with external media libraries
- Cloud storage support
- Mobile companion app

## Support

If you need help or have questions:

1. Check the [User Guide](user-guide.md) for common solutions
2. Look through existing [GitHub Issues](https://github.com/deadcoast/milkvideo/issues)
3. Create a new issue if your problem isn't covered

## Contributing

We welcome contributions! Please read our [Project Architecture](project-architecture.md) to understand the design principles and [API Reference](api-reference.md) for development details.

### Development Setup

```bash
git clone https://github.com/deadcoast/milkvideo.git
cd milkvideo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest  # Run tests
```

### Code Style

- Follow Black code formatting
- Use type hints throughout
- Write comprehensive docstrings
- Add tests for new features
- Follow the established project structure

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
