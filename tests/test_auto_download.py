#!/usr/bin/env python3
"""
Test script for auto-download functionality.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from videomilker.config.config_manager import ConfigManager
from videomilker.cli.menu_renderer import MenuRenderer
from rich.console import Console

def test_auto_download_confirmation():
    """Test the auto-download confirmation functionality."""
    console = Console()
    
    # Load configuration
    config_manager = ConfigManager()
    settings = config_manager.load_config()
    
    # Create menu renderer
    renderer = MenuRenderer(console, settings)
    
    print("Testing Auto-Download Confirmation")
    print("=" * 40)
    
    # Test 1: Auto-download OFF
    print("\n1. Testing with auto-download OFF:")
    settings.ui.auto_download = False
    result = renderer.show_download_confirmation("Test download?", settings.ui.auto_download)
    print(f"Result: {result}")
    
    # Test 2: Auto-download ON
    print("\n2. Testing with auto-download ON:")
    settings.ui.auto_download = True
    result = renderer.show_download_confirmation("Test download?", settings.ui.auto_download)
    print(f"Result: {result}")
    
    # Test 3: Manual confirmation (simulate user input)
    print("\n3. Testing manual confirmation:")
    settings.ui.auto_download = False
    print("This would normally prompt for user input")
    print("Expected prompt: 'Test download? [y/n/auto] (y):'")
    print("Expected responses:")
    print("  - 'y' or 'yes' or '': [ON] - Auto Start Downloads")
    print("  - 'n' or 'no': [OFF] - Auto Start Downloads")
    print("  - 'auto': [ON] - Auto Start Downloads")

if __name__ == "__main__":
    test_auto_download_confirmation() 