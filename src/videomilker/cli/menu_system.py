"""Main menu system for VideoMilker CLI."""

from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED

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
        self.menu_history = []  # Track menu navigation history
    
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
    
    def _navigate_to_menu(self, menu_name: str) -> None:
        """Navigate to a menu with proper history tracking."""
        if self.current_menu != menu_name:
            self.menu_history.append(self.current_menu)
            self.current_menu = menu_name
    
    def _go_back(self) -> None:
        """Go back to the previous menu in history."""
        if self.menu_history:
            self.current_menu = self.menu_history.pop()
        else:
            self.current_menu = "main"
    
    def _get_menu_title(self, menu_name: str) -> str:
        """Get the display title for a menu."""
        titles = {
            "main": "VideoMilker Main Menu",
            "quick_download": "Quick Download",
            "audio_download": "Audio-Only Download",
            "chapter_download": "Chapter Split Download",
            "batch_download": "Batch Download",
            "resume_downloads": "Resume Interrupted Downloads",
            "file_management": "File Management",
            "options": "Options & Settings",
            "history": "Download History",
            "help": "Help & Information"
        }
        return titles.get(menu_name, "Menu")
    
    def _handle_global_shortcuts(self, choice: str) -> bool:
        """Handle global keyboard shortcuts."""
        shortcuts = {
            # Navigation shortcuts
            '0': self._go_back,
            'b': self._go_back,
            'B': self._go_back,
            'q': self._handle_quit,
            'Q': self._handle_quit,
            
            # Menu shortcuts
            'h': self._handle_help,
            'H': self._handle_help,
            's': self._handle_options,
            'S': self._handle_options,
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
            'i': self._handle_history,
            'I': self._handle_history,
            
            # Special shortcuts
            '?': self._show_keyboard_shortcuts,
            'esc': self._go_back,
            'ESC': self._go_back,
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
        # Show welcome banner if this is the first time
        if not hasattr(self, '_main_menu_shown'):
            self.renderer.show_welcome_banner()
            self._main_menu_shown = True
        
        options = {
            "1": (" Quick Download", self._handle_quick_download),
            "2": (" Audio-Only Download", self._handle_audio_download),
            "3": (" Chapter Split Download", self._handle_chapter_download),
            "4": (" Batch Download", self._handle_batch_download),
            "5": (" Resume Interrupted Downloads", self._handle_resume_downloads),
            "6": (" File Management", self._handle_file_management),
            "7": (" Options & Settings", self._handle_options),
            "8": (" Download History", self._handle_history),
            "9": (" Help & Info", self._handle_help),
            "q": ("Quit Application", self._handle_quit),
        }
        
        # Simple shortcut hint
        shortcut_hint = "[dim]Press ? for keyboard shortcuts[/dim]"
        
        choice = self.renderer.show_menu(
            "VideoMilker Main Menu", 
            options, 
            show_shortcuts=True,
            extra_info=shortcut_hint
        )
        
        # Check for global shortcuts first
        if self._handle_global_shortcuts(choice):
            return
        
        if choice in options:
            options[choice][1]()
    
    def _handle_quick_download(self) -> None:
        """Handle quick download option."""
        self._navigate_to_menu("quick_download")
    
    def _handle_audio_download(self) -> None:
        """Handle audio-only download option."""
        self._navigate_to_menu("audio_download")
    
    def _handle_chapter_download(self) -> None:
        """Handle chapter split download option."""
        self._navigate_to_menu("chapter_download")
    
    def _handle_resume_downloads(self) -> None:
        """Handle resume interrupted downloads option."""
        self._navigate_to_menu("resume_downloads")
    
    def _handle_file_management(self) -> None:
        """Handle file management option."""
        self._navigate_to_menu("file_management")
    
    def _handle_batch_download(self) -> None:
        """Handle batch download option."""
        self._navigate_to_menu("batch_download")
    
    def _handle_options(self) -> None:
        """Handle options menu."""
        self._navigate_to_menu("options")
    
    def _handle_history(self) -> None:
        """Handle download history."""
        self._navigate_to_menu("history")
    
    def _handle_help(self) -> None:
        """Handle help and info."""
        self._navigate_to_menu("help")
    
    def _handle_quit(self) -> None:
        """Handle application quit."""
        if self.settings.ui.confirm_before_quit:
            # Check if there are active downloads
            queue_status = self.batch_processor.get_queue_status()
            has_active_downloads = queue_status['status'] in ['running', 'paused']
            
            if has_active_downloads:
                self.renderer.show_warning("""
                [bold]  Warning: Active Downloads[/bold]
                
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
        """Show quick download menu - simple URL input and immediate best quality download."""
        while self.current_menu == "quick_download":
            try:
                # Clear screen and show header
                if self.settings.ui.clear_screen:
                    self.renderer.clear_screen()
                
                # Show simple Quick Download header
                self._show_quick_download_header()
                
                # Get URL input - simple and direct
                url = self._get_quick_url_input()
                if not url:
                    self._go_back()
                    return
                
                # Immediate download with best quality (no format selection)
                if self._quick_download_execute(url):
                    # Success - ask if user wants to download another
                    if not self._ask_download_another():
                        self.current_menu = "main"
                        return
                else:
                    # Failed - try again or go back
                    if not self.renderer.show_confirmation("Try another URL?", default=True):
                        self._go_back()
                        return
                
            except KeyboardInterrupt:
                self.renderer.show_warning("\nOperation cancelled by user")
                self._go_back()
                return
            except Exception as e:
                self.renderer.show_error(f"Unexpected error: {str(e)}")
                if self.verbose:
                    self.console.print_exception()
                self.renderer.show_pause()
                continue
    
    def _show_quick_download_header(self) -> None:
        """Show the Quick Download menu header."""
        header_content = """
[bold blue]Quick Download[/bold blue]

Enter a video URL to download immediately in best quality.

[dim]• Automatically selects best available quality
• Downloads to: {download_path}
• Supported sites: YouTube, Vimeo, Dailymotion, and 1000+ others[/dim]
        """.format(download_path=self.file_manager.get_day_folder())
        
        panel = Panel(
            header_content,
            title="[bold blue] Quick Download[/bold blue]",
            border_style=self.renderer.theme['border_style'],
            box=self.renderer._get_box_style()
        )
        
        self.console.print(panel)
        self.console.print()
    
    def _get_quick_url_input(self) -> Optional[str]:
        """Get URL input for quick download - simple and direct."""
        while True:
            try:
                # Simple URL input prompt
                url = self.renderer.show_input_prompt(
                    "Enter video URL",
                    required=True
                )
                
                if not url:
                    return None
                
                # Validate the URL
                if self.input_handler.validate_url(url):
                    return url.strip()
                else:
                    self.renderer.show_error(
                        "Invalid URL format. Please check and try again.",
                        "Example: https://youtube.com/watch?v=..."
                    )
                    if not self.renderer.show_confirmation("Try again?", default=True):
                        return None
                
            except KeyboardInterrupt:
                return None
    
    def _quick_download_execute(self, url: str) -> bool:
        """Execute quick download with best quality - no user choices needed."""
        try:
            # Show that we're fetching info
            self.renderer.show_info(" Analyzing video...")
            
            # Get video info quickly
            video_info = self.downloader.get_video_info(url)
            
            # Show brief video info
            title = video_info.get('title', 'Unknown')[:60]
            uploader = video_info.get('uploader', 'Unknown')
            duration = video_info.get('duration', 0)
            
            # Format duration
            if duration:
                hours = duration // 3600
                minutes = (duration % 3600) // 60
                seconds = duration % 60
                if hours > 0:
                    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    duration_str = f"{minutes:02d}:{seconds:02d}"
            else:
                duration_str = "Unknown"
            
            # Quick preview
            preview = f"""
[bold green] Video Found[/bold green]

[bold]Title:[/bold] {title}
[bold]Channel:[/bold] {uploader}
[bold]Duration:[/bold] {duration_str}
[bold]Quality:[/bold] Best available
            """
            
            self.renderer.show_info(preview)
            
            # Immediate download confirmation
            if not self.renderer.show_download_confirmation(
                "Start download?", 
                self.settings.ui.auto_download
            ):
                return False
            
            # Execute download with best quality
            self.renderer.show_info(" Starting download...")
            
            # Use best quality format
            options = {'format': 'best'}
            result = self.downloader.download_single(url, options)
            
            if result.get('status') == 'completed':
                filename = result.get('filename', 'Unknown')
                file_size = result.get('filesize', 0)
                
                # Show success
                success_msg = f"""
 Download completed!

[bold]File:[/bold] {filename}
[bold]Size:[/bold] {file_size // (1024*1024) if file_size else 'Unknown'} MB
[bold]Location:[/bold] {self.file_manager.get_day_folder()}
                """
                
                self.renderer.show_success(success_msg)
                
                # Add to history
                self.history_manager.add_download(url, video_info, result)
                
                self.renderer.show_pause()
                return True
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                self.renderer.show_error(f"Download failed: {error_msg}")
                return False
                
        except Exception as e:
            from ..exceptions.download_errors import (
                NetworkError, URLValidationError, UnavailableContentError,
                PrivateContentError, GeoRestrictionError, AuthenticationError
            )
            
            # Handle specific error types with helpful messages
            if "private" in str(e).lower():
                self.renderer.show_error(
                    "Video is private or unavailable",
                    "Please check if the video is public and the URL is correct."
                )
            elif "geo" in str(e).lower() or "location" in str(e).lower():
                self.renderer.show_error(
                    "Video not available in your region",
                    "This video may be geo-restricted."
                )
            elif "age" in str(e).lower():
                self.renderer.show_error(
                    "Age-restricted content",
                    "This video requires age verification."
                )
            elif "network" in str(e).lower() or "connection" in str(e).lower():
                self.renderer.show_error(
                    "Network error",
                    "Please check your internet connection and try again."
                )
            else:
                self.renderer.show_error(
                    f"Download failed: {str(e)}",
                    "Please verify the URL is correct and try again."
                )
            
            self.renderer.show_pause()
            return False
    
    # Removed _fetch_video_info - now handled directly in _quick_download_execute for simplicity
    
    # Removed _show_video_preview_and_confirm - Quick Download shows minimal info only
    
    def _show_format_selection_workflow(self, url: str) -> Optional[str]:
        """Complete format selection workflow with detailed options."""
        while True:
            try:
                # Get available formats
                formats_info = self._get_format_information(url)
                if not formats_info:
                    return None
                
                # Show format selection menu
                choice = self._show_format_selection_menu(formats_info)
                
                if choice == "back":
                    return "back"
                elif choice == "detailed":
                    # Show detailed format list
                    detailed_choice = self._show_detailed_formats(url)
                    if detailed_choice and detailed_choice != "back":
                        return detailed_choice
                    continue  # Back to format menu
                elif choice:
                    return choice
                else:
                    return None  # Use default
                
            except Exception as e:
                self.renderer.show_error(f"Format selection failed: {str(e)}")
                if not self.renderer.show_confirmation("Try again?", default=True):
                    return None
    
    def _get_format_information(self, url: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive format information for the video."""
        try:
            with self.renderer.show_progress("Analyzing available formats...") as progress:
                task = progress.add_task("Loading formats...", total=100)
                
                # Get best formats
                progress.update(task, advance=30)
                best_formats = self.downloader.get_best_formats(url)
                
                # Get all formats for detailed view
                progress.update(task, advance=60)
                all_formats = self.downloader.list_formats(url)
                
                progress.update(task, completed=100)
                
                return {
                    'best_formats': best_formats,
                    'all_formats': all_formats
                }
                
        except Exception as e:
            self.renderer.show_error(f"Failed to analyze formats: {str(e)}")
            return None
    
    def _show_format_selection_menu(self, formats_info: Dict[str, Any]) -> Optional[str]:
        """Show the main format selection menu."""
        best_formats = formats_info.get('best_formats', {})
        
        # Create format options with quality indicators
        content = """
[bold blue] Quality Selection[/bold blue]

Choose your preferred video quality and format:
        """
        
        panel = Panel(
            content,
            title="[bold blue] Format Selection[/bold blue]",
            border_style="blue",
            box=self.renderer._get_box_style()
        )
        
        self.console.print(panel)
        
        # Build options based on available formats
        options = {}
        
        # Best quality option
        if best_formats.get('best'):
            best_info = best_formats['best']
            resolution = best_info.get('resolution', 'Unknown')
            filesize = best_info.get('filesize', 0)
            size_str = f" (~{filesize // (1024*1024)} MB)" if filesize else ""
            options["1"] = (f" Best Quality - {resolution}{size_str} (Recommended)", 
                           lambda: best_info.get('format_id', 'best'))
        
        # HD options
        if best_formats.get('1080p'):
            hd1080_info = best_formats['1080p']
            filesize = hd1080_info.get('filesize', 0)
            size_str = f" (~{filesize // (1024*1024)} MB)" if filesize else ""
            options["2"] = (f" 1080p Full HD{size_str}", 
                           lambda: hd1080_info.get('format_id', 'best[height<=1080]'))
        
        if best_formats.get('720p'):
            hd720_info = best_formats['720p']
            filesize = hd720_info.get('filesize', 0)
            size_str = f" (~{filesize // (1024*1024)} MB)" if filesize else ""
            options["3"] = (f" 720p HD{size_str}", 
                           lambda: hd720_info.get('format_id', 'best[height<=720]'))
        
        # Audio only option
        if best_formats.get('audio_only'):
            audio_info = best_formats['audio_only']
            bitrate = audio_info.get('abr', 'Unknown')
            filesize = audio_info.get('filesize', 0)
            size_str = f" (~{filesize // (1024*1024)} MB)" if filesize else ""
            options["4"] = (f" Audio Only - {bitrate}kbps{size_str}", 
                           lambda: audio_info.get('format_id', 'bestaudio'))
        
        # Lower quality option
        if best_formats.get('worst'):
            worst_info = best_formats['worst']
            resolution = worst_info.get('resolution', 'Unknown')
            filesize = worst_info.get('filesize', 0)
            size_str = f" (~{filesize // (1024*1024)} MB)" if filesize else ""
            options["5"] = (f" Lowest Quality - {resolution}{size_str} (Fastest)", 
                           lambda: worst_info.get('format_id', 'worst'))
        
        # Additional options
        options["6"] = (" Show All Available Formats", lambda: "detailed")
        options["7"] = (" Use Default Settings", lambda: None)
        options["0"] = ("← Back to URL Input", lambda: "back")
        
        choice = self.renderer.show_menu(
            "Select Video Quality", 
            options, 
            back_option=False,
            show_shortcuts=False
        )
        
        if choice in options:
            return options[choice][1]()
        
        return None
    
    def _show_detailed_formats(self, url: str) -> Optional[str]:
        """Show detailed format list with all available options."""
        try:
            # Get formatted formats
            formatted_formats = self.downloader.get_formatted_formats(url)
            
            if not formatted_formats:
                self.renderer.show_warning("No detailed formats available")
                return "back"
            
            # Create table of formats
            table = Table(title="Available Formats", border_style="blue")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Format", style="green")
            table.add_column("Resolution", style="yellow")
            table.add_column("Size", style="magenta")
            table.add_column("Codec", style="blue")
            
            # Limit to first 20 formats to avoid overwhelming
            display_formats = formatted_formats[:20]
            
            for fmt in display_formats:
                table.add_row(
                    str(fmt.get('format_id', 'N/A')),
                    fmt.get('format_note', 'N/A'),
                    fmt.get('resolution', 'N/A'),
                    fmt.get('filesize_str', 'N/A'),
                    fmt.get('vcodec', 'N/A')
                )
            
            self.console.print(table)
            self.console.print()
            
            if len(formatted_formats) > 20:
                self.renderer.show_info(f"Showing first 20 of {len(formatted_formats)} available formats")
            
            # Allow user to select a specific format ID
            format_id = self.renderer.show_input_prompt(
                "Enter format ID (or press Enter to go back)",
                required=False
            )
            
            if format_id and format_id.strip():
                # Validate the format ID
                valid_ids = [str(fmt.get('format_id', '')) for fmt in formatted_formats]
                if format_id.strip() in valid_ids:
                    return format_id.strip()
                else:
                    self.renderer.show_error(f"Invalid format ID: {format_id}")
                    self.renderer.show_pause()
            
            return "back"
            
        except Exception as e:
            self.renderer.show_error(f"Failed to show detailed formats: {str(e)}")
            return "back"
    
    def _confirm_and_download(self, url: str, video_info: Dict[str, Any], format_choice: Optional[str]) -> bool:
        """Final confirmation and download execution."""
        try:
            # Show download summary
            self._show_download_summary(video_info, format_choice)
            
            # Final confirmation
            if not self.renderer.show_download_confirmation(
                "Start download?", 
                self.settings.ui.auto_download
            ):
                return False
            
            # Execute download
            return self._execute_download(url, video_info, format_choice)
            
        except Exception as e:
            self.renderer.show_error(f"Download preparation failed: {str(e)}")
            return False
    
    def _show_download_summary(self, video_info: Dict[str, Any], format_choice: Optional[str]) -> None:
        """Show a summary of what will be downloaded."""
        title = video_info.get('title', 'Unknown')[:50]
        uploader = video_info.get('uploader', 'Unknown')
        
        # Format choice description
        if format_choice:
            if format_choice == 'best':
                format_desc = "Best available quality"
            elif format_choice == 'bestaudio':
                format_desc = "Audio only"
            elif 'height' in format_choice:
                if '720' in format_choice:
                    format_desc = "720p HD"
                elif '1080' in format_choice:
                    format_desc = "1080p Full HD"
                else:
                    format_desc = f"Custom ({format_choice})"
            else:
                format_desc = f"Format ID: {format_choice}"
        else:
            format_desc = "Default settings"
        
        # Download path
        download_path = self.file_manager.get_day_folder()
        
        summary_content = f"""
[bold green] Download Summary[/bold green]

[bold]Video:[/bold] {title}
[bold]Channel:[/bold] {uploader}
[bold]Quality:[/bold] {format_desc}
[bold]Save to:[/bold] {download_path}

[dim]Press Enter to start download, or 'n' to cancel[/dim]
        """
        
        panel = Panel(
            summary_content,
            title="[bold green] Ready to Download[/bold green]",
            border_style="green",
            box=self.renderer._get_box_style()
        )
        
        self.console.print(panel)
    
    def _execute_download(self, url: str, video_info: Dict[str, Any], format_choice: Optional[str]) -> bool:
        """Execute the download with progress tracking."""
        try:
            # Prepare download options
            options = {}
            if format_choice:
                options['format'] = format_choice
            
            # Start download with progress tracking
            self.renderer.show_info(" Starting download...")
            
            # Create a more detailed progress display
            title = video_info.get('title', 'Unknown')
            
            result = self.downloader.download_single(url, options)
            
            if result.get('status') == 'completed':
                filename = result.get('filename', 'Unknown')
                file_size = result.get('filesize', 0)
                
                # Show success message
                success_msg = f"""
 Download completed successfully!

File: {filename}
Size: {file_size // (1024*1024) if file_size else 'Unknown'} MB
Location: {self.file_manager.get_day_folder()}
                """
                
                self.renderer.show_success(success_msg)
                
                # Add to history
                self.history_manager.add_download(url, video_info, result)
                
                self.renderer.show_pause()
                return True
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                self.renderer.show_error(f"Download failed: {error_msg}")
                self.renderer.show_pause()
                return False
                
        except KeyboardInterrupt:
            self.renderer.show_warning("\nDownload cancelled by user")
            return False
        except Exception as e:
            self.renderer.show_error(f"Download failed: {str(e)}")
            if self.verbose:
                self.console.print_exception()
            self.renderer.show_pause()
            return False
    
    def _ask_download_another(self) -> bool:
        """Ask if user wants to download another video."""
        return self.renderer.show_confirmation(
            "Download another video?",
            default=False
        )
    
    # This method has been replaced by _execute_download and related methods above
    
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
        [bold]  Warning: Resume All Downloads[/bold]
        
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
        [bold]  Warning: Clean Up Partial Files[/bold]
        
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
                [bold]  Warning: Remove Duplicates[/bold]
                
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
            [bold]  Warning: Remove Old Files[/bold]
            
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
        """Show enhanced batch download menu with complete workflow."""
        while self.current_menu == "batch_download":
            try:
                # Clear screen and show header
                if self.settings.ui.clear_screen:
                    self.renderer.clear_screen()
                
                # Show Batch Download header
                self._show_batch_download_header()
                
                # Show main batch options
                choice = self._show_batch_main_options()
                
                if choice == "direct_urls":
                    self._handle_enhanced_direct_urls()
                elif choice == "file_loading":
                    self._handle_enhanced_file_loading()
                elif choice == "queue_management":
                    self._handle_enhanced_queue_management()
                elif choice == "audio_batch":
                    self._handle_enhanced_audio_batch()
                elif choice == "templates":
                    self._handle_batch_templates()
                elif choice == "back":
                    self._go_back()
                    return
                
            except KeyboardInterrupt:
                self.renderer.show_warning("\nOperation cancelled by user")
                self._go_back()
                return
            except Exception as e:
                self.renderer.show_error(f"Unexpected error: {str(e)}")
                if self.verbose:
                    self.console.print_exception()
                self.renderer.show_pause()
                continue
    
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
        [bold]  Warning: Stop Queue Processing[/bold]
        
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
        [bold]  Warning: Clear Download Queue[/bold]
        
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
    
    def _show_batch_download_header(self) -> None:
        """Show the Batch Download menu header."""
        header_content = """
[bold blue]Batch Download[/bold blue]

Download multiple videos with advanced queue management and processing options.

[dim]• Support for multiple input methods
• Concurrent download processing
• Progress tracking and pause/resume
• Audio-only batch processing
• Template creation and management[/dim]
        """
        
        panel = Panel(
            header_content,
            title="[bold blue] Batch Download[/bold blue]",
            border_style=self.renderer.theme['border_style'],
            box=self.renderer._get_box_style()
        )
        
        self.console.print(panel)
        self.console.print()
    
    def _show_batch_main_options(self) -> str:
        """Show main batch download options and return user choice."""
        options = {
            "1": (" Direct URL Input", lambda: "direct_urls"),
            "2": (" Load from File", lambda: "file_loading"),
            "3": (" Audio-Only Batch", lambda: "audio_batch"),
            "4": (" Queue Management", lambda: "queue_management"),
            "5": (" Templates & Tools", lambda: "templates"),
            "0": ("← Back to Main Menu", lambda: "back")
        }
        
        choice = self.renderer.show_menu(
            "Choose Batch Download Method", 
            options, 
            back_option=False,
            show_shortcuts=False
        )
        
        if choice in options:
            return options[choice][1]()
        
        return "back"
    
    def _handle_enhanced_direct_urls(self) -> None:
        """Handle enhanced direct URL input with multiple methods."""
        while True:
            try:
                # Show URL input options
                input_options = {
                    "1": (" Manual Entry", self._manual_batch_url_input),
                    "2": (" Paste from Clipboard", self._clipboard_batch_url_input),
                    "3": (" Select from Recent", self._recent_batch_url_input),
                    "4": (" Load from Text", self._text_batch_url_input),
                    "0": ("← Back to Batch Menu", lambda: None)
                }
                
                choice = self.renderer.show_menu(
                    "How would you like to provide URLs?", 
                    input_options, 
                    back_option=False,
                    show_shortcuts=False
                )
                
                if choice == "0":
                    break
                
                if choice in input_options:
                    urls = input_options[choice][1]()
                    if urls:
                        # Show URL summary and get format choice
                        if self._show_batch_url_summary(urls):
                            format_choice = self._get_batch_format_choice()
                            if self._confirm_batch_download(urls, format_choice):
                                self._execute_batch_download(urls, format_choice)
                                break
                        else:
                            continue  # User wants to try different input method
                    else:
                        continue  # No URLs provided, try again
                
            except KeyboardInterrupt:
                break
    
    def _handle_enhanced_file_loading(self) -> None:
        """Handle enhanced file loading for batch download."""
        while True:
            try:
                # Show file loading options
                file_options = {
                    "1": (" Browse for File", self._handle_browse_file),
                    "2": (" Enter File Path", self._handle_enter_file_path),
                    "3": (" Recent Files", self._handle_recent_files),
                    "4": (" Batch Templates", self._handle_batch_templates),
                    "0": ("← Back to Batch Menu", lambda: None)
                }
                
                choice = self.renderer.show_menu(
                    "How would you like to load URLs?", 
                    file_options, 
                    back_option=False,
                    show_shortcuts=False
                )
                
                if choice == "0":
                    break
                
                if choice in file_options:
                    urls = file_options[choice][1]()
                    if urls:
                        # Show URL summary and get format choice
                        if self._show_batch_url_summary(urls):
                            format_choice = self._get_batch_format_choice()
                            if self._confirm_batch_download(urls, format_choice):
                                self._execute_batch_download(urls, format_choice)
                                break
                        else:
                            continue  # User wants to try different method
                    else:
                        continue  # No URLs loaded, try again
                
            except KeyboardInterrupt:
                break
    
    def _handle_enhanced_queue_management(self) -> None:
        """Handle enhanced queue management with advanced features."""
        while True:
            try:
                status = self.batch_processor.get_queue_status()
                
                # Show enhanced status with more details
                status_info = f"""
                [bold]Queue Status: {status['status'].upper()}[/bold]
                
                 Queue Statistics:
                • Total URLs: {status['total_urls']}
                • Completed: {status['completed']}
                • Failed: {status['failed']}
                • Remaining: {status['remaining']}
                • Success Rate: {((status['completed']/(status['completed']+status['failed'])*100) if status['completed']+status['failed'] > 0 else 0.0):.1f}%
                """
                self.renderer.show_info(status_info)
                
                # Build enhanced options based on current status
                options = {}
                
                if status['status'] == 'idle':
                    options.update({
                        "1": (" Add URLs to Queue", self._add_urls_to_queue),
                        "2": (" Load URLs from File", self._load_urls_to_queue),
                        "3": (" Import from Clipboard", self._import_urls_from_clipboard),
                        "4": (" Load from Templates", self._load_urls_from_templates),
                    })
                elif status['status'] == 'running':
                    options.update({
                        "1": ("⏸ Pause Processing", self._pause_queue),
                        "2": ("⏹ Stop Processing", self._stop_queue),
                        "3": (" Show Progress", self._show_queue_progress),
                        "4": (" View Queue Contents", self._view_queue_contents),
                        "5": (" Performance Monitor", self._show_performance_monitor),
                    })
                elif status['status'] == 'paused':
                    options.update({
                        "1": (" Resume Processing", self._resume_queue),
                        "2": ("⏹ Stop Processing", self._stop_queue),
                        "3": (" Show Progress", self._show_queue_progress),
                        "4": (" View Queue Contents", self._view_queue_contents),
                        "5": (" Modify Queue", self._modify_queue),
                    })
                elif status['status'] == 'completed':
                    options.update({
                        "1": (" View Results", self._view_queue_results),
                        "2": (" Retry Failed Downloads", self._retry_failed_downloads),
                        "3": (" Export Results", self._export_queue_results),
                        "4": (" Generate Report", self._generate_queue_report),
                        "5": (" Clear Queue", self._clear_queue),
                    })
                
                # Common options
                options.update({
                    "6": (" Queue Analytics", self._show_queue_analytics),
                    "7": (" Queue Settings", self._handle_queue_settings),
                    "0": ("← Back to Batch Menu", lambda: None),
                })
                
                choice = self.renderer.show_menu("Enhanced Queue Management", options, back_option=False)
                
                if choice == "0":
                    break
                elif choice in options:
                    result = options[choice][1]()
                    if result is False:  # Return to batch menu
                        break
                else:
                    break
                    
            except KeyboardInterrupt:
                break
    
    def _handle_enhanced_audio_batch(self) -> None:
        """Handle enhanced audio-only batch processing."""
        while True:
            try:
                self.renderer.show_info("Enhanced Audio-Only Batch Processing")
                self.renderer.show_info("This feature allows you to download audio from multiple videos efficiently.")
                
                options = {
                    "1": (" Add Audio URLs", self._add_audio_urls_to_batch),
                    "2": (" Load Audio URLs from File", self._load_audio_urls_from_file),
                    "3": (" Audio Format Settings", self._handle_audio_batch_format_settings),
                    "4": (" Audio Quality Settings", self._handle_audio_batch_quality_settings),
                    "5": (" Audio Batch Statistics", self._show_audio_batch_statistics),
                    "0": ("← Back to Batch Menu", lambda: None),
                }
                
                choice = self.renderer.show_menu("Enhanced Audio Batch Processing", options, back_option=False)
                
                if choice == "0":
                    break
                elif choice in options:
                    options[choice][1]()
                
            except KeyboardInterrupt:
                break
    
    def _import_urls_from_clipboard(self) -> None:
        """Import URLs from clipboard."""
        try:
            import pyperclip
            clipboard_content = pyperclip.paste()
            
            if not clipboard_content:
                self.renderer.show_warning("Clipboard is empty")
                return
            
            # Parse URLs from clipboard content
            urls = []
            for line in clipboard_content.split('\n'):
                line = line.strip()
                if line and self.input_handler.validate_url(line):
                    urls.append(line)
            
            if urls:
                self.renderer.show_success(f"Imported {len(urls)} URLs from clipboard")
                if self._show_batch_url_summary(urls):
                    format_choice = self._get_batch_format_choice()
                    if self._confirm_batch_download(urls, format_choice):
                        self._execute_batch_download(urls, format_choice)
            else:
                self.renderer.show_warning("No valid URLs found in clipboard")
                
        except ImportError:
            self.renderer.show_error("pyperclip not installed. Install with: pip install pyperclip")
        except Exception as e:
            self.renderer.show_error(f"Failed to import from clipboard: {str(e)}")
    
    def _load_urls_from_templates(self) -> None:
        """Load URLs from batch templates."""
        try:
            # Get available templates
            templates = self._get_available_templates()
            
            if not templates:
                self.renderer.show_info("No templates available")
                return
            
            # Show template selection menu
            options = {}
            for i, template in enumerate(templates, 1):
                template_name = Path(template).stem
                options[str(i)] = (f" {template_name}", template)
            
            options["0"] = ("← Back", None)
            
            choice = self.renderer.show_menu("Select Template", options, back_option=False)
            
            if choice == "0" or choice not in options:
                return
            
            selected_template = options[choice][1]
            urls = self._load_urls_from_file(Path(selected_template))
            
            if urls:
                if self._show_batch_url_summary(urls):
                    format_choice = self._get_batch_format_choice()
                    if self._confirm_batch_download(urls, format_choice):
                        self._execute_batch_download(urls, format_choice)
                        
        except Exception as e:
            self.renderer.show_error(f"Failed to load from templates: {str(e)}")
    
    def _get_available_templates(self) -> List[str]:
        """Get list of available batch templates."""
        try:
            template_dir = Path(self.settings.download.path) / "templates"
            if template_dir.exists():
                return [str(f) for f in template_dir.glob("*.txt")]
            return []
        except Exception:
            return []
    
    def _show_performance_monitor(self) -> None:
        """Show performance monitoring information."""
        try:
            status = self.batch_processor.get_queue_status()
            
            # Get performance metrics
            performance_info = f"""
            [bold]Performance Monitor[/bold]
            
             Queue Performance:
            • Processing Speed: {status.get('speed', 'N/A')} downloads/min
            • Memory Usage: {status.get('memory_usage', 'N/A')} MB
            • CPU Usage: {status.get('cpu_usage', 'N/A')}%
            • Network Speed: {status.get('network_speed', 'N/A')} MB/s
            
            ⏱ Time Estimates:
            • Estimated Time Remaining: {status.get('eta', 'N/A')}
            • Average Time per Download: {status.get('avg_time', 'N/A')} seconds
            """
            
            self.renderer.show_info(performance_info)
            self.renderer.show_pause()
            
        except Exception as e:
            self.renderer.show_error(f"Failed to show performance monitor: {str(e)}")
    
    def _modify_queue(self) -> None:
        """Modify the current queue."""
        try:
            options = {
                "1": (" Reorder Queue", self._reorder_queue),
                "2": (" Remove Items", self._remove_queue_items),
                "3": (" Add More URLs", self._add_urls_to_queue),
                "4": (" Retry Failed", self._retry_failed_downloads),
                "0": ("← Back", lambda: None),
            }
            
            choice = self.renderer.show_menu("Modify Queue", options, back_option=False)
            
            if choice == "0":
                return
            elif choice in options:
                options[choice][1]()
                
        except Exception as e:
            self.renderer.show_error(f"Failed to modify queue: {str(e)}")
    
    def _export_queue_results(self) -> None:
        """Export queue results."""
        try:
            results = self.batch_processor.get_queue_results()
            
            if not results:
                self.renderer.show_info("No results to export")
                return
            
            export_options = {
                "1": (" Export as CSV", lambda: self._export_results_csv(results)),
                "2": (" Export as JSON", lambda: self._export_results_json(results)),
                "3": (" Export as Text", lambda: self._export_results_text(results)),
                "0": ("← Back", lambda: None),
            }
            
            choice = self.renderer.show_menu("Export Queue Results", export_options, back_option=False)
            
            if choice == "0":
                return
            elif choice in export_options:
                export_options[choice][1]()
                
        except Exception as e:
            self.renderer.show_error(f"Failed to export results: {str(e)}")
    
    def _generate_queue_report(self) -> None:
        """Generate a detailed queue report."""
        try:
            report = self.batch_processor.generate_report()
            
            if report:
                self.renderer.show_info("Queue Report Generated:")
                self.renderer.show_info(report)
                
                # Offer to save report
                if self.renderer.show_confirmation("Save report to file?", default=False):
                    report_path = self.batch_processor.save_report(report)
                    self.renderer.show_success(f"Report saved to: {report_path}")
            else:
                self.renderer.show_info("No report data available")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to generate report: {str(e)}")
    
    def _show_queue_analytics(self) -> None:
        """Show queue analytics and statistics."""
        try:
            analytics = self.batch_processor.get_analytics()
            
            if analytics:
                analytics_info = f"""
                [bold]Queue Analytics[/bold]
                
                 Performance Metrics:
                • Total Downloads: {analytics.get('total_downloads', 0)}
                • Success Rate: {analytics.get('success_rate', 0):.1f}%
                • Average Download Time: {analytics.get('avg_download_time', 0):.1f} seconds
                • Total Data Downloaded: {analytics.get('total_data_mb', 0):.1f} MB
                
                 Quality Metrics:
                • Average Video Quality: {analytics.get('avg_quality', 'N/A')}
                • Most Common Format: {analytics.get('most_common_format', 'N/A')}
                • Failed Download Reasons: {analytics.get('failure_reasons', 'N/A')}
                """
                
                self.renderer.show_info(analytics_info)
                self.renderer.show_pause()
            else:
                self.renderer.show_info("No analytics data available")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to show analytics: {str(e)}")
    
    def _handle_queue_settings(self) -> None:
        """Handle queue settings configuration."""
        try:
            while True:
                self.renderer.show_info(f"Current queue settings:")
                self.renderer.show_info(f"  • Max Concurrent: {self.settings.download.max_concurrent}")
                self.renderer.show_info(f"  • Retry Attempts: {self.settings.download.retries}")
                self.renderer.show_info(f"  • Timeout: {self.settings.download.timeout} seconds")
                
                options = {
                    "1": (" Concurrent Downloads", self._set_concurrent_limit),
                    "2": (" Retry Settings", self._handle_retry_settings),
                    "3": ("⏱ Timeout Settings", self._handle_timeout_settings),
                    "4": (" Memory Settings", self._handle_memory_settings),
                    "0": ("← Back", lambda: None),
                }
                
                choice = self.renderer.show_menu("Queue Settings", options, back_option=False)
                
                if choice == "0":
                    break
                elif choice in options:
                    options[choice][1]()
                
        except Exception as e:
            self.renderer.show_error(f"Failed to configure queue settings: {str(e)}")
    
    def _add_audio_urls_to_batch(self) -> None:
        """Add audio URLs to batch processing."""
        try:
            self.renderer.show_info("Enter audio URLs (one per line, press Enter twice when done):")
            
            urls = []
            while True:
                url = self.renderer.show_input_prompt(
                    f"Audio URL {len(urls) + 1} (or press Enter to finish)",
                    required=False
                )
                
                if not url:
                    break
                
                if self.input_handler.validate_url(url):
                    urls.append(url.strip())
                    self.renderer.show_success(f" Added: {url[:50]}...")
                else:
                    self.renderer.show_warning("Invalid URL, skipping...")
            
            if urls:
                if self._show_batch_url_summary(urls):
                    # Get audio format choice
                    audio_format = self._get_audio_batch_format()
                    if self._confirm_audio_batch_download(urls, audio_format):
                        self._execute_audio_batch_download(urls, audio_format)
            else:
                self.renderer.show_info("No URLs provided")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to add audio URLs: {str(e)}")
    
    def _load_audio_urls_from_file(self) -> None:
        """Load audio URLs from file."""
        try:
            file_path = self.renderer.show_input_prompt("Enter path to file containing audio URLs")
            
            if not file_path:
                return
            
            path_obj = Path(file_path).expanduser()
            if not path_obj.exists():
                self.renderer.show_error(f"File not found: {path_obj}")
                return
            
            urls = self._load_urls_from_file(path_obj)
            
            if urls:
                if self._show_batch_url_summary(urls):
                    audio_format = self._get_audio_batch_format()
                    if self._confirm_audio_batch_download(urls, audio_format):
                        self._execute_audio_batch_download(urls, audio_format)
                        
        except Exception as e:
            self.renderer.show_error(f"Failed to load audio URLs: {str(e)}")
    
    def _handle_audio_batch_format_settings(self) -> None:
        """Handle audio batch format settings."""
        try:
            self.renderer.show_info("Audio Batch Format Settings")
            self.renderer.show_info("Configure default audio format for batch processing")
            
            format_options = {
                "1": (" M4A (AAC)", "m4a"),
                "2": (" MP3", "mp3"),
                "3": (" OPUS", "opus"),
                "4": (" AAC", "aac"),
                "5": (" FLAC", "flac"),
                "0": ("← Back", lambda: None),
            }
            
            choice = self.renderer.show_menu("Select Audio Format", format_options, back_option=False)
            
            if choice == "0":
                return
            elif choice in format_options:
                selected_format = format_options[choice][1]
                self.settings.download.default_audio_format = selected_format
                self.config_manager.save_config()
                self.renderer.show_success(f"Default audio format set to: {selected_format}")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to set audio format: {str(e)}")
    
    def _handle_audio_batch_quality_settings(self) -> None:
        """Handle audio batch quality settings."""
        try:
            self.renderer.show_info("Audio Batch Quality Settings")
            self.renderer.show_info("Configure audio quality for batch processing")
            
            quality_options = {
                "1": (" Best Quality", "best"),
                "2": (" High Quality (192k)", "192"),
                "3": (" Medium Quality (128k)", "128"),
                "4": (" Low Quality (64k)", "64"),
                "0": ("← Back", lambda: None),
            }
            
            choice = self.renderer.show_menu("Select Audio Quality", quality_options, back_option=False)
            
            if choice == "0":
                return
            elif choice in quality_options:
                selected_quality = quality_options[choice][1]
                self.settings.download.default_audio_quality = selected_quality
                self.config_manager.save_config()
                self.renderer.show_success(f"Default audio quality set to: {selected_quality}")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to set audio quality: {str(e)}")
    
    def _show_audio_batch_statistics(self) -> None:
        """Show audio batch statistics."""
        try:
            stats = self.batch_processor.get_audio_batch_statistics()
            
            if stats:
                stats_info = f"""
                [bold]Audio Batch Statistics[/bold]
                
                 Processing Stats:
                • Total Audio Files: {stats.get('total_audio', 0)}
                • Successfully Processed: {stats.get('successful', 0)}
                • Failed: {stats.get('failed', 0)}
                • Success Rate: {stats.get('success_rate', 0):.1f}%
                
                 Format Distribution:
                • M4A: {stats.get('m4a_count', 0)}
                • MP3: {stats.get('mp3_count', 0)}
                • OPUS: {stats.get('opus_count', 0)}
                • FLAC: {stats.get('flac_count', 0)}
                
                 Total Size: {stats.get('total_size_mb', 0):.1f} MB
                """
                
                self.renderer.show_info(stats_info)
                self.renderer.show_pause()
            else:
                self.renderer.show_info("No audio batch statistics available")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to show audio statistics: {str(e)}")
    
    def _get_audio_batch_format(self) -> str:
        """Get audio format for batch processing."""
        try:
            format_options = {
                "1": (" M4A (AAC)", "m4a"),
                "2": (" MP3", "mp3"),
                "3": (" OPUS", "opus"),
                "4": (" AAC", "aac"),
                "5": (" FLAC", "flac"),
            }
            
            choice = self.renderer.show_menu("Select Audio Format for Batch", format_options, back_option=False)
            
            if choice in format_options:
                return format_options[choice][1]
            else:
                return "m4a"  # Default
                
        except Exception as e:
            self.renderer.show_error(f"Failed to get audio format: {str(e)}")
            return "m4a"
    
    def _confirm_audio_batch_download(self, urls: List[str], audio_format: str) -> bool:
        """Confirm audio batch download."""
        try:
            summary = f"""
            [bold]Audio Batch Download Summary[/bold]
            
             URLs to Process: {len(urls)}
             Audio Format: {audio_format.upper()}
             Download Path: {self.settings.download.path}
            
            Ready to start audio batch download?
            """
            
            self.renderer.show_info(summary)
            return self.renderer.show_confirmation("Start audio batch download?", default=True)
            
        except Exception as e:
            self.renderer.show_error(f"Failed to confirm audio batch download: {str(e)}")
            return False
    
    def _execute_audio_batch_download(self, urls: List[str], audio_format: str) -> None:
        """Execute audio batch download."""
        try:
            self.renderer.show_info(f"Starting audio batch download of {len(urls)} files...")
            
            # Use batch processor for audio downloads
            results = self.batch_processor.process_audio_batch(urls, audio_format)
            
            # Show results
            successful = len([r for r in results if r.get('status') == 'completed'])
            failed = len([r for r in results if r.get('status') == 'failed'])
            
            self.renderer.show_success(f"Audio batch download completed: {successful} successful, {failed} failed")
            
            # Show detailed results if requested
            if self.renderer.show_confirmation("Show detailed results?", default=False):
                self._show_batch_results(results, "Audio Batch Results")
                
        except Exception as e:
            self.renderer.show_error(f"Audio batch download failed: {str(e)}")
    
    def _reorder_queue(self) -> None:
        """Reorder items in the queue."""
        try:
            self.renderer.show_info("Queue reordering not yet implemented")
            # This would allow users to change the order of downloads in the queue
        except Exception as e:
            self.renderer.show_error(f"Failed to reorder queue: {str(e)}")
    
    def _remove_queue_items(self) -> None:
        """Remove items from the queue."""
        try:
            self.renderer.show_info("Queue item removal not yet implemented")
            # This would allow users to remove specific items from the queue
        except Exception as e:
            self.renderer.show_error(f"Failed to remove queue items: {str(e)}")
    
    def _handle_retry_settings(self) -> None:
        """Handle retry settings."""
        try:
            current_retries = self.settings.download.retries
            new_retries = self.renderer.show_input_prompt(
                f"Enter number of retry attempts (current: {current_retries})",
                default=str(current_retries)
            )
            
            if new_retries and new_retries.isdigit():
                retries = int(new_retries)
                if retries >= 0:
                    self.settings.download.retries = retries
                    self.config_manager.save_config()
                    self.renderer.show_success(f"Retry attempts set to {retries}")
                else:
                    self.renderer.show_error("Retry attempts must be 0 or greater")
            else:
                self.renderer.show_error("Invalid input")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to set retry attempts: {str(e)}")
    
    def _handle_timeout_settings(self) -> None:
        """Handle timeout settings."""
        try:
            current_timeout = getattr(self.settings.download, 'timeout', 30)
            new_timeout = self.renderer.show_input_prompt(
                f"Enter timeout in seconds (current: {current_timeout})",
                default=str(current_timeout)
            )
            
            if new_timeout and new_timeout.isdigit():
                timeout = int(new_timeout)
                if timeout > 0:
                    self.settings.download.timeout = timeout
                    self.config_manager.save_config()
                    self.renderer.show_success(f"Timeout set to {timeout} seconds")
                else:
                    self.renderer.show_error("Timeout must be greater than 0")
            else:
                self.renderer.show_error("Invalid input")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to set timeout: {str(e)}")
    
    def _handle_memory_settings(self) -> None:
        """Handle memory management settings."""
        try:
            self.renderer.show_info("Memory Management Settings")
            self.renderer.show_info("Configure memory usage for batch processing")
            
            options = {
                "1": (" Set Memory Limit", self._set_memory_limit),
                "2": (" Garbage Collection", self._handle_garbage_collection),
                "3": (" Memory Monitoring", self._show_memory_usage),
                "0": ("← Back", lambda: None),
            }
            
            choice = self.renderer.show_menu("Memory Settings", options, back_option=False)
            
            if choice == "0":
                return
            elif choice in options:
                options[choice][1]()
                
        except Exception as e:
            self.renderer.show_error(f"Failed to configure memory settings: {str(e)}")
    
    def _set_memory_limit(self) -> None:
        """Set memory limit for batch processing."""
        try:
            current_limit = getattr(self.settings.download, 'memory_limit_mb', 1024)
            new_limit = self.renderer.show_input_prompt(
                f"Enter memory limit in MB (current: {current_limit})",
                default=str(current_limit)
            )
            
            if new_limit and new_limit.isdigit():
                limit = int(new_limit)
                if limit > 0:
                    self.settings.download.memory_limit_mb = limit
                    self.config_manager.save_config()
                    self.renderer.show_success(f"Memory limit set to {limit} MB")
                else:
                    self.renderer.show_error("Memory limit must be greater than 0")
            else:
                self.renderer.show_error("Invalid input")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to set memory limit: {str(e)}")
    
    def _handle_garbage_collection(self) -> None:
        """Handle garbage collection settings."""
        try:
            self.renderer.show_info("Garbage Collection Settings")
            self.renderer.show_info("Configure automatic memory cleanup")
            
            options = {
                "1": (" Enable Auto GC", lambda: self._set_auto_gc(True)),
                "2": (" Disable Auto GC", lambda: self._set_auto_gc(False)),
                "3": (" Manual GC", self._run_manual_gc),
                "0": ("← Back", lambda: None),
            }
            
            choice = self.renderer.show_menu("Garbage Collection", options, back_option=False)
            
            if choice == "0":
                return
            elif choice in options:
                options[choice][1]()
                
        except Exception as e:
            self.renderer.show_error(f"Failed to configure garbage collection: {str(e)}")
    
    def _set_auto_gc(self, enabled: bool) -> None:
        """Set automatic garbage collection."""
        try:
            self.settings.download.auto_garbage_collection = enabled
            self.config_manager.save_config()
            self.renderer.show_success(f"Auto garbage collection {'enabled' if enabled else 'disabled'}")
        except Exception as e:
            self.renderer.show_error(f"Failed to set auto GC: {str(e)}")
    
    def _run_manual_gc(self) -> None:
        """Run manual garbage collection."""
        try:
            import gc
            gc.collect()
            self.renderer.show_success("Manual garbage collection completed")
        except Exception as e:
            self.renderer.show_error(f"Failed to run garbage collection: {str(e)}")
    
    def _show_memory_usage(self) -> None:
        """Show current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            memory_text = f"""
            [bold]Memory Usage[/bold]
            
             Current Memory: {memory_info.rss / 1024 / 1024:.1f} MB
             Virtual Memory: {memory_info.vms / 1024 / 1024:.1f} MB
             Memory Limit: {getattr(self.settings.download, 'memory_limit_mb', 1024)} MB
            """
            
            self.renderer.show_info(memory_text)
            self.renderer.show_pause()
            
        except ImportError:
            self.renderer.show_error("psutil not installed. Install with: pip install psutil")
        except Exception as e:
            self.renderer.show_error(f"Failed to show memory usage: {str(e)}")
    
    def _export_results_text(self, results: List[Dict[str, Any]]) -> None:
        """Export results as text."""
        try:
            text_path = self.batch_processor.export_results_as_text(results)
            self.renderer.show_success(f"Results exported to text: {text_path}")
        except Exception as e:
            self.renderer.show_error(f"Text export failed: {str(e)}")
    
    def _handle_batch_templates(self) -> None:
        """Handle batch templates and tools."""
        # This will be implemented to replace _handle_create_template
        self._handle_create_template()
    
    def _manual_batch_url_input(self) -> List[str]:
        """Get URLs through manual input for batch download."""
        self.renderer.show_info("Enter URLs one by one (press Enter twice when done):")
        
        urls = []
        while True:
            url = self.renderer.show_input_prompt(
                f"URL {len(urls) + 1} (or press Enter to finish)",
                required=False
            )
            
            if not url:
                break
            
            if self.input_handler.validate_url(url):
                urls.append(url.strip())
                self.renderer.show_success(f" Added: {url[:50]}...")
            else:
                self.renderer.show_error(f" Invalid URL: {url}")
                if not self.renderer.show_confirmation("Continue adding URLs?", default=True):
                    break
        
        return urls
    
    def _clipboard_batch_url_input(self) -> List[str]:
        """Get URLs from clipboard for batch download."""
        try:
            import pyperclip  # type: ignore
            clipboard_content = pyperclip.paste()
            
            if clipboard_content:
                # Parse URLs from clipboard content
                urls = self.input_handler.parse_urls_from_text(clipboard_content)
                
                if urls:
                    self.renderer.show_info(f"Found {len(urls)} URLs in clipboard:")
                    for i, url in enumerate(urls[:5], 1):  # Show first 5
                        self.renderer.show_info(f"  {i}. {url[:60]}...")
                    
                    if len(urls) > 5:
                        self.renderer.show_info(f"  ... and {len(urls) - 5} more")
                    
                    if self.renderer.show_confirmation("Use these URLs?"):
                        return urls
                else:
                    self.renderer.show_warning("No valid URLs found in clipboard")
            else:
                self.renderer.show_warning("Clipboard is empty")
                
        except ImportError:
            self.renderer.show_warning("Clipboard functionality not available (install pyperclip)")
        except Exception as e:
            self.renderer.show_warning(f"Could not access clipboard: {e}")
        
        return []
    
    def _recent_batch_url_input(self) -> List[str]:
        """Select URLs from recent downloads for batch download."""
        try:
            recent_downloads = self.history_manager.get_recent_downloads(limit=20)
            
            if not recent_downloads:
                self.renderer.show_info("No recent downloads found")
                return []
            
            # Create options from recent URLs
            options = {}
            for i, download in enumerate(recent_downloads[:15], 1):
                title = download.get('title', 'Unknown')[:40]
                url = download.get('url', '')
                options[str(i)] = (f"{title}...", lambda u=url: u)
            
            options["0"] = ("← Back", lambda: None)
            
            self.renderer.show_info("Select URLs from recent downloads:")
            choice = self.renderer.show_menu("Recent Downloads", options)
            
            if choice in options and choice != "0":
                selected_url = options[choice][1]()
                return [selected_url] if selected_url else []
            
        except Exception as e:
            self.renderer.show_error(f"Failed to load recent downloads: {e}")
        
        return []
    
    def _text_batch_url_input(self) -> List[str]:
        """Get URLs from text input for batch download."""
        self.renderer.show_info("Paste or type multiple URLs (one per line):")
        
        text_input = self.renderer.show_input_prompt(
            "URLs (press Enter when done)",
            required=False
        )
        
        if text_input:
            urls = self.input_handler.parse_urls_from_text(text_input)
            
            if urls:
                self.renderer.show_success(f"Parsed {len(urls)} URLs from text input")
                return urls
            else:
                self.renderer.show_warning("No valid URLs found in text input")
        
        return []
    
    def _show_batch_url_summary(self, urls: List[str]) -> bool:
        """Show summary of URLs and get user confirmation."""
        if not urls:
            self.renderer.show_warning("No URLs provided")
            return False
        
        # Show URL summary
        summary_content = f"""
[bold green] Batch Download Summary[/bold green]

[bold]Total URLs:[/bold] {len(urls)}
[bold]Estimated Time:[/bold] ~{len(urls) * 2} minutes (varies by video size)
[bold]Download Path:[/bold] {self.file_manager.get_day_folder()}

[bold]URLs:[/bold]
        """
        
        # Show first few URLs
        for i, url in enumerate(urls[:5], 1):
            summary_content += f"  {i}. {url[:60]}...\n"
        
        if len(urls) > 5:
            summary_content += f"  ... and {len(urls) - 5} more\n"
        
        panel = Panel(
            summary_content,
            title="[bold green] URLs Ready[/bold green]",
            border_style="green",
            box=self.renderer._get_box_style()
        )
        
        self.console.print(panel)
        
        return self.renderer.show_confirmation(
            "Proceed with these URLs?",
            default=True
        )
    
    def _get_batch_format_choice(self) -> Optional[str]:
        """Get format choice for batch download."""
        options = {
            "1": (" Best Quality (Recommended)", lambda: "best"),
            "2": (" 1080p Full HD", lambda: "best[height<=1080]"),
            "3": (" 720p HD", lambda: "best[height<=720]"),
            "4": (" Audio Only", lambda: "bestaudio"),
            "5": (" Lowest Quality (Fastest)", lambda: "worst"),
            "6": (" Use Default Settings", lambda: None),
            "0": ("← Back", lambda: "back")
        }
        
        choice = self.renderer.show_menu(
            "Select Quality for Batch Download", 
            options, 
            back_option=False,
            show_shortcuts=False
        )
        
        if choice in options:
            return options[choice][1]()
        
        return None
    
    def _confirm_batch_download(self, urls: List[str], format_choice: Optional[str]) -> bool:
        """Final confirmation for batch download."""
        format_desc = {
            "best": "Best available quality",
            "best[height<=1080]": "1080p Full HD",
            "best[height<=720]": "720p HD",
            "bestaudio": "Audio only",
            "worst": "Lowest quality (fastest)"
        }.get(format_choice, "Default settings") if format_choice else "Default settings"
        
        confirm_content = f"""
[bold yellow]  Final Confirmation[/bold yellow]

[bold]URLs:[/bold] {len(urls)}
[bold]Quality:[/bold] {format_desc}
[bold]Concurrent Downloads:[/bold] {self.settings.download.max_concurrent}
[bold]Estimated Time:[/bold] ~{len(urls) * 2} minutes

[dim]This will start downloading all videos in the background.[/dim]
        """
        
        panel = Panel(
            confirm_content,
            title="[bold yellow] Ready to Start[/bold yellow]",
            border_style="yellow",
            box=self.renderer._get_box_style()
        )
        
        self.console.print(panel)
        
        return self.renderer.show_confirmation(
            "Start batch download?",
            default=True
        )
    
    def _execute_batch_download(self, urls: List[str], format_choice: Optional[str]) -> None:
        """Execute the batch download with progress tracking."""
        try:
            # Prepare download options
            options = {}
            if format_choice:
                options['format'] = format_choice
            
            # Add URLs to queue
            self.batch_processor.add_urls_to_queue(urls)
            
            # Start processing
            self.renderer.show_info(" Starting batch download...")
            
            # Process with concurrency limits
            results = self.batch_processor.process_batch_with_limits(
                urls, 
                max_concurrent=self.settings.download.max_concurrent,
                options=options
            )
            
            # Show results
            self._show_batch_results(results, "Batch Download Results")
            
        except Exception as e:
            self.renderer.show_error(f"Batch download failed: {str(e)}")
            if self.verbose:
                self.console.print_exception()
            self.renderer.show_pause()
    
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
    
    def _handle_enter_file_path(self) -> List[str]:
        """Handle manual file path entry for batch loading."""
        file_path = self.renderer.show_input_prompt("Enter the path to your batch file")
        
        if not file_path:
            return []
        
        try:
            path_obj = Path(file_path).expanduser()
            if not path_obj.exists():
                self.renderer.show_error(f"File not found: {path_obj}")
                return []
            
            if not path_obj.is_file():
                self.renderer.show_error(f"Path is not a file: {path_obj}")
                return []
            
            return self._load_urls_from_file(path_obj)
            
        except Exception as e:
            self.renderer.show_error(f"Failed to load file: {str(e)}")
            return []
    
    def _handle_recent_files(self) -> List[str]:
        """Handle loading from recent batch files."""
        try:
            # Get recent batch files from history or config
            recent_files = self._get_recent_batch_files()
            
            if not recent_files:
                self.renderer.show_info("No recent batch files found")
                return []
            
            # Show recent files menu
            options = {}
            for i, file_path in enumerate(recent_files, 1):
                file_name = Path(file_path).name
                options[str(i)] = (f" {file_name}", file_path)
            
            options["0"] = ("← Back", None)
            
            choice = self.renderer.show_menu("Select Recent File", options, back_option=False)
            
            if choice == "0" or choice not in options:
                return []
            
            selected_file = Path(options[choice][1])
            if selected_file.exists():
                return self._load_urls_from_file(selected_file)
            else:
                self.renderer.show_error(f"File no longer exists: {selected_file}")
                return []
                
        except Exception as e:
            self.renderer.show_error(f"Failed to load recent files: {str(e)}")
            return []
    
    def _get_recent_batch_files(self) -> List[str]:
        """Get list of recent batch files."""
        try:
            # This could be stored in config or history
            # For now, return empty list - can be enhanced later
            return []
        except Exception:
            return []
    
    def _load_urls_from_file(self, file_path: Path) -> List[str]:
        """Load URLs from a file."""
        try:
            urls = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip empty lines and comments
                        if self.input_handler.validate_url(line):
                            urls.append(line)
                        else:
                            self.renderer.show_warning(f"Invalid URL on line {line_num}: {line[:50]}...")
            
            if urls:
                self.renderer.show_success(f"Loaded {len(urls)} valid URLs from {file_path.name}")
            else:
                self.renderer.show_warning("No valid URLs found in file")
            
            return urls
            
        except Exception as e:
            self.renderer.show_error(f"Failed to read file: {str(e)}")
            return []
    
    def _show_options_menu(self) -> None:
        """Show enhanced options and settings menu."""
        while self.current_menu == "options":
            try:
                if self.settings.ui.clear_screen:
                    self.renderer.clear_screen()
                
                # Show current configuration summary
                self._show_configuration_summary()
                
                options = {
                    "1": (" Download Path Settings", self._handle_enhanced_path_settings),
                    "2": (" Format & Quality Settings", self._handle_enhanced_format_settings),
                    "3": (" File Organization Settings", self._handle_enhanced_organization_settings),
                    "4": (" Performance Settings", self._handle_enhanced_performance_settings),
                    "5": (" Advanced yt-dlp Options", self._handle_enhanced_advanced_settings),
                    "6": (" Configuration Management", self._handle_enhanced_config_management),
                    "7": (" Configuration Wizard", self._handle_enhanced_configuration_wizard),
                    "8": (" View Current Settings", self._handle_view_current_settings),
                    "9": (" Reset to Defaults", self._handle_enhanced_reset_defaults),
                    "0": ("← Back to Main Menu", lambda: None),
                }
                
                choice = self.renderer.show_menu("Options & Settings", options, show_shortcuts=True)
                
                if choice == "0":
                    self._go_back()
                    return
                elif choice in options:
                    options[choice][1]()
                
            except KeyboardInterrupt:
                self.renderer.show_warning("\nOperation cancelled by user")
                self._go_back()
                return
            except Exception as e:
                self.renderer.show_error(f"Unexpected error: {str(e)}")
                if self.verbose:
                    self.console.print_exception()
                self.renderer.show_pause()
                continue
    
    def _show_configuration_summary(self) -> None:
        """Show a summary of current configuration."""
        try:
            summary = f"""
            [bold]Current Configuration:[/bold]
            
             Download Path: {self.settings.download.path}
             Default Quality: {self.settings.download.default_quality}
             Default Format: {self.settings.download.default_format}
             Max Concurrent: {self.settings.download.max_concurrent}
             Create Day Folders: {'Yes' if self.settings.download.create_day_folders else 'No'}
             Auto Download: {'Yes' if self.settings.ui.auto_download else 'No'}
            """
            self.renderer.show_info(summary)
        except Exception as e:
            self.renderer.show_warning(f"Could not display configuration summary: {str(e)}")
    
    def _handle_enhanced_path_settings(self) -> None:
        """Handle enhanced download path settings."""
        while True:
            try:
                current_path = self.settings.download.path
                self.renderer.show_info(f"Current download path: {current_path}")
                
                # Show folder structure preview
                folder_structure = f"""
                Folder Structure:
                 {current_path}/
                     DD/ (current day folders)
                         YYYY-MM-DD_video-title.ext
                """
                self.renderer.show_info(folder_structure)
                
                options = {
                    "1": (" Set Custom Download Path", self._set_custom_path),
                    "2": (" Use Default Downloads Folder", self._set_default_path),
                    "3": (" Browse for Folder", self._browse_for_folder),
                    "4": (" Test Path", self._test_path),
                    "5": (" Show Path Info", self._show_path_info),
                    "0": ("← Back to Options Menu", lambda: None),
                }
                
                choice = self.renderer.show_menu("Download Path Settings", options, back_option=False)
                
                if choice == "0":
                    break
                elif choice in options:
                    options[choice][1]()
                
            except KeyboardInterrupt:
                break
    
    def _handle_enhanced_format_settings(self) -> None:
        """Handle enhanced format and quality settings."""
        while True:
            try:
                self.renderer.show_info(f"Current format settings:")
                self.renderer.show_info(f"  • Default Quality: {self.settings.download.default_quality}")
                self.renderer.show_info(f"  • Default Format: {self.settings.download.default_format}")
                
                options = {
                    "1": (" Set Default Quality", self._set_default_quality),
                    "2": (" Set Default Format", self._set_default_format),
                    "3": (" Audio Format Settings", self._handle_audio_format_settings),
                    "4": (" Quality Presets", self._handle_quality_presets),
                    "5": (" Advanced Format Options", self._handle_advanced_format_options),
                    "0": ("← Back to Options Menu", lambda: None),
                }
                
                choice = self.renderer.show_menu("Format & Quality Settings", options, back_option=False)
                
                if choice == "0":
                    break
                elif choice in options:
                    options[choice][1]()
                
            except KeyboardInterrupt:
                break
    
    def _handle_enhanced_organization_settings(self) -> None:
        """Handle enhanced file organization settings."""
        while True:
            try:
                self.renderer.show_info(f"Current organization settings:")
                self.renderer.show_info(f"  • Create Day Folders: {self.settings.download.create_day_folders}")
                self.renderer.show_info(f"  • File Naming: {self.settings.download.file_naming}")
                
                options = {
                    "1": (" Day Folder Settings", self._handle_day_folder_settings),
                    "2": (" File Naming Settings", self._handle_file_naming_settings),
                    "3": (" Folder Structure Settings", self._handle_folder_structure_settings),
                    "4": (" Metadata Settings", self._handle_metadata_settings),
                    "0": ("← Back to Options Menu", lambda: None),
                }
                
                choice = self.renderer.show_menu("File Organization Settings", options, back_option=False)
                
                if choice == "0":
                    break
                elif choice in options:
                    options[choice][1]()
                
            except KeyboardInterrupt:
                break
    
    def _handle_enhanced_performance_settings(self) -> None:
        """Handle enhanced performance settings."""
        while True:
            try:
                self.renderer.show_info(f"Current performance settings:")
                self.renderer.show_info(f"  • Max Concurrent Downloads: {self.settings.download.max_concurrent}")
                
                options = {
                    "1": (" Concurrent Download Limits", self._set_concurrent_limit),
                    "2": (" Memory Management", self._handle_memory_settings),
                    "3": (" Network Settings", self._handle_network_settings),
                    "4": (" Performance Monitoring", self._view_performance_settings),
                    "0": ("← Back to Options Menu", lambda: None),
                }
                
                choice = self.renderer.show_menu("Performance Settings", options, back_option=False)
                
                if choice == "0":
                    break
                elif choice in options:
                    options[choice][1]()
                
            except KeyboardInterrupt:
                break
    
    def _handle_enhanced_advanced_settings(self) -> None:
        """Handle enhanced advanced yt-dlp options."""
        while True:
            try:
                options = {
                    "1": (" yt-dlp Arguments", self._handle_ytdlp_arguments),
                    "2": (" Proxy Settings", self._handle_proxy_settings),
                    "3": (" Cookie Management", self._handle_cookie_settings),
                    "4": (" Authentication", self._handle_auth_settings),
                    "5": (" Custom Headers", self._handle_custom_headers),
                    "0": ("← Back to Options Menu", lambda: None),
                }
                
                choice = self.renderer.show_menu("Advanced yt-dlp Options", options, back_option=False)
                
                if choice == "0":
                    break
                elif choice in options:
                    options[choice][1]()
                
            except KeyboardInterrupt:
                break
    
    def _handle_enhanced_config_management(self) -> None:
        """Handle enhanced configuration management."""
        while True:
            try:
                options = {
                    "1": (" Export Configuration", self._export_configuration),
                    "2": (" Import Configuration", self._import_configuration),
                    "3": (" Validate Configuration", self._validate_configuration),
                    "4": (" Auto-Fix Configuration", self._auto_fix_configuration),
                    "5": (" View/Edit Config Files", self._handle_config_files),
                    "6": (" Configuration Backup", self._handle_config_backup),
                    "0": ("← Back to Options Menu", lambda: None),
                }
                
                choice = self.renderer.show_menu("Configuration Management", options, back_option=False)
                
                if choice == "0":
                    break
                elif choice in options:
                    options[choice][1]()
                
            except KeyboardInterrupt:
                break
    
    def _handle_enhanced_configuration_wizard(self) -> None:
        """Handle enhanced configuration wizard."""
        self._handle_configuration_wizard()
    
    def _handle_enhanced_reset_defaults(self) -> None:
        """Handle enhanced reset to defaults."""
        self._handle_reset_defaults()
    
    def _handle_path_settings(self) -> None:
        """Handle download path settings."""
        current_path = self.settings.download.path
        self.renderer.show_info(f"Current download path: {current_path}")
        
        # Show folder structure preview
        folder_structure = f"""
        Folder Structure:
         {current_path}/
             DD/ (current day folders)
                 YYYY-MM-DD_video-title.ext
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
                        [bold]  Warning: Import Configuration[/bold]
                        
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
                self.renderer.show_success(f"   {fix}")
            
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
        [bold]  Warning: Reset to Defaults[/bold]
        
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
        """Show enhanced download history menu."""
        while self.current_menu == "history":
            try:
                if self.settings.ui.clear_screen:
                    self.renderer.clear_screen()
                
                # Show recent downloads summary
                self._show_recent_downloads_summary()
                
                options = {
                    "1": (" View Full History", self._handle_enhanced_full_history),
                    "2": (" Search History", self._handle_enhanced_search_history),
                    "3": (" Advanced Search", self._handle_enhanced_advanced_search),
                    "4": (" Download Statistics", self._handle_download_statistics),
                    "5": (" Export History", self._handle_export_history),
                    "6": (" Open Download Folder", self._handle_open_folder),
                    "7": (" Clear History", self._handle_enhanced_clear_history),
                    "8": (" History Settings", self._handle_history_settings),
                    "0": ("← Back to Main Menu", lambda: None),
                }
                
                choice = self.renderer.show_menu("Download History", options, show_shortcuts=True)
                
                if choice == "0":
                    self._go_back()
                    return
                elif choice in options:
                    options[choice][1]()
                
            except KeyboardInterrupt:
                self.renderer.show_warning("\nOperation cancelled by user")
                self._go_back()
                return
            except Exception as e:
                self.renderer.show_error(f"Unexpected error: {str(e)}")
                if self.verbose:
                    self.console.print_exception()
                self.renderer.show_pause()
                continue
    
    def _show_recent_downloads_summary(self) -> None:
        """Show recent downloads summary."""
        try:
            history = self.history_manager.get_recent_downloads(5)
            
            if history:
                summary = f"""
                [bold]Recent Downloads:[/bold]
                
                """
                for i, entry in enumerate(history[:5], 1):
                    title = entry.get('title', 'Unknown')[:40]
                    status = entry.get('status', 'unknown')
                    date = entry.get('timestamp', 'Unknown')[:10]
                    summary += f"  {i}. {title}... ({status}) - {date}\n"
                
                self.renderer.show_info(summary)
            else:
                self.renderer.show_info("No recent downloads found")
                
        except Exception as e:
            self.renderer.show_warning(f"Could not load recent downloads: {str(e)}")
    
    def _handle_enhanced_full_history(self) -> None:
        """Handle enhanced full history view with pagination."""
        try:
            page = 1
            page_size = 20
            
            while True:
                history = self.history_manager.get_all_downloads()
                total_entries = len(history)
                total_pages = (total_entries + page_size - 1) // page_size
                
                start_idx = (page - 1) * page_size
                end_idx = start_idx + page_size
                page_entries = history[start_idx:end_idx]
                
                # Show page info
                page_info = f"""
                [bold]Download History - Page {page} of {total_pages}[/bold]
                Showing entries {start_idx + 1}-{min(end_idx, total_entries)} of {total_entries}
                """
                self.renderer.show_info(page_info)
                
                if page_entries:
                    self.renderer.show_download_summary(page_entries)
                else:
                    self.renderer.show_info("No downloads found")
                
                # Pagination options
                options = {}
                if page > 1:
                    options["1"] = (" Previous Page", lambda: "prev")
                if page < total_pages:
                    options["2"] = (" Next Page", lambda: "next")
                options["3"] = (" Search", lambda: "search")
                options["4"] = (" Statistics", lambda: "stats")
                options["0"] = ("← Back", lambda: "back")
                
                choice = self.renderer.show_menu("History Navigation", options, back_option=False)
                
                if choice == "0" or choice not in options:
                    break
                elif options[choice][1]() == "prev":
                    page = max(1, page - 1)
                elif options[choice][1]() == "next":
                    page = min(total_pages, page + 1)
                elif options[choice][1]() == "search":
                    self._handle_enhanced_search_history()
                    break
                elif options[choice][1]() == "stats":
                    self._handle_download_statistics()
                    break
                
        except Exception as e:
            self.renderer.show_error(f"Failed to load full history: {str(e)}")
            self.renderer.show_pause()
    
    def _handle_enhanced_search_history(self) -> None:
        """Handle enhanced search history with multiple search types."""
        while True:
            try:
                search_options = {
                    "1": (" Search by Title", lambda: self._search_by_title()),
                    "2": (" Search by URL", lambda: self._search_by_url()),
                    "3": (" Search by Uploader", lambda: self._search_by_uploader()),
                    "4": (" Search by Date Range", lambda: self._search_by_date_range()),
                    "5": (" Search by Status", lambda: self._search_by_status()),
                    "6": (" Advanced Search", lambda: self._handle_enhanced_advanced_search()),
                    "0": ("← Back", lambda: None),
                }
                
                choice = self.renderer.show_menu("Search History", search_options, back_option=False)
                
                if choice == "0":
                    break
                elif choice in search_options:
                    results = search_options[choice][1]()
                    if results:
                        self._display_search_results(results)
                    break
                
            except KeyboardInterrupt:
                break
    
    def _handle_enhanced_advanced_search(self) -> None:
        """Handle enhanced advanced search with multiple filters."""
        try:
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
            
            # URL filter
            url = self.renderer.show_input_prompt("URL (leave empty to skip)", required=False)
            if url:
                filters['url'] = url
            
            # Status filter
            status_options = {
                "1": ("completed", "Completed downloads"),
                "2": ("failed", "Failed downloads"),
                "3": ("cancelled", "Cancelled downloads"),
                "4": ("in_progress", "In progress downloads"),
                "0": ("", "Skip status filter"),
            }
            
            status_choice = self.renderer.show_menu("Select Status Filter", status_options, back_option=False)
            if status_choice in status_options and status_options[status_choice][0]:
                filters['status'] = status_options[status_choice][0]
            
            # Date range filter
            date_range = self.renderer.show_input_prompt("Date range (YYYY-MM-DD to YYYY-MM-DD, leave empty to skip)", required=False)
            if date_range:
                filters['date_range'] = date_range
            
            # Size filter
            min_size = self.renderer.show_input_prompt("Minimum file size in MB (leave empty to skip)", required=False)
            if min_size and min_size.isdigit():
                filters['min_size'] = int(min_size)
            
            max_size = self.renderer.show_input_prompt("Maximum file size in MB (leave empty to skip)", required=False)
            if max_size and max_size.isdigit():
                filters['max_size'] = int(max_size)
            
            # Limit results
            limit_str = self.renderer.show_input_prompt("Limit results (leave empty for no limit)", required=False)
            if limit_str and limit_str.isdigit():
                filters['limit'] = int(limit_str)
            
            try:
                results = self.history_manager.advanced_search(filters)
                
                if results:
                    self.renderer.show_success(f"Found {len(results)} results")
                    self._display_search_results(results)
                else:
                    self.renderer.show_info("No results found")
                    
            except Exception as e:
                self.renderer.show_error(f"Advanced search failed: {str(e)}")
            
        except Exception as e:
            self.renderer.show_error(f"Advanced search failed: {str(e)}")
    
    def _handle_download_statistics(self) -> None:
        """Handle download statistics display."""
        try:
            history = self.history_manager.get_all_downloads()
            
            if not history:
                self.renderer.show_info("No download history available for statistics")
                return
            
            # Calculate statistics
            total_downloads = len(history)
            completed = len([h for h in history if h.get('status') == 'completed'])
            failed = len([h for h in history if h.get('status') == 'failed'])
            cancelled = len([h for h in history if h.get('status') == 'cancelled'])
            
            total_size = sum(h.get('file_size', 0) for h in history if h.get('file_size'))
            avg_size = total_size / completed if completed > 0 else 0
            
            # Status breakdown
            status_stats = f"""
            [bold]Download Statistics:[/bold]
            
             Total Downloads: {total_downloads}
             Completed: {completed} ({(completed/total_downloads)*100:.1f}%)
             Failed: {failed} ({(failed/total_downloads)*100:.1f}%)
            ⏹ Cancelled: {cancelled} ({(cancelled/total_downloads)*100:.1f}%)
            
             Total Size: {total_size / (1024*1024):.1f} MB
             Average Size: {avg_size / (1024*1024):.1f} MB
            """
            
            self.renderer.show_info(status_stats)
            
            # Show recent activity
            recent_history = history[-10:] if len(history) > 10 else history
            if recent_history:
                recent_activity = "\n[bold]Recent Activity:[/bold]\n"
                for entry in recent_history:
                    title = entry.get('title', 'Unknown')[:30]
                    date = entry.get('timestamp', 'Unknown')[:10]
                    status = entry.get('status', 'unknown')
                    recent_activity += f"  • {title}... ({status}) - {date}\n"
                
                self.renderer.show_info(recent_activity)
            
            self.renderer.show_pause()
            
        except Exception as e:
            self.renderer.show_error(f"Failed to generate statistics: {str(e)}")
            self.renderer.show_pause()
    
    def _handle_export_history(self) -> None:
        """Handle history export functionality."""
        try:
            export_options = {
                "1": (" Export as CSV", lambda: self._export_history_csv()),
                "2": (" Export as JSON", lambda: self._export_history_json()),
                "3": (" Export as Text", lambda: self._export_history_text()),
                "4": (" Export Statistics", lambda: self._export_history_stats()),
                "0": ("← Back", lambda: None),
            }
            
            choice = self.renderer.show_menu("Export History", export_options, back_option=False)
            
            if choice == "0":
                return
            elif choice in export_options:
                export_options[choice][1]()
                
        except Exception as e:
            self.renderer.show_error(f"Export failed: {str(e)}")
    
    def _handle_enhanced_clear_history(self) -> None:
        """Handle enhanced clear history with confirmation and options."""
        try:
            self.renderer.show_warning("""
            [bold]Clear Download History[/bold]
            
            This will permanently delete all download history records.
            This action cannot be undone.
            """)
            
            clear_options = {
                "1": (" Clear All History", lambda: "all"),
                "2": (" Clear Old History (>30 days)", lambda: "old"),
                "3": (" Clear Failed Downloads Only", lambda: "failed"),
                "4": (" Clear Statistics Only", lambda: "stats"),
                "0": ("← Cancel", lambda: "cancel"),
            }
            
            choice = self.renderer.show_menu("Clear History Options", clear_options, back_option=False)
            
            if choice == "0" or choice not in clear_options:
                return
            
            clear_type = clear_options[choice][1]()
            
            if clear_type == "cancel":
                return
            
            # Confirm the action
            if self.renderer.show_confirmation("Are you sure you want to proceed?", default=False):
                if clear_type == "all":
                    self.history_manager.clear_all_history()
                    self.renderer.show_success("All download history cleared")
                elif clear_type == "old":
                    self.history_manager.clear_old_history(days=30)
                    self.renderer.show_success("Old download history cleared")
                elif clear_type == "failed":
                    self.history_manager.clear_failed_downloads()
                    self.renderer.show_success("Failed downloads cleared from history")
                elif clear_type == "stats":
                    self.history_manager.clear_statistics()
                    self.renderer.show_success("Download statistics cleared")
            
        except Exception as e:
            self.renderer.show_error(f"Failed to clear history: {str(e)}")
    
    def _handle_history_settings(self) -> None:
        """Handle history settings configuration."""
        try:
            while True:
                self.renderer.show_info(f"Current history settings:")
                self.renderer.show_info(f"  • Max Entries: {self.settings.history.max_entries}")
                self.renderer.show_info(f"  • Auto Cleanup: {self.settings.history.auto_cleanup}")
                self.renderer.show_info(f"  • Cleanup Days: {self.settings.history.cleanup_days}")
                
                options = {
                    "1": (" Set Max Entries", self._set_max_history_entries),
                    "2": (" Auto Cleanup Settings", self._handle_auto_cleanup_settings),
                    "3": (" Cleanup Interval", self._set_cleanup_interval),
                    "4": (" Storage Settings", self._handle_history_storage_settings),
                    "0": ("← Back", lambda: None),
                }
                
                choice = self.renderer.show_menu("History Settings", options, back_option=False)
                
                if choice == "0":
                    break
                elif choice in options:
                    options[choice][1]()
                
        except Exception as e:
            self.renderer.show_error(f"Failed to configure history settings: {str(e)}")
    
    def _set_max_history_entries(self) -> None:
        """Set maximum history entries."""
        try:
            current_max = self.settings.history.max_entries
            new_max = self.renderer.show_input_prompt(
                f"Enter maximum history entries (current: {current_max})",
                default=str(current_max)
            )
            
            if new_max and new_max.isdigit():
                max_entries = int(new_max)
                if max_entries > 0:
                    self.settings.history.max_entries = max_entries
                    self.config_manager.save_config()
                    self.renderer.show_success(f"Maximum history entries set to {max_entries}")
                else:
                    self.renderer.show_error("Maximum entries must be greater than 0")
            else:
                self.renderer.show_error("Invalid input")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to set max entries: {str(e)}")
    
    def _handle_auto_cleanup_settings(self) -> None:
        """Handle auto cleanup settings."""
        try:
            current_setting = self.settings.history.auto_cleanup
            new_setting = self.renderer.show_confirmation(
                f"Enable auto cleanup? (current: {'Yes' if current_setting else 'No'})",
                default=current_setting
            )
            
            self.settings.history.auto_cleanup = new_setting
            self.config_manager.save_config()
            self.renderer.show_success(f"Auto cleanup {'enabled' if new_setting else 'disabled'}")
            
        except Exception as e:
            self.renderer.show_error(f"Failed to set auto cleanup: {str(e)}")
    
    def _set_cleanup_interval(self) -> None:
        """Set cleanup interval in days."""
        try:
            current_days = self.settings.history.cleanup_days
            new_days = self.renderer.show_input_prompt(
                f"Enter cleanup interval in days (current: {current_days})",
                default=str(current_days)
            )
            
            if new_days and new_days.isdigit():
                days = int(new_days)
                if days > 0:
                    self.settings.history.cleanup_days = days
                    self.config_manager.save_config()
                    self.renderer.show_success(f"Cleanup interval set to {days} days")
                else:
                    self.renderer.show_error("Cleanup interval must be greater than 0")
            else:
                self.renderer.show_error("Invalid input")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to set cleanup interval: {str(e)}")
    
    def _handle_history_storage_settings(self) -> None:
        """Handle history storage settings."""
        try:
            self.renderer.show_info("History storage settings:")
            self.renderer.show_info("  • History is stored in JSON format")
            self.renderer.show_info("  • Location: ~/.config/videomilker/download_history.json")
            self.renderer.show_info("  • Backup is created automatically")
            
            options = {
                "1": (" Change Storage Location", self._change_history_storage_location),
                "2": (" Create Backup", self._create_history_backup),
                "3": (" Restore from Backup", self._restore_history_backup),
                "4": (" Storage Info", self._show_history_storage_info),
                "0": ("← Back", lambda: None),
            }
            
            choice = self.renderer.show_menu("History Storage Settings", options, back_option=False)
            
            if choice == "0":
                return
            elif choice in options:
                options[choice][1]()
                
        except Exception as e:
            self.renderer.show_error(f"Failed to configure storage settings: {str(e)}")
    
    def _change_history_storage_location(self) -> None:
        """Change history storage location."""
        try:
            current_location = self.history_manager.get_storage_location()
            self.renderer.show_info(f"Current storage location: {current_location}")
            
            new_location = self.renderer.show_input_prompt(
                "Enter new storage location (leave empty to cancel)",
                required=False
            )
            
            if new_location:
                # This would need to be implemented in HistoryManager
                self.renderer.show_info("Storage location change not yet implemented")
            else:
                self.renderer.show_info("Storage location change cancelled")
                
        except Exception as e:
            self.renderer.show_error(f"Failed to change storage location: {str(e)}")
    
    def _create_history_backup(self) -> None:
        """Create history backup."""
        try:
            backup_path = self.history_manager.create_backup()
            self.renderer.show_success(f"History backup created: {backup_path}")
        except Exception as e:
            self.renderer.show_error(f"Failed to create backup: {str(e)}")
    
    def _restore_history_backup(self) -> None:
        """Restore history from backup."""
        try:
            self.renderer.show_warning("Restoring from backup will replace current history")
            if self.renderer.show_confirmation("Are you sure?", default=False):
                backup_path = self.history_manager.restore_backup()
                self.renderer.show_success(f"History restored from: {backup_path}")
        except Exception as e:
            self.renderer.show_error(f"Failed to restore backup: {str(e)}")
    
    def _show_history_storage_info(self) -> None:
        """Show history storage information."""
        try:
            storage_info = self.history_manager.get_storage_info()
            
            info_text = f"""
            [bold]History Storage Information:[/bold]
            
             Location: {storage_info.get('location', 'Unknown')}
             Total Entries: {storage_info.get('total_entries', 0)}
             File Size: {storage_info.get('file_size_mb', 0):.2f} MB
             Last Modified: {storage_info.get('last_modified', 'Unknown')}
             Auto Backup: {'Yes' if storage_info.get('auto_backup', False) else 'No'}
            """
            
            self.renderer.show_info(info_text)
            self.renderer.show_pause()
            
        except Exception as e:
            self.renderer.show_error(f"Failed to get storage info: {str(e)}")
    
    def _search_by_title(self) -> List[Dict[str, Any]]:
        """Search history by title."""
        query = self.renderer.show_input_prompt("Enter title to search for")
        if query:
            return self.history_manager.search_by_title(query)
        return []
    
    def _search_by_url(self) -> List[Dict[str, Any]]:
        """Search history by URL."""
        query = self.renderer.show_input_prompt("Enter URL to search for")
        if query:
            return self.history_manager.search_by_url(query)
        return []
    
    def _search_by_uploader(self) -> List[Dict[str, Any]]:
        """Search history by uploader."""
        query = self.renderer.show_input_prompt("Enter uploader to search for")
        if query:
            return self.history_manager.search_by_uploader(query)
        return []
    
    def _search_by_date_range(self) -> List[Dict[str, Any]]:
        """Search history by date range."""
        start_date = self.renderer.show_input_prompt("Enter start date (YYYY-MM-DD)")
        end_date = self.renderer.show_input_prompt("Enter end date (YYYY-MM-DD)")
        
        if start_date and end_date:
            return self.history_manager.search_by_date_range(start_date, end_date)
        return []
    
    def _search_by_status(self) -> List[Dict[str, Any]]:
        """Search history by status."""
        status_options = {
            "1": "completed",
            "2": "failed", 
            "3": "cancelled",
            "4": "in_progress"
        }
        
        choice = self.renderer.show_menu("Select Status", status_options, back_option=False)
        if choice in status_options:
            return self.history_manager.search_by_status(status_options[choice])
        return []
    
    def _display_search_results(self, results: List[Dict[str, Any]]) -> None:
        """Display search results."""
        if results:
            self.renderer.show_success(f"Found {len(results)} results")
            self.renderer.show_download_summary(results)
            
            # Show options for results
            options = {
                "1": (" Export Results", lambda: self._export_search_results(results)),
                "2": (" Refine Search", lambda: self._handle_enhanced_search_history()),
                "0": ("← Back", lambda: None),
            }
            
            choice = self.renderer.show_menu("Search Results", options, back_option=False)
            if choice in options:
                options[choice][1]()
        else:
            self.renderer.show_info("No results found")
    
    def _export_search_results(self, results: List[Dict[str, Any]]) -> None:
        """Export search results."""
        try:
            export_options = {
                "1": (" Export as CSV", lambda: self._export_results_csv(results)),
                "2": (" Export as JSON", lambda: self._export_results_json(results)),
                "0": ("← Back", lambda: None),
            }
            
            choice = self.renderer.show_menu("Export Search Results", export_options, back_option=False)
            if choice in export_options:
                export_options[choice][1]()
                
        except Exception as e:
            self.renderer.show_error(f"Export failed: {str(e)}")
    
    def _export_history_csv(self) -> None:
        """Export history as CSV."""
        try:
            history = self.history_manager.get_all_downloads()
            if history:
                csv_path = self.history_manager.export_as_csv(history)
                self.renderer.show_success(f"History exported to CSV: {csv_path}")
            else:
                self.renderer.show_info("No history to export")
        except Exception as e:
            self.renderer.show_error(f"CSV export failed: {str(e)}")
    
    def _export_history_json(self) -> None:
        """Export history as JSON."""
        try:
            history = self.history_manager.get_all_downloads()
            if history:
                json_path = self.history_manager.export_as_json(history)
                self.renderer.show_success(f"History exported to JSON: {json_path}")
            else:
                self.renderer.show_info("No history to export")
        except Exception as e:
            self.renderer.show_error(f"JSON export failed: {str(e)}")
    
    def _export_history_text(self) -> None:
        """Export history as text."""
        try:
            history = self.history_manager.get_all_downloads()
            if history:
                text_path = self.history_manager.export_as_text(history)
                self.renderer.show_success(f"History exported to text: {text_path}")
            else:
                self.renderer.show_info("No history to export")
        except Exception as e:
            self.renderer.show_error(f"Text export failed: {str(e)}")
    
    def _export_history_stats(self) -> None:
        """Export history statistics."""
        try:
            stats_path = self.history_manager.export_statistics()
            self.renderer.show_success(f"Statistics exported to: {stats_path}")
        except Exception as e:
            self.renderer.show_error(f"Statistics export failed: {str(e)}")
    
    def _export_results_csv(self, results: List[Dict[str, Any]]) -> None:
        """Export search results as CSV."""
        try:
            csv_path = self.history_manager.export_as_csv(results, prefix="search_results")
            self.renderer.show_success(f"Search results exported to CSV: {csv_path}")
        except Exception as e:
            self.renderer.show_error(f"CSV export failed: {str(e)}")
    
    def _export_results_json(self, results: List[Dict[str, Any]]) -> None:
        """Export search results as JSON."""
        try:
            json_path = self.history_manager.export_as_json(results, prefix="search_results")
            self.renderer.show_success(f"Search results exported to JSON: {json_path}")
        except Exception as e:
            self.renderer.show_error(f"JSON export failed: {str(e)}")
    
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
        [bold]  Warning: Clear Download History[/bold]
        
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
        """Show comprehensive help and information menu."""
        while self.current_menu == "help":
            try:
                if self.settings.ui.clear_screen:
                    self.renderer.clear_screen()
                
                # Show help menu options
                options = {
                    "1": (" General Help & Overview", self._show_general_help),
                    "2": (" Quick Download Guide", self._show_quick_download_help),
                    "3": (" Batch Download Guide", self._show_batch_download_help),
                    "4": (" File Management Guide", self._show_file_management_help),
                    "5": (" Configuration Guide", self._show_configuration_help),
                    "6": (" Keyboard Shortcuts", self._show_keyboard_shortcuts),
                    "7": (" Troubleshooting", self._show_troubleshooting_help),
                    "8": (" About VideoMilker", self._show_about_info),
                    "0": ("← Back to Main Menu", lambda: None),
                }
                
                choice = self.renderer.show_menu("Help & Information", options, show_shortcuts=True)
                
                if choice == "0":
                    self._go_back()
                    return
                elif choice in options:
                    options[choice][1]()
                
            except KeyboardInterrupt:
                self.renderer.show_warning("\nOperation cancelled by user")
                self._go_back()
                return
            except Exception as e:
                self.renderer.show_error(f"Unexpected error: {str(e)}")
                if self.verbose:
                    self.console.print_exception()
                self.renderer.show_pause()
                continue
    
    def _show_general_help(self) -> None:
        """Show general help information."""
        help_text = """
        [bold]VideoMilker - General Help[/bold]
        
        [bold]What is VideoMilker?[/bold]
        VideoMilker is an intuitive CLI interface for yt-dlp that transforms complex 
        command-line arguments into user-friendly menu-driven workflows.
        
        [bold]Key Features:[/bold]
        • Quick single video downloads with preview
        • Batch processing of multiple URLs
        • Audio-only downloads with format selection
        • Chapter splitting and extraction
        • Intelligent file organization
        • Download history and management
        • Progress tracking and error recovery
        
        [bold]Supported Platforms:[/bold]
        • YouTube, Vimeo, Dailymotion, and 1000+ other sites
        • All formats supported by yt-dlp
        • Cross-platform (Windows, macOS, Linux)
        
        [bold]Getting Started:[/bold]
        1. Use Quick Download for single videos
        2. Use Batch Download for multiple videos
        3. Configure settings in Options & Settings
        4. View history in Download History
        """
        
        panel = Panel(
            help_text,
            title="[bold green]General Help[/bold green]",
            border_style="green",
            box=ROUNDED
        )
        self.console.print(panel)
        self.renderer.show_pause()
    
    def _show_quick_download_help(self) -> None:
        """Show quick download help."""
        help_text = """
        [bold]Quick Download Guide[/bold]
        
        [bold]Purpose:[/bold]
        Download a single video with minimal configuration and maximum convenience.
        
        [bold]Workflow:[/bold]
        1. Enter video URL when prompted
        2. Preview video information (optional)
        3. Select format/quality (optional)
        4. Confirm and start download
        
        [bold]Features:[/bold]
        • Automatic URL validation
        • Video information preview
        • Format selection with quality options
        • Progress tracking with speed and ETA
        • Automatic file organization
        
        [bold]Tips:[/bold]
        • Use 'v' to preview video info before downloading
        • Use 'f' to select specific format/quality
        • Files are automatically organized by date
        • Progress is shown in real-time
        """
        
        panel = Panel(
            help_text,
            title="[bold blue]Quick Download Help[/bold blue]",
            border_style="blue",
            box=ROUNDED
        )
        self.console.print(panel)
        self.renderer.show_pause()
    
    def _show_batch_download_help(self) -> None:
        """Show batch download help."""
        help_text = """
        [bold]Batch Download Guide[/bold]
        
        [bold]Purpose:[/bold]
        Download multiple videos efficiently with queue management and progress tracking.
        
        [bold]Input Methods:[/bold]
        1. Direct URL input - paste URLs one by one
        2. File loading - load URLs from text file
        3. Clipboard - paste multiple URLs at once
        4. Recent URLs - use URLs from history
        
        [bold]Queue Management:[/bold]
        • Pause/resume downloads
        • Stop processing
        • View progress and results
        • Retry failed downloads
        • Clear queue
        
        [bold]Features:[/bold]
        • Concurrent downloads (configurable limit)
        • Progress tracking for each download
        • Error handling and recovery
        • Batch logging and results
        • Memory optimization for large batches
        
        [bold]Tips:[/bold]
        • Use concurrent limit to avoid overwhelming your connection
        • Check queue status regularly
        • Use pause/resume for long batch operations
        • Review failed downloads and retry if needed
        """
        
        panel = Panel(
            help_text,
            title="[bold cyan]Batch Download Help[/bold cyan]",
            border_style="cyan",
            box=ROUNDED
        )
        self.console.print(panel)
        self.renderer.show_pause()
    
    def _show_file_management_help(self) -> None:
        """Show file management help."""
        help_text = """
        [bold]File Management Guide[/bold]
        
        [bold]Duplicate Detection:[/bold]
        • Hash-based detection (most accurate)
        • Name/size comparison (fast)
        • Similarity detection (fuzzy matching)
        • Preview before deletion
        
        [bold]File Organization:[/bold]
        • Type-based sorting (video, audio, etc.)
        • Date-based organization
        • Custom folder structures
        • Automatic cleanup
        
        [bold]Storage Analysis:[/bold]
        • Disk usage monitoring
        • Large file identification
        • Old file detection
        • Cleanup recommendations
        
        [bold]Cleanup Tools:[/bold]
        • Remove large files (>500MB)
        • Remove old files (>90 days)
        • Remove empty folders
        • Bulk operations with confirmation
        
        [bold]Tips:[/bold]
        • Always preview before deleting
        • Use storage analysis to identify cleanup opportunities
        • Regular cleanup helps maintain performance
        • Backup important files before bulk operations
        """
        
        panel = Panel(
            help_text,
            title="[bold yellow]File Management Help[/bold yellow]",
            border_style="yellow",
            box=ROUNDED
        )
        self.console.print(panel)
        self.renderer.show_pause()
    
    def _show_configuration_help(self) -> None:
        """Show configuration help."""
        help_text = """
        [bold]Configuration Guide[/bold]
        
        [bold]Download Settings:[/bold]
        • Download path configuration
        • File naming templates
        • Default quality and format
        • Concurrent download limits
        • Auto-download options
        
        [bold]Organization Settings:[/bold]
        • Day-based folder creation
        • File naming conventions
        • Batch file organization
        • History management
        
        [bold]UI Settings:[/bold]
        • Theme selection (default, dark, light, minimal)
        • Progress display options
        • Confirmation dialogs
        • Screen clearing preferences
        
        [bold]Configuration Files:[/bold]
        • JSON-based configuration
        • Automatic validation
        • Import/export functionality
        • Configuration wizard
        • Auto-fix capabilities
        
        [bold]Tips:[/bold]
        • Use configuration wizard for first-time setup
        • Export configuration for backup
        • Validate configuration regularly
        • Use auto-fix for common issues
        """
        
        panel = Panel(
            help_text,
            title="[bold magenta]Configuration Help[/bold magenta]",
            border_style="magenta",
            box=ROUNDED
        )
        self.console.print(panel)
        self.renderer.show_pause()
    
    def _show_keyboard_shortcuts(self) -> None:
        """Show comprehensive keyboard shortcuts guide."""
        shortcuts_text = """
        [bold]VideoMilker Keyboard Shortcuts[/bold]
        
        [bold green]Global Navigation Shortcuts:[/bold green]
        • [bold]0, b, B[/bold] - Go Back to previous menu
        • [bold]q, Q[/bold] - Quit application
        • [bold]?[/bold] - Show this help (keyboard shortcuts)
        • [bold]ESC[/bold] - Go back (alternative)
        
        [bold green]Direct Menu Access:[/bold green]
        • [bold]d, D[/bold] - Quick Download
        • [bold]a, A[/bold] - Audio-Only Download
        • [bold]c, C[/bold] - Chapter Split Download
        • [bold]b, B[/bold] - Batch Download
        • [bold]r, R[/bold] - Resume Interrupted Downloads
        • [bold]f, F[/bold] - File Management
        • [bold]s, S[/bold] - Options & Settings
        • [bold]i, I[/bold] - Download History
        • [bold]h, H[/bold] - Help & Info
        
        [bold green]General Navigation:[/bold green]
        • [bold]Arrow Keys[/bold] - Navigate menu options
        • [bold]Enter[/bold] - Select/confirm option
        • [bold]Tab[/bold] - Auto-complete where available
        • [bold]Ctrl+C[/bold] - Cancel current operation
        
        [bold green]Input & Editing:[/bold green]
        • [bold]Ctrl+D[/bold] - Finish URL input (batch mode)
        • [bold]Ctrl+U[/bold] - Clear current input
        • [bold]Ctrl+W[/bold] - Delete word backward
        • [bold]Ctrl+K[/bold] - Delete to end of line
        
        [bold green]Download Controls:[/bold green]
        • [bold]p[/bold] - Pause batch processing
        • [bold]s[/bold] - Skip current download (batch mode)
        • [bold]r[/bold] - Resume paused downloads
        • [bold]c[/bold] - Cancel current download
        
        [bold green]File Management:[/bold green]
        • [bold]d[/bold] - Delete selected files
        • [bold]o[/bold] - Organize files by type
        • [bold]c[/bold] - Clean up empty folders
        • [bold]a[/bold] - Analyze storage usage
        
        [bold green]History & Search:[/bold green]
        • [bold]f[/bold] - Find in history
        • [bold]n[/bold] - Next search result
        • [bold]p[/bold] - Previous search result
        • [bold]e[/bold] - Export history
        
        [bold green]Configuration:[/bold green]
        • [bold]v[/bold] - View current settings
        • [bold]e[/bold] - Export configuration
        • [bold]i[/bold] - Import configuration
        • [bold]r[/bold] - Reset to defaults
        
        [bold green]Help & Information:[/bold green]
        • [bold]1-8[/bold] - Navigate help sections
        • [bold]g[/bold] - General help
        • [bold]t[/bold] - Troubleshooting
        • [bold]a[/bold] - About VideoMilker
        
        [bold yellow]Tip:[/bold yellow] Most shortcuts work from any menu level. 
        Use [bold]?[/bold] anytime to see this help, or [bold]0[/bold] to go back.
        """
        
        panel = Panel(
            shortcuts_text,
            title="[bold green]Keyboard Shortcuts[/bold green]",
            border_style="green",
            box=ROUNDED
        )
        self.console.print(panel)
        self.renderer.show_pause()
    
    def _show_troubleshooting_help(self) -> None:
        """Show troubleshooting help."""
        help_text = """
        [bold]Troubleshooting Guide[/bold]
        
        [bold]Common Issues:[/bold]
        
        [bold]Download Fails:[/bold]
        • Check internet connection
        • Verify URL is accessible
        • Try different format/quality
        • Check if video is region-restricted
        
        [bold]Slow Downloads:[/bold]
        • Reduce concurrent download limit
        • Check network speed
        • Try different quality settings
        • Use audio-only for faster downloads
        
        [bold]File Organization Issues:[/bold]
        • Check download path permissions
        • Verify folder structure settings
        • Use configuration validation
        • Reset to defaults if needed
        
        [bold]Configuration Problems:[/bold]
        • Run configuration validation
        • Use auto-fix feature
        • Reset to defaults
        • Check file permissions
        
        [bold]Performance Issues:[/bold]
        • Reduce concurrent downloads
        • Clear download history
        • Clean up old files
        • Restart application
        
        [bold]Getting Help:[/bold]
        • Check this help section
        • Review error messages carefully
        • Use verbose mode for details
        • Check configuration settings
        """
        
        panel = Panel(
            help_text,
            title="[bold orange]Troubleshooting Help[/bold orange]",
            border_style="orange",
            box=ROUNDED
        )
        self.console.print(panel)
        self.renderer.show_pause()
    
    def _show_about_info(self) -> None:
        """Show about information."""
        from ..version import __version__
        
        about_text = f"""
        [bold]VideoMilker v{__version__}[/bold]
        
        [bold]Description:[/bold]
        An intuitive, tree-structured CLI interface for yt-dlp that eliminates 
        complex command-line arguments and provides standardized workflows with 
        visual feedback using the Rich library.
        
        [bold]Features:[/bold]
        • Rich terminal UI with colors and progress bars
        • Menu-driven interface for easy navigation
        • Batch download processing with queue management
        • File organization and management tools
        • Download history and analytics
        • Configuration management with validation
        • Error handling and recovery
        
        [bold]Technologies:[/bold]
        • Python 3.8+
        • Rich (terminal UI)
        • Click (CLI framework)
        • yt-dlp (video downloading)
        • Pydantic (configuration)
        
        [bold]License:[/bold]
        MIT License - Open source and free to use
        
        [bold]Support:[/bold]
        • GitHub Issues: https://github.com/videomilker/videomilker/issues
        • Documentation: https://videomilker.readthedocs.io/
        • Help: Use 'h' or '?' from any menu
        """
        
        panel = Panel(
            about_text,
            title="[bold purple]About VideoMilker[/bold purple]",
            border_style="purple",
            box=ROUNDED
        )
        self.console.print(panel)
        self.renderer.show_pause()
