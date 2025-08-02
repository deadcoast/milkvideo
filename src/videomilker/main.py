#!/usr/bin/env python3
"""
VideoMilker main entry point.

This module provides the main CLI interface for VideoMilker.
"""

import sys
import click
from rich.console import Console
from rich.traceback import install

from .cli.menu_system import MenuSystem
from .config.config_manager import ConfigManager
from .version import __version__

# Install rich traceback handler
install(show_locals=True)

console = Console()


@click.command()
@click.version_option(__version__)
@click.option(
    "--config", 
    "-c", 
    help="Path to configuration file",
    type=click.Path(exists=True)
)
@click.option(
    "--verbose", 
    "-v", 
    is_flag=True, 
    help="Enable verbose logging"
)
@click.option(
    "--download-path",
    "-d",
    help="Set download path",
    type=click.Path()
)
@click.option(
    "--link",
    "-l",
    help="Quick download - download URL directly with default settings",
    type=str
)
@click.option(
    "--url",
    "-u",
    help="Download a single URL directly (legacy option, use --link instead)",
    type=str
)
def main(config: str = None, verbose: bool = False, download_path: str = None, link: str = None, url: str = None):
    """VideoMilker - An intuitive CLI interface for yt-dlp."""
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager()
        
        # Load configuration
        settings = config_manager.load_config(config_path=config)
        
        # Override download path if specified
        if download_path:
            settings.download.path = download_path
            config_manager.save_config()
        
        # Handle quick link download (--link or -l)
        download_url = link or url
        if download_url:
            from .core.downloader import VideoDownloader
            downloader = VideoDownloader(settings, console)
            
            if not downloader.validate_url(download_url):
                console.print(f"[red]Invalid URL: {download_url}[/red]")
                sys.exit(1)
            
            console.print(f"[cyan]Downloading: {download_url}[/cyan]")
            try:
                result = downloader.download_single(download_url)
                if result['status'] == 'completed':
                    console.print(f"[green]Download completed: {result.get('filename', 'Unknown')}[/green]")
                else:
                    console.print(f"[red]Download failed[/red]")
                    sys.exit(1)
            except Exception as e:
                console.print(f"[red]Download failed: {e}[/red]")
                sys.exit(1)
            return
        
        # Initialize menu system (default behavior when no URL provided)
        menu_system = MenuSystem(settings=settings, verbose=verbose)
        
        # Start the application
        menu_system.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Application interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
