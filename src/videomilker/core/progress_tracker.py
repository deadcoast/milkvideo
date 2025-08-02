"""Progress tracking for VideoMilker downloads."""

import time
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn, TransferSpeedColumn, FileSizeColumn
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table


@dataclass
class DownloadProgress:
    """Represents the progress of a single download."""
    url: str
    title: str = ""
    progress: float = 0.0
    speed: float = 0.0
    eta: Optional[float] = None
    size: int = 0
    downloaded: int = 0
    status: str = "initializing"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Get the duration of the download."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return datetime.now() - self.start_time
        return None
    
    @property
    def speed_mbps(self) -> float:
        """Get speed in MB/s."""
        return self.speed / (1024 * 1024) if self.speed else 0.0
    
    @property
    def size_mb(self) -> float:
        """Get size in MB."""
        return self.size / (1024 * 1024) if self.size else 0.0
    
    @property
    def downloaded_mb(self) -> float:
        """Get downloaded size in MB."""
        return self.downloaded / (1024 * 1024) if self.downloaded else 0.0


class ProgressTracker:
    """Tracks download progress and provides visual feedback."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize the progress tracker."""
        self.console = console or Console()
        self.downloads: Dict[str, DownloadProgress] = {}
        self.callbacks: Dict[str, Callable] = {}
        self.live_display: Optional[Live] = None
        self.progress_bars: Optional[Progress] = None
        
    def add_download(self, download_id: str, url: str, title: str = "") -> None:
        """Add a new download to track."""
        self.downloads[download_id] = DownloadProgress(url=url, title=title)
    
    def update_progress(self, download_id: str, progress: float, speed: float = 0.0, 
                       eta: Optional[float] = None, size: int = 0, downloaded: int = 0) -> None:
        """Update progress for a specific download."""
        if download_id in self.downloads:
            download = self.downloads[download_id]
            download.progress = progress
            download.speed = speed
            download.eta = eta
            download.size = size
            download.downloaded = downloaded
            download.status = "downloading"
            
            # Call callback if registered
            if download_id in self.callbacks:
                self.callbacks[download_id](download)
    
    def complete_download(self, download_id: str, success: bool = True, error: Optional[str] = None) -> None:
        """Mark a download as completed."""
        if download_id in self.downloads:
            download = self.downloads[download_id]
            download.end_time = datetime.now()
            download.status = "completed" if success else "failed"
            download.error = error
            download.progress = 100.0 if success else download.progress
    
    def get_download(self, download_id: str) -> Optional[DownloadProgress]:
        """Get download progress by ID."""
        return self.downloads.get(download_id)
    
    def get_all_downloads(self) -> Dict[str, DownloadProgress]:
        """Get all tracked downloads."""
        return self.downloads.copy()
    
    def remove_download(self, download_id: str) -> None:
        """Remove a download from tracking."""
        if download_id in self.downloads:
            del self.downloads[download_id]
        if download_id in self.callbacks:
            del self.callbacks[download_id]
    
    def clear_all(self) -> None:
        """Clear all downloads."""
        self.downloads.clear()
        self.callbacks.clear()
    
    def register_callback(self, download_id: str, callback: Callable[[DownloadProgress], None]) -> None:
        """Register a callback for progress updates."""
        self.callbacks[download_id] = callback
    
    def unregister_callback(self, download_id: str) -> None:
        """Unregister a callback."""
        if download_id in self.callbacks:
            del self.callbacks[download_id]
    
    def start_live_display(self) -> None:
        """Start live progress display."""
        self.progress_bars = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
            console=self.console
        )
        
        self.live_display = Live(self.progress_bars, console=self.console, refresh_per_second=4)
        self.live_display.start()
    
    def stop_live_display(self) -> None:
        """Stop live progress display."""
        if self.live_display:
            self.live_display.stop()
            self.live_display = None
        if self.progress_bars:
            self.progress_bars = None
    
    def create_progress_table(self) -> Table:
        """Create a table showing all download progress."""
        table = Table(title="Download Progress")
        table.add_column("URL", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Progress", style="yellow")
        table.add_column("Speed", style="blue")
        table.add_column("ETA", style="magenta")
        table.add_column("Status", style="red")
        
        for download in self.downloads.values():
            progress_text = f"{download.progress:.1f}%"
            speed_text = f"{download.speed_mbps:.2f} MB/s" if download.speed > 0 else "N/A"
            eta_text = str(timedelta(seconds=int(download.eta))) if download.eta else "N/A"
            
            table.add_row(
                download.url[:50] + "..." if len(download.url) > 50 else download.url,
                download.title[:30] + "..." if len(download.title) > 30 else download.title,
                progress_text,
                speed_text,
                eta_text,
                download.status
            )
        
        return table
    
    def create_summary_panel(self) -> Panel:
        """Create a summary panel of all downloads."""
        total_downloads = len(self.downloads)
        completed = len([d for d in self.downloads.values() if d.status == "completed"])
        failed = len([d for d in self.downloads.values() if d.status == "failed"])
        downloading = len([d for d in self.downloads.values() if d.status == "downloading"])
        
        total_size = sum(d.size_mb for d in self.downloads.values() if d.size > 0)
        downloaded_size = sum(d.downloaded_mb for d in self.downloads.values() if d.downloaded > 0)
        
        summary_text = f"""
        Total Downloads: {total_downloads}
        Completed: {completed} | Failed: {failed} | Downloading: {downloading}
        Total Size: {total_size:.2f} MB | Downloaded: {downloaded_size:.2f} MB
        """
        
        return Panel(summary_text, title="Download Summary", border_style="blue")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get download statistics."""
        total_downloads = len(self.downloads)
        completed = len([d for d in self.downloads.values() if d.status == "completed"])
        failed = len([d for d in self.downloads.values() if d.status == "failed"])
        downloading = len([d for d in self.downloads.values() if d.status == "downloading"])
        
        total_size = sum(d.size_mb for d in self.downloads.values() if d.size > 0)
        downloaded_size = sum(d.downloaded_mb for d in self.downloads.values() if d.downloaded > 0)
        
        total_duration = sum(
            (d.duration.total_seconds() for d in self.downloads.values() if d.duration),
            0.0
        )
        
        avg_speed = sum(d.speed_mbps for d in self.downloads.values() if d.speed > 0) / max(
            len([d for d in self.downloads.values() if d.speed > 0]), 1
        )
        
        return {
            "total_downloads": total_downloads,
            "completed": completed,
            "failed": failed,
            "downloading": downloading,
            "success_rate": (completed / total_downloads * 100) if total_downloads > 0 else 0,
            "total_size_mb": total_size,
            "downloaded_size_mb": downloaded_size,
            "total_duration_seconds": total_duration,
            "average_speed_mbps": avg_speed
        } 