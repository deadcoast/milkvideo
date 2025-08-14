"""File management for VideoMilker downloads."""

import hashlib
import json
import os
import shutil
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

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

        if not self.settings.download.create_day_folders:
            return self.base_path
        day_folder = self.base_path / f"{date.day:02d}"
        day_folder.mkdir(parents=True, exist_ok=True)
        return day_folder

    def get_batch_folder(self, date: Optional[datetime] = None) -> Path:
        """Get the batch downloads folder for a specific day."""
        day_folder = self.get_day_folder(date)
        batch_folder = day_folder / "batch_downloads"
        batch_folder.mkdir(parents=True, exist_ok=True)
        return batch_folder

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename for safe storage."""
        if self.settings.download.restrict_filenames:
            # Use slugify for strict ASCII-only filenames
            return slugify(filename, allow_unicode=False, separator="_")
        # Allow Unicode but remove/replace problematic characters
        import re

        # Remove null bytes and control characters
        filename = re.sub(r"[\x00-\x1f\x7f]", "", filename)
        # Replace problematic characters on Windows
        filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
        # Remove leading/trailing spaces and dots
        filename = filename.strip(" .")
        return filename

    def generate_filename(self, title: str, ext: str, date: Optional[datetime] = None) -> str:
        """Generate a filename based on the naming template."""
        if date is None:
            date = datetime.now()

        # Create a template context
        context = {
            "title": self.sanitize_filename(title),
            "ext": ext,
            "upload_date": date.strftime("%Y-%m-%d"),
            "upload_date_short": date.strftime("%Y%m%d"),
            "day": f"{date.day:02d}",
            "month": f"{date.month:02d}",
            "year": str(date.year),
            "timestamp": str(int(date.timestamp())),
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
        info_file = download_path.with_suffix(".info.json")

        # Add metadata
        info["_videomilker_metadata"] = {
            "download_date": datetime.now().isoformat(),
            "download_path": str(download_path),
            "settings_version": self.settings.version,
        }

        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2, ensure_ascii=False)

        return info_file

    def save_batch_log(self, batch_folder: Path, urls: List[str], results: List[Dict[str, Any]]) -> Path:
        """Save batch download log."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = batch_folder / f"batch_log_{timestamp}.json"

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "total_urls": len(urls),
            "successful": len([r for r in results if r.get("status") == "completed"]),
            "failed": len([r for r in results if r.get("status") == "failed"]),
            "urls": urls,
            "results": results,
        }

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        return log_file

    def cleanup_temp_files(self, folder: Path) -> None:
        """Clean up temporary files in a folder."""
        temp_extensions = [".part", ".tmp", ".temp"]

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
                "total": stat.total,
                "used": stat.used,
                "free": stat.free,
                "total_gb": stat.total // (1024**3),
                "used_gb": stat.used // (1024**3),
                "free_gb": stat.free // (1024**3),
            }
        except Exception:
            return {"total": 0, "used": 0, "free": 0, "total_gb": 0, "used_gb": 0, "free_gb": 0}

    def check_disk_space(self, required_size: int, path: Optional[Path] = None) -> bool:
        """Check if there's enough disk space for a download."""
        disk_info = self.get_disk_space(path)
        return disk_info["free"] >= required_size

    def get_folder_size(self, folder: Path) -> int:
        """Get the total size of a folder in bytes."""
        total_size = 0

        try:
            for file_path in folder.rglob("*"):
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
                if file_path.is_file() and file_path.suffix.lower() in [
                    ".mp4",
                    ".mkv",
                    ".webm",
                    ".avi",
                    ".mov",
                    ".m4a",
                    ".mp3",
                    ".opus",
                    ".aac",
                    ".flac",
                ]:
                    stat = file_path.stat()
                    downloads.append(
                        {
                            "path": file_path,
                            "name": file_path.name,
                            "size": stat.st_size,
                            "size_mb": stat.st_size / (1024 * 1024),
                            "modified": datetime.fromtimestamp(stat.st_mtime),
                            "created": datetime.fromtimestamp(stat.st_ctime),
                        }
                    )
        except Exception:
            pass

        return downloads

    def organize_downloads(self, source_folder: Path, target_folder: Optional[Path] = None) -> None:
        """Organize downloads by moving them to day-based folders."""
        if target_folder is None:
            target_folder = self.base_path

        downloads = self.list_downloads(source_folder, recursive=False)

        for download in downloads:
            file_path = download["path"]
            modified_date = download["modified"]

            # Get target day folder
            day_folder = self.get_day_folder(modified_date)

            # Move file to day folder
            target_path = day_folder / file_path.name
            target_path = self.get_unique_filename(day_folder, file_path.name)

            try:
                shutil.move(str(file_path), str(target_path))
            except Exception as e:
                raise FileError(f"Failed to move {file_path} to {target_path}: {e}") from e

    def create_backup(self, source_path: Path, backup_folder: Optional[Path] = None) -> Path:
        """Create a backup of a file or folder."""
        if backup_folder is None:
            backup_folder = self.base_path / "backups"

        backup_folder.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

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
            for file_path in folder.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_date:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception:
                        pass
        except Exception:
            pass

        return deleted_count

    def calculate_file_hash(self, file_path: Path, algorithm: str = "md5", chunk_size: int = 8192) -> str:
        """Calculate hash of a file."""
        try:
            hash_obj = hashlib.new(algorithm)

            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hash_obj.update(chunk)

            return hash_obj.hexdigest()

        except Exception as e:
            raise FileError(f"Failed to calculate hash for {file_path}: {e}") from e

    def find_duplicates_by_hash(
        self, folder: Optional[Path] = None, recursive: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Find duplicate files by comparing their hashes."""
        if folder is None:
            folder = self.base_path

        file_hashes: Dict[str, List[Dict[str, Any]]] = {}

        downloads = self.list_downloads(folder, recursive)

        for download in downloads:
            file_path = download["path"]

            try:
                file_hash = self.calculate_file_hash(file_path)

                if file_hash not in file_hashes:
                    file_hashes[file_hash] = []

                file_info = {
                    "path": file_path,
                    "name": file_path.name,
                    "size": download["size"],
                    "size_mb": download["size_mb"],
                    "modified": download["modified"],
                    "hash": file_hash,
                }

                file_hashes[file_hash].append(file_info)

            except Exception:
                continue  # Skip files that can't be hashed

        return {hash_val: files for hash_val, files in file_hashes.items() if len(files) > 1}

    def find_duplicates_by_name_size(
        self, folder: Optional[Path] = None, recursive: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Find potential duplicates by comparing filename and size."""
        if folder is None:
            folder = self.base_path

        file_groups: Dict[str, List[Dict[str, Any]]] = {}

        downloads = self.list_downloads(folder, recursive)

        for download in downloads:
            # Create a key from filename and size
            key = f"{download['name']}_{download['size']}"

            if key not in file_groups:
                file_groups[key] = []

            file_groups[key].append(download)

        return {key: files for key, files in file_groups.items() if len(files) > 1}

    def find_similar_files(
        self, folder: Optional[Path] = None, similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Find files with similar names (potential duplicates with different quality)."""
        if folder is None:
            folder = self.base_path

        downloads = self.list_downloads(folder, recursive=True)
        similar_groups = []

        # Group files by similar base names
        for i, file1 in enumerate(downloads):
            for j, file2 in enumerate(downloads[i + 1 :], i + 1):
                similarity = self._calculate_name_similarity(file1["name"], file2["name"])

                if similarity >= similarity_threshold:
                    similar_groups.append(
                        {
                            "similarity": similarity,
                            "files": [file1, file2],
                            "size_diff_mb": abs(file1["size_mb"] - file2["size_mb"]),
                        }
                    )

        return similar_groups

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two filenames using basic string similarity."""
        # Remove extensions and normalize
        name1_clean = Path(name1).stem.lower()
        name2_clean = Path(name2).stem.lower()

        # Remove common patterns that might indicate quality differences
        patterns_to_remove = [
            r"_\d+p",
            r"_720p?",
            r"_1080p?",
            r"_480p?",
            r"_360p?",
            r"_hd",
            r"_sd",
            r"_high",
            r"_low",
            r"_best",
            r"_worst",
            r"_\d+kbps",
            r"_\d+k",
            r"_mp3",
            r"_m4a",
            r"_flac",
        ]

        import re

        for pattern in patterns_to_remove:
            name1_clean = re.sub(pattern, "", name1_clean)
            name2_clean = re.sub(pattern, "", name2_clean)

        # Calculate Levenshtein distance ratio
        return self._levenshtein_ratio(name1_clean, name2_clean)

    def _levenshtein_ratio(self, s1: str, s2: str) -> float:
        """Calculate the Levenshtein distance ratio between two strings."""
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        len1, len2 = len(s1), len(s2)

        # Create matrix
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        # Initialize first row and column
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j

        # Fill matrix
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1
                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,  # deletion
                    matrix[i][j - 1] + 1,  # insertion
                    matrix[i - 1][j - 1] + cost,  # substitution
                )

        distance = matrix[len1][len2]
        max_len = max(len1, len2)

        return 1.0 - (distance / max_len) if max_len > 0 else 1.0

    def remove_duplicates(
        self, duplicates: Dict[str, List[Dict[str, Any]]], keep_strategy: str = "newest"
    ) -> List[str]:
        """Remove duplicate files based on the specified strategy.

        Args:
            duplicates: Dictionary of duplicate file groups
            keep_strategy: Strategy for which file to keep ('newest', 'oldest', 'largest', 'smallest')

        Returns:
            List of removed file paths
        """
        removed_files = []

        for file_group in duplicates.values():
            if len(file_group) <= 1:
                continue

            # Sort files based on strategy
            if keep_strategy == "newest":
                sorted_files = sorted(file_group, key=lambda f: f["modified"], reverse=True)
            elif keep_strategy == "oldest":
                sorted_files = sorted(file_group, key=lambda f: f["modified"])
            elif keep_strategy == "largest":
                sorted_files = sorted(file_group, key=lambda f: f["size"], reverse=True)
            elif keep_strategy == "smallest":
                sorted_files = sorted(file_group, key=lambda f: f["size"])
            else:
                sorted_files = file_group

            # Keep the first file, remove the rest
            files_to_remove = sorted_files[1:]

            for file_info in files_to_remove:
                try:
                    file_path = file_info["path"]
                    file_path.unlink()
                    removed_files.append(str(file_path))
                except Exception:
                    pass  # Skip files that can't be removed

        return removed_files

    def get_large_files(self, folder: Optional[Path] = None, size_threshold_mb: float = 500.0) -> List[Dict[str, Any]]:
        """Find files larger than the specified threshold."""
        if folder is None:
            folder = self.base_path

        threshold_bytes = size_threshold_mb * 1024 * 1024
        downloads = self.list_downloads(folder, recursive=True)

        large_files = [download for download in downloads if download["size"] > threshold_bytes]
        # Sort by size (largest first)
        large_files.sort(key=lambda f: f["size"], reverse=True)

        return large_files

    def get_old_files(self, folder: Optional[Path] = None, days_threshold: int = 30) -> List[Dict[str, Any]]:
        """Find files older than the specified threshold."""
        if folder is None:
            folder = self.base_path

        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        downloads = self.list_downloads(folder, recursive=True)

        old_files = [download for download in downloads if download["modified"] < cutoff_date]
        # Sort by age (oldest first)
        old_files.sort(key=lambda f: f["modified"])

        return old_files

    def cleanup_empty_folders(self, folder: Optional[Path] = None) -> List[str]:
        """Remove empty folders recursively."""
        if folder is None:
            folder = self.base_path

        removed_folders = []

        try:
            # Walk through folders bottom-up to handle nested empty folders
            for root, dirs, files in os.walk(folder, topdown=False):
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name

                    try:
                        # Check if folder is empty
                        if not any(dir_path.iterdir()):
                            dir_path.rmdir()
                            removed_folders.append(str(dir_path))
                    except Exception:
                        pass  # Skip folders that can't be removed
        except Exception:
            pass

        return removed_folders

    def move_files_by_extension(
        self, source_folder: Optional[Path] = None, extension_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, int]:
        """Organize files by moving them to folders based on their extensions."""
        if source_folder is None:
            source_folder = self.base_path

        if extension_mapping is None:
            extension_mapping = {
                ".mp4": "videos",
                ".mkv": "videos",
                ".webm": "videos",
                ".avi": "videos",
                ".mov": "videos",
                ".mp3": "audio",
                ".m4a": "audio",
                ".flac": "audio",
                ".opus": "audio",
                ".aac": "audio",
                ".jpg": "images",
                ".png": "images",
                ".jpeg": "images",
                ".srt": "subtitles",
                ".vtt": "subtitles",
                ".json": "metadata",
            }

        moved_counts = {}

        downloads = self.list_downloads(source_folder, recursive=False)

        for download in downloads:
            file_path = download["path"]
            extension = file_path.suffix.lower()

            if extension in extension_mapping:
                target_folder_name = extension_mapping[extension]
                target_folder = source_folder / target_folder_name
                target_folder.mkdir(exist_ok=True)

                target_path = self.get_unique_filename(target_folder, file_path.name)

                try:
                    shutil.move(str(file_path), str(target_path))
                    moved_counts[target_folder_name] = moved_counts.get(target_folder_name, 0) + 1
                except Exception:
                    pass  # Skip files that can't be moved

        return moved_counts

    def analyze_storage_usage(self, folder: Optional[Path] = None) -> Dict[str, Any]:
        """Analyze storage usage and provide recommendations."""
        if folder is None:
            folder = self.base_path

        downloads = self.list_downloads(folder, recursive=True)

        if not downloads:
            return {"total_files": 0, "total_size_mb": 0, "recommendations": ["No files found in download folder"]}

        # Calculate statistics
        total_size = sum(d["size"] for d in downloads)
        total_files = len(downloads)

        # Group by extension
        extension_stats = {}
        for download in downloads:
            ext = Path(download["name"]).suffix.lower()
            if ext not in extension_stats:
                extension_stats[ext] = {"count": 0, "size": 0}
            extension_stats[ext]["count"] += 1
            extension_stats[ext]["size"] += download["size"]

        # Find duplicates
        duplicates = self.find_duplicates_by_hash(folder)
        duplicate_count = sum(len(files) - 1 for files in duplicates.values())
        duplicate_size = sum(
            sum(f["size"] for f in files[1:])
            for files in duplicates.values()  # Size of duplicates (excluding first)
        )

        # Find large files
        large_files = self.get_large_files(folder, 500.0)

        # Find old files
        old_files = self.get_old_files(folder, 90)

        # Generate recommendations
        recommendations = []

        if duplicate_count > 0:
            recommendations.append(
                f"Remove {duplicate_count} duplicate files to save {duplicate_size / (1024 * 1024):.1f} MB"
            )

        if len(large_files) > 10:
            recommendations.append(f"Review {len(large_files)} large files (>500MB) for potential cleanup")

        if len(old_files) > 20:
            recommendations.append(f"Consider archiving or removing {len(old_files)} old files (>90 days)")

        if total_size > 10 * 1024 * 1024 * 1024:  # 10GB
            recommendations.append("Consider organizing files by date or type to improve management")

        return {
            "total_files": total_files,
            "total_size_mb": total_size / (1024 * 1024),
            "total_size_gb": total_size / (1024 * 1024 * 1024),
            "extension_stats": extension_stats,
            "duplicates_count": duplicate_count,
            "duplicates_size_mb": duplicate_size / (1024 * 1024),
            "large_files_count": len(large_files),
            "old_files_count": len(old_files),
            "recommendations": recommendations,
        }
