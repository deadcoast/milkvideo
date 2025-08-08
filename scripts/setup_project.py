#!/usr/bin/env python3
"""
VideoMilker Project Setup Script

This script creates the complete directory structure and initial files
for the VideoMilker CLI application.

Usage:
    python setup_project.py [--force] [--dry-run]
    
Options:
    --force     Overwrite existing files
    --dry-run   Show what would be created without actually creating files
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

class ProjectSetup:
    """Handles the creation of project directory structure and initial files."""
    
    def __init__(self, root_path: Path, force: bool = False, dry_run: bool = False):
        self.root_path = Path(root_path).resolve()
        self.force = force
        self.dry_run = dry_run
        self.created_files = []
        self.created_dirs = []
        self.console = Console()
        
    def create_directory_structure(self) -> None:
        """Create the complete directory structure."""
        
        directories = [
            # Main source directories
            "src/videomilker/cli",
            "src/videomilker/core", 
            "src/videomilker/config",
            "src/videomilker/history",
            "src/videomilker/utils",
            "src/videomilker/exceptions",
            
            # Test directories
            "tests/test_cli",
            "tests/test_core",
            "tests/test_config", 
            "tests/test_utils",
            
            # Documentation
            "docs",
            
            # Configuration
            "config/themes",
            "config/templates",
            
            # Data directories
            "data/downloads",
            "data/history",
            "data/logs",
            "data/temp",
            
            # Utility scripts
            "scripts",
            
            # Assets
            "assets/icons",
            "assets/templates",
            
            # Build directories
            "build/dist",
            "build/exe",
            "build/temp"
        ]
        
        for directory in directories:
            self._create_directory(directory)
    
    def create_initial_files(self) -> None:
        """Create initial project files with basic content."""
        
        # Root level files
        self._create_file(".gitignore", self._get_gitignore_content())
        self._create_file("README.md", self._get_readme_content())
        self._create_file("requirements.txt", self._get_requirements_content())
        self._create_file("setup.py", self._get_setup_py_content())
        self._create_file("pyproject.toml", self._get_pyproject_content())
        self._create_file("LICENSE", self._get_license_content())
        
        # Python __init__.py files
        init_files = [
            "src/__init__.py",
            "src/videomilker/__init__.py",
            "src/videomilker/cli/__init__.py",
            "src/videomilker/core/__init__.py",
            "src/videomilker/config/__init__.py",
            "src/videomilker/history/__init__.py",
            "src/videomilker/utils/__init__.py",
            "src/videomilker/exceptions/__init__.py",
            "tests/__init__.py",
            "tests/test_cli/__init__.py",
            "tests/test_core/__init__.py",
            "tests/test_config/__init__.py",
            "tests/test_utils/__init__.py"
        ]
        
        for init_file in init_files:
            self._create_file(init_file, self._get_init_content(init_file))
        
        # Main application files
        self._create_file("src/videomilker/main.py", self._get_main_py_content())
        self._create_file("src/videomilker/version.py", self._get_version_content())
        
        # CLI module files
        self._create_file("src/videomilker/cli/menu_system.py", self._get_menu_system_content())
        self._create_file("src/videomilker/cli/menu_renderer.py", self._get_menu_renderer_content())
        self._create_file("src/videomilker/cli/styles.py", self._get_styles_content())
        
        # Core module files
        self._create_file("src/videomilker/core/downloader.py", self._get_downloader_content())
        self._create_file("src/videomilker/core/file_manager.py", self._get_file_manager_content())
        
        # Configuration files
        self._create_file("src/videomilker/config/settings.py", self._get_settings_content())
        self._create_file("config/default_config.json", self._get_default_config_content())
        
        # Test configuration
        self._create_file("tests/conftest.py", self._get_conftest_content())
        
        # Documentation files
        self._create_file("docs/README.md", self._get_docs_readme_content())
        self._create_file("docs/installation.md", self._get_installation_content())
        
        # Data placeholder files
        self._create_file("data/downloads/.gitkeep", "")
        self._create_file("data/history/.gitkeep", "")
        self._create_file("data/logs/.gitkeep", "")
        self._create_file("data/temp/.gitkeep", "")
    
    def _create_directory(self, path: str) -> None:
        """Create a directory if it doesn't exist."""
        full_path = self.root_path / path
        
        if self.dry_run:
            print(f"[DRY RUN] Would create directory: {full_path}")
            return
            
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            self.created_dirs.append(str(full_path))
            print(f" Created directory: {path}")
        else:
            print(f"• Directory exists: {path}")
    
    def _create_file(self, path: str, content: str) -> None:
        """Create a file with the given content."""
        full_path = self.root_path / path
        
        if self.dry_run:
            print(f"[DRY RUN] Would create file: {full_path}")
            return
            
        if full_path.exists() and not self.force:
            print(f"• File exists (skipping): {path}")
            return
            
        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.created_files.append(str(full_path))
            print(f" Created file: {path}")
        except Exception as e:
            print(f" Failed to create {path}: {e}")
    
    # Content generation methods
    def _get_gitignore_content(self) -> str:
        return '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Application specific
