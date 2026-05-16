from ..ports.downloader import DownloaderRegistry
from .ytdlp_downloader import YtDlpDownloader


def create_default_registry():
    registry = DownloaderRegistry()
    registry.register(YtDlpDownloader())
    return registry
