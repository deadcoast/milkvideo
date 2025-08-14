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
@click.option("--config", "-c", help="Path to configuration file", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--download-path", "-d", help="Set download path", type=click.Path())
@click.option("--link", "-l", help="Quick download - download URL directly with default settings", type=str)
@click.option("--url", "-u", help="Download a single URL directly (legacy option, use --link instead)", type=str)
def main(config: str = None, verbose: bool = False, download_path: str = None, link: str = None, url: str = None):
    """VideoMilker - An intuitive CLI interface for yt-dlp."""

    try:
        # Initialize configuration manager
        config_manager = ConfigManager()

        # Load configuration
        settings = config_manager.load_config(config_path=config)

        # Validate configuration on startup
        is_valid, errors = config_manager.validate_config(settings)

        if not is_valid:
            console.print("[yellow]Configuration validation found issues:[/yellow]")
            for error in errors:
                console.print(f"[red]  • {error}[/red]")

            # Try to auto-fix configuration issues
            if verbose:
                console.print("[cyan]Attempting to auto-fix configuration issues...[/cyan]")

            fixes_applied, fixes = config_manager.auto_fix_config(settings)

            if fixes_applied:
                console.print("[green]Auto-fixed configuration issues:[/green]")
                for fix in fixes:
                    console.print(f"[green]   {fix}[/green]")

                # Re-validate after fixes
                is_valid, remaining_errors = config_manager.validate_config(settings)
                if is_valid:
                    console.print("[green]Configuration is now valid![/green]")
                else:
                    console.print("[yellow]Some configuration issues remain:[/yellow]")
                    for error in remaining_errors:
                        console.print(f"[red]  • {error}[/red]")
            else:
                console.print("[yellow]Could not auto-fix configuration issues. Please check your settings.[/yellow]")

            if verbose:
                console.print("[dim]Press Enter to continue or Ctrl+C to exit...[/dim]")
                try:
                    input()
                except KeyboardInterrupt:
                    sys.exit(0)

        # Override download path if specified
        if download_path:
            settings.download.path = download_path
            config_manager.save_config()

        if download_url := link or url:
            from .core.downloader import VideoDownloader

            downloader = VideoDownloader(settings, console)

            if not downloader.validate_url(download_url):
                console.print(f"[red]Invalid URL: {download_url}[/red]")
                sys.exit(1)

            console.print(f"[cyan]Downloading: {download_url}[/cyan]")
            try:
                result = downloader.download_single(download_url)
                if result["status"] == "completed":
                    console.print(f"[green]Download completed: {result.get('filename', 'Unknown')}[/green]")
                else:
                    console.print("[red]Download failed[/red]")
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
