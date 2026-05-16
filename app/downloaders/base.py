from pathlib import Path
from typing import Protocol


class DownloadProvider(Protocol):
    name: str

    def supports(self, url: str) -> bool:
        ...

    def download(self, url: str, output_dir: str | Path, output_format: str) -> str:
        ...
