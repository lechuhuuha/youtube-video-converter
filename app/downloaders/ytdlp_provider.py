from urllib.parse import urlparse

from .ytdlp_facade import YtDlpFacade


class YtDlpProvider:
    name = "yt-dlp"

    def __init__(self, facade=None):
        self.facade = facade or YtDlpFacade()

    def supports(self, url: str) -> bool:
        return urlparse(url).scheme in {"http", "https"}

    def download(self, url, output_dir, output_format):
        return self.facade.download(url, output_dir, output_format)
