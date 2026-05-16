from pathlib import Path
from typing import Protocol

from ..domain.models import OutputFormat


class Downloader(Protocol):
    name: str

    def supports(self, url: str) -> bool: ...

    def download(self, url: str, output_dir: str | Path, output_format: OutputFormat) -> str: ...


class NoDownloaderError(ValueError):
    pass


class DownloaderRegistry:
    def __init__(self):
        self._providers: list[Downloader] = []

    def register(self, provider: Downloader):
        self._providers.append(provider)

    def resolve(self, url: str) -> Downloader:
        for provider in self._providers:
            if provider.supports(url):
                return provider

        raise NoDownloaderError(f"No downloader supports this URL: {url}")
