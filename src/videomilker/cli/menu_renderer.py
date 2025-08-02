"""Rich UI menu renderer for VideoMilker CLI."""

from typing import Dict, List, Optional, Tuple, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.columns import Columns
from rich.align import Align
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.box import ROUNDED, DOUBLE, SIMPLE
from rich.style import Style

from ..config.settings import Settings
from ..config.defaults import THEMES


class MenuRenderer:
    """Renders beautiful Rich UI menus for VideoMilker."""
    
    def __init__(self, console: Console, settings: Optional[Settings] = None):
        """Initialize the menu renderer."""
        self.console = console
        self.settings = settings
        self.theme = self._get_theme()
    
    def _get_theme(self) -> Dict[str, str]:
        """Get the current theme configuration."""
        if self.settings:
            theme_name = self.settings.ui.theme
            return THEMES.get(theme_name, THEMES["default"])
        return THEMES["default"]
    
    def show_welcome_banner(self) -> None:
        """Display the welcome banner."""
        banner_text = """
        [bold blue][/bold blue]
        [bold blue]                                                              [/bold blue]
        [bold blue]                    [white]VideoMilker v1.0[/white]                    [/bold blue]
        [bold blue]                                                              [/bold blue]
        [bold blue]              [yellow]An intuitive CLI for yt-dlp[/yellow]              [/bold blue]
        [bold blue]                                                              [/bold blue]
        [bold blue][/bold blue]
        """
        
        self.console.print(banner_text, justify="center")
        self.console.print()
    
    def show_menu(self, title: str, options: Dict[str, Tuple[str, Any]], 
                  back_option: bool = True) -> str:
        """Display a menu with options and return the user's choice."""
        # Create menu panel
        menu_content = []
        
        for key, (description, _) in options.items():
            if key == "q":
                menu_content.append(f"[red]{key}[/red] - {description}")
            elif key == "0" and back_option:
                menu_content.append(f"[dim]{key}[/dim] - {description}")
            else:
                menu_content.append(f"[{self.theme['highlight_style']}]{key}[/{self.theme['highlight_style']}] - {description}")
        
        if back_option and "0" not in options:
            menu_content.append(f"[dim]0[/dim] - ← Back")
        
        menu_text = "\n".join(menu_content)
        
        panel = Panel(
            menu_text,
            title=f"[bold {self.theme['border_style']}]{title}[/bold {self.theme['border_style']}]",
            border_style=self.theme['border_style'],
            box=self._get_box_style()
        )
        
        self.console.print(panel)
        
        # Get user input
        while True:
            choice = Prompt.ask(
                f"[{self.theme['highlight_style']}]Select an option[/{self.theme['highlight_style']}]",
                choices=list(options.keys()) + (["0"] if back_option and "0" not in options else [])
            )
            
            if choice in options or (choice == "0" and back_option):
                return choice
            
            self.console.print(f"[{self.theme['error_style']}]Invalid option. Please try again.[/{self.theme['error_style']}]")
    
    def show_input_prompt(self, prompt: str, default: str = "", 
                         required: bool = True) -> str:
        """Display an input prompt."""
        while True:
            value = Prompt.ask(
                f"[{self.theme['highlight_style']}]{prompt}[/{self.theme['highlight_style']}]",
                default=default
            )
            
            if not required or value.strip():
                return value.strip()
            
            self.console.print(f"[{self.theme['error_style']}]This field is required.[/{self.theme['error_style']}]")
    
    def show_confirmation(self, message: str, default: bool = True) -> bool:
        """Display a confirmation dialog."""
        return Confirm.ask(
            f"[{self.theme['highlight_style']}]{message}[/{self.theme['highlight_style']}]",
            default=default
        )
    
    def show_download_confirmation(self, message: str = "Start download?", auto_download: bool = False) -> bool:
        """Display a download confirmation dialog with auto option."""
        if auto_download:
            self.console.print(f"[{self.theme['success_style']}][ON] - Auto Start Downloads[/{self.theme['success_style']}]")
            return True
        
        # Show the confirmation prompt with auto option
        prompt = f"[{self.theme['highlight_style']}]{message} [y/n/auto] (y):[/{self.theme['highlight_style']}]"
        
        while True:
            response = self.console.input(prompt).strip().lower()
            
            if response in ['y', 'yes', '']:
                self.console.print(f"[{self.theme['success_style']}][ON] - Auto Start Downloads[/{self.theme['success_style']}]")
                return True
            elif response in ['n', 'no']:
                self.console.print(f"[{self.theme['warning_style']}][OFF] - Auto Start Downloads[/{self.theme['warning_style']}]")
                return False
            elif response in ['auto']:
                self.console.print(f"[{self.theme['success_style']}][ON] - Auto Start Downloads[/{self.theme['success_style']}]")
                return True
            else:
                self.console.print(f"[{self.theme['error_style']}]Invalid input. Please enter y, n, or auto.[/{self.theme['error_style']}]")
    
    def show_progress(self, description: str, total: Optional[int] = None) -> Progress:
        """Create and display a progress bar."""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TimeElapsedColumn(),
            console=self.console
        )
        
        if total:
            progress.add_task(description, total=total)
        else:
            progress.add_task(description)
        
        return progress
    
    def show_download_progress(self, title: str, progress: float, 
                              speed: float = 0.0, eta: Optional[float] = None,
                              size: int = 0, downloaded: int = 0) -> None:
        """Display download progress with detailed information."""
        progress_text = f"Progress: {'' * int(progress / 5)}{'' * (20 - int(progress / 5))} {progress:.1f}%"
        
        if speed > 0:
            speed_text = f"Speed: {speed / (1024 * 1024):.2f} MB/s"
        else:
            speed_text = "Speed: Calculating..."
        
        if eta:
            eta_text = f"ETA: {eta:.0f}s"
        else:
            eta_text = "ETA: Calculating..."
        
        if size > 0:
            size_text = f"Size: {downloaded / (1024 * 1024):.1f} MB / {size / (1024 * 1024):.1f} MB"
        else:
            size_text = "Size: Unknown"
        
        content = f"""
        [bold]{title}[/bold]
        
        {progress_text}
        {speed_text}    {eta_text}
        {size_text}
        
        [dim]Press Ctrl+C to cancel[/dim]
        """
        
        panel = Panel(
            content,
            title="[bold blue]Download Progress[/bold blue]",
            border_style="blue",
            box=ROUNDED
        )
        
        self.console.print(panel)
    
    def show_error(self, error: str, details: Optional[str] = None) -> None:
        """Display an error message."""
        content = f"[{self.theme['error_style']}]{error}[/{self.theme['error_style']}]"
        
        if details:
            content += f"\n\n[dim]{details}[/dim]"
        
        panel = Panel(
            content,
            title="[bold red]Error[/bold red]",
            border_style="red",
            box=ROUNDED
        )
        
        self.console.print(panel)
    
    def show_success(self, message: str) -> None:
        """Display a success message."""
        panel = Panel(
            f"[{self.theme['success_style']}]{message}[/{self.theme['success_style']}]",
            title="[bold green]Success[/bold green]",
            border_style="green",
            box=ROUNDED
        )
        
        self.console.print(panel)
    
    def show_warning(self, message: str) -> None:
        """Display a warning message."""
        panel = Panel(
            f"[{self.theme['warning_style']}]{message}[/{self.theme['warning_style']}]",
            title="[bold yellow]Warning[/bold yellow]",
            border_style="yellow",
            box=ROUNDED
        )
        
        self.console.print(panel)
    
    def show_info(self, message: str) -> None:
        """Display an info message."""
        panel = Panel(
            f"[{self.theme.get('info_style', 'cyan')}]{message}[/{self.theme.get('info_style', 'cyan')}]",
            title="[bold cyan]Information[/bold cyan]",
            border_style="cyan",
            box=ROUNDED
        )
        
        self.console.print(panel)
    
    def show_table(self, title: str, headers: List[str], rows: List[List[str]]) -> None:
        """Display a table."""
        table = Table(title=title, border_style=self.theme['border_style'])
        
        for header in headers:
            table.add_column(header, style=self.theme['highlight_style'])
        
        for row in rows:
            table.add_row(*row)
        
        self.console.print(table)
    
    def show_download_summary(self, downloads: List[Dict[str, Any]]) -> None:
        """Display a summary of downloads."""
        if not downloads:
            self.show_info("No downloads to display.")
            return
        
        table = Table(title="Download Summary", border_style=self.theme['border_style'])
        table.add_column("Title", style="green", no_wrap=True)
        table.add_column("Status", style="yellow")
        table.add_column("Size", style="blue")
        table.add_column("Duration", style="magenta")
        
        for download in downloads:
            title = download.get('title', 'Unknown')[:40] + "..." if len(download.get('title', '')) > 40 else download.get('title', 'Unknown')
            status = download.get('status', 'unknown')
            size = f"{download.get('size_mb', 0):.1f} MB" if download.get('size_mb') else "Unknown"
            duration = str(download.get('duration', 'Unknown'))
            
            table.add_row(title, status, size, duration)
        
        self.console.print(table)
    
    def show_settings(self, settings: Settings) -> None:
        """Display current settings."""
        content = f"""
        [bold]Download Settings:[/bold]
        Path: {settings.download.path}
        Create Day Folders: {settings.download.create_day_folders}
        File Naming: {settings.download.file_naming}
        Default Quality: {settings.download.default_quality}
        Default Format: {settings.download.default_format}
        Max Concurrent: {settings.download.max_concurrent}
        
        [bold]UI Settings:[/bold]
        Theme: {settings.ui.theme}
        Show Progress Details: {settings.ui.show_progress_details}
        Confirm Before Quit: {settings.ui.confirm_before_quit}
        
        [bold]History Settings:[/bold]
        Max Entries: {settings.history.max_entries}
        Auto Cleanup: {settings.history.auto_cleanup}
        Cleanup Days: {settings.history.cleanup_days}
        """
        
        panel = Panel(
            content,
            title="[bold blue]Current Settings[/bold blue]",
            border_style="blue",
            box=ROUNDED
        )
        
        self.console.print(panel)
    
    def show_help(self) -> None:
        """Display help information."""
        help_text = """
        [bold]VideoMilker - Help[/bold]
        
        [bold]Quick Download:[/bold]
        Download a single video with default settings.
        
        [bold]Batch Download:[/bold]
        Download multiple videos from a list or file.
        
        [bold]Options & Settings:[/bold]
        Configure download paths, formats, and preferences.
        
        [bold]Download History:[/bold]
        View and manage your download history.
        
        [bold]Navigation:[/bold]
        • Use number keys to select options
        • Press '0' to go back
        • Press 'q' to quit
        • Press Ctrl+C to cancel operations
        
        [bold]Tips:[/bold]
        • URLs are automatically validated
        • Files are organized by date
        • Progress is shown in real-time
        • Errors are handled gracefully
        """
        
        panel = Panel(
            help_text,
            title="[bold green]Help & Information[/bold green]",
            border_style="green",
            box=ROUNDED
        )
        
        self.console.print(panel)
    
    def _get_box_style(self) -> Any:
        """Get the box style based on theme."""
        style = self.theme.get('menu_style', 'rounded')
        
        if style == 'rounded':
            return ROUNDED
        elif style == 'double':
            return DOUBLE
        elif style == 'single':
            return SIMPLE
        else:
            return ROUNDED
    
    def clear_screen(self) -> None:
        """Clear the console screen."""
        self.console.clear()
    
    def show_pause(self) -> None:
        """Display a pause prompt."""
        self.console.print()
        Prompt.ask(f"[{self.theme['highlight_style']}]Press Enter to continue[/{self.theme['highlight_style']}]")
    
    def show_separator(self) -> None:
        """Display a separator line."""
        self.console.print(f"[{self.theme['border_style']}][/{self.theme['border_style']}]" * 80)
