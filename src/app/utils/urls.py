import re
from urllib.parse import parse_qs, urlparse


URL_PATTERN = re.compile(r"https?://[^\s,]+", re.IGNORECASE)


def parse_download_urls(text):
    urls = []
    seen = set()

    for match in URL_PATTERN.finditer(text):
        url = normalize_download_url(match.group(0).rstrip(").]"))
        if url and url not in seen:
            urls.append(url)
            seen.add(url)

    return urls


def normalize_download_url(url):
    return normalize_youtube_url(url) or url


def normalize_youtube_url(url):
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")
    video_id = None

    if host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/")[2]
        elif parsed.path.startswith("/embed/"):
            video_id = parsed.path.split("/")[2]
    elif host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]

    if not video_id:
        return None

    return f"https://www.youtube.com/watch?v={video_id}"
