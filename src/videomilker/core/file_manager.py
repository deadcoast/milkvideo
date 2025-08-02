"""File management for VideoMilker downloads."""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from slugify import slugify

from ..config.settings import Settings
from ..exceptions.download_errors import FileError


class FileManager:
    """Manages file operations and organization for VideoMilker."""
    
    def __init__(self, settings: Settings):
        """Initialize the file manager."""
        self.settings = settings
        self.base_path = Path(settings.download.path).expanduser()
        self.ensure_base_directory()
    
    def ensure_base_directory(self) -> None:
        """Ensure the base download directory exists."""
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def get_day_folder(self, date: Optional[datetime] = None) -> Path:
        """Get the folder for a specific day (DD format)."""
        if date is None:
            date = datetime.now()
        
        if self.settings.download.create_day_folders:
            day_folder = self.base_path / f"{date.day:02d}"
            day_folder.mkdir(parents=True, exist_ok=True)
            return day_folder
        else:
            return self.base_path
    
    def get_batch_folder(self, date: Optional[datetime] = None) -> Path:
        """Get the batch downloads folder for a specific day."""
        day_folder = self.get_day_folder(date)
        batch_folder = day_folder / "batch_downloads"
        batch_folder.mkdir(parents=True, exist_ok=True)
        return batch_folder
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename for safe storage."""
        # Remove or replace problematic characters
        if self.settings.download.restrict_filenames:
            # Use slugify for strict ASCII-only filenames
            return slugify(filename, allow_unicode=False, separator='_')
        else:
            # Allow Unicode but remove/replace problematic characters
            import re
            # Remove null bytes and control characters
            filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
            # Replace problematic characters on Windows
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            # Remove leading/trailing spaces and dots
            filename = filename.strip(' .')
            return filename
    
    def generate_filename(self, title: str, ext: str, date: Optional[datetime] = None) -> str:
        """Generate a filename based on the naming template."""
        if date is None:
            date = datetime.now()
        
        # Create a template context
        context = {
            'title': self.sanitize_filename(title),
            'ext': ext,
            'upload_date': date.strftime('%Y-%m-%d'),
            'upload_date_short': date.strftime('%Y%m%d'),
            'day': f"{date.day:02d}",
            'month': f"{date.month:02d}",
            'year': str(date.year),
            'timestamp': str(int(date.timestamp())),
        }
        
        # Apply the naming template
        template = self.settings.download.file_naming
        filename = template
        
        # Replace template variables
        for key, value in context.items():
            placeholder = f"%({key})s"
            filename = filename.replace(placeholder, str(value))
        
        # Ensure we have a valid extension
        if not filename.endswith(f".{ext}"):
            filename = f"{filename}.{ext}"
        
        return filename
    
    def get_unique_filename(self, base_path: Path, filename: str) -> Path:
        """Get a unique filename by adding a number if the file exists."""
        file_path = base_path / filename
        
        if not file_path.exists():
            return file_path
        
        # Split filename and extension
        stem = file_path.stem
        suffix = file_path.suffix
        counter = 1
        
        while True:
            new_filename = f"{stem}_{counter}{suffix}"
            new_path = base_path / new_filename
            
            if not new_path.exists():
                return new_path
            
            counter += 1
    
    def save_download_info(self, download_path: Path, info: Dict[str, Any]) -> Path:
        """Save download information to a JSON file."""
        info_file = download_path.with_suffix('.info.json')
        
        # Add metadata
        info['_videomilker_metadata'] = {
            'download_date': datetime.now().isoformat(),
            'download_path': str(download_path),
            'settings_version': self.settings.version
        }
        
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        return info_file
    
    def save_batch_log(self, batch_folder: Path, urls: List[str], results: List[Dict[str, Any]]) -> Path:
        """Save batch download log."""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = batch_folder / f"batch_log_{timestamp}.json"
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'total_urls': len(urls),
            'successful': len([r for r in results if r.get('status') == 'completed']),
            'failed': len([r for r in results if r.get('status') == 'failed']),
            'urls': urls,
            'results': results
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        return log_file
    
    def cleanup_temp_files(self, folder: Path) -> None:
        """Clean up temporary files in a folder."""
        temp_extensions = ['.part', '.tmp', '.temp']
        
        for ext in temp_extensions:
            for temp_file in folder.glob(f"*{ext}"):
                try:
                    temp_file.unlink()
                except Exception:
                    pass  # Ignore cleanup errors
    
    def get_disk_space(self, path: Optional[Path] = None) -> Dict[str, int]:
        """Get available disk space information."""
        if path is None:
            path = self.base_path
        
        try:
            stat = shutil.disk_usage(path)
            return {
                'total': stat.total,
                'used': stat.used,
                'free': stat.free,
                'total_gb': stat.total // (1024**3),
                'used_gb': stat.used // (1024**3),
                'free_gb': stat.free // (1024**3)
            }
        except Exception:
            return {
                'total': 0,
                'used': 0,
                'free': 0,
                'total_gb': 0,
                'used_gb': 0,
                'free_gb': 0
            }
    
    def check_disk_space(self, required_size: int, path: Optional[Path] = None) -> bool:
        """Check if there's enough disk space for a download."""
        disk_info = self.get_disk_space(path)
        return disk_info['free'] >= required_size
    
    def get_folder_size(self, folder: Path) -> int:
        """Get the total size of a folder in bytes."""
        total_size = 0
        
        try:
            for file_path in folder.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        
        return total_size
    
    def list_downloads(self, folder: Optional[Path] = None, recursive: bool = True) -> List[Dict[str, Any]]:
        """List all downloaded files in a folder."""
        if folder is None:
            folder = self.base_path
        
        downloads = []
        
        try:
            pattern = "**/*" if recursive else "*"
            for file_path in folder.glob(pattern):
                if file_path.is_file() and file_path.suffix.lower() in ['.mp4', '.mkv', '.webm', '.avi', '.mov', '.m4a', '.mp3', '.opus', '.aac', '.flac']:
                    stat = file_path.stat()
                    downloads.append({
                        'path': file_path,
                        'name': file_path.name,
                        'size': stat.st_size,
                        'size_mb': stat.st_size / (1024 * 1024),
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'created': datetime.fromtimestamp(stat.st_ctime)
                    })
        except Exception:
            pass
        
        return downloads
    
    def organize_downloads(self, source_folder: Path, target_folder: Optional[Path] = None) -> None:
        """Organize downloads by moving them to day-based folders."""
        if target_folder is None:
            target_folder = self.base_path
        
        downloads = self.list_downloads(source_folder, recursive=False)
        
        for download in downloads:
            file_path = download['path']
            modified_date = download['modified']
            
            # Get target day folder
            day_folder = self.get_day_folder(modified_date)
            
            # Move file to day folder
            target_path = day_folder / file_path.name
            target_path = self.get_unique_filename(day_folder, file_path.name)
            
            try:
                shutil.move(str(file_path), str(target_path))
            except Exception as e:
                raise FileError(f"Failed to move {file_path} to {target_path}: {e}")
    
    def create_backup(self, source_path: Path, backup_folder: Optional[Path] = None) -> Path:
        """Create a backup of a file or folder."""
        if backup_folder is None:
            backup_folder = self.base_path / "backups"
        
        backup_folder.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if source_path.is_file():
            backup_path = backup_folder / f"{source_path.stem}_{timestamp}{source_path.suffix}"
            shutil.copy2(source_path, backup_path)
        else:
            backup_path = backup_folder / f"{source_path.name}_{timestamp}"
            shutil.copytree(source_path, backup_path)
        
        return backup_path
    
    def cleanup_old_files(self, days: int = 30, folder: Optional[Path] = None) -> int:
        """Clean up files older than specified days."""
        if folder is None:
            folder = self.base_path
        
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        try:
            for file_path in folder.rglob('*'):
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_date:
                        try:
                            file_path.unlink()
                            deleted_count += 1
                        except Exception:
                            pass
        except Exception:
            pass
        
        return deleted_count
