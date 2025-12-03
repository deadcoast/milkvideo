#!/usr/bin/env python3
"""Tests for VideoMilker components."""

import io
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from videomilker.cli.input_handler import InputHandler
from videomilker.cli.menu_renderer import MenuRenderer
from videomilker.config.config_manager import ConfigManager
from videomilker.config.settings import DownloadSettings, Settings
from videomilker.core.file_manager import FileManager


def test_configuration(tmp_path):
    config_dir = tmp_path / "config"
    config_manager = ConfigManager(config_dir=config_dir)

    settings = config_manager.load_config()

    assert (config_dir / "videomilker.json").exists()
    assert isinstance(settings, Settings)
    assert settings.download.path


def test_menu_renderer_renders_welcome_banner():
    console = Console(record=True, file=io.StringIO())
    renderer = MenuRenderer(console, Settings())

    renderer.show_welcome_banner()
    output = console.export_text()

    assert "VideoMilker" in output
    assert renderer.theme


def test_settings_helpers_use_download_path(tmp_path):
    settings = Settings(download=DownloadSettings(path=str(tmp_path)))

    download_path = settings.get_download_path()
    expected_day_folder = f"{datetime.now().day:02d}"
    options = settings.get_yt_dlp_options()

    assert download_path.parent == tmp_path
    assert download_path.name == expected_day_folder
    assert options["outtmpl"] == settings.download.file_naming
    assert options["format"] == settings.download.default_quality


def test_file_manager_creates_day_folder_and_filename(tmp_path):
    settings = Settings(download=DownloadSettings(path=str(tmp_path)))
    file_manager = FileManager(settings)

    day_folder = file_manager.get_day_folder()
    filename = file_manager.generate_filename("Test Video", "mp4")

    assert day_folder.exists()
    assert day_folder.is_dir()
    assert day_folder.parent == Path(settings.download.path).expanduser()
    assert filename.endswith(".mp4")
    assert "test_video" in filename


def test_input_handler_validation_and_suggestions():
    handler = InputHandler()

    valid_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    invalid_url = "not-a-url"
    filename = handler.suggest_filename("Test Video Title", "mp4")

    assert handler.validate_url(valid_url)
    assert not handler.validate_url(invalid_url)
    assert filename.endswith(".mp4")
    assert "Test Video Title" in filename

