"""Pytest configuration and fixtures."""

import shutil
import tempfile
from pathlib import Path

import pytest

from src.videomilker.config.settings import DownloadSettings
from src.videomilker.config.settings import Settings


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_settings(temp_dir):
    """Create test settings with temporary directory."""
    return Settings(download=DownloadSettings(path=str(temp_dir / "downloads")))


@pytest.fixture
def sample_urls():
    """Sample URLs for testing."""
    return ["https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://www.youtube.com/watch?v=jNQXAC9IVRw"]


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
