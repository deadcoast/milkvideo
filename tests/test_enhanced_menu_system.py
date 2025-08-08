#!/usr/bin/env python3
"""
Test suite for enhanced menu system functionality.

This module tests the improved navigation, keyboard shortcuts, and help system.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from videomilker.cli.menu_system import MenuSystem
from videomilker.config.settings import Settings
from videomilker.config.config_manager import ConfigManager


class TestEnhancedMenuSystem:
    """Test enhanced menu system functionality."""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for testing."""
        settings = Mock()
        
        # Mock UI settings
        settings.ui = Mock()
        settings.ui.clear_screen = False
        settings.ui.confirm_before_quit = False
        settings.ui.auto_download = False
        
        # Mock download settings
        settings.download = Mock()
        settings.download.path = "/tmp/test_downloads"
        settings.download.create_day_folders = True
        settings.download.file_naming = "YYYY-MM-DD_{title}"
        settings.download.default_quality = "best"
        settings.download.default_format = "mp4"
        settings.download.max_concurrent = 3
        
        # Mock history settings
        settings.history = Mock()
        settings.history.max_entries = 1000
        settings.history.auto_cleanup = True
        settings.history.cleanup_days = 30
        
        return settings
    
    @pytest.fixture
    def menu_system(self, mock_settings):
        """Create a menu system instance for testing."""
        with patch('videomilker.cli.menu_system.Console'), \
             patch('videomilker.cli.menu_system.MenuRenderer'), \
             patch('videomilker.cli.menu_system.InputHandler'), \
             patch('videomilker.cli.menu_system.ConfigManager'), \
             patch('videomilker.cli.menu_system.VideoDownloader'), \
             patch('videomilker.cli.menu_system.BatchProcessor'), \
             patch('videomilker.cli.menu_system.FileManager'), \
             patch('videomilker.cli.menu_system.HistoryManager'):
            
            menu = MenuSystem(mock_settings, verbose=False)
            menu.console = Mock()
            menu.renderer = Mock()
            menu.input_handler = Mock()
            menu.config_manager = Mock()
            menu.downloader = Mock()
            menu.batch_processor = Mock()
            menu.file_manager = Mock()
            menu.history_manager = Mock()
            
            return menu
    
    def test_navigation_system(self, menu_system):
        """Test the enhanced navigation system."""
        # Test initial state
        assert menu_system.current_menu == "main"
        assert menu_system.menu_history == []
        
        # Test navigation to menu
        menu_system._navigate_to_menu("quick_download")
        assert menu_system.current_menu == "quick_download"
        assert menu_system.menu_history == ["main"]
        
        # Test navigation to another menu
        menu_system._navigate_to_menu("batch_download")
        assert menu_system.current_menu == "batch_download"
        assert menu_system.menu_history == ["main", "quick_download"]
        
        # Test going back
        menu_system._go_back()
        assert menu_system.current_menu == "quick_download"
        assert menu_system.menu_history == ["main"]
        
        # Test going back again
        menu_system._go_back()
        assert menu_system.current_menu == "main"
        assert menu_system.menu_history == []
        
        # Test going back when no history
        menu_system._go_back()
        assert menu_system.current_menu == "main"
    
    def test_menu_titles(self, menu_system):
        """Test menu title generation."""
        titles = {
            "main": "VideoMilker Main Menu",
            "quick_download": "Quick Download",
            "audio_download": "Audio-Only Download",
            "chapter_download": "Chapter Split Download",
            "batch_download": "Batch Download",
            "resume_downloads": "Resume Interrupted Downloads",
            "file_management": "File Management",
            "options": "Options & Settings",
            "history": "Download History",
            "help": "Help & Information"
        }
        
        for menu_name, expected_title in titles.items():
            assert menu_system._get_menu_title(menu_name) == expected_title
        
        # Test unknown menu
        assert menu_system._get_menu_title("unknown") == "Menu"
    
    def test_global_shortcuts(self, menu_system):
        """Test global keyboard shortcuts."""
        # Test navigation shortcuts
        assert menu_system._handle_global_shortcuts("0") is True
        assert menu_system._handle_global_shortcuts("b") is True
        assert menu_system._handle_global_shortcuts("B") is True
        
        # Test quit shortcuts
        assert menu_system._handle_global_shortcuts("q") is True
        assert menu_system._handle_global_shortcuts("Q") is True
        
        # Test menu shortcuts
        assert menu_system._handle_global_shortcuts("h") is True
        assert menu_system._handle_global_shortcuts("H") is True
        assert menu_system._handle_global_shortcuts("s") is True
        assert menu_system._handle_global_shortcuts("S") is True
        assert menu_system._handle_global_shortcuts("d") is True
        assert menu_system._handle_global_shortcuts("D") is True
        assert menu_system._handle_global_shortcuts("a") is True
        assert menu_system._handle_global_shortcuts("A") is True
        assert menu_system._handle_global_shortcuts("c") is True
        assert menu_system._handle_global_shortcuts("C") is True
        assert menu_system._handle_global_shortcuts("r") is True
        assert menu_system._handle_global_shortcuts("R") is True
        assert menu_system._handle_global_shortcuts("f") is True
        assert menu_system._handle_global_shortcuts("F") is True
        assert menu_system._handle_global_shortcuts("i") is True
        assert menu_system._handle_global_shortcuts("I") is True
        
        # Test special shortcuts
        assert menu_system._handle_global_shortcuts("?") is True
        assert menu_system._handle_global_shortcuts("esc") is True
        assert menu_system._handle_global_shortcuts("ESC") is True
        
        # Test unknown shortcut
        assert menu_system._handle_global_shortcuts("x") is False
    
    def test_menu_handlers(self, menu_system):
        """Test menu handler functions."""
        # Test that handlers use navigation system
        menu_system._handle_quick_download()
        assert menu_system.current_menu == "quick_download"
        assert menu_system.menu_history == ["main"]
        
        menu_system._handle_audio_download()
        assert menu_system.current_menu == "audio_download"
        assert menu_system.menu_history == ["main", "quick_download"]
        
        menu_system._handle_chapter_download()
        assert menu_system.current_menu == "chapter_download"
        assert menu_system.menu_history == ["main", "quick_download", "audio_download"]
        
        menu_system._handle_batch_download()
        assert menu_system.current_menu == "batch_download"
        assert len(menu_system.menu_history) == 4
        
        menu_system._handle_resume_downloads()
        assert menu_system.current_menu == "resume_downloads"
        
        menu_system._handle_file_management()
        assert menu_system.current_menu == "file_management"
        
        menu_system._handle_options()
        assert menu_system.current_menu == "options"
        
        menu_system._handle_history()
        assert menu_system.current_menu == "history"
        
        menu_system._handle_help()
        assert menu_system.current_menu == "help"
    
    def test_help_menu_structure(self, menu_system):
        """Test help menu structure and options."""
        # Mock the renderer to capture menu calls
        menu_system.renderer.show_menu.return_value = "0"  # Back option
        
        # Set current menu to help so the while loop executes
        menu_system.current_menu = "help"
        
        # Test help menu shows correct options
        menu_system._show_help_menu()
        
        # Verify show_menu was called
        assert menu_system.renderer.show_menu.called
        
        # Get the call arguments
        call_args = menu_system.renderer.show_menu.call_args
        if call_args and call_args[0]:
            title = call_args[0][0]
            assert title == "Help & Information"  # Title
            
            if len(call_args[0]) > 1:
                options = call_args[0][1]  # Options dict
                expected_options = [
                    "1", "2", "3", "4", "5", "6", "7", "8", "0"
                ]
                
                for option in expected_options:
                    assert option in options
                
                # Verify option descriptions
                assert "General Help" in options["1"][0]
                assert "Quick Download Guide" in options["2"][0]
                assert "Batch Download Guide" in options["3"][0]
                assert "File Management Guide" in options["4"][0]
                assert "Configuration Guide" in options["5"][0]
                assert "Keyboard Shortcuts" in options["6"][0]
                assert "Troubleshooting" in options["7"][0]
                assert "About VideoMilker" in options["8"][0]
                assert "Back to Main Menu" in options["0"][0]
    
    def test_help_content_functions(self, menu_system):
        """Test individual help content functions."""
        # Test that help functions display content and pause
        menu_system._show_general_help()
        menu_system.console.print.assert_called()
        menu_system.renderer.show_pause.assert_called()
        
        menu_system._show_quick_download_help()
        menu_system.console.print.assert_called()
        menu_system.renderer.show_pause.assert_called()
        
        menu_system._show_batch_download_help()
        menu_system.console.print.assert_called()
        menu_system.renderer.show_pause.assert_called()
        
        menu_system._show_file_management_help()
        menu_system.console.print.assert_called()
        menu_system.renderer.show_pause.assert_called()
        
        menu_system._show_configuration_help()
        menu_system.console.print.assert_called()
        menu_system.renderer.show_pause.assert_called()
        
        menu_system._show_keyboard_shortcuts()
        menu_system.console.print.assert_called()
        menu_system.renderer.show_pause.assert_called()
        
        menu_system._show_troubleshooting_help()
        menu_system.console.print.assert_called()
        menu_system.renderer.show_pause.assert_called()
        
        menu_system._show_about_info()
        menu_system.console.print.assert_called()
        menu_system.renderer.show_pause.assert_called()
    
    def test_main_menu_enhancements(self, menu_system):
        """Test main menu enhancements."""
        # Mock renderer
        menu_system.renderer.show_menu.return_value = "q"
        
        # Test main menu shows welcome banner on first call
        menu_system._show_main_menu()
        menu_system.renderer.show_welcome_banner.assert_called_once()
        
        # Test main menu doesn't show banner on subsequent calls
        menu_system._show_main_menu()
        # Should still be called only once
        assert menu_system.renderer.show_welcome_banner.call_count == 1
        
        # Test that show_menu is called with extra_info
        call_args = menu_system.renderer.show_menu.call_args
        assert "extra_info" in call_args[1]
        assert "Global Shortcuts" in call_args[1]["extra_info"]
    
    def test_error_handling(self, menu_system):
        """Test error handling in menu system."""
        # Test KeyboardInterrupt handling
        menu_system.renderer.show_menu.side_effect = KeyboardInterrupt()
        
        # Set current menu to help so the while loop executes
        menu_system.current_menu = "help"
        
        # Should handle gracefully and go back
        menu_system._show_help_menu()
        
        # Verify warning was shown
        assert menu_system.renderer.show_warning.called
        call_args = menu_system.renderer.show_warning.call_args
        if call_args and call_args[0]:
            assert "cancelled by user" in call_args[0][0]
    
    def test_menu_renderer_enhancements(self):
        """Test menu renderer enhancements."""
        from videomilker.cli.menu_renderer import MenuRenderer
        
        with patch('videomilker.cli.menu_renderer.Console') as mock_console_class, \
             patch('videomilker.cli.menu_renderer.Prompt') as mock_prompt:
            
            mock_console = Mock()
            mock_console_class.return_value = mock_console
            mock_prompt.ask.return_value = "1"  # Return a valid choice
            
            renderer = MenuRenderer(mock_console)
            
            # Test show_menu with extra_info
            options = {"1": ("Test Option", None)}
            
            result = renderer.show_menu("Test Menu", options, extra_info="Extra info here")
            
            # Verify the menu content includes extra_info
            # The console.print should be called with a Panel that contains the extra_info
            assert mock_console.print.called
            call_args = mock_console.print.call_args
            
            # Check that the panel was created and contains our extra_info
            panel_arg = call_args[0][0]
            assert hasattr(panel_arg, 'renderable')  # Should be a Panel
            panel_content = str(panel_arg.renderable)
            assert "Extra info here" in panel_content
            
            # Verify result
            assert result == "1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
