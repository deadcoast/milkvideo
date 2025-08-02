#!/usr/bin/env python3
"""
Simple test script for VideoMilker.

This script tests the basic functionality of VideoMilker components.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from videomilker.config.config_manager import ConfigManager
from videomilker.config.settings import Settings
from videomilker.cli.menu_renderer import MenuRenderer
from rich.console import Console


def test_configuration():
    """Test configuration management."""
    print("Testing configuration management...")
    
    try:
        # Test config manager
        config_manager = ConfigManager()
        settings = config_manager.load_config()
        
        print(f"✓ Configuration loaded successfully")
        print(f"  Download path: {settings.download.path}")
        print(f"  Default quality: {settings.download.default_quality}")
        print(f"  Theme: {settings.ui.theme}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_menu_renderer():
    """Test menu renderer."""
    print("\nTesting menu renderer...")
    
    try:
        console = Console()
        settings = Settings()
        renderer = MenuRenderer(console, settings)
        
        # Test welcome banner
        renderer.show_welcome_banner()
        
        print("✓ Menu renderer initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Menu renderer test failed: {e}")
        return False


def test_settings():
    """Test settings functionality."""
    print("\nTesting settings functionality...")
    
    try:
        settings = Settings()
        
        # Test download path resolution
        download_path = settings.get_download_path()
        print(f"✓ Download path resolved: {download_path}")
        
        # Test yt-dlp options
        yt_dlp_options = settings.get_yt_dlp_options()
        print(f"✓ yt-dlp options generated: {len(yt_dlp_options)} options")
        
        return True
    except Exception as e:
        print(f"✗ Settings test failed: {e}")
        return False


def test_file_manager():
    """Test file manager."""
    print("\nTesting file manager...")
    
    try:
        from videomilker.core.file_manager import FileManager
        
        settings = Settings()
        file_manager = FileManager(settings)
        
        # Test day folder creation
        day_folder = file_manager.get_day_folder()
        print(f"✓ Day folder: {day_folder}")
        
        # Test filename generation
        filename = file_manager.generate_filename("Test Video", "mp4")
        print(f"✓ Generated filename: {filename}")
        
        return True
    except Exception as e:
        print(f"✗ File manager test failed: {e}")
        return False


def test_input_handler():
    """Test input handler."""
    print("\nTesting input handler...")
    
    try:
        from videomilker.cli.input_handler import InputHandler
        
        handler = InputHandler()
        
        # Test URL validation
        valid_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        invalid_url = "not-a-url"
        
        assert handler.validate_url(valid_url) == True
        assert handler.validate_url(invalid_url) == False
        print("✓ URL validation working")
        
        # Test filename suggestion
        filename = handler.suggest_filename("Test Video Title", "mp4")
        print(f"✓ Suggested filename: {filename}")
        
        return True
    except Exception as e:
        print(f"✗ Input handler test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("VideoMilker Test Suite")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_settings,
        test_file_manager,
        test_input_handler,
        test_menu_renderer,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! VideoMilker is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 