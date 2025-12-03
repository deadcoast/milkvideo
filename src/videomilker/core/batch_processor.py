"""Batch processing for VideoMilker downloads."""

import threading
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from rich.console import Console
from rich.progress import BarColumn
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.progress import TimeElapsedColumn

from ..config.settings import Settings
from ..core.downloader import VideoDownloader
from ..core.file_manager import FileManager
from ..exceptions.download_errors import BatchProcessingError


class QueueStatus(Enum):
    """Queue status enumeration."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"


class DownloadQueue:
    """Manages a queue of downloads with pause/resume functionality."""

    def __init__(self, settings: Settings, console: Optional[Console] = None):
        """Initialize the download queue."""
        self.settings = settings
        self.console = console or Console()
        self.downloader = VideoDownloader(settings, console)
        self.file_manager = FileManager(settings)

        # Queue state
        self.urls: List[str] = []
        self.results: List[Dict[str, Any]] = []
        self.current_index: int = 0
        self.status: QueueStatus = QueueStatus.IDLE

        # Threading
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None

        # Statistics
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.total_size: int = 0
        self.downloaded_size: int = 0

    def add_url(self, url: str) -> None:
        """Add a URL to the queue."""
        with self._lock:
            if url not in self.urls:
                self.urls.append(url)

    def add_urls(self, urls: List[str]) -> None:
        """Add multiple URLs to the queue."""
        with self._lock:
            for url in urls:
                if url not in self.urls:
                    self.urls.append(url)

    def remove_url(self, url: str) -> bool:
        """Remove a URL from the queue."""
        with self._lock:
            if url in self.urls:
                self.urls.remove(url)
                return True
            return False

    def clear_queue(self) -> None:
        """Clear the entire queue."""
        with self._lock:
            self.urls.clear()
            self.results.clear()
            self.current_index = 0
            self.status = QueueStatus.IDLE

    def get_queue_status(self) -> Dict[str, Any]:
        """Get the current queue status."""
        with self._lock:
            return {
                "status": self.status.value,
                "total_urls": len(self.urls),
                "completed": len(self.results),
                "current_index": self.current_index,
                "remaining": len(self.urls) - self.current_index,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "total_size": self.total_size,
                "downloaded_size": self.downloaded_size,
            }

    def start_processing(self, options: Optional[Dict[str, Any]] = None) -> None:
        """Start processing the queue."""
        if self.status == QueueStatus.RUNNING:
            return

        with self._lock:
            if not self.urls:
                self.console.print("[yellow]Queue is empty. Add URLs first.[/yellow]")
                return

            self.status = QueueStatus.RUNNING
            self.start_time = datetime.now()
            self._stop_event.clear()
            self._pause_event.clear()

            # Start worker thread
            self._worker_thread = threading.Thread(target=self._process_queue, args=(options,), daemon=True)
            self._worker_thread.start()

    def pause_processing(self) -> None:
        """Pause queue processing."""
        if self.status == QueueStatus.RUNNING:
            self.status = QueueStatus.PAUSED
            self._pause_event.set()
            self.console.print("[yellow]Queue processing paused.[/yellow]")

    def resume_processing(self) -> None:
        """Resume queue processing."""
        if self.status == QueueStatus.PAUSED:
            self.status = QueueStatus.RUNNING
            self._pause_event.clear()
            self.console.print("[green]Queue processing resumed.[/green]")

    def stop_processing(self) -> None:
        """Stop queue processing."""
        if self.status in [QueueStatus.RUNNING, QueueStatus.PAUSED]:
            self.status = QueueStatus.STOPPED
            self._stop_event.set()
            self._pause_event.set()
            self.end_time = datetime.now()
            self.console.print("[red]Queue processing stopped.[/red]")

    def _process_queue(self, options: Optional[Dict[str, Any]] = None) -> None:
        """Internal method to process the queue."""
        try:
            while self.current_index < len(self.urls) and not self._stop_event.is_set():
                # Check for pause
                if self._pause_event.is_set():
                    time.sleep(0.1)
                    continue

                # Get current URL
                with self._lock:
                    if self.current_index >= len(self.urls):
                        break
                    url = self.urls[self.current_index]

                try:
                    # Download the video
                    result = self.downloader.download_single(url, options)

                    # Ensure result has the URL and timestamp
                    if isinstance(result, dict):
                        result["url"] = url
                        result["timestamp"] = datetime.now().isoformat()

                        # Update statistics
                        if result.get("status") == "completed":
                            self.downloaded_size += result.get("size", 0)

                    # Add to results
                    with self._lock:
                        self.results.append(result)
                        self.current_index += 1

                    # Small delay to prevent overwhelming the system
                    time.sleep(0.1)

                except Exception as e:
                    # Log error and continue
                    error_result = {
                        "status": "failed",
                        "url": url,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }

                    with self._lock:
                        self.results.append(error_result)
                        self.current_index += 1

                    self.console.print(f"[red]Failed to download {url}: {e}[/red]")

            # Mark as completed
            with self._lock:
                if self.current_index >= len(self.urls):
                    self.status = QueueStatus.COMPLETED
                    self.end_time = datetime.now()
                    self.console.print("[green]Queue processing completed.[/green]")
                else:
                    self.status = QueueStatus.STOPPED
                    self.end_time = datetime.now()

        except Exception as e:
            with self._lock:
                self.status = QueueStatus.STOPPED
                self.end_time = datetime.now()
            self.console.print(f"[red]Queue processing error: {e}[/red]")

    def get_results(self) -> List[Dict[str, Any]]:
        """Get the current results."""
        with self._lock:
            return self.results.copy()

    def get_failed_downloads(self) -> List[Dict[str, Any]]:
        """Get failed downloads from results."""
        with self._lock:
            return [result for result in self.results if result.get("status") == "failed"]

    def retry_failed_downloads(self, options: Optional[Dict[str, Any]] = None) -> None:
        """Retry failed downloads."""
        if failed := self.get_failed_downloads():
            failed_urls = [result["url"] for result in failed]
            self.add_urls(failed_urls)
            self.start_processing(options)


class BatchProcessor:
    """Handles batch download processing."""

    def __init__(self, settings: Settings, console: Optional[Console] = None):
        """Initialize the batch processor."""
        self.settings = settings
        self.console = console or Console()
        self.downloader = VideoDownloader(settings, console)
        self.file_manager = FileManager(settings)
        self.queue = DownloadQueue(settings, console)

    def load_urls_from_file(self, file_path: Path) -> List[str]:
        """Load URLs from a text file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            urls = []
            lines = content.strip().split("\n")

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):  # Skip comments and empty lines
                    urls.append(line)

            return urls

        except Exception as e:
            raise BatchProcessingError(f"Failed to load URLs from file: {e}") from e

    def save_urls_to_file(self, urls: List[str], file_path: Path) -> None:
        """Save URLs to a text file."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                for url in urls:
                    f.write(f"{url}\n")

        except Exception as e:
            raise BatchProcessingError(f"Failed to save URLs to file: {e}") from e

    # Queue management methods
    def add_to_queue(self, url: str) -> None:
        """Add a URL to the download queue."""
        self.queue.add_url(url)

    def add_urls_to_queue(self, urls: List[str]) -> None:
        """Add multiple URLs to the download queue."""
        self.queue.add_urls(urls)

    def remove_from_queue(self, url: str) -> bool:
        """Remove a URL from the download queue."""
        return self.queue.remove_url(url)

    def clear_queue(self) -> None:
        """Clear the download queue."""
        self.queue.clear_queue()

    def get_queue_status(self) -> Dict[str, Any]:
        """Get the current queue status."""
        return self.queue.get_queue_status()

    def start_queue_processing(self, options: Optional[Dict[str, Any]] = None) -> None:
        """Start processing the download queue."""
        self.queue.start_processing(options)

    def pause_queue_processing(self) -> None:
        """Pause queue processing."""
        self.queue.pause_processing()

    def resume_queue_processing(self) -> None:
        """Resume queue processing."""
        self.queue.resume_processing()

    def stop_queue_processing(self) -> None:
        """Stop queue processing."""
        self.queue.stop_processing()

    def get_queue_results(self) -> List[Dict[str, Any]]:
        """Get results from the queue."""
        return self.queue.get_results()

    def retry_failed_queue_downloads(self, options: Optional[Dict[str, Any]] = None) -> None:
        """Retry failed downloads in the queue."""
        self.queue.retry_failed_downloads(options)

    def process_batch(self, urls: List[str], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Process a batch of URLs for download with memory optimization."""
        if not urls:
            return []

        total_urls = len(urls)
        completed_count = 0
        failed_count = 0

        # Create progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task(f"Processing {total_urls} URLs", total=total_urls)

            # Process URLs in chunks to optimize memory usage
            chunk_size = min(50, max(10, total_urls // 10))  # Adaptive chunk size
            results = []

            for chunk_start in range(0, total_urls, chunk_size):
                chunk_end = min(chunk_start + chunk_size, total_urls)
                chunk_urls = urls[chunk_start:chunk_end]

                # Process chunk
                for i, url in enumerate(chunk_urls):
                    global_index = chunk_start + i

                    try:
                        # Update progress description
                        progress.update(task, description=f"Downloading {global_index + 1}/{total_urls}: {url[:50]}...")

                        # Download the video
                        result = self.downloader.download_single(url, options)

                        # Ensure result has the URL
                        if isinstance(result, dict):
                            result["url"] = url
                            result["timestamp"] = datetime.now().isoformat()

                        results.append(result)
                        completed_count += 1

                        # Update progress
                        progress.advance(task)

                    except Exception as e:
                        # Log error and continue
                        error_result = {
                            "status": "failed",
                            "url": url,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat(),
                        }
                        results.append(error_result)
                        failed_count += 1
                        progress.advance(task)

                        self.console.print(f"[red]Failed to download {url}: {e}[/red]")

                # Memory cleanup after each chunk
                import gc

                gc.collect()

                # Log memory usage if verbose
                if hasattr(self, "verbose") and self.verbose:
                    import psutil

                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    self.console.print(f"[dim]Memory usage: {memory_mb:.1f} MB[/dim]")

        # Save batch log
        self._save_batch_log(urls, results)

        return results

    def process_audio_batch(
        self, urls: List[str], audio_format: str = "mp3", options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Process a batch of URLs for audio-only extraction."""
        if not urls:
            return []

        # Prepare audio-specific options
        audio_options = {
            "format": f"bestaudio[ext={audio_format}]/bestaudio",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": audio_format, "preferredquality": "192"}
            ],
            "outtmpl": "%(upload_date)s_%(title)s.%(ext)s",
        }

        # Merge with provided options
        if options:
            audio_options |= options

        results = []
        total_urls = len(urls)

        # Create progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task(f"Extracting audio from {total_urls} videos", total=total_urls)

            for i, url in enumerate(urls):
                try:
                    # Update progress description
                    progress.update(task, description=f"Extracting audio {i + 1}/{total_urls}: {url[:50]}...")

                    # Download the audio
                    result = self.downloader.download_single(url, audio_options)

                    # Ensure result has the URL
                    if isinstance(result, dict):
                        result["url"] = url
                        result["timestamp"] = datetime.now().isoformat()
                        result["audio_format"] = audio_format

                    results.append(result)

                    # Update progress
                    progress.advance(task)

                except Exception as e:
                    # Log error and continue
                    error_result = {
                        "status": "failed",
                        "url": url,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                        "audio_format": audio_format,
                    }
                    results.append(error_result)
                    progress.advance(task)

                    self.console.print(f"[red]Failed to extract audio from {url}: {e}[/red]")

        # Save batch log
        self._save_batch_log(urls, results)

        return results

    def process_batch_with_validation(
        self, urls: List[str], options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Process batch with URL validation."""
        # Validate URLs first
        valid_urls = []
        invalid_urls = []

        for url in urls:
            if self.downloader.validate_url(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)

        if invalid_urls:
            self.console.print(f"[yellow]Warning: {len(invalid_urls)} invalid URLs found:[/yellow]")
            for url in invalid_urls:
                self.console.print(f"  [red]• {url}[/red]")

        if not valid_urls:
            self.console.print("[red]No valid URLs to process[/red]")
            return []

        # Process valid URLs
        return self.process_batch(valid_urls, options)

    def process_batch_with_limits(
        self, urls: List[str], max_concurrent: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Process batch with concurrency limits using threading."""
        if max_concurrent is None:
            max_concurrent = self.settings.download.max_concurrent

        if not urls:
            return []

        # Create a thread-safe queue for results
        from queue import Queue

        result_queue = Queue()

        # Create a thread-safe counter for progress
        from threading import Lock

        progress_lock = Lock()
        completed_count = 0

        def download_worker(url: str, worker_id: int) -> None:
            """Worker function for downloading a single URL."""
            nonlocal completed_count

            try:
                # Download the video
                result = self.downloader.download_single(url, options)

                # Ensure result has the URL
                if isinstance(result, dict):
                    result["url"] = url
                    result["timestamp"] = datetime.now().isoformat()
                    result["worker_id"] = worker_id

                result_queue.put(result)

            except Exception as e:
                # Log error and continue
                error_result = {
                    "status": "failed",
                    "url": url,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "worker_id": worker_id,
                }
                result_queue.put(error_result)

                self.console.print(f"[red]Worker {worker_id}: Failed to download {url}: {e}[/red]")

            finally:
                # Update progress
                with progress_lock:
                    completed_count += 1

        # Create progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task(f"Processing {len(urls)} URLs (max {max_concurrent} concurrent)", total=len(urls))

            # Start worker threads with memory optimization
            threads = []
            active_threads = 0

            # Process URLs in chunks to manage memory
            chunk_size = min(100, max(20, len(urls) // 5))  # Adaptive chunk size for concurrent processing

            for chunk_start in range(0, len(urls), chunk_size):
                chunk_end = min(chunk_start + chunk_size, len(urls))
                chunk_urls = urls[chunk_start:chunk_end]

                # Process chunk
                for i, url in enumerate(chunk_urls):
                    global_index = chunk_start + i

                    # Wait if we've reached the concurrency limit
                    while active_threads >= max_concurrent:
                        # Check for completed threads
                        for thread in threads[:]:
                            if not thread.is_alive():
                                threads.remove(thread)
                                active_threads -= 1

                        if active_threads >= max_concurrent:
                            time.sleep(0.1)  # Small delay before checking again

                    # Start new thread
                    thread = threading.Thread(target=download_worker, args=(url, global_index + 1))
                    thread.daemon = True
                    thread.start()
                    threads.append(thread)
                    active_threads += 1

                    # Update progress description
                    progress.update(
                        task,
                        description=f"Active: {active_threads}/{max_concurrent}, Completed: {completed_count}/{len(urls)}",
                    )

                # Memory cleanup after each chunk
                import gc

                gc.collect()

                # Log memory usage if verbose
                if hasattr(self, "verbose") and self.verbose:
                    import psutil

                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    self.console.print(f"[dim]Memory usage: {memory_mb:.1f} MB[/dim]")

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Collect results
            results = []
            while not result_queue.empty():
                results.append(result_queue.get())

            # Update progress to completion
            progress.update(task, completed=len(urls))

        # Save batch log
        self._save_batch_log(urls, results)

        return results

    def process_audio_batch_with_limits(
        self,
        urls: List[str],
        audio_format: str = "mp3",
        max_concurrent: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Process audio batch with concurrency limits using threading."""
        if max_concurrent is None:
            max_concurrent = self.settings.download.max_concurrent

        if not urls:
            return []

        # Prepare audio-specific options
        audio_options = {
            "format": f"bestaudio[ext={audio_format}]/bestaudio",
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": audio_format, "preferredquality": "192"}
            ],
            "outtmpl": "%(upload_date)s_%(title)s.%(ext)s",
        }

        # Merge with provided options
        if options:
            audio_options.update(options)

        # Create a thread-safe queue for results
        from queue import Queue

        result_queue = Queue()

        # Create a thread-safe counter for progress
        from threading import Lock

        progress_lock = Lock()
        completed_count = 0

        def audio_worker(url: str, worker_id: int) -> None:
            """Worker function for extracting audio from a single URL."""
            nonlocal completed_count

            try:
                # Download the audio
                result = self.downloader.download_single(url, audio_options)

                # Ensure result has the URL
                if isinstance(result, dict):
                    result["url"] = url
                    result["timestamp"] = datetime.now().isoformat()
                    result["worker_id"] = worker_id
                    result["audio_format"] = audio_format

                result_queue.put(result)

            except Exception as e:
                # Log error and continue
                error_result = {
                    "status": "failed",
                    "url": url,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "worker_id": worker_id,
                    "audio_format": audio_format,
                }
                result_queue.put(error_result)

                self.console.print(f"[red]Worker {worker_id}: Failed to extract audio from {url}: {e}[/red]")

            finally:
                # Update progress
                with progress_lock:
                    completed_count += 1

        # Create progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task(
                f"Extracting audio from {len(urls)} videos (max {max_concurrent} concurrent)", total=len(urls)
            )

            # Start worker threads
            threads = []
            active_threads = 0

            for i, url in enumerate(urls):
                # Wait if we've reached the concurrency limit
                while active_threads >= max_concurrent:
                    # Check for completed threads
                    for thread in threads[:]:
                        if not thread.is_alive():
                            threads.remove(thread)
                            active_threads -= 1

                    if active_threads >= max_concurrent:
                        time.sleep(0.1)  # Small delay before checking again

                # Start new thread
                thread = threading.Thread(target=audio_worker, args=(url, i + 1))
                thread.daemon = True
                thread.start()
                threads.append(thread)
                active_threads += 1

                # Update progress description
                progress.update(
                    task,
                    description=f"Active: {active_threads}/{max_concurrent}, Completed: {completed_count}/{len(urls)}",
                )

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Collect results
            results = []
            while not result_queue.empty():
                results.append(result_queue.get())

            # Update progress to completion
            progress.update(task, completed=len(urls))

        # Save batch log
        self._save_batch_log(urls, results)

        return results

    def _save_batch_log(self, urls: List[str], results: List[Dict[str, Any]]) -> None:
        """Save batch processing log."""
        try:
            # Get batch folder
            batch_folder = self.file_manager.get_batch_folder()

            # Create log data
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "total_urls": len(urls),
                "successful": len([r for r in results if r.get("status") == "completed"]),
                "failed": len([r for r in results if r.get("status") == "failed"]),
                "urls": urls,
                "results": results,
            }

            # Save log file
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_file = batch_folder / f"batch_log_{timestamp}.json"

            import json

            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.console.print(f"[yellow]Warning: Failed to save batch log: {e}[/yellow]")

    def get_batch_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics from batch processing results."""
        total = len(results)
        successful = len([r for r in results if r.get("status") == "completed"])
        failed = len([r for r in results if r.get("status") == "failed"])

        total_size = sum(r.get("size", 0) for r in results if r.get("status") == "completed" and r.get("size"))

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024) if total_size > 0 else 0,
        }

    def retry_failed_downloads(
        self, results: List[Dict[str, Any]], options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retry failed downloads from a previous batch."""
        failed_urls = [r["url"] for r in results if r.get("status") == "failed" and r.get("url")]

        if not failed_urls:
            self.console.print("[green]No failed downloads to retry[/green]")
            return []

        self.console.print(f"[yellow]Retrying {len(failed_urls)} failed downloads...[/yellow]")

        return self.process_batch(failed_urls, options)

    def create_batch_template(self, template_path: Path) -> None:
        """Create a batch file template."""
        template_content = """# VideoMilker Batch Download Template
# Add one URL per line
# Lines starting with # are comments and will be ignored
# Example URLs:

# https://www.youtube.com/watch?v=example1
# https://www.youtube.com/watch?v=example2
# https://vimeo.com/example3

"""

        try:
            template_path.parent.mkdir(parents=True, exist_ok=True)

            with open(template_path, "w", encoding="utf-8") as f:
                f.write(template_content)

            self.console.print(f"[green]Batch template created: {template_path}[/green]")

        except Exception as e:
            raise BatchProcessingError(f"Failed to create batch template: {e}") from e

    def validate_batch_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate a batch file and return statistics."""
        try:
            urls = self.load_urls_from_file(file_path)

            valid_urls = []
            invalid_urls = []

            for url in urls:
                if self.downloader.validate_url(url):
                    valid_urls.append(url)
                else:
                    invalid_urls.append(url)

            return {
                "total_urls": len(urls),
                "valid_urls": len(valid_urls),
                "invalid_urls": len(invalid_urls),
                "valid_url_list": valid_urls,
                "invalid_url_list": invalid_urls,
                "is_valid": not invalid_urls,
            }

        except Exception as e:
            raise BatchProcessingError(f"Failed to validate batch file: {e}") from e

    def estimate_batch_size(self, urls: List[str]) -> Dict[str, Any]:
        """Estimate the total size of a batch download."""
        total_size = 0
        size_estimates = []

        for url in urls:
            try:
                # Get video info to estimate size
                info = self.downloader.get_video_info(url)
                if size := info.get("filesize", 0):
                    total_size += size
                    size_estimates.append(
                        {
                            "url": url,
                            "title": info.get("title", "Unknown"),
                            "size": size,
                            "size_mb": size / (1024 * 1024),
                        }
                    )
                else:
                    size_estimates.append({"url": url, "title": info.get("title", "Unknown"), "size": 0, "size_mb": 0})

            except Exception:
                size_estimates.append({"url": url, "title": "Unknown", "size": 0, "size_mb": 0})

        return {
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "total_size_gb": total_size / (1024 * 1024 * 1024),
            "url_count": len(urls),
            "size_estimates": size_estimates,
        }

    def estimate_memory_usage(self, urls: List[str], max_concurrent: Optional[int] = None) -> Dict[str, Any]:
        """Estimate memory usage for batch processing."""
        if max_concurrent is None:
            max_concurrent = self.settings.download.max_concurrent

        # Base memory usage per download (rough estimate)
        base_memory_per_download = 50 * 1024 * 1024  # 50 MB per download

        # Estimated memory usage
        estimated_memory = base_memory_per_download * max_concurrent

        # Add overhead for the application
        application_overhead = 100 * 1024 * 1024  # 100 MB base

        total_estimated = estimated_memory + application_overhead

        # Get current memory usage
        try:
            import psutil

            process = psutil.Process()
            current_memory = process.memory_info().rss
            available_memory = psutil.virtual_memory().available
        except ImportError:
            current_memory = 0
            available_memory = 0

        return {
            "estimated_memory_mb": total_estimated / (1024 * 1024),
            "current_memory_mb": current_memory / (1024 * 1024),
            "available_memory_mb": available_memory / (1024 * 1024),
            "max_concurrent": max_concurrent,
            "url_count": len(urls),
            "memory_safe": (total_estimated < available_memory if available_memory > 0 else True),
        }
