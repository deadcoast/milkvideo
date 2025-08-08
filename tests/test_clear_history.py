"""Test clear history functionality."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import sqlite3
from datetime import datetime, timedelta

from src.videomilker.history.history_manager import HistoryManager
from src.videomilker.config.settings import Settings


class TestClearHistory:
    """Test clear history functionality."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)
        
        yield db_path
        
        # Cleanup
        if db_path.exists():
            db_path.unlink()
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.history = Mock()
        settings.history.database_path = "test_history.db"
        settings.history.auto_cleanup = False
        settings.history.cleanup_days = 30
        return settings
    
    @pytest.fixture
    def history_manager(self, mock_settings, temp_db):
        """Create a history manager with a temporary database."""
        with patch.object(HistoryManager, '_get_database_path', return_value=temp_db):
            hm = HistoryManager(mock_settings)
            return hm
    
    def test_clear_all_history(self, history_manager):
        """Test clearing all history."""
        # Add some test data
        with sqlite3.connect(history_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO downloads (url, title, download_date, status)
                VALUES (?, ?, ?, ?)
            """, ("http://example.com", "Test Video", datetime.now().isoformat(), "completed"))
            conn.commit()
        
        # Verify data exists
        downloads = history_manager.get_all_downloads()
        assert len(downloads) == 1
        
        # Clear all history
        result = history_manager.clear_all_history()
        assert result == 1
        
        # Verify data is gone
        downloads = history_manager.get_all_downloads()
        assert len(downloads) == 0
    
    def test_clear_old_history(self, history_manager):
        """Test clearing old history."""
        # Add test data with different dates
        now = datetime.now()
        old_date = (now - timedelta(days=40)).isoformat()
        recent_date = (now - timedelta(days=10)).isoformat()
        
        with sqlite3.connect(history_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO downloads (url, title, download_date, status)
                VALUES (?, ?, ?, ?), (?, ?, ?, ?)
            """, (
                "http://old.com", "Old Video", old_date, "completed",
                "http://recent.com", "Recent Video", recent_date, "completed"
            ))
            conn.commit()
        
        # Verify both records exist
        downloads = history_manager.get_all_downloads()
        assert len(downloads) == 2
        
        # Clear old history (older than 30 days)
        result = history_manager.clear_old_history(days=30)
        assert result == 1
        
        # Verify only recent record remains
        downloads = history_manager.get_all_downloads()
        assert len(downloads) == 1
        assert downloads[0]['title'] == "Recent Video"
    
    def test_clear_failed_downloads(self, history_manager):
        """Test clearing failed downloads only."""
        # Add test data with different statuses
        with sqlite3.connect(history_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO downloads (url, title, download_date, status)
                VALUES (?, ?, ?, ?), (?, ?, ?, ?), (?, ?, ?, ?)
            """, (
                "http://success.com", "Success Video", datetime.now().isoformat(), "completed",
                "http://failed1.com", "Failed Video 1", datetime.now().isoformat(), "failed",
                "http://failed2.com", "Failed Video 2", datetime.now().isoformat(), "failed"
            ))
            conn.commit()
        
        # Verify all records exist
        downloads = history_manager.get_all_downloads()
        assert len(downloads) == 3
        
        # Clear failed downloads only
        result = history_manager.clear_failed_downloads()
        assert result == 2
        
        # Verify only successful record remains
        downloads = history_manager.get_all_downloads()
        assert len(downloads) == 1
        assert downloads[0]['status'] == "completed"
        assert downloads[0]['title'] == "Success Video"
    
    def test_clear_statistics(self, history_manager):
        """Test clearing statistics (should return 0 as it's a placeholder)."""
        result = history_manager.clear_statistics()
        assert result == 0
    
    def test_clear_history_with_no_data(self, history_manager):
        """Test clearing history when no data exists."""
        result = history_manager.clear_all_history()
        assert result == 0
        
        downloads = history_manager.get_all_downloads()
        assert len(downloads) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
