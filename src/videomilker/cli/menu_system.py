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
        elif self.current_menu == "batch_download":
            self._show_batch_download_menu()
        elif self.current_menu == "options":
            self._show_options_menu()
        elif self.current_menu == "history":
            self._show_history_menu()
        elif self.current_menu == "help":
            self._show_help_menu()
        else:
            self.current_menu = "main"
    
    def _show_main_menu(self) -> None:
        """Display and handle the main menu."""
        options = {
            "1": (" Quick Download", self._handle_quick_download),
            "2": (" Batch Download", self._handle_batch_download),
            "3": (" Options & Settings", self._handle_options),
            "4": (" Download History", self._handle_history),
            "5": (" Help & Info", self._handle_help),
            "q": ("Quit Application", self._handle_quit),
        }
        
        choice = self.renderer.show_menu("VideoMilker Main Menu", options)
        
        if choice in options:
            options[choice][1]()
    
    def _handle_quick_download(self) -> None:
        """Handle quick download option."""
        self.current_menu = "quick_download"
    
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
            
            # Confirm download
            if self.renderer.show_download_confirmation("Start download?", self.settings.ui.auto_download):
                self._download_single_video(url, video_info)
            
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
    
    def _download_single_video(self, url: str, video_info: Dict[str, Any]) -> None:
        """Download a single video with progress tracking."""
        try:
            self.renderer.show_info("Starting download...")
            
            # Create progress display
            progress = self.renderer.show_progress(f"Downloading: {video_info.get('title', 'Unknown')}")
            
            # Download the video
            result = self.downloader.download_single(url)
            
            if result['status'] == 'completed':
                self.renderer.show_success(f"Download completed: {result.get('filename', 'Unknown')}")
                
                # Log to history
                self.history_manager.add_download(url, video_info, result)
                
            else:
                self.renderer.show_error("Download failed")
                
        except Exception as e:
            self.renderer.show_error(f"Download failed: {str(e)}")
    
    def _show_batch_download_menu(self) -> None:
        """Show batch download menu."""
        options = {
            "1": (" Paste URLs directly", self._handle_direct_urls),
            "2": (" Load from batch file", self._handle_batch_file),
            "3": (" Browse for batch file", self._handle_browse_file),
            "4": (" Create batch template", self._handle_create_template),
            "5": (" Show batch folder", self._handle_show_batch_folder),
            "0": ("← Back to Main Menu", lambda: None),
        }
        
        choice = self.renderer.show_menu("Batch Download", options)
        
        if choice in options:
            options[choice][1]()
        
        self.current_menu = "main"
    
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
        
        if self.renderer.show_download_confirmation(f"Download {len(urls)} videos?", self.settings.ui.auto_download):
            try:
                results = self.batch_processor.process_batch(urls)
                
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
            "5": (" Advanced yt-dlp Options", self._handle_advanced_settings),
            "6": (" View/Edit Config Files", self._handle_config_files),
            "7": (" Reset to Defaults", self._handle_reset_defaults),
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
        
        new_path = self.renderer.show_input_prompt("Enter new download path", default=current_path)
        
        if new_path and new_path != current_path:
            try:
                self.settings.download.path = new_path
                self.config_manager.save_config()
                self.renderer.show_success("Download path updated successfully")
            except Exception as e:
                self.renderer.show_error(f"Failed to update path: {str(e)}")
    
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
    
    def _handle_advanced_settings(self) -> None:
        """Handle advanced settings."""
        self.renderer.show_info("Advanced settings - coming soon!")
        self.renderer.show_pause()
    
    def _handle_config_files(self) -> None:
        """Handle config file management."""
        self.renderer.show_settings(self.settings)
        self.renderer.show_pause()
    
    def _handle_reset_defaults(self) -> None:
        """Handle reset to defaults."""
        if self.renderer.show_confirmation("Reset all settings to defaults? This cannot be undone."):
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
                "2": (" Clear History", self._handle_clear_history),
                "3": (" Open Download Folder", self._handle_open_folder),
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
    
    def _handle_clear_history(self) -> None:
        """Handle history clearing."""
        if self.renderer.show_confirmation("Clear all download history? This cannot be undone."):
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
