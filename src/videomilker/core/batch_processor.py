"""Batch processing for VideoMilker downloads."""

from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from ..config.settings import Settings
from ..core.downloader import VideoDownloader
from ..core.file_manager import FileManager
from ..exceptions.download_errors import BatchProcessingError


class BatchProcessor:
    """Handles batch download processing."""
    
    def __init__(self, settings: Settings, console: Optional[Console] = None):
        """Initialize the batch processor."""
        self.settings = settings
        self.console = console or Console()
        self.downloader = VideoDownloader(settings, console)
        self.file_manager = FileManager(settings)
    
    def load_urls_from_file(self, file_path: Path) -> List[str]:
        """Load URLs from a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            urls = []
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip comments and empty lines
                    urls.append(line)
            
            return urls
            
        except Exception as e:
            raise BatchProcessingError(f"Failed to load URLs from file: {e}")
    
    def save_urls_to_file(self, urls: List[str], file_path: Path) -> None:
        """Save URLs to a text file."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                for url in urls:
                    f.write(f"{url}\n")
                    
        except Exception as e:
            raise BatchProcessingError(f"Failed to save URLs to file: {e}")
    
    def process_batch(self, urls: List[str], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Process a batch of URLs for download."""
        if not urls:
            return []
        
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
            console=self.console
        ) as progress:
            
            task = progress.add_task(f"Processing {total_urls} URLs", total=total_urls)
            
            for i, url in enumerate(urls):
                try:
                    # Update progress description
                    progress.update(task, description=f"Downloading {i+1}/{total_urls}: {url[:50]}...")
                    
                    # Download the video
                    result = self.downloader.download_single(url, options)
                    
                    # Ensure result has the URL
                    if isinstance(result, dict):
                        result['url'] = url
                        result['timestamp'] = datetime.now().isoformat()
                    
                    results.append(result)
                    
                    # Update progress
                    progress.advance(task)
                    
                except Exception as e:
                    # Log error and continue
                    error_result = {
                        'status': 'failed',
                        'url': url,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    results.append(error_result)
                    progress.advance(task)
                    
                    self.console.print(f"[red]Failed to download {url}: {e}[/red]")
        
        # Save batch log
        self._save_batch_log(urls, results)
        
        return results
    
    def process_batch_with_validation(self, urls: List[str], 
                                    options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
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
    
    def process_batch_with_limits(self, urls: List[str], 
                                max_concurrent: Optional[int] = None,
                                options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Process batch with concurrency limits."""
        if max_concurrent is None:
            max_concurrent = self.settings.download.max_concurrent
        
        # Split URLs into chunks
        chunks = [urls[i:i + max_concurrent] for i in range(0, len(urls), max_concurrent)]
        
        all_results = []
        
        for chunk in chunks:
            chunk_results = self.process_batch(chunk, options)
            all_results.extend(chunk_results)
        
        return all_results
    
    def _save_batch_log(self, urls: List[str], results: List[Dict[str, Any]]) -> None:
        """Save batch processing log."""
        try:
            # Get batch folder
            batch_folder = self.file_manager.get_batch_folder()
            
            # Create log data
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'total_urls': len(urls),
                'successful': len([r for r in results if r.get('status') == 'completed']),
                'failed': len([r for r in results if r.get('status') == 'failed']),
                'urls': urls,
                'results': results
            }
            
            # Save log file
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            log_file = batch_folder / f"batch_log_{timestamp}.json"
            
            import json
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.console.print(f"[yellow]Warning: Failed to save batch log: {e}[/yellow]")
    
    def get_batch_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics from batch processing results."""
        total = len(results)
        successful = len([r for r in results if r.get('status') == 'completed'])
        failed = len([r for r in results if r.get('status') == 'failed'])
        
        total_size = sum(
            r.get('size', 0) for r in results 
            if r.get('status') == 'completed' and r.get('size')
        )
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024) if total_size > 0 else 0
        }
    
    def retry_failed_downloads(self, results: List[Dict[str, Any]], 
                             options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retry failed downloads from a previous batch."""
        failed_urls = [
            r['url'] for r in results 
            if r.get('status') == 'failed' and r.get('url')
        ]
        
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
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
                
            self.console.print(f"[green]Batch template created: {template_path}[/green]")
            
        except Exception as e:
            raise BatchProcessingError(f"Failed to create batch template: {e}")
    
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
                'total_urls': len(urls),
                'valid_urls': len(valid_urls),
                'invalid_urls': len(invalid_urls),
                'valid_url_list': valid_urls,
                'invalid_url_list': invalid_urls,
                'is_valid': len(invalid_urls) == 0
            }
            
        except Exception as e:
            raise BatchProcessingError(f"Failed to validate batch file: {e}")
    
    def estimate_batch_size(self, urls: List[str]) -> Dict[str, Any]:
        """Estimate the total size of a batch download."""
        total_size = 0
        size_estimates = []
        
        for url in urls:
            try:
                # Get video info to estimate size
                info = self.downloader.get_video_info(url)
                size = info.get('filesize', 0)
                
                if size:
                    total_size += size
                    size_estimates.append({
                        'url': url,
                        'title': info.get('title', 'Unknown'),
                        'size': size,
                        'size_mb': size / (1024 * 1024)
                    })
                else:
                    size_estimates.append({
                        'url': url,
                        'title': info.get('title', 'Unknown'),
                        'size': 0,
                        'size_mb': 0
                    })
                    
            except Exception:
                size_estimates.append({
                    'url': url,
                    'title': 'Unknown',
                    'size': 0,
                    'size_mb': 0
                })
        
        return {
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'total_size_gb': total_size / (1024 * 1024 * 1024),
            'url_count': len(urls),
            'size_estimates': size_estimates
        } 