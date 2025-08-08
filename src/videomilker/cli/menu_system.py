"""Main menu system for VideoMilker CLI."""

from typing import Optional, Dict, Any, List
from pathlib import Path
from rich.console import Console

from .menu_renderer import MenuRenderer
from .input_handler import InputHandler
from ..config.settings import Settings
from ..config.config_manager import ConfigManager
from ..core.downloader import VideoDownloader
from ..core.batch_processor import BatchProcessor
from ..core.file_manager import FileManager
from ..history.history_manager import HistoryManager
from ..exceptions.download_errors import DownloadError, ValidationError


class MenuSystem:
    """Main menu controller for the VideoMilker CLI application."""
    
    def __init__(self, settings: Settings, verbose: bool = False):
        """Initialize the menu system."""
        self.settings = settings
        self.verbose = verbose
        self.console = Console()
        self.renderer = MenuRenderer(console=self.console, settings=settings)
        self.input_handler = InputHandler()
        
        # Initialize core components
        self.config_manager = ConfigManager()
        self.downloader = VideoDownloader(settings, self.console)
        self.batch_processor = BatchProcessor(settings, self.console)
        self.file_manager = FileManager(settings)
        self.history_manager = HistoryManager(settings)
        
        # Menu state
        self.current_menu = "main"
        self.running = True
        self.menu_stack = []
    
    def run(self) -> None:
        """Start the main menu loop."""
        if self.settings.ui.clear_screen:
            self.renderer.clear_screen()
        
        self.renderer.show_welcome_banner()
        
        while self.running:
            try:
                self._handle_menu()
            except KeyboardInterrupt:
                self._handle_quit()
                break
            except Exception as e:
                self.renderer.show_error(f"Unexpected error: {str(e)}")
                if self.verbose:
                    self.console.print_exception()
                self.renderer.show_pause()
    
    def _handle_menu(self) -> None:
        """Handle the current menu state."""
        if self.current_menu == "main":
            self._show_main_menu()
        elif self.current_menu == "quick_download":
            self._show_quick_download_menu()
        elif self.current_menu == "audio_download":
            self._show_audio_download_menu()
        elif self.current_menu == "chapter_download":
            self._show_chapter_download_menu()
        elif self.current_menu == "batch_download":
            self._show_batch_download_menu()
        elif self.current_menu == "resume_downloads":
            self._show_resume_downloads_menu()
        elif self.current_menu == "file_management":
            self._show_file_management_menu()
        elif self.current_menu == "options":
            self._show_options_menu()
        elif self.current_menu == "history":
            self._show_history_menu()
        elif self.current_menu == "help":
            self._show_help_menu()
        else:
            self.current_menu = "main"
    
    def _handle_global_shortcuts(self, choice: str) -> bool:
        """Handle global keyboard shortcuts."""
        shortcuts = {
            'q': self._handle_quit,
            'Q': self._handle_quit,
            'h': self._handle_help,
            'H': self._handle_help,
            's': self._handle_settings,
            'S': self._handle_settings,
            'd': self._handle_quick_download,
            'D': self._handle_quick_download,
            'a': self._handle_audio_download,
            'A': self._handle_audio_download,
            'c': self._handle_chapter_download,
            'C': self._handle_chapter_download,
            'b': self._handle_batch_download,
            'B': self._handle_batch_download,
            'r': self._handle_resume_downloads,
            'R': self._handle_resume_downloads,
            'f': self._handle_file_management,
            'F': self._handle_file_management,
        }
        
        if choice in shortcuts:
            shortcuts[choice]()
            return True
        return False
    
    def _handle_settings(self) -> None:
        """Handle settings shortcut."""
        self.current_menu = "options"
    
    def _show_main_menu(self) -> None:
        """Display and handle the main menu."""
        options = {
            "1": (" Quick Download (D)", self._handle_quick_download),
            "2": (" Audio-Only Download (A)", self._handle_audio_download),
            "3": (" Chapter Split Download (C)", self._handle_chapter_download),
            "4": (" Batch Download (B)", self._handle_batch_download),
            "5": (" Resume Interrupted Downloads (R)", self._handle_resume_downloads),
            "6": (" File Management (F)", self._handle_file_management),
            "7": (" Options & Settings (S)", self._handle_options),
            "8": (" Download History", self._handle_history),
            "9": (" Help & Info (H)", self._handle_help),
            "q": ("Quit Application (Q)", self._handle_quit),
        }
        
        choice = self.renderer.show_menu("VideoMilker Main Menu", options, show_shortcuts=True)
        
        # Check for global shortcuts first
        if self._handle_global_shortcuts(choice):
            return
        
        if choice in options:
            options[choice][1]()
    
    def _handle_quick_download(self) -> None:
        """Handle quick download option."""
        self.current_menu = "quick_download"
    
    def _handle_audio_download(self) -> None:
        """Handle audio-only download option."""
        self.current_menu = "audio_download"
    
    def _handle_chapter_download(self) -> None:
        """Handle chapter split download option."""
        self.current_menu = "chapter_download"
    
    def _handle_resume_downloads(self) -> None:
        """Handle resume interrupted downloads option."""
        self.current_menu = "resume_downloads"
    
    def _handle_file_management(self) -> None:
        """Handle file management option."""
        self.current_menu = "file_management"
    
    def _handle_batch_download(self) -> None:
        """Handle batch download option."""
        self.current_menu = "batch_download"
    
    def _handle_options(self) -> None:
        """Handle options menu."""
        self.current_menu = "options"
    
    def _handle_history(self) -> None:
        """Handle download history."""
        self.current_menu = "history"
    
    def _handle_help(self) -> None:
        """Handle help and info."""
        self.current_menu = "help"
    
    def _handle_quit(self) -> None:
        """Handle application quit."""
        if self.settings.ui.confirm_before_quit:
            # Check if there are active downloads
            queue_status = self.batch_processor.get_queue_status()
            has_active_downloads = queue_status['status'] in ['running', 'paused']
            
            if has_active_downloads:
                self.renderer.show_warning("""
                [bold]⚠️  Warning: Active Downloads[/bold]
                
                You have active downloads in progress.
                Quitting now will interrupt these downloads.
                
                Consider pausing or stopping the queue first.
                """)
            
            if self.renderer.show_confirmation("Are you sure you want to quit?"):
                self.renderer.show_success("Thanks for using VideoMilker!")
                self.running = False
        else:
            self.renderer.show_success("Thanks for using VideoMilker!")
            self.running = False
    
    def _show_quick_download_menu(self) -> None:
        """Show quick download menu."""
        self.renderer.show_info("Quick Download - Enter a video URL to download")
        
        url = self.renderer.show_input_prompt("Enter video URL", required=True)
        
        if not url:
            self.current_menu = "main"
            return
        
        # Validate URL
        if not self.downloader.validate_url(url):
            self.renderer.show_error("Invalid or unsupported URL")
            self.renderer.show_pause()
            return
        
                # Get video info
        try:
            self.renderer.show_info("Fetching video information...")
            video_info = self.downloader.get_video_info(url)
            
            # Show video preview
            self._show_video_preview(video_info)
            
            # Show format selection options
            format_choice = self._show_format_selection(url)
            
            # Confirm download
            if self.renderer.show_download_confirmation("Start download?", self.settings.ui.auto_download):
                self._download_single_video(url, video_info, format_choice)
            
        except Exception as e:
            self.renderer.show_error(f"Failed to get video info: {str(e)}")
            self.renderer.show_pause()
        
        self.current_menu = "main"
    
    def _show_video_preview(self, video_info: Dict[str, Any]) -> None:
        """Show video information preview."""
        title = video_info.get('title', 'Unknown')
        duration = video_info.get('duration', 0)
        uploader = video_info.get('uploader', 'Unknown')
        view_count = video_info.get('view_count', 0)
        
        content = f"""
        [bold]Title:[/bold] {title}
        [bold]Uploader:[/bold] {uploader}
        [bold]Duration:[/bold] {duration} seconds
        [bold]Views:[/bold] {view_count:,}
        """
        
        self.renderer.show_info(content)
    
    def _show_format_selection(self, url: str) -> Optional[str]:
        """Show format selection menu."""
        try:
            # Get best formats
            best_formats = self.downloader.get_best_formats(url)
            
            # Create options
            options = {
                "1": (" Best Quality (Recommended)", lambda: best_formats.get('best', {}).get('format_id', 'best')),
                "2": (" 720p HD", lambda: best_formats.get('720p', {}).get('format_id', 'best[height<=720]')),
                "3": (" 1080p Full HD", lambda: best_formats.get('1080p', {}).get('format_id', 'best[height<=1080]')),
                "4": (" Audio Only", lambda: best_formats.get('audio_only', {}).get('format_id', 'bestaudio')),
                "5": (" Lowest Quality", lambda: best_formats.get('worst', {}).get('format_id', 'worst')),
                "6": (" Show All Formats", self._show_all_formats),
                "7": (" Use Default Settings", lambda: None),
                "0": ("← Back", lambda: None),
            }
            
            choice = self.renderer.show_menu("Select Format", options)
            
            if choice in options:
                result = options[choice][1]()
                if result is not None:
                    return result
            
            return None
            
        except Exception as e:
            self.renderer.show_error(f"Failed to get formats: {str(e)}")
            return None
    
    def _show_all_formats(self) -> Optional[str]:
        """Show all available formats."""
        try:
            # This would need the URL from the context, so we'll implement a simpler version
            self.renderer.show_info("All formats view - coming soon!")
            self.renderer.show_pause()
            return None
        except Exception as e:
            self.renderer.show_error(f"Failed to show formats: {str(e)}")
            return None
    
    def _download_single_video(self, url: str, video_info: Dict[str, Any], format_choice: Optional[str] = None) -> None:
        """Download a single video with progress tracking."""
        try:
            self.renderer.show_info("Starting download...")
            
            # Prepare download options
            options = {}
            if format_choice:
                options['format'] = format_choice
                self.renderer.show_info(f"Using format: {format_choice}")
            
            # Create progress display
            progress = self.renderer.show_progress(f"Downloading: {video_info.get('title', 'Unknown')}")
            
            # Download the video
            result = self.downloader.download_single(url, options)
            
            if result['status'] == 'completed':
                self.renderer.show_success(f"Download completed: {result.get('filename', 'Unknown')}")
                
                # Log to history
                self.history_manager.add_download(url, video_info, result)
                
            else:
                self.renderer.show_error("Download failed")
                
        except Exception as e:
            self.renderer.show_error(f"Download failed: {str(e)}")
    
    def _show_audio_download_menu(self) -> None:
        """Show audio-only download menu."""
        self.renderer.show_info("Audio-Only Download - Extract audio from videos")
        
        url = self.renderer.show_input_prompt("Enter video URL", required=True)
        
        if not url:
            self.current_menu = "main"
            return
        
        # Validate URL
        if not self.downloader.validate_url(url):
            self.renderer.show_error("Invalid or unsupported URL")
            self.renderer.show_pause()
            return
        
        # Get video info
        try:
            self.renderer.show_info("Fetching video information...")
            video_info = self.downloader.get_video_info(url)
            
            # Show video preview
            self._show_video_preview(video_info)
            
            # Show audio format selection
            audio_format = self._show_audio_format_selection()
            
            # Confirm download
            if self.renderer.show_download_confirmation("Start audio extraction?", self.settings.ui.auto_download):
                self._download_audio_only(url, video_info, audio_format)
            
        except Exception as e:
            self.renderer.show_error(f"Failed to get video info: {str(e)}")
            self.renderer.show_pause()
        
        self.current_menu = "main"
    
    def _show_audio_format_selection(self) -> str:
        """Show audio format selection menu."""
        self.renderer.show_info("Select audio format:")
        
        format_options = {
            "1": (" MP3 (Compatible, smaller size)", "mp3"),
            "2": (" M4A (High quality, smaller size)", "m4a"),
            "3": (" FLAC (Lossless, larger size)", "flac"),
            "4": (" OGG (Open format, good quality)", "ogg"),
            "5": (" WAV (Uncompressed, largest size)", "wav"),
            "0": (" Use default (MP3)", lambda: "mp3"),
        }
        
        choice = self.renderer.show_menu("Audio Format Selection", format_options)
        
        if choice in format_options:
            result = format_options[choice][1]
            if callable(result):
                return result()
            return result
        
        return "mp3"  # Default
    
    def _download_audio_only(self, url: str, video_info: Dict[str, Any], audio_format: str) -> None:
        """Download audio-only from a video."""
        try:
            self.renderer.show_info(f"Starting audio extraction to {audio_format.upper()} format...")
            
            # Prepare download options for audio extraction
            options = {
                'format': f'bestaudio[ext={audio_format}]/bestaudio',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_format,
                    'preferredquality': '192',
                }],
                'outtmpl': f'%(upload_date)s_%(title)s.%(ext)s'
            }
            
            # Create progress display
            progress = self.renderer.show_progress(f"Extracting audio: {video_info.get('title', 'Unknown')}")
            
            # Download the audio
            result = self.downloader.download_single(url, options)
            
            if result['status'] == 'completed':
                self.renderer.show_success(f"Audio extraction completed: {result.get('filename', 'Unknown')}")
                
                # Log to history
                self.history_manager.add_download(url, video_info, result)
                
            else:
                self.renderer.show_error("Audio extraction failed")
                
        except Exception as e:
            self.renderer.show_error(f"Audio extraction failed: {str(e)}")
    
    def _show_chapter_download_menu(self) -> None:
        """Show chapter split download menu."""
        self.renderer.show_info("Chapter Split Download - Split videos by chapters")
        
        url = self.renderer.show_input_prompt("Enter video URL", required=True)
        
        if not url:
            self.current_menu = "main"
            return
        
        # Validate URL
        if not self.downloader.validate_url(url):
            self.renderer.show_error("Invalid or unsupported URL")
            self.renderer.show_pause()
            return
        
        # Get video info and chapters
        try:
            self.renderer.show_info("Fetching video information and chapters...")
            video_info = self.downloader.get_video_info(url)
            chapters = self.downloader.get_chapters(url)
            
            # Show video preview
            self._show_video_preview(video_info)
            
            # Show chapter information
            if chapters:
                self._show_chapter_preview(chapters)
                
                # Confirm chapter splitting
                if self.renderer.show_download_confirmation("Start chapter split download?", self.settings.ui.auto_download):
                    self._download_with_chapters(url, video_info)
            else:
                self.renderer.show_warning("No chapters found in this video.")
                self.renderer.show_info("You can still download the full video without splitting.")
                
                if self.renderer.show_download_confirmation("Download full video without chapters?", self.settings.ui.auto_download):
                    self._download_single_video(url, video_info)
            
        except Exception as e:
            self.renderer.show_error(f"Failed to get video info: {str(e)}")
            self.renderer.show_pause()
        
        self.current_menu = "main"
    
    def _show_chapter_preview(self, chapters: List[Dict[str, Any]]) -> None:
        """Show chapter preview information."""
        self.renderer.show_info(f"Found {len(chapters)} chapters:")
        
        chapter_info = []
        for chapter in chapters[:10]:  # Show first 10 chapters
            duration_min = chapter['duration'] // 60
            duration_sec = chapter['duration'] % 60
            chapter_info.append(f"  {chapter['index']:2d}. {chapter['title']} ({duration_min}:{duration_sec:02d})")
        
        if len(chapters) > 10:
            chapter_info.append(f"  ... and {len(chapters) - 10} more chapters")
        
        self.renderer.show_info("\n".join(chapter_info))
    
    def _download_with_chapters(self, url: str, video_info: Dict[str, Any]) -> None:
        """Download video with chapter splitting."""
        try:
            self.renderer.show_info("Starting chapter split download...")
            
            # Create progress display
            progress = self.renderer.show_progress(f"Downloading with chapters: {video_info.get('title', 'Unknown')}")
            
            # Download with chapters
            result = self.downloader.download_with_chapters(url)
            
            if result['status'] == 'completed':
                chapter_count = result.get('chapter_count', 0)
                self.renderer.show_success(f"Chapter split download completed: {chapter_count} chapters created")
                
                # Log to history
                self.history_manager.add_download(url, video_info, result)
                
            else:
                self.renderer.show_error("Chapter split download failed")
                
        except Exception as e:
            self.renderer.show_error(f"Chapter split download failed: {str(e)}")
    
    def _show_resume_downloads_menu(self) -> None:
        """Show resume interrupted downloads menu."""
        self.renderer.show_info("Resume Interrupted Downloads")
        
        # Find interrupted downloads
        interrupted_downloads = self.downloader.find_interrupted_downloads()
        
        if not interrupted_downloads:
            self.renderer.show_info("No interrupted downloads found.")
            self.renderer.show_info("All downloads appear to be complete.")
            self.renderer.show_pause()
            self.current_menu = "main"
            return
        
        # Show interrupted downloads
        self.renderer.show_info(f"Found {len(interrupted_downloads)} interrupted downloads:")
        
        for i, download in enumerate(interrupted_downloads, 1):
            size_mb = download['size'] / (1024 * 1024)
            modified_str = download['modified'].strftime("%Y-%m-%d %H:%M")
            self.renderer.show_info(f"  {i}. {download['filename']} ({size_mb:.1f} MB, {modified_str})")
        
        # Show options
        options = {
            "1": (" Resume All Downloads", self._resume_all_downloads),
            "2": (" Resume Specific Download", self._resume_specific_download),
            "3": (" Clean Up Old Partial Files", self._cleanup_partial_files),
            "0": ("← Back to Main Menu", lambda: None),
        }
        
        choice = self.renderer.show_menu("Resume Downloads", options)
        
        if choice in options:
            options[choice][1](interrupted_downloads)
        
        self.current_menu = "main"
    
    def _resume_all_downloads(self, interrupted_downloads: List[Dict[str, Any]]) -> None:
        """Resume all interrupted downloads."""
        self.renderer.show_warning("""
        [bold]⚠️  Warning: Resume All Downloads[/bold]
        
        This will attempt to resume all interrupted downloads.
        Note: You may need to provide URLs for some downloads.
        """)
        
        if self.renderer.show_confirmation("Resume all interrupted downloads?", default=False):
            self.renderer.show_info("Resume functionality requires URLs for each download.")
            self.renderer.show_info("Please use the 'Resume Specific Download' option instead.")
            self.renderer.show_pause()
    
    def _resume_specific_download(self, interrupted_downloads: List[Dict[str, Any]]) -> None:
        """Resume a specific interrupted download."""
        if not interrupted_downloads:
            return
        
        # Show download selection
        self.renderer.show_info("Select a download to resume:")
        
        for i, download in enumerate(interrupted_downloads, 1):
            size_mb = download['size'] / (1024 * 1024)
            modified_str = download['modified'].strftime("%Y-%m-%d %H:%M")
            self.renderer.show_info(f"  {i}. {download['filename']} ({size_mb:.1f} MB, {modified_str})")
        
        try:
            choice = int(self.renderer.show_input_prompt("Enter download number", required=True))
            
            if 1 <= choice <= len(interrupted_downloads):
                selected_download = interrupted_downloads[choice - 1]
                
                # Get URL for resume
                url = self.renderer.show_input_prompt("Enter the original URL for this download", required=True)
                
                if url and self.downloader.validate_url(url):
                    self.renderer.show_info(f"Resuming download: {selected_download['filename']}")
                    
                    try:
                        result = self.downloader.resume_download(selected_download['filepath'], url)
                        
                        if result['status'] == 'completed':
                            self.renderer.show_success("Download resumed and completed successfully!")
                        else:
                            self.renderer.show_error("Failed to resume download")
                            
                    except Exception as e:
                        self.renderer.show_error(f"Failed to resume download: {str(e)}")
                else:
                    self.renderer.show_error("Invalid URL provided")
            else:
                self.renderer.show_error("Invalid selection")
                
        except ValueError:
            self.renderer.show_error("Please enter a valid number")
        except Exception as e:
            self.renderer.show_error(f"Error: {str(e)}")
    
    def _cleanup_partial_files(self, interrupted_downloads: List[Dict[str, Any]] = None) -> None:
        """Clean up old partial download files."""
        self.renderer.show_warning("""
        [bold]⚠️  Warning: Clean Up Partial Files[/bold]
        
        This will permanently delete old partial download files.
        Only files older than 7 days will be removed.
        """)
        
        if self.renderer.show_confirmation("Clean up old partial files?", default=False):
            try:
                cleaned_files = self.downloader.cleanup_partial_files()
                
                if cleaned_files:
                    self.renderer.show_success(f"Cleaned up {len(cleaned_files)} old partial files")
                    for file_path in cleaned_files[:5]:  # Show first 5
                        self.renderer.show_info(f"  • {file_path}")
                    if len(cleaned_files) > 5:
                        self.renderer.show_info(f"  • ... and {len(cleaned_files) - 5} more")
                else:
                    self.renderer.show_info("No old partial files found to clean up")
                    
            except Exception as e:
                self.renderer.show_error(f"Failed to clean up files: {str(e)}")
    
    def _show_file_management_menu(self) -> None:
        """Show file management menu."""
        self.renderer.show_info("File Management - Organize and clean up your downloads")
        
        # Show storage overview
        try:
            storage_info = self.file_manager.analyze_storage_usage()
            
            overview = f"""
            Storage Overview:
            • Total files: {storage_info['total_files']}
            • Total size: {storage_info['total_size_gb']:.2f} GB
            • Duplicates: {storage_info['duplicates_count']} files ({storage_info['duplicates_size_mb']:.1f} MB)
            • Large files: {storage_info['large_files_count']} (>500MB)
            • Old files: {storage_info['old_files_count']} (>90 days)
            """
            self.renderer.show_info(overview)
            
            if storage_info['recommendations']:
                self.renderer.show_info("Recommendations:")
                for rec in storage_info['recommendations']:
                    self.renderer.show_info(f"  • {rec}")
                    
        except Exception as e:
            self.renderer.show_warning(f"Could not analyze storage: {str(e)}")
        
        # Show menu options
        options = {
            "1": (" Find & Remove Duplicates", self._handle_duplicate_detection),
            "2": (" Organize Files by Type", self._handle_organize_files),
            "3": (" Clean Up Large Files", self._handle_large_files),
            "4": (" Clean Up Old Files", self._handle_old_files),
            "5": (" Remove Empty Folders", self._handle_empty_folders),
            "6": (" Storage Analysis", self._handle_storage_analysis),
            "0": ("← Back to Main Menu", lambda: None),
        }
        
        choice = self.renderer.show_menu("File Management", options)
        
        if choice in options:
            options[choice][1]()
        
        self.current_menu = "main"
    
    def _handle_duplicate_detection(self) -> None:
        """Handle duplicate detection and removal."""
        self.renderer.show_info("Scanning for duplicate files...")
        
        try:
            # Find duplicates by hash (most accurate)
            duplicates = self.file_manager.find_duplicates_by_hash()
            
            if not duplicates:
                self.renderer.show_success("No duplicate files found!")
                self.renderer.show_pause()
                return
            
            total_duplicates = sum(len(files) - 1 for files in duplicates.values())
            total_size = sum(
                sum(f['size'] for f in files[1:]) 
                for files in duplicates.values()
            )
            
            self.renderer.show_info(f"""
            Found {total_duplicates} duplicate files in {len(duplicates)} groups
            Total wasted space: {total_size / (1024*1024):.1f} MB
            """)
            
            # Show first few duplicate groups as examples
            self.renderer.show_info("Examples:")
            for i, (hash_val, files) in enumerate(list(duplicates.items())[:3]):
                self.renderer.show_info(f"  Group {i+1}: {len(files)} files, {files[0]['name']}")
                for file_info in files:
                    modified_str = file_info['modified'].strftime("%Y-%m-%d %H:%M")
                    self.renderer.show_info(f"    • {file_info['path']} ({modified_str})")
            
            if len(duplicates) > 3:
                self.renderer.show_info(f"  ... and {len(duplicates) - 3} more groups")
            
            # Ask for removal strategy
            strategy_options = {
                "1": (" Keep newest, remove older", "newest"),
                "2": (" Keep oldest, remove newer", "oldest"),
                "3": (" Keep largest, remove smaller", "largest"),
                "4": (" Keep smallest, remove larger", "smallest"),
                "0": (" Cancel", None),
            }
            
            strategy_choice = self.renderer.show_menu("Which files should be kept?", strategy_options)
            
            if strategy_choice in strategy_options and strategy_options[strategy_choice][1]:
                strategy = strategy_options[strategy_choice][1]
                
                self.renderer.show_warning(f"""
                [bold]⚠️  Warning: Remove Duplicates[/bold]
                
                This will permanently delete {total_duplicates} duplicate files.
                Strategy: Keep {strategy} file from each group.
                Space to be freed: {total_size / (1024*1024):.1f} MB
                """)
                
                if self.renderer.show_confirmation("Remove duplicate files?", default=False):
                    try:
                        removed_files = self.file_manager.remove_duplicates(duplicates, strategy)
                        self.renderer.show_success(f"Removed {len(removed_files)} duplicate files")
                        
                        if removed_files and len(removed_files) <= 10:
                            self.renderer.show_info("Removed files:")
                            for file_path in removed_files:
                                self.renderer.show_info(f"  • {file_path}")
                                
                    except Exception as e:
                        self.renderer.show_error(f"Failed to remove duplicates: {str(e)}")
            
        except Exception as e:
            self.renderer.show_error(f"Duplicate detection failed: {str(e)}")
        
        self.renderer.show_pause()
    
    def _handle_organize_files(self) -> None:
        """Handle organizing files by type."""
        self.renderer.show_info("Organizing files by type...")
        
        try:
            moved_counts = self.file_manager.move_files_by_extension()
            
            if moved_counts:
                self.renderer.show_success("Files organized successfully!")
                for folder, count in moved_counts.items():
                    self.renderer.show_info(f"  • {count} files moved to '{folder}' folder")
            else:
                self.renderer.show_info("No files needed to be organized")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to organize files: {str(e)}")
        
        self.renderer.show_pause()
    
    def _handle_large_files(self) -> None:
        """Handle large file management."""
        self.renderer.show_info("Finding large files (>500MB)...")
        
        try:
            large_files = self.file_manager.get_large_files()
            
            if not large_files:
                self.renderer.show_success("No large files found!")
                self.renderer.show_pause()
                return
            
            total_size = sum(f['size'] for f in large_files)
            
            self.renderer.show_info(f"""
            Found {len(large_files)} large files
            Total size: {total_size / (1024*1024*1024):.2f} GB
            """)
            
            # Show largest files
            self.renderer.show_info("Largest files:")
            for i, file_info in enumerate(large_files[:10]):
                size_gb = file_info['size_mb'] / 1024
                self.renderer.show_info(f"  {i+1}. {file_info['name']} ({size_gb:.2f} GB)")
            
            if len(large_files) > 10:
                self.renderer.show_info(f"  ... and {len(large_files) - 10} more")
            
            self.renderer.show_info("You can manually review and delete large files if needed.")
            
        except Exception as e:
            self.renderer.show_error(f"Failed to find large files: {str(e)}")
        
        self.renderer.show_pause()
    
    def _handle_old_files(self) -> None:
        """Handle old file management."""
        days = 90
        self.renderer.show_info(f"Finding files older than {days} days...")
        
        try:
            old_files = self.file_manager.get_old_files(days_threshold=days)
            
            if not old_files:
                self.renderer.show_success(f"No files older than {days} days found!")
                self.renderer.show_pause()
                return
            
            total_size = sum(f['size'] for f in old_files)
            
            self.renderer.show_info(f"""
            Found {len(old_files)} old files
            Total size: {total_size / (1024*1024*1024):.2f} GB
            """)
            
            # Show oldest files
            self.renderer.show_info("Oldest files:")
            for i, file_info in enumerate(old_files[:10]):
                age_days = (datetime.now() - file_info['modified']).days
                self.renderer.show_info(f"  {i+1}. {file_info['name']} ({age_days} days old)")
            
            if len(old_files) > 10:
                self.renderer.show_info(f"  ... and {len(old_files) - 10} more")
            
            self.renderer.show_warning(f"""
            [bold]⚠️  Warning: Remove Old Files[/bold]
            
            This will permanently delete {len(old_files)} files older than {days} days.
            Total space to be freed: {total_size / (1024*1024*1024):.2f} GB
            """)
            
            if self.renderer.show_confirmation(f"Remove files older than {days} days?", default=False):
                try:
                    deleted_count = self.file_manager.cleanup_old_files(days)
                    self.renderer.show_success(f"Removed {deleted_count} old files")
                    
                except Exception as e:
                    self.renderer.show_error(f"Failed to remove old files: {str(e)}")
            
        except Exception as e:
            self.renderer.show_error(f"Failed to find old files: {str(e)}")
        
        self.renderer.show_pause()
    
    def _handle_empty_folders(self) -> None:
        """Handle empty folder cleanup."""
        self.renderer.show_info("Scanning for empty folders...")
        
        try:
            empty_folders = self.file_manager.cleanup_empty_folders()
            
            if empty_folders:
                self.renderer.show_success(f"Removed {len(empty_folders)} empty folders")
                
                if len(empty_folders) <= 10:
                    self.renderer.show_info("Removed folders:")
                    for folder in empty_folders:
                        self.renderer.show_info(f"  • {folder}")
            else:
                self.renderer.show_info("No empty folders found")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to clean up empty folders: {str(e)}")
        
        self.renderer.show_pause()
    
    def _handle_storage_analysis(self) -> None:
        """Handle detailed storage analysis."""
        self.renderer.show_info("Analyzing storage usage...")
        
        try:
            storage_info = self.file_manager.analyze_storage_usage()
            
            # Show detailed analysis
            analysis = f"""
            Detailed Storage Analysis:
            
            Total Statistics:
            • Files: {storage_info['total_files']}
            • Size: {storage_info['total_size_gb']:.2f} GB ({storage_info['total_size_mb']:.1f} MB)
            
            File Types:
            """
            
            # Add extension statistics
            for ext, stats in sorted(storage_info['extension_stats'].items(), 
                                   key=lambda x: x[1]['size'], reverse=True)[:10]:
                size_mb = stats['size'] / (1024 * 1024)
                analysis += f"            • {ext or 'no extension'}: {stats['count']} files, {size_mb:.1f} MB\n"
            
            analysis += f"""
            
            Cleanup Opportunities:
            • Duplicates: {storage_info['duplicates_count']} files ({storage_info['duplicates_size_mb']:.1f} MB)
            • Large files: {storage_info['large_files_count']} (>500MB)
            • Old files: {storage_info['old_files_count']} (>90 days)
            
            Recommendations:
            """
            
            for rec in storage_info['recommendations']:
                analysis += f"            • {rec}\n"
            
            self.renderer.show_info(analysis)
            
        except Exception as e:
            self.renderer.show_error(f"Storage analysis failed: {str(e)}")
        
        self.renderer.show_pause()
    
    def _show_batch_download_menu(self) -> None:
        """Show batch download menu."""
        options = {
            "1": (" Paste URLs directly", self._handle_direct_urls),
            "2": (" Load from batch file", self._handle_batch_file),
            "3": (" Browse for batch file", self._handle_browse_file),
            "4": (" Audio-only batch processing", self._handle_audio_batch),
            "5": (" Create batch template", self._handle_create_template),
            "6": (" Show batch folder", self._handle_show_batch_folder),
            "7": (" Queue Management", self._handle_queue_management),
            "0": ("← Back to Main Menu", lambda: None),
        }
        
        choice = self.renderer.show_menu("Batch Download", options)
        
        if choice in options:
            options[choice][1]()
        
        self.current_menu = "main"
    
    def _handle_queue_management(self) -> None:
        """Handle queue management menu."""
        while True:
            status = self.batch_processor.get_queue_status()
            
            # Show current status
            status_info = f"""
            Queue Status: {status['status'].upper()}
            Total URLs: {status['total_urls']}
            Completed: {status['completed']}
            Remaining: {status['remaining']}
            """
            self.renderer.show_info(status_info)
            
            # Build options based on current status
            options = {}
            
            if status['status'] == 'idle':
                options.update({
                    "1": (" Add URLs to Queue", self._add_urls_to_queue),
                    "2": (" Load URLs from File", self._load_urls_to_queue),
                })
            elif status['status'] == 'running':
                options.update({
                    "1": (" Pause Processing", self._pause_queue),
                    "2": (" Stop Processing", self._stop_queue),
                    "3": (" Show Progress", self._show_queue_progress),
                })
            elif status['status'] == 'paused':
                options.update({
                    "1": (" Resume Processing", self._resume_queue),
                    "2": (" Stop Processing", self._stop_queue),
                    "3": (" Show Progress", self._show_queue_progress),
                })
            elif status['status'] == 'completed':
                options.update({
                    "1": (" View Results", self._view_queue_results),
                    "2": (" Retry Failed Downloads", self._retry_failed_downloads),
                    "3": (" Clear Queue", self._clear_queue),
                })
            
            options.update({
                "4": (" View Queue Contents", self._view_queue_contents),
                "0": ("← Back to Batch Menu", lambda: None),
            })
            
            choice = self.renderer.show_menu("Queue Management", options)
            
            if choice in options:
                result = options[choice][1]()
                if result is False:  # Return to batch menu
                    break
            else:
                break
    
    def _add_urls_to_queue(self) -> None:
        """Add URLs to the queue."""
        self.renderer.show_info("Enter URLs (one per line, press Enter twice when done):")
        
        urls = []
        while True:
            url = self.renderer.show_input_prompt("Enter URL (or press Enter to finish)", required=False)
            
            if not url:
                break
            
            if self.downloader.validate_url(url):
                urls.append(url)
                self.renderer.show_success(f"Added: {url}")
            else:
                self.renderer.show_error(f"Invalid URL: {url}")
        
        if urls:
            self.batch_processor.add_urls_to_queue(urls)
            self.renderer.show_success(f"Added {len(urls)} URLs to queue")
        else:
            self.renderer.show_info("No URLs added to queue")
    
    def _load_urls_to_queue(self) -> None:
        """Load URLs from file to queue."""
        file_path = self.renderer.show_input_prompt("Enter path to file with URLs")
        
        if file_path:
            try:
                path_obj = Path(file_path).expanduser()
                urls = self.batch_processor.load_urls_from_file(path_obj)
                
                if urls:
                    self.batch_processor.add_urls_to_queue(urls)
                    self.renderer.show_success(f"Loaded {len(urls)} URLs from {path_obj}")
                else:
                    self.renderer.show_warning("No valid URLs found in file")
            except Exception as e:
                self.renderer.show_error(f"Failed to load URLs: {str(e)}")
    
    def _pause_queue(self) -> None:
        """Pause queue processing."""
        self.batch_processor.pause_queue_processing()
    
    def _resume_queue(self) -> None:
        """Resume queue processing."""
        self.batch_processor.resume_queue_processing()
    
    def _stop_queue(self) -> None:
        """Stop queue processing."""
        self.renderer.show_warning("""
        [bold]⚠️  Warning: Stop Queue Processing[/bold]
        
        This will stop all ongoing downloads and cancel any remaining items in the queue.
        Currently downloading files will be interrupted.
        
        Are you sure you want to stop the queue?
        """)
        
        if self.renderer.show_confirmation("Stop queue processing?", default=False):
            self.batch_processor.stop_queue_processing()
    
    def _show_queue_progress(self) -> None:
        """Show queue progress."""
        status = self.batch_processor.get_queue_status()
        
        if status['total_urls'] > 0:
            progress = (status['completed'] / status['total_urls']) * 100
            progress_info = f"""
            Progress: {progress:.1f}%
            Completed: {status['completed']}/{status['total_urls']}
            Remaining: {status['remaining']}
            Status: {status['status'].upper()}
            """
            self.renderer.show_info(progress_info)
        else:
            self.renderer.show_info("Queue is empty")
    
    def _view_queue_results(self) -> None:
        """View queue results."""
        results = self.batch_processor.get_queue_results()
        
        if results:
            self.renderer.show_download_summary(results)
        else:
            self.renderer.show_info("No results available")
    
    def _retry_failed_downloads(self) -> None:
        """Retry failed downloads."""
        failed = self.batch_processor.queue.get_failed_downloads()
        
        if failed:
            self.renderer.show_info(f"Retrying {len(failed)} failed downloads...")
            self.batch_processor.retry_failed_queue_downloads()
        else:
            self.renderer.show_info("No failed downloads to retry")
    
    def _clear_queue(self) -> None:
        """Clear the queue."""
        self.renderer.show_warning("""
        [bold]⚠️  Warning: Clear Download Queue[/bold]
        
        This will remove ALL items from the download queue.
        Any pending downloads will be lost.
        
        Currently downloading files will continue, but queued items will be removed.
        """)
        
        if self.renderer.show_confirmation("Clear the entire queue?", default=False):
            self.batch_processor.clear_queue()
            self.renderer.show_success("Queue cleared")
    
    def _view_queue_contents(self) -> None:
        """View queue contents."""
        status = self.batch_processor.get_queue_status()
        
        if status['total_urls'] > 0:
            # Show first few URLs
            urls = self.batch_processor.queue.urls[:5]  # Show first 5
            content = "\n".join([f"• {url}" for url in urls])
            
            if status['total_urls'] > 5:
                content += f"\n... and {status['total_urls'] - 5} more URLs"
            
            self.renderer.show_info(f"Queue Contents:\n{content}")
        else:
            self.renderer.show_info("Queue is empty")
    
    def _handle_direct_urls(self) -> None:
        """Handle direct URL input for batch download."""
        self.renderer.show_info("Enter URLs (one per line, press Enter twice when done):")
        
        urls = []
        while True:
            url = self.renderer.show_input_prompt("Enter URL (or press Enter to finish)", required=False)
            
            if not url:
                break
            
            if self.downloader.validate_url(url):
                urls.append(url)
                self.renderer.show_success(f"Added: {url}")
            else:
                self.renderer.show_warning(f"Invalid URL: {url}")
        
        if urls:
            self._process_batch_download(urls)
        else:
            self.renderer.show_warning("No valid URLs provided")
    
    def _handle_batch_file(self) -> None:
        """Handle batch file loading."""
        # Show batch folder location first
        try:
            batch_folder = self.file_manager.get_batch_folder()
            self.renderer.show_info(f"Batch folder: {batch_folder}")
        except Exception:
            pass
        
        file_path = self.renderer.show_input_prompt("Enter batch file path", required=True)
        
        try:
            urls = self.batch_processor.load_urls_from_file(Path(file_path))
            if urls:
                self.renderer.show_info(f"Loaded {len(urls)} URLs from file")
                self._process_batch_download(urls)
            else:
                self.renderer.show_warning("No URLs found in file")
        except Exception as e:
            self.renderer.show_error(f"Failed to load batch file: {str(e)}")
    
    def _handle_browse_file(self) -> None:
        """Handle file browsing for batch download."""
        # This would typically open a file dialog
        # For CLI, we'll use the same as direct file input
        self._handle_batch_file()
    
    def _handle_audio_batch(self) -> None:
        """Handle audio-only batch processing."""
        self.renderer.show_info("Audio-Only Batch Processing")
        
        # Get audio format
        audio_format = self._show_audio_format_selection()
        
        # Get URLs
        self.renderer.show_info("Enter URLs (one per line, press Enter twice when done):")
        
        urls = []
        while True:
            url = self.renderer.show_input_prompt("Enter URL (or press Enter to finish)", required=False)
            
            if not url:
                break
            
            if self.downloader.validate_url(url):
                urls.append(url)
                self.renderer.show_success(f"Added: {url}")
            else:
                self.renderer.show_error(f"Invalid URL: {url}")
        
        if urls:
            self.renderer.show_info(f"Processing {len(urls)} URLs for audio extraction...")
            
            try:
                # Show concurrency info
                max_concurrent = self.settings.download.max_concurrent
                self.renderer.show_info(f"Using concurrent audio extraction: {max_concurrent}")
                
                # Process audio batch with concurrency
                results = self.batch_processor.process_audio_batch_with_limits(urls, audio_format)
                
                # Show results
                self._show_batch_results(results, f"Audio extraction ({audio_format.upper()})")
                
            except Exception as e:
                self.renderer.show_error(f"Audio batch processing failed: {str(e)}")
        else:
            self.renderer.show_info("No URLs to process")
    
    def _show_batch_results(self, results: List[Dict[str, Any]], title: str = "Batch Results") -> None:
        """Show batch processing results."""
        if not results:
            self.renderer.show_info("No results to display")
            return
        
        # Count results
        total = len(results)
        successful = sum(1 for r in results if r.get('status') == 'completed')
        failed = total - successful
        
        # Show summary
        summary = f"""
        {title} Summary:
        • Total: {total}
        • Successful: {successful}
        • Failed: {failed}
        • Success Rate: {(successful/total)*100:.1f}%
        """
        self.renderer.show_info(summary)
        
        # Show failed downloads if any
        if failed > 0:
            failed_downloads = [r for r in results if r.get('status') != 'completed']
            self.renderer.show_warning(f"Failed downloads ({failed}):")
            for result in failed_downloads:
                self.renderer.show_error(f"  • {result.get('url', 'Unknown')}: {result.get('error', 'Unknown error')}")
        
        self.renderer.show_pause()
    
    def _handle_create_template(self) -> None:
        """Handle creating a batch template file."""
        try:
            # Get the batch folder
            batch_folder = self.file_manager.get_batch_folder()
            template_path = batch_folder / "batch_template.txt"
            
            # Create the template
            self.batch_processor.create_batch_template(template_path)
            
            self.renderer.show_success(f"Batch template created: {template_path}")
            self.renderer.show_info("You can now edit this file and add your URLs, one per line.")
            
        except Exception as e:
            self.renderer.show_error(f"Failed to create batch template: {str(e)}")
    
    def _handle_show_batch_folder(self) -> None:
        """Handle showing the batch folder location."""
        try:
            batch_folder = self.file_manager.get_batch_folder()
            self.renderer.show_info(f"Batch folder location: {batch_folder}")
            self.renderer.show_info("You can place your batch files (.txt) in this folder.")
            self.renderer.show_info("Each line should contain one URL.")
            self.renderer.show_info("Lines starting with # are treated as comments.")
            
        except Exception as e:
            self.renderer.show_error(f"Failed to get batch folder: {str(e)}")
    
    def _process_batch_download(self, urls: List[str]) -> None:
        """Process batch download."""
        self.renderer.show_info(f"Starting batch download of {len(urls)} videos...")
        
        # Show concurrency info
        max_concurrent = self.settings.download.max_concurrent
        self.renderer.show_info(f"Using concurrent downloads: {max_concurrent}")
        
        # Show memory usage estimation
        try:
            memory_info = self.batch_processor.estimate_memory_usage(urls, max_concurrent)
            
            memory_summary = f"""
            Memory Usage Estimation:
            • Estimated memory: {memory_info['estimated_memory_mb']:.1f} MB
            • Current memory: {memory_info['current_memory_mb']:.1f} MB
            • Available memory: {memory_info['available_memory_mb']:.1f} MB
            • Memory safe: {'Yes' if memory_info['memory_safe'] else 'No'}
            """
            self.renderer.show_info(memory_summary)
            
            if not memory_info['memory_safe']:
                self.renderer.show_warning("Warning: Estimated memory usage may exceed available memory.")
                if not self.renderer.show_confirmation("Continue anyway?", default=False):
                    return
                    
        except Exception as e:
            self.renderer.show_warning(f"Could not estimate memory usage: {str(e)}")
        
        if self.renderer.show_download_confirmation(f"Download {len(urls)} videos?", self.settings.ui.auto_download):
            try:
                # Use concurrent processing for better performance
                results = self.batch_processor.process_batch_with_limits(urls)
                
                # Show results summary
                successful = len([r for r in results if r.get('status') == 'completed'])
                failed = len([r for r in results if r.get('status') == 'failed'])
                
                self.renderer.show_success(f"Batch download completed: {successful} successful, {failed} failed")
                
            except Exception as e:
                self.renderer.show_error(f"Batch download failed: {str(e)}")
    
    def _show_options_menu(self) -> None:
        """Show options and settings menu."""
        options = {
            "1": (" Download Path Settings", self._handle_path_settings),
            "2": (" Auto-Download Settings", self._handle_auto_download_settings),
            "3": (" Audio/Video Format Settings", self._handle_format_settings),
            "4": (" File Organization Settings", self._handle_organization_settings),
            "5": (" Performance Settings", self._handle_performance_settings),
            "6": (" Advanced yt-dlp Options", self._handle_advanced_settings),
            "7": (" View/Edit Config Files", self._handle_config_files),
            "8": (" Configuration Wizard", self._handle_configuration_wizard),
            "9": (" Reset to Defaults", self._handle_reset_defaults),
            "0": ("← Back to Main Menu", lambda: None),
        }
        
        choice = self.renderer.show_menu("Options & Settings", options)
        
        if choice in options:
            options[choice][1]()
        
        self.current_menu = "main"
    
    def _handle_path_settings(self) -> None:
        """Handle download path settings."""
        current_path = self.settings.download.path
        self.renderer.show_info(f"Current download path: {current_path}")
        
        # Show folder structure preview
        folder_structure = f"""
        Folder Structure:
        └── {current_path}/
            └── DD/ (current day folders)
                └── YYYY-MM-DD_video-title.ext
        """
        self.renderer.show_info(folder_structure)
        
        options = {
            "1": (" Set Custom Download Path", self._set_custom_path),
            "2": (" Use Default Downloads Folder", self._set_default_path),
            "3": (" Browse for Folder", self._browse_for_folder),
            "4": (" Test Path", self._test_path),
            "0": ("← Back to Options Menu", lambda: None),
        }
        
        choice = self.renderer.show_menu("Download Path Settings", options)
        
        if choice in options:
            options[choice][1]()
    
    def _set_custom_path(self) -> None:
        """Set a custom download path."""
        current_path = self.settings.download.path
        new_path = self.renderer.show_input_prompt("Enter new download path", default=current_path)
        
        if new_path and new_path != current_path:
            try:
                # Validate and create path if it doesn't exist
                path_obj = Path(new_path).expanduser()
                path_obj.mkdir(parents=True, exist_ok=True)
                
                self.settings.download.path = str(path_obj)
                self.config_manager.save_config()
                self.renderer.show_success(f"Download path updated to: {path_obj}")
            except Exception as e:
                self.renderer.show_error(f"Failed to update path: {str(e)}")
    
    def _set_default_path(self) -> None:
        """Set the default downloads folder."""
        try:
            default_path = str(Path.home() / "Downloads" / "VideoMilker")
            path_obj = Path(default_path)
            path_obj.mkdir(parents=True, exist_ok=True)
            
            self.settings.download.path = default_path
            self.config_manager.save_config()
            self.renderer.show_success(f"Download path set to default: {default_path}")
        except Exception as e:
            self.renderer.show_error(f"Failed to set default path: {str(e)}")
    
    def _browse_for_folder(self) -> None:
        """Browse for a folder using system file dialog."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            # Create a hidden root window
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Open folder dialog
            folder_path = filedialog.askdirectory(
                title="Select Download Folder",
                initialdir=self.settings.download.path
            )
            
            if folder_path:
                path_obj = Path(folder_path)
                self.settings.download.path = str(path_obj)
                self.config_manager.save_config()
                self.renderer.show_success(f"Download path set to: {path_obj}")
            else:
                self.renderer.show_info("No folder selected")
                
        except ImportError:
            self.renderer.show_error("File dialog not available. Please enter path manually.")
        except Exception as e:
            self.renderer.show_error(f"Failed to browse for folder: {str(e)}")
    
    def _test_path(self) -> None:
        """Test if the current download path is accessible."""
        try:
            path_obj = Path(self.settings.download.path).expanduser()
            
            if path_obj.exists():
                if path_obj.is_dir():
                    # Test write permissions
                    test_file = path_obj / ".test_write"
                    try:
                        test_file.touch()
                        test_file.unlink()
                        self.renderer.show_success(f"Path is accessible and writable: {path_obj}")
                    except PermissionError:
                        self.renderer.show_error(f"Path exists but is not writable: {path_obj}")
                else:
                    self.renderer.show_error(f"Path exists but is not a directory: {path_obj}")
            else:
                # Try to create the directory
                path_obj.mkdir(parents=True, exist_ok=True)
                self.renderer.show_success(f"Path created successfully: {path_obj}")
                
        except Exception as e:
            self.renderer.show_error(f"Path test failed: {str(e)}")
    
    def _handle_auto_download_settings(self) -> None:
        """Handle auto-download settings."""
        current_status = "ON" if self.settings.ui.auto_download else "OFF"
        self.renderer.show_info(f"Current auto-download status: {current_status}")
        
        if self.renderer.show_confirmation("Toggle auto-download setting?"):
            self.settings.ui.auto_download = not self.settings.ui.auto_download
            try:
                self.config_manager.save_config()
                new_status = "ON" if self.settings.ui.auto_download else "OFF"
                self.renderer.show_success(f"Auto-download setting updated: {new_status}")
            except Exception as e:
                self.renderer.show_error(f"Failed to update auto-download setting: {str(e)}")
    
    def _handle_format_settings(self) -> None:
        """Handle format settings."""
        self.renderer.show_info("Format settings - coming soon!")
        self.renderer.show_pause()
    
    def _handle_organization_settings(self) -> None:
        """Handle file organization settings."""
        self.renderer.show_info("File organization settings - coming soon!")
        self.renderer.show_pause()
    
    def _handle_performance_settings(self) -> None:
        """Handle performance settings."""
        current_concurrent = self.settings.download.max_concurrent
        self.renderer.show_info(f"Current concurrent download limit: {current_concurrent}")
        
        self.renderer.show_info("""
        Performance Settings:
        • Concurrent Downloads: Number of simultaneous downloads
        • Higher values = faster downloads but more resource usage
        • Recommended: 3-5 for most connections
        • Maximum: 10 (to avoid overwhelming servers)
        """)
        
        options = {
            "1": (" Set Concurrent Download Limit", self._set_concurrent_limit),
            "2": (" View Current Performance Settings", self._view_performance_settings),
            "0": ("← Back to Options Menu", lambda: None),
        }
        
        choice = self.renderer.show_menu("Performance Settings", options)
        
        if choice in options:
            options[choice][1]()
    
    def _set_concurrent_limit(self) -> None:
        """Set the concurrent download limit."""
        current = self.settings.download.max_concurrent
        
        self.renderer.show_info(f"Current limit: {current} concurrent downloads")
        
        try:
            new_limit = self.renderer.show_input_prompt(
                f"Enter new limit (1-10, current: {current})", 
                required=True,
                default=str(current)
            )
            
            if new_limit:
                limit = int(new_limit)
                if 1 <= limit <= 10:
                    self.settings.download.max_concurrent = limit
                    self.config_manager.save_config()
                    self.renderer.show_success(f"Concurrent download limit set to: {limit}")
                else:
                    self.renderer.show_error("Limit must be between 1 and 10")
            else:
                self.renderer.show_info("No changes made")
                
        except ValueError:
            self.renderer.show_error("Please enter a valid number")
        except Exception as e:
            self.renderer.show_error(f"Failed to update setting: {str(e)}")
    
    def _view_performance_settings(self) -> None:
        """View current performance settings."""
        settings_info = f"""
        Current Performance Settings:
        
        • Concurrent Downloads: {self.settings.download.max_concurrent}
        • Retries: {self.settings.download.retries}
        • Fragment Retries: {self.settings.download.fragment_retries}
        • Socket Timeout: {self.settings.download.socket_timeout}s
        • Sleep Between Requests: {self.settings.download.sleep_requests}s
        """
        
        self.renderer.show_info(settings_info)
        self.renderer.show_pause()
    
    def _handle_advanced_settings(self) -> None:
        """Handle advanced settings."""
        self.renderer.show_info("Advanced settings - coming soon!")
        self.renderer.show_pause()
    
    def _handle_config_files(self) -> None:
        """Handle config file management."""
        options = {
            "1": (" View Current Settings", self._view_current_settings),
            "2": (" Export Configuration", self._export_configuration),
            "3": (" Import Configuration", self._import_configuration),
            "4": (" Validate Configuration", self._validate_configuration),
            "5": (" Auto-Fix Configuration", self._auto_fix_configuration),
            "0": ("← Back to Options Menu", lambda: None),
        }
        
        choice = self.renderer.show_menu("Configuration Management", options)
        
        if choice in options:
            options[choice][1]()
    
    def _view_current_settings(self) -> None:
        """View current configuration settings."""
        self.renderer.show_settings(self.settings)
        self.renderer.show_pause()
    
    def _export_configuration(self) -> None:
        """Export configuration to a file."""
        export_path = self.renderer.show_input_prompt("Enter export file path", default="videomilker_config_export.json")
        
        if export_path:
            try:
                path_obj = Path(export_path).expanduser()
                self.config_manager.export_config(path_obj)
                self.renderer.show_success(f"Configuration exported to: {path_obj}")
            except Exception as e:
                self.renderer.show_error(f"Failed to export configuration: {str(e)}")
        
        self.renderer.show_pause()
    
    def _import_configuration(self) -> None:
        """Import configuration from a file."""
        import_path = self.renderer.show_input_prompt("Enter import file path")
        
        if import_path:
            try:
                path_obj = Path(import_path).expanduser()
                if not path_obj.exists():
                    self.renderer.show_error(f"Configuration file not found: {path_obj}")
                else:
                    # Validate the imported configuration
                    imported_settings = self.config_manager.import_config(path_obj)
                    is_valid, errors = self.config_manager.validate_config(imported_settings)
                    
                    if is_valid:
                        self.renderer.show_warning("""
                        [bold]⚠️  Warning: Import Configuration[/bold]
                        
                        This will replace your current configuration with the imported settings.
                        Your current settings will be backed up, but this action will change:
                        
                        • Download paths and preferences
                        • UI settings and themes
                        • Quality and format settings
                        • All other configuration options
                        """)
                        
                        if self.renderer.show_confirmation("Import configuration and replace current settings?", default=False):
                            self.settings = imported_settings
                            self.config_manager.save_config()
                            self.renderer.show_success(f"Configuration imported from: {path_obj}")
                    else:
                        self.renderer.show_error("Imported configuration has validation errors:")
                        for error in errors:
                            self.renderer.show_error(f"  • {error}")
                        self.renderer.show_info("Configuration was not imported due to validation errors.")
            except Exception as e:
                self.renderer.show_error(f"Failed to import configuration: {str(e)}")
        
        self.renderer.show_pause()
    
    def _validate_configuration(self) -> None:
        """Validate current configuration."""
        is_valid, errors = self.config_manager.validate_config(self.settings)
        
        if is_valid:
            self.renderer.show_success("Configuration is valid!")
        else:
            self.renderer.show_error("Configuration validation found issues:")
            for error in errors:
                self.renderer.show_error(f"  • {error}")
        
        self.renderer.show_pause()
    
    def _auto_fix_configuration(self) -> None:
        """Auto-fix configuration issues."""
        fixes_applied, fixes = self.config_manager.auto_fix_config(self.settings)
        
        if fixes_applied:
            self.renderer.show_success("Auto-fixed configuration issues:")
            for fix in fixes:
                self.renderer.show_success(f"  ✓ {fix}")
            
            # Re-validate after fixes
            is_valid, remaining_errors = self.config_manager.validate_config(self.settings)
            if is_valid:
                self.renderer.show_success("Configuration is now valid!")
            else:
                self.renderer.show_warning("Some configuration issues remain:")
                for error in remaining_errors:
                    self.renderer.show_error(f"  • {error}")
        else:
            self.renderer.show_info("No configuration issues found or could be auto-fixed.")
        
        self.renderer.show_pause()
    
    def _handle_configuration_wizard(self) -> None:
        """Handle configuration wizard for first-time users."""
        self.renderer.show_info("""
        [bold]VideoMilker Configuration Wizard[/bold]
        
        This wizard will help you set up VideoMilker with optimal settings
        for your needs. You can skip any step by pressing Enter.
        """)
        
        if not self.renderer.show_confirmation("Start configuration wizard?"):
            return
        
        # Step 1: Download Path
        self.renderer.show_info("[bold]Step 1: Download Location[/bold]")
        self.renderer.show_info("Where would you like to save your downloaded videos?")
        
        path_options = {
            "1": (" Default Downloads Folder", lambda: str(Path.home() / "Downloads" / "VideoMilker")),
            "2": (" Custom Path", lambda: self.renderer.show_input_prompt("Enter custom download path")),
            "3": (" Browse for Folder", self._browse_for_folder_wizard),
            "0": (" Skip this step", lambda: None),
        }
        
        path_choice = self.renderer.show_menu("Select Download Location", path_options)
        if path_choice in path_options:
            result = path_options[path_choice][1]()
            if result:
                try:
                    path_obj = Path(result).expanduser()
                    path_obj.mkdir(parents=True, exist_ok=True)
                    self.settings.download.path = str(path_obj)
                    self.renderer.show_success(f"Download path set to: {path_obj}")
                except Exception as e:
                    self.renderer.show_error(f"Failed to set download path: {str(e)}")
        
        # Step 2: Video Quality
        self.renderer.show_info("[bold]Step 2: Default Video Quality[/bold]")
        self.renderer.show_info("What quality would you prefer for video downloads?")
        
        quality_options = {
            "1": (" Best Quality (Recommended)", "best"),
            "2": (" 720p HD", "720p"),
            "3": (" 1080p Full HD", "1080p"),
            "4": (" Audio Only (MP3)", "audio_only"),
            "5": (" Audio Only (M4A)", "audio_m4a"),
            "6": (" Audio Only (FLAC)", "audio_flac"),
            "7": (" Lowest Quality (Fastest)", "worst"),
            "0": (" Skip this step", lambda: None),
        }
        
        quality_choice = self.renderer.show_menu("Select Default Quality", quality_options)
        if quality_choice in quality_options and quality_choice != "0":
            self.settings.download.default_quality = quality_options[quality_choice][1]
            self.renderer.show_success(f"Default quality set to: {quality_options[quality_choice][1]}")
        
        # Step 3: File Organization
        self.renderer.show_info("[bold]Step 3: File Organization[/bold]")
        self.renderer.show_info("How would you like to organize your downloaded files?")
        
        if self.renderer.show_confirmation("Create separate folders for each day?"):
            self.settings.download.create_day_folders = True
            self.renderer.show_success("Day-based organization enabled")
        else:
            self.settings.download.create_day_folders = False
            self.renderer.show_success("All files will be saved in the main download folder")
        
        # Step 4: Auto-Download
        self.renderer.show_info("[bold]Step 4: Auto-Download[/bold]")
        self.renderer.show_info("Would you like downloads to start automatically without confirmation?")
        
        if self.renderer.show_confirmation("Enable auto-download?"):
            self.settings.ui.auto_download = True
            self.renderer.show_success("Auto-download enabled")
        else:
            self.settings.ui.auto_download = False
            self.renderer.show_success("Auto-download disabled (you'll be asked to confirm each download)")
        
        # Step 5: Theme
        self.renderer.show_info("[bold]Step 5: Interface Theme[/bold]")
        self.renderer.show_info("Choose your preferred interface theme:")
        
        theme_options = {
            "1": (" Default Theme", "default"),
            "2": (" Dark Theme", "dark"),
            "3": (" Light Theme", "light"),
            "4": (" Minimal Theme", "minimal"),
            "0": (" Skip this step", lambda: None),
        }
        
        theme_choice = self.renderer.show_menu("Select Theme", theme_options)
        if theme_choice in theme_options and theme_choice != "0":
            self.settings.ui.theme = theme_options[theme_choice][1]
            self.renderer.show_success(f"Theme set to: {theme_options[theme_choice][1]}")
        
        # Save configuration
        try:
            self.config_manager.save_config()
            self.renderer.show_success("Configuration saved successfully!")
        except Exception as e:
            self.renderer.show_error(f"Failed to save configuration: {str(e)}")
        
        # Show summary
        self.renderer.show_info("""
        [bold]Configuration Summary:[/bold]
        
        Download Path: {path}
        Default Quality: {quality}
        Day Folders: {day_folders}
        Auto-Download: {auto_download}
        Theme: {theme}
        """.format(
            path=self.settings.download.path,
            quality=self.settings.download.default_quality,
            day_folders="Enabled" if self.settings.download.create_day_folders else "Disabled",
            auto_download="Enabled" if self.settings.ui.auto_download else "Disabled",
            theme=self.settings.ui.theme
        ))
        
        self.renderer.show_pause()
    
    def _browse_for_folder_wizard(self) -> str:
        """Browse for folder in wizard mode."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            # Create a hidden root window
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Open folder dialog
            folder_path = filedialog.askdirectory(
                title="Select Download Folder",
                initialdir=self.settings.download.path
            )
            
            if folder_path:
                return folder_path
            else:
                return ""
                
        except ImportError:
            self.renderer.show_error("File dialog not available. Please enter path manually.")
            return self.renderer.show_input_prompt("Enter download path")
        except Exception as e:
            self.renderer.show_error(f"Failed to browse for folder: {str(e)}")
            return ""
    
    def _handle_reset_defaults(self) -> None:
        """Handle reset to defaults."""
        self.renderer.show_warning("""
        [bold]⚠️  Warning: Reset to Defaults[/bold]
        
        This will reset ALL your settings to their default values.
        This action cannot be undone.
        
        You will lose:
        • Custom download paths
        • Quality preferences
        • UI theme settings
        • Auto-download settings
        • All other customizations
        """)
        
        if self.renderer.show_confirmation("Are you absolutely sure you want to reset all settings?", default=False):
            try:
                self.settings = self.config_manager.reset_to_defaults()
                self.renderer.show_success("Settings reset to defaults")
            except Exception as e:
                self.renderer.show_error(f"Failed to reset settings: {str(e)}")
    
    def _show_history_menu(self) -> None:
        """Show download history menu."""
        try:
            history = self.history_manager.get_recent_downloads(10)
            
            if history:
                self.renderer.show_download_summary(history)
            else:
                self.renderer.show_info("No download history found")
            
            options = {
                "1": (" View Full History", self._handle_full_history),
                "2": (" Search History", self._handle_search_history),
                "3": (" Advanced Search", self._handle_advanced_search),
                "4": (" Clear History", self._handle_clear_history),
                "5": (" Open Download Folder", self._handle_open_folder),
                "0": ("← Back to Main Menu", lambda: None),
            }
            
            choice = self.renderer.show_menu("Download History", options)
            
            if choice in options:
                options[choice][1]()
                
        except Exception as e:
            self.renderer.show_error(f"Failed to load history: {str(e)}")
        
        self.current_menu = "main"
    
    def _handle_full_history(self) -> None:
        """Handle full history view."""
        try:
            history = self.history_manager.get_all_downloads()
            self.renderer.show_download_summary(history)
        except Exception as e:
            self.renderer.show_error(f"Failed to load full history: {str(e)}")
        
        self.renderer.show_pause()
    
    def _handle_search_history(self) -> None:
        """Handle basic history search."""
        query = self.renderer.show_input_prompt("Enter search term (title, uploader, or URL)")
        
        if query:
            try:
                results = self.history_manager.search_downloads(query)
                
                if results:
                    self.renderer.show_success(f"Found {len(results)} results")
                    self.renderer.show_download_summary(results)
                else:
                    self.renderer.show_info("No results found")
                    
            except Exception as e:
                self.renderer.show_error(f"Search failed: {str(e)}")
        
        self.renderer.show_pause()
    
    def _handle_advanced_search(self) -> None:
        """Handle advanced history search."""
        self.renderer.show_info("Advanced Search - Enter search criteria:")
        
        filters = {}
        
        # Title filter
        title = self.renderer.show_input_prompt("Title (leave empty to skip)", required=False)
        if title:
            filters['title'] = title
        
        # Uploader filter
        uploader = self.renderer.show_input_prompt("Uploader (leave empty to skip)", required=False)
        if uploader:
            filters['uploader'] = uploader
        
        # Status filter
        status_options = {
            "1": ("completed", "Completed downloads"),
            "2": ("failed", "Failed downloads"),
            "3": ("cancelled", "Cancelled downloads"),
            "0": ("", "Skip status filter"),
        }
        
        status_choice = self.renderer.show_menu("Select Status Filter", status_options)
        if status_choice in status_options and status_options[status_choice][0]:
            filters['status'] = status_options[status_choice][0]
        
        # Limit results
        limit_str = self.renderer.show_input_prompt("Limit results (leave empty for no limit)", required=False)
        if limit_str and limit_str.isdigit():
            filters['limit'] = int(limit_str)
        
        try:
            results = self.history_manager.advanced_search(filters)
            
            if results:
                self.renderer.show_success(f"Found {len(results)} results")
                self.renderer.show_download_summary(results)
            else:
                self.renderer.show_info("No results found")
                
        except Exception as e:
            self.renderer.show_error(f"Advanced search failed: {str(e)}")
        
        self.renderer.show_pause()
    
    def _handle_clear_history(self) -> None:
        """Handle history clearing."""
        self.renderer.show_warning("""
        [bold]⚠️  Warning: Clear Download History[/bold]
        
        This will permanently delete ALL your download history.
        This action cannot be undone.
        
        You will lose:
        • All download records
        • Download statistics
        • File information
        • Download timestamps
        """)
        
        if self.renderer.show_confirmation("Are you absolutely sure you want to clear all download history?", default=False):
            try:
                self.history_manager.clear_history()
                self.renderer.show_success("History cleared successfully")
            except Exception as e:
                self.renderer.show_error(f"Failed to clear history: {str(e)}")
    
    def _handle_open_folder(self) -> None:
        """Handle opening download folder."""
        try:
            import subprocess
            import platform
            
            folder_path = self.settings.get_download_path()
            
            if platform.system() == "Windows":
                subprocess.run(["explorer", str(folder_path)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(folder_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(folder_path)])
                
            self.renderer.show_success(f"Opened folder: {folder_path}")
            
        except Exception as e:
            self.renderer.show_error(f"Failed to open folder: {str(e)}")
    
    def _show_help_menu(self) -> None:
        """Show help and information menu."""
        self.renderer.show_help()
        self.renderer.show_pause()
        self.current_menu = "main"
