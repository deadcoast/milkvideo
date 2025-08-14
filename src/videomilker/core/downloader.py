"""Core downloader functionality for VideoMilker."""

import asyncio
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import yt_dlp
from rich.console import Console

from ..config.settings import Settings
from ..exceptions.download_errors import DownloadError
from ..exceptions.download_errors import FormatError
from .file_manager import FileManager
from .progress_tracker import ProgressTracker


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
            "id": download_id,
            "url": url,
            "options": options or {},
            "status": "queued",
            "progress": 0.0,
            "speed": 0,
            "eta": None,
            "size": 0,
            "filename": "",
            "error": None,
            "start_time": None,
            "end_time": None,
        }

        self.download_queue.append(download_item)
        return download_id

    def get_queue_status(self) -> Dict[str, Any]:
        """Get the current queue status."""
        return {
            "total": len(self.download_queue),
            "queued": len([d for d in self.download_queue if d["status"] == "queued"]),
            "downloading": len([d for d in self.download_queue if d["status"] == "downloading"]),
            "completed": len([d for d in self.download_queue if d["status"] == "completed"]),
            "failed": len([d for d in self.download_queue if d["status"] == "failed"]),
            "current": self.current_download,
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
                progress_callback["info"] = info

                # Download the video
                ydl.download([url])

            return {
                "status": "completed",
                "info": info,
                "filename": self._get_downloaded_filename(info, yt_dlp_options),
            }

        except Exception as e:
            # Map yt-dlp errors to appropriate VideoMilker exceptions
            from ..exceptions.download_errors import create_error_with_context
            from ..exceptions.download_errors import map_yt_dlp_error

            error_message = str(e)
            error_class = map_yt_dlp_error(error_message)
            error = create_error_with_context(error_class, error_message, url)
            raise error from e

    def download_batch(self, urls: List[str], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Download multiple videos in batch."""
        results = []

        for i, url in enumerate(urls):
            try:
                self.console.print(f"[cyan]Downloading {i + 1}/{len(urls)}: {url}[/cyan]")
                result = self.download_single(url, options)
                results.append(result)

            except Exception as e:
                self.console.print(f"[red]Failed to download {url}: {e!s}[/red]")
                results.append({"status": "failed", "url": url, "error": str(e)})

        return results

    def _prepare_yt_dlp_options(self, custom_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare yt-dlp options from settings and custom options."""
        # Start with default settings
        options = self.settings.get_yt_dlp_options()

        # Set output path
        download_path = self.settings.get_download_path()
        download_path.mkdir(parents=True, exist_ok=True)
        options["outtmpl"] = str(download_path / options["outtmpl"])

        # Add progress hooks
        options["progress_hooks"] = [self._progress_hook]

        # Add resume options
        options.update(
            {
                "continue": True,  # Enable download resume
                "resume": True,  # Resume partial downloads
                "fragment_retries": self.settings.download.fragment_retries,
                "retries": self.settings.download.retries,
                "retry_sleep": self.settings.download.retry_sleep,
                "max_sleep_interval": self.settings.download.max_sleep_interval,
            }
        )

        # Add custom options
        if custom_options:
            options.update(custom_options)

        return options

    def _create_progress_callback(self) -> Dict[str, Any]:
        """Create a progress callback for tracking download progress."""
        return {"info": None, "progress": 0.0, "speed": 0, "eta": None, "size": 0, "filename": ""}

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """Progress hook for yt-dlp."""
        if d["status"] == "downloading":
            # Update progress information
            if d.get("total_bytes"):
                progress = (d["downloaded_bytes"] / d["total_bytes"]) * 100
            elif d.get("total_bytes_estimate"):
                progress = (d["downloaded_bytes"] / d["total_bytes_estimate"]) * 100
            else:
                progress = 0.0

            # Update current download info
            if self.current_download:
                self.current_download.update(
                    {
                        "progress": progress,
                        "speed": d.get("speed", 0),
                        "eta": d.get("eta"),
                        "size": d.get("total_bytes", 0),
                        "filename": d.get("filename", ""),
                    }
                )

            # Update progress tracker
            self.progress_tracker.update_progress(progress, d.get("speed", 0), d.get("eta"))

        elif d["status"] == "finished":
            # Download completed
            if self.current_download:
                self.current_download.update({"status": "completed", "progress": 100.0, "end_time": datetime.now()})

    def _get_downloaded_filename(self, info: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Get the filename of the downloaded file."""
        # Try to get the actual filename from the info
        if info.get("requested_downloads"):
            return info["requested_downloads"][0]["filepath"]

        # Fallback to constructing the filename
        template = options.get("outtmpl", "%(title)s.%(ext)s")
        try:
            import yt_dlp

            filename = yt_dlp.utils.render_template(template, info)
            return yt_dlp.utils.sanitize_filename(filename)
        except Exception:
            # Final fallback
            title = info.get("title", "video")
            ext = info.get("ext", "mp4")
            return f"{title}.{ext}"

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video information without downloading."""
        try:
            options = {"quiet": True, "no_warnings": True, "extract_flat": False}

            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                return ydl.sanitize_info(info)

        except Exception as e:
            # Map yt-dlp errors to appropriate VideoMilker exceptions
            from ..exceptions.download_errors import create_error_with_context
            from ..exceptions.download_errors import map_yt_dlp_error

            error_message = str(e)
            error_class = map_yt_dlp_error(error_message)
            error = create_error_with_context(error_class, error_message, url)
            raise error from e

    def list_formats(self, url: str) -> List[Dict[str, Any]]:
        """List available formats for a video."""
        try:
            options = {"quiet": True, "no_warnings": True}

            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get("formats", [])

        except Exception as e:
            raise FormatError(f"Failed to list formats for {url}: {e!s}") from e

    def get_formatted_formats(self, url: str) -> List[Dict[str, Any]]:
        """Get formatted list of available formats for easy selection."""
        try:
            formats = self.list_formats(url)
            formatted_formats = []

            for fmt in formats:
                format_id = fmt.get("format_id", "N/A")
                ext = fmt.get("ext", "N/A")
                resolution = fmt.get("resolution", "N/A")
                filesize = fmt.get("filesize", 0)
                fps = fmt.get("fps", 0)
                vcodec = fmt.get("vcodec", "none")
                acodec = fmt.get("acodec", "none")

                # Determine format type
                if vcodec != "none" and acodec != "none":
                    format_type = "video+audio"
                elif vcodec != "none":
                    format_type = "video only"
                elif acodec != "none":
                    format_type = "audio only"
                else:
                    format_type = "unknown"

                # Format display string
                size_str = f"{filesize / (1024 * 1024):.1f}MB" if filesize > 0 else "Unknown"
                fps_str = f"{fps}fps" if fps > 0 else ""
                display_name = f"{format_id} - {ext} - {resolution} {fps_str} - {size_str} - {format_type}"

                formatted_formats.append(
                    {
                        "format_id": format_id,
                        "display_name": display_name,
                        "ext": ext,
                        "resolution": resolution,
                        "filesize": filesize,
                        "fps": fps,
                        "vcodec": vcodec,
                        "acodec": acodec,
                        "format_type": format_type,
                        "original_format": fmt,
                    }
                )

            return formatted_formats

        except Exception as e:
            raise FormatError(f"Failed to get formatted formats for {url}: {e!s}") from e

    def get_best_formats(self, url: str) -> Dict[str, Any]:
        """Get the best available formats for different quality levels."""
        try:
            formats = self.list_formats(url)
            best_formats = {
                "best": None,
                "worst": None,
                "best_video": None,
                "best_audio": None,
                "720p": None,
                "1080p": None,
                "audio_only": None,
            }

            for fmt in formats:
                format_id = fmt.get("format_id", "")
                resolution = fmt.get("resolution", "")
                vcodec = fmt.get("vcodec", "none")
                acodec = fmt.get("acodec", "none")
                filesize = fmt.get("filesize", 0)

                # Best overall (video + audio)
                if (
                    vcodec != "none"
                    and acodec != "none"
                    and (best_formats["best"] is None or filesize > best_formats["best"].get("filesize", 0))
                ):
                    best_formats["best"] = fmt

                # Worst overall
                if (
                    vcodec != "none"
                    and acodec != "none"
                    and (best_formats["worst"] is None or filesize < best_formats["worst"].get("filesize", 0))
                ):
                    best_formats["worst"] = fmt

                # Best video only
                if (
                    vcodec != "none"
                    and acodec == "none"
                    and (best_formats["best_video"] is None or filesize > best_formats["best_video"].get("filesize", 0))
                ):
                    best_formats["best_video"] = fmt

                # Best audio only
                if (
                    vcodec == "none"
                    and acodec != "none"
                    and (best_formats["best_audio"] is None or filesize > best_formats["best_audio"].get("filesize", 0))
                ):
                    best_formats["best_audio"] = fmt

                # 720p
                if "720" in resolution and vcodec != "none" and best_formats["720p"] is None:
                    best_formats["720p"] = fmt

                # 1080p
                if "1080" in resolution and vcodec != "none" and best_formats["1080p"] is None:
                    best_formats["1080p"] = fmt

                # Audio only
                if vcodec == "none" and acodec != "none" and best_formats["audio_only"] is None:
                    best_formats["audio_only"] = fmt

            return best_formats

        except Exception as e:
            raise FormatError(f"Failed to get best formats for {url}: {e!s}") from e

    def get_chapters(self, url: str) -> List[Dict[str, Any]]:
        """Get chapter information for a video."""
        try:
            # Get video info with chapters
            video_info = self.get_video_info(url)

            chapters = video_info.get("chapters", [])

            if not chapters:
                return []

            return [
                {
                    "index": i,
                    "title": chapter.get("title", f"Chapter {i}"),
                    "start_time": chapter.get("start_time", 0),
                    "end_time": chapter.get("end_time", 0),
                    "duration": chapter.get("end_time", 0) - chapter.get("start_time", 0),
                }
                for i, chapter in enumerate(chapters, 1)
            ]
        except Exception as e:
            raise DownloadError(f"Failed to get chapters for {url}: {e!s}") from e

    def download_with_chapters(self, url: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Download a video with chapter splitting enabled."""
        try:
            # Prepare options for chapter splitting
            chapter_options = {
                "splitchapters": True,
                "outtmpl": "%(upload_date)s_%(title)s/%(section_number)s-%(section_title)s.%(ext)s",
            }

            # Merge with provided options
            if options:
                chapter_options |= options

            # Download with chapter splitting
            result = self.download_single(url, chapter_options)

            # Add chapter information to result
            try:
                chapters = self.get_chapters(url)
                result["chapters"] = chapters
                result["chapter_count"] = len(chapters)
            except Exception:
                result["chapters"] = []
                result["chapter_count"] = 0

            return result

        except Exception as e:
            raise DownloadError(f"Failed to download with chapters: {e!s}") from e

    def validate_url(self, url: str) -> bool:
        """Validate if a URL is supported by yt-dlp."""
        try:
            options = {"quiet": True, "no_warnings": True, "extract_flat": True}

            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.extract_info(url, download=False)
                return True

        except Exception:
            return False

    def cancel_download(self) -> bool:
        """Cancel the current download."""
        if self.current_download and self.current_download["status"] == "downloading":
            self.current_download["status"] = "cancelled"
            self.current_download["end_time"] = datetime.now()
            return True
        return False

    def clear_queue(self) -> None:
        """Clear the download queue."""
        self.download_queue.clear()
        self.current_download = None

    def get_download_history(self) -> List[Dict[str, Any]]:
        """Get download history."""
        return [d for d in self.download_queue if d["status"] in ["completed", "failed", "cancelled"]]

    def find_interrupted_downloads(self) -> List[Dict[str, Any]]:
        """Find downloads that were interrupted and can be resumed."""
        interrupted = []

        # Check download path for partial files
        download_path = self.settings.get_download_path()

        if download_path.exists():
            for file_path in download_path.rglob("*.part"):
                # Get file info
                file_info = {
                    "filepath": str(file_path),
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime),
                    "can_resume": True,
                }
                interrupted.append(file_info)

        return interrupted

    def resume_download(self, filepath: str, url: str = None) -> Dict[str, Any]:
        """Resume an interrupted download."""
        try:
            # Prepare options for resume
            options = self._prepare_yt_dlp_options()

            # If URL is provided, use it; otherwise try to extract from filename
            if not url:
                # Try to extract URL from filename or metadata
                # This is a simplified approach - in practice, you might want to store URLs with partial files
                raise ValueError("URL is required for resume functionality")

            # Download with resume
            result = self.download_single(url, options)

            # Add resume information
            result["resumed"] = True
            result["original_filepath"] = filepath

            return result

        except Exception as e:
            raise DownloadError(f"Failed to resume download: {e!s}") from e

    def cleanup_partial_files(self, older_than_days: int = 7) -> List[str]:
        """Clean up old partial download files."""
        cleaned_files = []
        cutoff_time = datetime.now() - timedelta(days=older_than_days)

        download_path = self.settings.get_download_path()

        if download_path.exists():
            for file_path in download_path.rglob("*.part"):
                if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_time:
                    try:
                        file_path.unlink()
                        cleaned_files.append(str(file_path))
                    except Exception:
                        pass  # Skip files that can't be deleted

        return cleaned_files


class AsyncVideoDownloader(VideoDownloader):
    """Asynchronous version of the video downloader."""

    async def download_single_async(self, url: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Download a single video asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.download_single, url, options)

    async def download_batch_async(
        self, urls: List[str], options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
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
