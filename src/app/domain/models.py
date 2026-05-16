from dataclasses import dataclass, field
from enum import Enum


class OutputFormat(str, Enum):
    MP3 = "mp3"
    MP4 = "mp4"


@dataclass
class BatchResult:
    succeeded: list = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.succeeded) + len(self.failed)

    @property
    def all_succeeded(self) -> bool:
        return not self.failed
