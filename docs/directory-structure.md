# VideoMilker Complete Directory Structure

```plaintext
milkvideo/                              # Root project directory
├── .venv/                              # Virtual environment (existing)
├── .gitignore                          # Git ignore file
├── README.md                           # Project documentation
├── requirements.txt                    # Python dependencies
├── setup.py                            # Package setup configuration
├── pyproject.toml                      # Modern Python project config
├── LICENSE                             # Project license
├── sample_batch.txt                    # Sample batch file for testing
├── install.sh                          # Installation script
├── install_global.sh                   # Global installation script
│
├── src/                               # Main source code directory
│   ├── __init__.py
│   ├── remove_emojis.py               # Utility for cleaning filenames
│   ├── videomilker/                   # Main package
│   │   ├── __init__.py
│   │   ├── main.py                    # Entry point for CLI (Click-based)
│   │   ├── version.py                 # Version management
│   │   │
│   │   ├── cli/                       # CLI interface modules
│   │   │   ├── __init__.py
│   │   │   ├── menu_system.py         # Main menu controller and logic
│   │   │   ├── menu_renderer.py       # Rich UI rendering and display
│   │   │   ├── input_handler.py       # User input processing and validation
│   │   │   └── styles.py              # UI themes and styling definitions
│   │   │
│   │   ├── core/                      # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── downloader.py          # Main download management with yt-dlp
│   │   │   ├── batch_processor.py     # Batch download logic and queue management
│   │   │   ├── progress_tracker.py    # Progress monitoring and display
│   │   │   └── file_manager.py        # File operations and organization
│   │   │
│   │   ├── config/                    # Configuration management
│   │   │   ├── __init__.py
│   │   │   ├── settings.py            # Pydantic-based settings models
│   │   │   ├── config_manager.py      # Config file operations and migration
│   │   │   └── defaults.py            # Default configurations and presets
│   │   │
│   │   ├── history/                   # Download history
│   │   │   ├── __init__.py
│   │   │   └── history_manager.py     # History operations and database handling
│   │   │
│   │   ├── utils/                     # Utility functions
│   │   │   └── __init__.py            # Currently empty, ready for utilities
│   │   │
│   │   └── exceptions/                # Custom exceptions
│   │       ├── __init__.py
│   │       ├── download_errors.py     # Download-related errors and mappings
│   │       ├── config_errors.py       # Configuration errors
│   │       └── validation_errors.py   # Validation errors
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── conftest.py                    # Pytest configuration and fixtures
│   ├── test_videomilker.py            # Main application tests
│   ├── test_auto_download.py          # Auto-download functionality tests
│   ├── test_batch_functionality.py    # Batch processing tests
│   ├── test_cli/                      # CLI tests
│   │   └── __init__.py
│   ├── test_config/                   # Configuration tests
│   │   └── __init__.py
│   ├── test_core/                     # Core functionality tests
│   │   └── __init__.py
│   └── test_utils/                    # Utility tests
│       └── __init__.py
│
├── docs/                              # Documentation
│   ├── README.md                      # Documentation overview
│   ├── installation.md                # Installation guide
│   ├── directory-structure.md         # This file - project structure
│   ├── project-architecture.md        # Design and architecture overview
│   └── TODO.md                        # Development tasks and improvements
│
├── config/                            # Default configuration files
│   ├── default_config.json            # Default application configuration
│   ├── themes/                        # UI theme configurations
│   └── templates/                     # Template files
│
├── data/                              # Application data directory
│   ├── downloads/                     # Default download location
│   │   └── .gitkeep
│   ├── history/                       # Download history storage
│   │   └── .gitkeep
│   ├── logs/                          # Application logs
│   │   └── .gitkeep
│   └── temp/                          # Temporary files
│       └── .gitkeep
│
├── scripts/                           # Utility scripts
│   └── setup_project.py               # Project setup and initialization script
│
├── assets/                            # Static assets
│   ├── icons/                         # Application icons
│   └── templates/                     # Asset templates
│
├── htmlcov/                           # Test coverage reports
├── .coverage                          # Coverage data
├── coverage.xml                       # Coverage report in XML format
└── build/                             # Build artifacts (if any)
```

## Key Directory Explanations

### **src/videomilker/** - Main Package

- **main.py**: Click-based CLI entry point with command-line options
- **cli/**: Rich-based terminal UI components
  - `menu_system.py`: Main menu logic and state management
  - `menu_renderer.py`: Rich UI rendering and display components
  - `input_handler.py`: User input processing and validation
  - `styles.py`: UI styling and theme definitions
- **core/**: Core download and processing functionality
  - `downloader.py`: yt-dlp integration and download management
  - `batch_processor.py`: Batch download queue and processing
  - `progress_tracker.py`: Progress monitoring with Rich UI
  - `file_manager.py`: File operations and organization
- **config/**: Configuration management system
  - `settings.py`: Pydantic models for type-safe configuration
  - `config_manager.py`: Config file operations and migration
  - `defaults.py`: Default settings and presets
- **history/**: Download history tracking
  - `history_manager.py`: History operations and database management
- **exceptions/**: Custom exception classes
  - `download_errors.py`: Comprehensive error handling for downloads
  - `config_errors.py`: Configuration-related errors
  - `validation_errors.py`: Input validation errors
- **utils/**: Shared utility functions (currently minimal)

### **tests/** - Test Suite

- Organized to mirror the source structure
- Uses pytest framework
- Includes fixtures in `conftest.py`
- Tests for main functionality, CLI, config, and core components

### **config/** - Configuration

- `default_config.json`: Default application settings
- User config stored in `~/.config/videomilker/videomilker.json`
- Theme and template configurations

### **data/** - Application Data

- Download storage location
- History database storage
- Application logs
- Temporary file storage

### **docs/** - Documentation

- Project structure and architecture documentation
- Installation and setup guides
- Development tasks and TODO items

## Key Implementation Details

### **CLI Framework**: Click

- Command-line argument parsing
- Version display
- Help text generation
- Direct download options (`--link`, `--url`)

### **UI Framework**: Rich

- Terminal UI components
- Progress bars and spinners
- Colorized output
- Tables and panels

### **Download Engine**: yt-dlp

- Video downloading capabilities
- Format selection
- Progress tracking
- Error handling

### **Configuration**: Pydantic

- Type-safe configuration models
- JSON serialization/deserialization
- Validation and defaults

### **File Organization**

- Day-based folder structure (DD format)
- Configurable file naming templates
- Automatic path creation

This structure supports:

- ✅ Modular development and testing
- ✅ Rich terminal UI with Click CLI
- ✅ Type-safe configuration management
- ✅ Comprehensive error handling
- ✅ Download history tracking
- ✅ Batch processing capabilities
