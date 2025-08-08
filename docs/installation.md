# Installation Guide

This guide covers how to install and set up VideoMilker on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- git (for development installation)

## Quick Start

### Option 1: Using pip (Recommended)

```bash
pip install videomilker
```

### Option 2: From Source

```bash
# Clone the repository
git clone https://github.com/videomilker/videomilker.git
cd videomilker

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Verification

Verify your installation by running:

```bash
videomilker --version
```

You should see the VideoMilker version number.

## First Run

Start VideoMilker with:

```bash
videomilker
```

On first run, VideoMilker will:

1. Create configuration directories
2. Set up default download locations
3. Show the main menu

## Configuration

### Default Locations

VideoMilker creates the following directories:

- **Downloads**: `~/Downloads/VideoMilker/`
- **Config**: `~/.videomilker/`
- **Logs**: `~/.videomilker/logs/`

### Custom Configuration

You can specify a custom config file:

```bash
videomilker --config /path/to/your/config.json
```

## Dependencies

VideoMilker automatically installs:

- `yt-dlp` - Video downloading engine
- `rich` - Terminal UI library
- `click` - Command-line interface framework
- `pydantic` - Data validation
- `toml` - Configuration file support

## Troubleshooting

### Common Issues

- **"Command not found: videomilker"**

- Ensure pip installation completed successfully
- Check that Python scripts directory is in your PATH

- **"Permission denied" errors**

- On macOS/Linux, you may need to run: `chmod +x ~/.local/bin/videomilker`
- Or install with: `pip install --user videomilker`

- **yt-dlp not found**

- VideoMilker will attempt to use the system yt-dlp installation
- If not found, it will use the bundled version

### Getting Help

If you encounter issues:

1. Run with verbose mode: `videomilker --verbose`
2. Check the logs in `~/.videomilker/logs/`
3. Report issues on GitHub with log output

## Next Steps

- Read the [User Guide](user_guide.md) for detailed usage instructions
- Customize your [Configuration](user_guide.md#configuration)
- Explore [Advanced Features](user_guide.md#advanced-features)
