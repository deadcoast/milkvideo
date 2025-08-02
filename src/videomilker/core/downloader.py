"""Core downloader functionality for VideoMilker."""

import asyncio
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
import yt_dlp
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn

from ..config.settings import Settings
from ..exceptions.download_errors import DownloadError, FormatError, NetworkError
from .progress_tracker import ProgressTracker
from .file_manager import FileManager


class VideoDownloader:
    """Main video downloader class with yt-dlp integration."""
    
    def __init__(self, settings: Settings, console: Optional[Console] = None):
        """Initialize the downloader."""
        self.settings = settings
        self.console = console or Console()
        self.file_manager = FileManager(settings)
        self.progress_tracker = ProgressTracker()
        self.download_queue: List[Dict[str, Any]] = []
        self.current_download: Optional[Dict[str, Any]] = None
        self.is_downloading = False
        
    def add_to_queue(self, url: str, options: Optional[Dict[str, Any]] = None) -> str:
        """Add a URL to the download queue."""
        download_id = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        download_item = {
            'id': download_id,
            'url': url,
            'options': options or {},
            'status': 'queued',
            'progress': 0.0,
            'speed': 0,
            'eta': None,
            'size': 0,
            'filename': '',
            'error': None,
            'start_time': None,
            'end_time': None
        }
        
        self.download_queue.append(download_item)
        return download_id
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get the current queue status."""
        return {
            'total': len(self.download_queue),
            'queued': len([d for d in self.download_queue if d['status'] == 'queued']),
            'downloading': len([d for d in self.download_queue if d['status'] == 'downloading']),
            'completed': len([d for d in self.download_queue if d['status'] == 'completed']),
            'failed': len([d for d in self.download_queue if d['status'] == 'failed']),
            'current': self.current_download
        }
    
    def download_single(self, url: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Download a single video."""
        try:
            # Prepare download options
            yt_dlp_options = self._prepare_yt_dlp_options(options)
            
            # Create progress callback
            progress_callback = self._create_progress_callback()
            
            # Download the video
            with yt_dlp.YoutubeDL(yt_dlp_options) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                
                # Update progress callback with info
                progress_callback['info'] = info
                
                # Download the video
                ydl.download([url])
            
            return {
                'status': 'completed',
                'info': info,
                'filename': self._get_downloaded_filename(info, yt_dlp_options)
            }
            
        except Exception as e:
            raise DownloadError(f"Failed to download {url}: {str(e)}")
    
    def download_batch(self, urls: List[str], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Download multiple videos in batch."""
        results = []
        
        for i, url in enumerate(urls):
            try:
                self.console.print(f"[cyan]Downloading {i+1}/{len(urls)}: {url}[/cyan]")
                result = self.download_single(url, options)
                results.append(result)
                
            except Exception as e:
                self.console.print(f"[red]Failed to download {url}: {str(e)}[/red]")
                results.append({
                    'status': 'failed',
                    'url': url,
                    'error': str(e)
                })
        
        return results
    
    def _prepare_yt_dlp_options(self, custom_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare yt-dlp options from settings and custom options."""
        # Start with default settings
        options = self.settings.get_yt_dlp_options()
        
        # Set output path
        download_path = self.settings.get_download_path()
        download_path.mkdir(parents=True, exist_ok=True)
        options['outtmpl'] = str(download_path / options['outtmpl'])
        
        # Add progress hooks
        options['progress_hooks'] = [self._progress_hook]
        
        # Add custom options
        if custom_options:
            options.update(custom_options)
        
        return options
    
    def _create_progress_callback(self) -> Dict[str, Any]:
        """Create a progress callback for tracking download progress."""
        return {
            'info': None,
            'progress': 0.0,
            'speed': 0,
            'eta': None,
            'size': 0,
            'filename': ''
        }
    
    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """Progress hook for yt-dlp."""
        if d['status'] == 'downloading':
            # Update progress information
            if 'total_bytes' in d and d['total_bytes']:
                progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
            else:
                progress = 0.0
            
            # Update current download info
            if self.current_download:
                self.current_download.update({
                    'progress': progress,
                    'speed': d.get('speed', 0),
                    'eta': d.get('eta', None),
                    'size': d.get('total_bytes', 0),
                    'filename': d.get('filename', '')
                })
            
            # Update progress tracker
            self.progress_tracker.update_progress(progress, d.get('speed', 0), d.get('eta'))
            
        elif d['status'] == 'finished':
            # Download completed
            if self.current_download:
                self.current_download.update({
                    'status': 'completed',
                    'progress': 100.0,
                    'end_time': datetime.now()
                })
    
    def _get_downloaded_filename(self, info: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Get the filename of the downloaded file."""
        # Try to get the actual filename from the info
        if 'requested_downloads' in info and info['requested_downloads']:
            return info['requested_downloads'][0]['filepath']
        
        # Fallback to constructing the filename
        template = options.get('outtmpl', '%(title)s.%(ext)s')
        try:
            import yt_dlp
            filename = yt_dlp.utils.render_template(template, info)
            return yt_dlp.utils.sanitize_filename(filename)
        except Exception:
            # Final fallback
            title = info.get('title', 'video')
            ext = info.get('ext', 'mp4')
            return f"{title}.{ext}"
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video information without downloading."""
        try:
            options = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False
            }
            
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                return ydl.sanitize_info(info)
                
        except Exception as e:
            raise DownloadError(f"Failed to get video info for {url}: {str(e)}")
    
    def list_formats(self, url: str) -> List[Dict[str, Any]]:
        """List available formats for a video."""
        try:
            options = {
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('formats', [])
                
        except Exception as e:
            raise FormatError(f"Failed to list formats for {url}: {str(e)}")
    
    def validate_url(self, url: str) -> bool:
        """Validate if a URL is supported by yt-dlp."""
        try:
            options = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True
            }
            
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.extract_info(url, download=False)
                return True
                
        except Exception:
            return False
    
    def cancel_download(self) -> bool:
        """Cancel the current download."""
        if self.current_download and self.current_download['status'] == 'downloading':
            self.current_download['status'] = 'cancelled'
            self.current_download['end_time'] = datetime.now()
            return True
        return False
    
    def clear_queue(self) -> None:
        """Clear the download queue."""
        self.download_queue.clear()
        self.current_download = None
    
    def get_download_history(self) -> List[Dict[str, Any]]:
        """Get download history."""
        return [d for d in self.download_queue if d['status'] in ['completed', 'failed', 'cancelled']]


class AsyncVideoDownloader(VideoDownloader):
    """Asynchronous version of the video downloader."""
    
    async def download_single_async(self, url: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Download a single video asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.download_single, url, options)
    
    async def download_batch_async(self, urls: List[str], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Download multiple videos asynchronously."""
        tasks = []
        for url in urls:
            task = self.download_single_async(url, options)
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def get_video_info_async(self, url: str) -> Dict[str, Any]:
        """Get video information asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_video_info, url)
