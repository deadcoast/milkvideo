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
- **Batch Processing**: Download multiple videos with queue management
- **Smart File Organization**: Automatic day-based folder structure
- **Configuration Management**: Type-safe settings with Pydantic models
- **Download History**: Track and manage download history
- **Error Handling**: Comprehensive error handling with user-friendly messages

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

### ✅ Completed Features

- Rich-based terminal UI with menu system
- Click CLI with command-line options
- yt-dlp integration for video downloading
- Configuration management with JSON files
- Download history tracking
- Batch download processing
- Progress tracking and display
- File organization and naming
- Error handling and recovery
- Type-safe configuration with Pydantic

### 🚧 In Development

- Enhanced batch processing features
- Additional UI themes and customization
- Advanced format selection options
- Plugin system for extensibility

### 📋 Planned Features

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
