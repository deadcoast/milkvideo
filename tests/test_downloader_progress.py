"""Tests for VideoDownloader progress tracking."""

from src.videomilker.core.downloader import VideoDownloader


def test_progress_updates_single_download(monkeypatch, test_settings):
    """Ensure progress updates include download ID and metrics."""

    downloader = VideoDownloader(test_settings)
    progress_calls = []

    # Spy on progress updates
    original_update = downloader.progress_tracker.update_progress

    def capture_progress(download_id, progress, speed=0.0, eta=None, size=0, downloaded=0):
        progress_calls.append((download_id, progress, speed, eta, size, downloaded))
        return original_update(download_id, progress, speed, eta, size, downloaded)

    monkeypatch.setattr(downloader.progress_tracker, "update_progress", capture_progress)

    class MockYDL:
        def __init__(self, options):
            self.options = options

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def extract_info(self, url, download=False):
            return {
                "id": "abc123",
                "title": "Sample Video",
                "requested_downloads": [{"filepath": "sample.mp4"}],
            }

        def download(self, urls):
            for hook in self.options["progress_hooks"]:
                hook(
                    {
                        "status": "downloading",
                        "downloaded_bytes": 512,
                        "total_bytes": 1024,
                        "speed": 1000,
                        "eta": 5,
                        "filename": "sample.mp4",
                    }
                )
            for hook in self.options["progress_hooks"]:
                hook({"status": "finished"})

    monkeypatch.setattr("src.videomilker.core.downloader.yt_dlp.YoutubeDL", MockYDL)

    downloader.download_single("https://example.com/video")

    current_id = downloader.current_download["id"]
    tracked_progress = downloader.progress_tracker.get_download(current_id)

    assert progress_calls, "Progress updates were not captured"
    assert progress_calls[0][0] == current_id
    assert progress_calls[0][1] == 50.0
    assert progress_calls[0][2] == 1000
    assert progress_calls[0][3] == 5
    assert progress_calls[0][4] == 1024
    assert progress_calls[0][5] == 512

    assert tracked_progress is not None
    assert tracked_progress.progress == 100.0
    assert tracked_progress.speed == 1000
    assert tracked_progress.eta == 5
    assert tracked_progress.size == 1024
    assert tracked_progress.downloaded == 512
    assert tracked_progress.status == "completed"
