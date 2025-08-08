"""Download history management for VideoMilker."""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from ..config.settings import Settings
from ..exceptions.download_errors import HistoryError, DatabaseError


class HistoryManager:
    """Manages download history using SQLite database."""
    
    def __init__(self, settings: Settings):
        """Initialize the history manager."""
        self.settings = settings
        self.db_path = self._get_database_path()
        self._ensure_database()
    
    def _get_database_path(self) -> Path:
        """Get the database file path."""
        if self.settings.history.database_path.startswith('/'):
            # Absolute path
            return Path(self.settings.history.database_path)
        else:
            # Relative to config directory
            config_dir = Path.home() / ".config" / "videomilker"
            return config_dir / self.settings.history.database_path
    
    def _ensure_database(self) -> None:
        """Ensure the database exists and has the correct schema."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create downloads table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS downloads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL,
                        title TEXT,
                        filename TEXT,
                        file_path TEXT,
                        file_size INTEGER,
                        duration INTEGER,
                        uploader TEXT,
                        upload_date TEXT,
                        download_date TEXT NOT NULL,
                        status TEXT NOT NULL,
                        error_message TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_downloads_url 
                    ON downloads(url)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_downloads_date 
                    ON downloads(download_date)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_downloads_status 
                    ON downloads(status)
                """)
                
                conn.commit()
                
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {e}")
    
    def add_download(self, url: str, video_info: Dict[str, Any], 
                    result: Dict[str, Any]) -> int:
        """Add a download to the history."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract information
                title = video_info.get('title', '')
                filename = result.get('filename', '')
                file_path = str(Path(filename)) if filename else ''
                file_size = video_info.get('filesize', 0)
                duration = video_info.get('duration', 0)
                uploader = video_info.get('uploader', '')
                upload_date = video_info.get('upload_date', '')
                status = result.get('status', 'unknown')
                error_message = result.get('error', '')
                metadata = json.dumps(video_info, ensure_ascii=False)
                
                cursor.execute("""
                    INSERT INTO downloads (
                        url, title, filename, file_path, file_size, duration,
                        uploader, upload_date, download_date, status, error_message, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    url, title, filename, file_path, file_size, duration,
                    uploader, upload_date, datetime.now().isoformat(), 
                    status, error_message, metadata
                ))
                
                download_id = cursor.lastrowid
                conn.commit()
                
                # Cleanup old entries if needed
                self._cleanup_old_entries()
                
                return download_id
                
        except Exception as e:
            raise HistoryError(f"Failed to add download to history: {e}")
    
    def get_download(self, download_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific download by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM downloads WHERE id = ?
                """, (download_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                
                return None
                
        except Exception as e:
            raise HistoryError(f"Failed to get download: {e}")
    
    def get_recent_downloads(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent downloads."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM downloads 
                    ORDER BY download_date DESC 
                    LIMIT ?
                """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            raise HistoryError(f"Failed to get recent downloads: {e}")
    
    def get_all_downloads(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all downloads."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if limit:
                    cursor.execute("""
                        SELECT * FROM downloads 
                        ORDER BY download_date DESC 
                        LIMIT ?
                    """, (limit,))
                else:
                    cursor.execute("""
                        SELECT * FROM downloads 
                        ORDER BY download_date DESC
                    """)
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            raise HistoryError(f"Failed to get all downloads: {e}")
    
    def search_downloads(self, query: str) -> List[Dict[str, Any]]:
        """Search downloads by title, uploader, or URL."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                search_pattern = f"%{query}%"
                cursor.execute("""
                    SELECT * FROM downloads 
                    WHERE title LIKE ? OR uploader LIKE ? OR url LIKE ?
                    ORDER BY download_date DESC
                """, (search_pattern, search_pattern, search_pattern))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            raise HistoryError(f"Failed to search downloads: {e}")
    
    def advanced_search(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Advanced search with multiple filters."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Build query dynamically
                query_parts = ["SELECT * FROM downloads WHERE 1=1"]
                params = []
                
                # Title filter
                if 'title' in filters and filters['title']:
                    query_parts.append("AND title LIKE ?")
                    params.append(f"%{filters['title']}%")
                
                # Uploader filter
                if 'uploader' in filters and filters['uploader']:
                    query_parts.append("AND uploader LIKE ?")
                    params.append(f"%{filters['uploader']}%")
                
                # Status filter
                if 'status' in filters and filters['status']:
                    query_parts.append("AND status = ?")
                    params.append(filters['status'])
                
                # Date range filter
                if 'start_date' in filters and filters['start_date']:
                    query_parts.append("AND download_date >= ?")
                    params.append(filters['start_date'].isoformat())
                
                if 'end_date' in filters and filters['end_date']:
                    query_parts.append("AND download_date <= ?")
                    params.append(filters['end_date'].isoformat())
                
                # File size filter
                if 'min_size' in filters and filters['min_size']:
                    query_parts.append("AND file_size >= ?")
                    params.append(filters['min_size'])
                
                if 'max_size' in filters and filters['max_size']:
                    query_parts.append("AND file_size <= ?")
                    params.append(filters['max_size'])
                
                # Duration filter
                if 'min_duration' in filters and filters['min_duration']:
                    query_parts.append("AND duration >= ?")
                    params.append(filters['min_duration'])
                
                if 'max_duration' in filters and filters['max_duration']:
                    query_parts.append("AND duration <= ?")
                    params.append(filters['max_duration'])
                
                # Order by
                order_by = filters.get('order_by', 'download_date DESC')
                query_parts.append(f"ORDER BY {order_by}")
                
                # Limit
                if 'limit' in filters and filters['limit']:
                    query_parts.append("LIMIT ?")
                    params.append(filters['limit'])
                
                query = " ".join(query_parts)
                cursor.execute(query, params)
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            raise HistoryError(f"Failed to perform advanced search: {e}")
    
    def search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on partial query."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                search_pattern = f"%{partial_query}%"
                
                # Get title suggestions
                cursor.execute("""
                    SELECT DISTINCT title FROM downloads 
                    WHERE title LIKE ? AND title IS NOT NULL
                    LIMIT 5
                """, (search_pattern,))
                title_suggestions = [row[0] for row in cursor.fetchall()]
                
                # Get uploader suggestions
                cursor.execute("""
                    SELECT DISTINCT uploader FROM downloads 
                    WHERE uploader LIKE ? AND uploader IS NOT NULL
                    LIMIT 5
                """, (search_pattern,))
                uploader_suggestions = [row[0] for row in cursor.fetchall()]
                
                return title_suggestions + uploader_suggestions
                
        except Exception as e:
            raise HistoryError(f"Failed to get search suggestions: {e}")
    
    def get_downloads_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get downloads by status."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM downloads 
                    WHERE status = ?
                    ORDER BY download_date DESC
                """, (status,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            raise HistoryError(f"Failed to get downloads by status: {e}")
    
    def get_downloads_by_date_range(self, start_date: datetime, 
                                  end_date: datetime) -> List[Dict[str, Any]]:
        """Get downloads within a date range."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM downloads 
                    WHERE download_date BETWEEN ? AND ?
                    ORDER BY download_date DESC
                """, (start_date.isoformat(), end_date.isoformat()))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            raise HistoryError(f"Failed to get downloads by date range: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get download statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total downloads
                cursor.execute("SELECT COUNT(*) FROM downloads")
                total_downloads = cursor.fetchone()[0]
                
                # Successful downloads
                cursor.execute("SELECT COUNT(*) FROM downloads WHERE status = 'completed'")
                successful_downloads = cursor.fetchone()[0]
                
                # Failed downloads
                cursor.execute("SELECT COUNT(*) FROM downloads WHERE status = 'failed'")
                failed_downloads = cursor.fetchone()[0]
                
                # Total file size
                cursor.execute("SELECT SUM(file_size) FROM downloads WHERE status = 'completed'")
                total_size = cursor.fetchone()[0] or 0
                
                # Average file size
                cursor.execute("SELECT AVG(file_size) FROM downloads WHERE status = 'completed'")
                avg_size = cursor.fetchone()[0] or 0
                
                # Downloads today
                today = datetime.now().date()
                cursor.execute("""
                    SELECT COUNT(*) FROM downloads 
                    WHERE DATE(download_date) = ?
                """, (today.isoformat(),))
                downloads_today = cursor.fetchone()[0]
                
                # Downloads this week
                week_ago = today - timedelta(days=7)
                cursor.execute("""
                    SELECT COUNT(*) FROM downloads 
                    WHERE DATE(download_date) >= ?
                """, (week_ago.isoformat(),))
                downloads_this_week = cursor.fetchone()[0]
                
                return {
                    'total_downloads': total_downloads,
                    'successful_downloads': successful_downloads,
                    'failed_downloads': failed_downloads,
                    'success_rate': (successful_downloads / total_downloads * 100) if total_downloads > 0 else 0,
                    'total_size_bytes': total_size,
                    'total_size_mb': total_size / (1024 * 1024),
                    'total_size_gb': total_size / (1024 * 1024 * 1024),
                    'average_size_bytes': avg_size,
                    'average_size_mb': avg_size / (1024 * 1024),
                    'downloads_today': downloads_today,
                    'downloads_this_week': downloads_this_week
                }
                
        except Exception as e:
            raise HistoryError(f"Failed to get statistics: {e}")
    
    def update_download(self, download_id: int, updates: Dict[str, Any]) -> bool:
        """Update a download record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build update query
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ['title', 'filename', 'file_path', 'file_size', 
                              'duration', 'uploader', 'upload_date', 'status', 
                              'error_message', 'metadata']:
                        set_clauses.append(f"{key} = ?")
                        values.append(value)
                
                if not set_clauses:
                    return False
                
                values.append(download_id)
                
                cursor.execute(f"""
                    UPDATE downloads 
                    SET {', '.join(set_clauses)}
                    WHERE id = ?
                """, values)
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            raise HistoryError(f"Failed to update download: {e}")
    
    def delete_download(self, download_id: int) -> bool:
        """Delete a download record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM downloads WHERE id = ?", (download_id,))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            raise HistoryError(f"Failed to delete download: {e}")
    
    def clear_history(self) -> int:
        """Clear all download history."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM downloads")
                conn.commit()
                
                return cursor.rowcount
                
        except Exception as e:
            raise HistoryError(f"Failed to clear history: {e}")
    
    def _cleanup_old_entries(self) -> None:
        """Clean up old entries based on settings."""
        if not self.settings.history.auto_cleanup:
            return
        
        try:
            cutoff_date = datetime.now() - timedelta(days=self.settings.history.cleanup_days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM downloads 
                    WHERE download_date < ?
                """, (cutoff_date.isoformat(),))
                
                conn.commit()
                
        except Exception as e:
            # Don't raise error for cleanup failures
            pass
    
    def export_history(self, export_path: Path, format: str = 'json') -> None:
        """Export download history to a file."""
        try:
            downloads = self.get_all_downloads()
            
            if format.lower() == 'json':
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(downloads, f, indent=2, ensure_ascii=False, default=str)
            
            elif format.lower() == 'csv':
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    if downloads:
                        writer = csv.DictWriter(f, fieldnames=downloads[0].keys())
                        writer.writeheader()
                        writer.writerows(downloads)
            
            else:
                raise HistoryError(f"Unsupported export format: {format}")
                
        except Exception as e:
            raise HistoryError(f"Failed to export history: {e}")
    
    def import_history(self, import_path: Path, format: str = 'json') -> int:
        """Import download history from a file."""
        try:
            if format.lower() == 'json':
                with open(import_path, 'r', encoding='utf-8') as f:
                    downloads = json.load(f)
            
            elif format.lower() == 'csv':
                import csv
                downloads = []
                with open(import_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    downloads = list(reader)
            
            else:
                raise HistoryError(f"Unsupported import format: {format}")
            
            # Import downloads
            imported_count = 0
            for download in downloads:
                try:
                    self.add_download(
                        download['url'],
                        json.loads(download.get('metadata', '{}')),
                        {'status': download.get('status', 'unknown')}
                    )
                    imported_count += 1
                except Exception:
                    # Skip invalid entries
                    continue
            
            return imported_count
            
        except Exception as e:
            raise HistoryError(f"Failed to import history: {e}")
    
    def backup_database(self, backup_path: Path) -> None:
        """Create a backup of the database."""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
        except Exception as e:
            raise HistoryError(f"Failed to backup database: {e}")
    
    def restore_database(self, backup_path: Path) -> None:
        """Restore database from backup."""
        try:
            import shutil
            shutil.copy2(backup_path, self.db_path)
        except Exception as e:
            raise HistoryError(f"Failed to restore database: {e}") 