data/downloads/*
!data/downloads/.gitkeep
data/logs/*.log
data/temp/*
!data/temp/.gitkeep
config/user_config.json
*.db
*.sqlite
'''

    def _get_readme_content(self) -> str:
        return '''# VideoMilker

An intuitive CLI interface for yt-dlp that simplifies video downloading with organized workflows.

## Features

-  Simple video downloading with URL input
-  Batch download support
-  Automatic file organization by date
-  Easy configuration management
-  Download history tracking
-  Rich terminal interface

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python -m src.videomilker.main`

## Documentation

See the `docs/` directory for detailed documentation.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
'''

    def _get_requirements_content(self) -> str:
        return '''# Core dependencies
rich>=13.0.0
click>=8.0.0
yt-dlp>=2023.12.30
pathlib2>=2.3.0

# Configuration and data
pydantic>=2.0.0
toml>=0.10.0

# Database and history
sqlite3

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0

# Development
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.0.0

# Build and packaging
setuptools>=65.0.0
wheel>=0.38.0
build>=0.10.0
twine>=4.0.0
'''

    def _get_setup_py_content(self) -> str:
        return '''#!/usr/bin/env python3
"""VideoMilker setup configuration."""

from setuptools import setup, find_packages
from pathlib import Path

# Read version
version_file = Path(__file__).parent / "src" / "videomilker" / "version.py"
version_info = {}
exec(version_file.read_text(), version_info)

# Read long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="videomilker",
    version=version_info["__version__"],
    description="An intuitive CLI interface for yt-dlp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="VideoMilker Team",
    author_email="team@videomilker.com",
    url="https://github.com/videomilker/videomilker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.0.0",
        "click>=8.0.0",
        "yt-dlp>=2023.12.30",
        "pydantic>=2.0.0",
        "toml>=0.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "videomilker=videomilker.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: System :: Archiving",
    ],
    keywords="video download cli yt-dlp youtube",
)
'''

    def _get_pyproject_content(self) -> str:
        return '''[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "videomilker"
dynamic = ["version"]
description = "An intuitive CLI interface for yt-dlp"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "VideoMilker Team", email = "team@videomilker.com"}
]
keywords = ["video", "download", "cli", "yt-dlp", "youtube"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: End Users/Desktop", 
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Multimedia :: Video",
    "Topic :: System :: Archiving",
]

dependencies = [
    "rich>=13.0.0",
    "click>=8.0.0", 
    "yt-dlp>=2023.12.30",
    "pydantic>=2.0.0",
    "toml>=0.10.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]

[project.scripts]
videomilker = "videomilker.main:main"

[tool.setuptools.dynamic]
version = {attr = "videomilker.version.__version__"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --tb=short"

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
'''

    def _get_license_content(self) -> str:
        year = datetime.now().year
        return f'''MIT License

Copyright (c) {year} VideoMilker Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

    def _get_init_content(self, file_path: str) -> str:
        """Generate appropriate __init__.py content based on the module."""
        if "videomilker/__init__.py" in file_path:
            return '''"""VideoMilker - An intuitive CLI interface for yt-dlp."""

from .version import __version__

__all__ = ["__version__"]
'''
        elif "cli/__init__.py" in file_path:
            return '''"""CLI interface components."""

from .menu_system import MenuSystem
from .menu_renderer import MenuRenderer

__all__ = ["MenuSystem", "MenuRenderer"]
'''
        else:
            return '"""Package initialization."""\n'

    def _get_main_py_content(self) -> str:
        return '''#!/usr/bin/env python3
"""
VideoMilker main entry point.

This module provides the main CLI interface for VideoMilker.
"""

import sys
import click
from rich.console import Console
from rich.traceback import install

from .cli.menu_system import MenuSystem
from .config.settings import load_config
from .version import __version__

# Install rich traceback handler
install(show_locals=True)

console = Console()


@click.command()
@click.version_option(__version__)
@click.option(
    "--config", 
    "-c", 
    help="Path to configuration file",
    type=click.Path(exists=True)
)
@click.option(
    "--verbose", 
    "-v", 
    is_flag=True, 
    help="Enable verbose logging"
)
def main(config: str = None, verbose: bool = False):
    """VideoMilker - An intuitive CLI interface for yt-dlp."""
    
    try:
        # Load configuration
        settings = load_config(config_path=config)
        
        # Initialize menu system
        menu_system = MenuSystem(settings=settings, verbose=verbose)
        
        # Start the application
        menu_system.run()
        
    except KeyboardInterrupt:
        console.print("\\n[yellow]Application interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
'''

    def _get_version_content(self) -> str:
        return '''"""Version information for VideoMilker."""

__version__ = "1.0.0"
__version_info__ = tuple(int(i) for i in __version__.split("."))

# Build information
__build__ = "dev"
__date__ = "2024-01-15"
'''

    def _get_menu_system_content(self) -> str:
        return '''"""Main menu system for VideoMilker CLI."""

from typing import Optional, Dict, Any
from rich.console import Console

from .menu_renderer import MenuRenderer
from ..config.settings import Settings


class MenuSystem:
    """Main menu controller for the VideoMilker CLI application."""
    
    def __init__(self, settings: Settings, verbose: bool = False):
        """Initialize the menu system."""
        self.settings = settings
        self.verbose = verbose
        self.console = Console()
        self.renderer = MenuRenderer(console=self.console)
        self.current_menu = "main"
        self.running = True
    
    def run(self) -> None:
        """Start the main menu loop."""
        self.console.clear()
        self.renderer.show_welcome_banner()
        
        while self.running:
            try:
                self._handle_menu()
            except KeyboardInterrupt:
                self._handle_quit()
                break
    
    def _handle_menu(self) -> None:
        """Handle the current menu state."""
        if self.current_menu == "main":
            self._show_main_menu()
        elif self.current_menu == "download":
            self._show_download_menu()
        elif self.current_menu == "batch":
            self._show_batch_menu()
        elif self.current_menu == "options":
            self._show_options_menu()
        else:
            self.current_menu = "main"
    
    def _show_main_menu(self) -> None:
        """Display and handle the main menu."""
        options = {
            "1": (" Quick Download", self._handle_quick_download),
            "2": (" Batch Download", self._handle_batch_download),
            "3": (" Options & Settings", self._handle_options),
            "4": (" Download History", self._handle_history),
            "5": (" Help & Info", self._handle_help),
            "q": ("Quit Application", self._handle_quit),
        }
        
        choice = self.renderer.show_menu("VideoMilker Main Menu", options)
        
        if choice in options:
            options[choice][1]()
    
    def _handle_quick_download(self) -> None:
        """Handle quick download option."""
        self.current_menu = "download"
    
    def _handle_batch_download(self) -> None:
        """Handle batch download option.""" 
        self.current_menu = "batch"
    
    def _handle_options(self) -> None:
        """Handle options menu."""
        self.current_menu = "options"
    
    def _handle_history(self) -> None:
        """Handle download history."""
        self.console.print("[yellow]Download history feature coming soon![/yellow]")
        input("Press Enter to continue...")
    
    def _handle_help(self) -> None:
        """Handle help and info."""
        self.console.print("[yellow]Help and info feature coming soon![/yellow]")
        input("Press Enter to continue...")
    
    def _handle_quit(self) -> None:
        """Handle application quit."""
        self.console.print("[yellow]Thanks for using VideoMilker![/yellow]")
        self.running = False
    
    def _show_download_menu(self) -> None:
        """Show download menu (placeholder)."""
        self.console.print("[yellow]Download menu coming soon![/yellow]")
        input("Press Enter to go back...")
        self.current_menu = "main"
    
    def _show_batch_menu(self) -> None:
        """Show batch download menu (placeholder)."""
        self.console.print("[yellow]Batch download menu coming soon![/yellow]")
        input("Press Enter to go back...")
        self.current_menu = "main"
    
    def _show_options_menu(self) -> None:
        """Show options menu (placeholder)."""
        self.console.print("[yellow]Options menu coming soon![/yellow]")
        input("Press Enter to go back...")
        self.current_menu = "main"
'''

    def _get_menu_renderer_content(self) -> str:
        return '''"""Menu rendering utilities using Rich."""

from typing import Dict, Tuple, Callable, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align


class MenuRenderer:
    """Handles the visual rendering of menus using Rich."""
    
    def __init__(self, console: Console):
        """Initialize the menu renderer."""
        self.console = console
'''

    def _get_default_config_content(self) -> str:
        home = str(Path.home())
        return f'''{{
  "version": "1.0.0",
  "download": {{
    "path": "{home}/Downloads/VideoMilker",
    "create_day_folders": true,
    "file_naming": "%(upload_date)s_%(title)s",
    "default_quality": "best",
    "default_format": "mp4",
    "max_concurrent": 3,
    "auto_subtitle": false,
    "save_thumbnail": false
  }},
  "ui": {{
    "theme": "default",
    "show_progress_details": true,
    "confirm_before_quit": true,
    "clear_screen": true
  }},
  "history": {{
    "max_entries": 1000,
    "auto_cleanup": true,
    "cleanup_days": 30
  }}
}}'''

    def _get_conftest_content(self) -> str:
        return '''"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.videomilker.config.settings import Settings, DownloadSettings


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_settings(temp_dir):
    """Create test settings with temporary directory."""
    return Settings(
        download=DownloadSettings(path=str(temp_dir / "downloads"))
    )


@pytest.fixture
def sample_urls():
    """Sample URLs for testing."""
    return [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    ]


@pytest.fixture
def mock_ytdlp_success(monkeypatch):
    """Mock successful yt-dlp execution."""
    def mock_run(*args, **kwargs):
        class MockResult:
            returncode = 0
            stdout = "Download completed successfully"
            stderr = ""
        return MockResult()
    
    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture
def mock_ytdlp_failure(monkeypatch):
    """Mock failed yt-dlp execution."""
    def mock_run(*args, **kwargs):
        from subprocess import CalledProcessError
        raise CalledProcessError(1, "yt-dlp", "Video unavailable")
    
    monkeypatch.setattr("subprocess.run", mock_run)
'''

    def _get_docs_readme_content(self) -> str:
        return '''# VideoMilker Documentation

Welcome to the VideoMilker documentation. This directory contains comprehensive guides and references for using and developing VideoMilker.

## Documentation Structure

- **[Installation Guide](installation.md)** - How to install and set up VideoMilker
- **[User Guide](user_guide.md)** - Complete user manual with examples
- **[API Reference](api_reference.md)** - Developer API documentation
- **[Contributing Guide](contributing.md)** - How to contribute to the project
- **[Changelog](changelog.md)** - Version history and changes

## Quick Links

### For Users
- [Getting Started](installation.md#quick-start)
- [Basic Usage](user_guide.md#basic-usage)
- [Configuration](user_guide.md#configuration)
- [Troubleshooting](user_guide.md#troubleshooting)

### For Developers
- [Development Setup](contributing.md#development-setup)
- [API Documentation](api_reference.md)
- [Testing Guide](contributing.md#testing)
- [Code Style](contributing.md#code-style)

## Support

If you need help or have questions:

1. Check the [User Guide](user_guide.md) for common solutions
2. Look through existing [GitHub Issues](https://github.com/videomilker/videomilker/issues)
3. Create a new issue if your problem isn't covered

## Contributing

We welcome contributions! Please read our [Contributing Guide](contributing.md) to get started.
'''

    def _get_installation_content(self) -> str:
        return '''# Installation Guide

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
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

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

**"Command not found: videomilker"**
- Ensure pip installation completed successfully
- Check that Python scripts directory is in your PATH

**"Permission denied" errors**
- On macOS/Linux, you may need to run: `chmod +x ~/.local/bin/videomilker`
- Or install with: `pip install --user videomilker`

**yt-dlp not found**
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
'''

    def run_setup(self) -> None:
        """Run the complete project setup."""
        print(" Setting up VideoMilker project structure...")
        print(f"Root directory: {self.root_path}")
        print()
        
        try:
            # Create directory structure
            print(" Creating directory structure...")
            self.create_directory_structure()
            print()
            
            # Create files
            print(" Creating initial files...")
            self.create_initial_files()
            print()
            
            # Summary
            print(" Project setup completed successfully!")
            print(f"Created {len(self.created_dirs)} directories")
            print(f"Created {len(self.created_files)} files")
            
            if not self.dry_run:
                print()
                print(" Next Steps:")
                print("1. Navigate to the project directory:")
                print(f"   cd {self.root_path}")
                print("2. Activate virtual environment:")
                print("   source .venv/bin/activate  # Linux/Mac")
                print("   .venv\\Scripts\\activate     # Windows")
                print("3. Install dependencies:")
                print("   pip install -r requirements.txt")
                print("4. Run the application:")
                print("   python -m src.videomilker.main")
                
        except Exception as e:
            print(f" Setup failed: {e}")
            if self.dry_run:
                print("(This was a dry run - no files were actually created)")
            sys.exit(1)

    def cleanup_old_files(self, days_to_keep: int = 30) -> int:
        """Clean up files older than specified days."""
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
        cleaned_count = 0
        
        for day_folder in self.base_path.iterdir():
            if not day_folder.is_dir():
                continue
                
            for file_path in day_folder.rglob('*'):
                if file_path.is_file():
                    try:
                        if file_path.stat().st_mtime < cutoff_date:
                            file_path.unlink()
                            cleaned_count += 1
                    except (OSError, FileNotFoundError):
                        continue
            
            # Remove empty directories
            try:
                if not any(day_folder.iterdir()):
                    day_folder.rmdir()
            except OSError:
                continue
        
        return cleaned_count

    def show_welcome_banner(self) -> None:
        """Display the welcome banner."""
        banner_text = Text("Welcome to VideoMilker!", style="bold blue")
        banner = Panel(
            Align.center(banner_text),
            style="blue",
            padding=(1, 2)
        )
        self.console.print(banner)
        self.console.print()
    
    def show_menu(self, title: str, options: Dict[str, Tuple[str, Callable]]) -> str:
        """Display a menu and get user input."""
        # Create menu table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Description", style="white")
        
        for key, (description, _) in options.items():
            table.add_row(f"[{key}]", description)
        
        # Display menu in panel
        menu_panel = Panel(
            table,
            title=title,
            title_align="center",
            style="blue"
        )
        
        self.console.print(menu_panel)
        
        # Get user input
        while True:
            try:
                choice = self.console.input("\\nSelect an option: ").strip().lower()
                if choice in options:
                    return choice
                else:
                    self.console.print("[red]Invalid option. Please try again.[/red]")
            except (EOFError, KeyboardInterrupt):
                return "q"

    def _get_styles_content(self) -> str:
        """Generate content for the styles module."""
        return '''"""Rich styles and themes for VideoMilker CLI."""

from rich.style import Style
from rich.theme import Theme

# Custom styles
SUCCESS_STYLE = Style(color="green", bold=True)
ERROR_STYLE = Style(color="red", bold=True)
WARNING_STYLE = Style(color="yellow", bold=True)
INFO_STYLE = Style(color="blue", bold=True)
PROGRESS_STYLE = Style(color="cyan", bold=True)

# Menu styles
MENU_TITLE_STYLE = Style(color="blue", bold=True)
MENU_OPTION_STYLE = Style(color="white")
MENU_SELECTED_STYLE = Style(color="cyan", bold=True)

# Download styles
DOWNLOAD_PROGRESS_STYLE = Style(color="green")
DOWNLOAD_ERROR_STYLE = Style(color="red")
DOWNLOAD_SUCCESS_STYLE = Style(color="green", bold=True)

# Custom theme
VIDEOMILKER_THEME = Theme({
    "success": SUCCESS_STYLE,
    "error": ERROR_STYLE,
    "warning": WARNING_STYLE,
    "info": INFO_STYLE,
    "progress": PROGRESS_STYLE,
    "menu.title": MENU_TITLE_STYLE,
    "menu.option": MENU_OPTION_STYLE,
    "menu.selected": MENU_SELECTED_STYLE,
    "download.progress": DOWNLOAD_PROGRESS_STYLE,
    "download.error": DOWNLOAD_ERROR_STYLE,
    "download.success": DOWNLOAD_SUCCESS_STYLE,
})
'''

    def _get_downloader_content(self) -> str:
        """Generate content for the downloader module."""
        return '''"""Core download functionality using yt-dlp."""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from ..config.settings import DownloadSettings


@dataclass
class DownloadResult:
    """Result of a download operation."""
    success: bool
    file_path: Optional[Path] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class VideoDownloader:
    """Handles video downloading using yt-dlp."""
    
    def __init__(self, settings: DownloadSettings, console: Console):
        self.settings = settings
        self.console = console
    
    def download_video(self, url: str, output_path: Optional[Path] = None) -> DownloadResult:
        """Download a video from the given URL."""
        if output_path is None:
            output_path = Path(self.settings.path)
        
        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Build yt-dlp command
        cmd = [
            "yt-dlp",
            "--format", self.settings.default_quality,
            "--output", str(output_path / self.settings.file_naming),
            "--write-info-json",
            "--write-thumbnail" if self.settings.save_thumbnail else "--no-write-thumbnail",
            "--write-subs" if self.settings.auto_subtitle else "--no-write-subs",
            "--newline",
            url
        ]
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Downloading {url}", total=None)
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                progress.update(task, completed=True)
            
            # Parse output to find downloaded file
            output_files = list(output_path.glob("*"))
            if output_files:
                return DownloadResult(
                    success=True,
                    file_path=output_files[0],
                    metadata=self._parse_metadata(output_files[0])
                )
            else:
                return DownloadResult(
                    success=False,
                    error_message="No files were downloaded"
                )
                
        except subprocess.CalledProcessError as e:
            return DownloadResult(
                success=False,
                error_message=f"Download failed: {e.stderr}"
            )
        except Exception as e:
            return DownloadResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def _parse_metadata(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse metadata from the downloaded file."""
        info_file = file_path.with_suffix('.info.json')
        if info_file.exists():
            try:
                with open(info_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return None
'''

    def _get_file_manager_content(self) -> str:
        """Generate content for the file manager module."""
        return '''"""File management utilities for VideoMilker."""

import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta

from rich.console import Console


class FileManager:
    """Handles file operations and organization."""
    
    def __init__(self, base_path: Path, console: Console):
        self.base_path = base_path
        self.console = console
    
    def organize_by_date(self, file_path: Path) -> Path:
        """Organize files by date in day-based folders."""
        if not file_path.exists():
            return file_path
        
        # Get file modification time
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        date_folder = mtime.strftime("%Y-%m-%d")
        
        # Create date folder
        day_path = self.base_path / date_folder
        day_path.mkdir(parents=True, exist_ok=True)
        
        # Move file to date folder
        new_path = day_path / file_path.name
        if new_path != file_path:
            shutil.move(str(file_path), str(new_path))
            self.console.print(f"Moved {file_path.name} to {date_folder}/")
        
        return new_path
    
    def cleanup_old_files(self, days_to_keep: int = 30) -> int:
        """Remove files older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cleaned_count = 0
        
        for day_folder in self.base_path.iterdir():
            if not day_folder.is_dir():
                continue
            
            # Check if folder name is a date
            try:
                folder_date = datetime.strptime(day_folder.name, "%Y-%m-%d")
                if folder_date < cutoff_date:
                    shutil.rmtree(day_folder)
                    cleaned_count += 1
                    self.console.print(f"Removed old folder: {day_folder.name}")
            except ValueError:
                # Not a date folder, skip
                continue
        
        return cleaned_count
    
    def get_file_info(self, file_path: Path) -> dict:
        """Get information about a file."""
        if not file_path.exists():
            return {}
        
        stat = file_path.stat()
        return {
            "name": file_path.name,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "created": datetime.fromtimestamp(stat.st_ctime),
            "extension": file_path.suffix,
        }
'''

    def _get_settings_content(self) -> str:
        """Generate content for the settings module."""
        return '''"""Configuration settings for VideoMilker."""

import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field


class DownloadSettings(BaseModel):
    """Download configuration settings."""
    path: str = Field(default="~/Downloads/VideoMilker", description="Download directory")
    create_day_folders: bool = Field(default=True, description="Organize files by date")
    file_naming: str = Field(default="%(upload_date)s_%(title)s", description="File naming pattern")
    default_quality: str = Field(default="best", description="Default video quality")
    default_format: str = Field(default="mp4", description="Default video format")
    max_concurrent: int = Field(default=3, description="Maximum concurrent downloads")
    auto_subtitle: bool = Field(default=False, description="Automatically download subtitles")
    save_thumbnail: bool = Field(default=False, description="Save video thumbnails")


class UISettings(BaseModel):
    """UI configuration settings."""
    theme: str = Field(default="default", description="UI theme")
    show_progress_details: bool = Field(default=True, description="Show detailed progress")
    confirm_before_quit: bool = Field(default=True, description="Confirm before quitting")
    clear_screen: bool = Field(default=True, description="Clear screen on startup")


class HistorySettings(BaseModel):
    """History configuration settings."""
    max_entries: int = Field(default=1000, description="Maximum history entries")
    auto_cleanup: bool = Field(default=True, description="Auto-cleanup old entries")
    cleanup_days: int = Field(default=30, description="Days to keep history")


class Settings(BaseModel):
    """Main application settings."""
    version: str = Field(default="1.0.0", description="Settings version")
    download: DownloadSettings = Field(default_factory=DownloadSettings)
    ui: UISettings = Field(default_factory=UISettings)
    history: HistorySettings = Field(default_factory=HistorySettings)
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> "Settings":
        """Load settings from a JSON file."""
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
            return cls(**data)
        return cls()
    
    def save_to_file(self, file_path: Path) -> None:
        """Save settings to a JSON file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(asdict(self), f, indent=2, default=str)
'''


def main():
    """Main function to run the setup script."""
    parser = argparse.ArgumentParser(
        description="VideoMilker Project Setup Script",
        epilog="This script creates the complete directory structure and initial files for VideoMilker."
    )
    
    parser.add_argument(
        "path", 
        nargs="?", 
        default=".", 
        help="Root directory for the project (default: current directory)"
    )
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Overwrite existing files"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be created without actually creating files"
    )
    
    args = parser.parse_args()
    
    # Create and run setup
    setup = ProjectSetup(
        root_path=args.path,
        force=args.force,
        dry_run=args.dry_run
    )
    
    setup.run_setup()


if __name__ == "__main__":
    main()