from pathlib import Path

from .. import PROJECT_ROOT


DEFAULT_COOKIES_PATH = PROJECT_ROOT / "cookies.txt"


class CookieStore:
    def __init__(self, cookies_path=DEFAULT_COOKIES_PATH):
        self.path = Path(cookies_path)

    def exists(self):
        return self.path.exists()

    def cookie_sources(self):
        sources = [None]
        if self.exists():
            sources.append("file")
        return sources
