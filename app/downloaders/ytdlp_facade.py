import shutil
import sys
from pathlib import Path

from ..errors import (
    COOKIE_RETRY_ERROR_TERMS,
    build_download_error,
    build_python_too_old_help,
)
from ..paths import COOKIES_PATH


class YtDlpFacade:
    def __init__(self, cookies_path=COOKIES_PATH):
        self.cookies_path = Path(cookies_path)

    def download(self, url, output_dir, output_format):
        if sys.version_info < (3, 10):
            raise RuntimeError(build_python_too_old_help())

        YoutubeDL = self._load_youtube_dl()
        last_error = None
        cookie_sources = self._cookie_sources()

        for cookie_source in cookie_sources:
            for prefer_hls in self._hls_attempts(output_format):
                options = self.build_options(
                    output_dir,
                    output_format,
                    prefer_hls,
                    cookie_source,
                )

                try:
                    with YoutubeDL(options) as downloader:
                        info = downloader.extract_info(url, download=True)
                except Exception as error:
                    last_error = error
                    if should_retry_with_cookie_file(error):
                        if cookie_source == cookie_sources[-1]:
                            raise build_download_error(
                                error,
                                tried_cookie_file=cookie_source == "file",
                            )

                        break
                else:
                    return info.get("title", "Online download")

        raise build_download_error(last_error)

    def build_options(
        self,
        output_dir,
        output_format,
        prefer_hls,
        cookie_source=None,
    ):
        output_template = str(Path(output_dir) / "%(title).200B [%(id)s].%(ext)s")
        options = {
            "noplaylist": True,
            "outtmpl": output_template,
            "retries": 3,
            "fragment_retries": 3,
            "sleep_interval_requests": 1,
            "sleep_interval": 2,
            "max_sleep_interval": 5,
            "windowsfilenames": True,
        }

        js_runtimes = get_available_js_runtimes()
        if js_runtimes:
            options["js_runtimes"] = js_runtimes

        if cookie_source == "file":
            options["cookiefile"] = str(self.cookies_path)

        try:
            import imageio_ffmpeg
        except ModuleNotFoundError:
            pass
        else:
            options["ffmpeg_location"] = imageio_ffmpeg.get_ffmpeg_exe()

        try:
            import curl_cffi  # noqa: F401
            from yt_dlp.networking.impersonate import ImpersonateTarget
        except ModuleNotFoundError:
            pass
        else:
            options["impersonate"] = ImpersonateTarget.from_str("chrome")

        if output_format == "mp3":
            options.update(
                {
                    "format": build_audio_format_selector(prefer_hls),
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }
            )
        else:
            options.update(
                {
                    "format": build_video_format_selector(prefer_hls),
                    "format_sort": ["fps", "res", "br"],
                    "format_sort_force": True,
                    "merge_output_format": "mp4",
                }
            )

        return options

    def _cookie_sources(self):
        sources = [None]

        if self.cookies_path.exists():
            sources.append("file")

        return sources

    def _hls_attempts(self, output_format):
        if output_format == "mp3":
            return False, True

        return True, False

    def _load_youtube_dl(self):
        try:
            from yt_dlp import YoutubeDL
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "yt-dlp is not installed. Install it with: pip install yt-dlp"
            ) from error

        return YoutubeDL


def build_audio_format_selector(prefer_hls):
    if prefer_hls:
        return "ba*[protocol^=m3u8]/b*[protocol^=m3u8]/ba*/best"

    return "ba*/bestaudio/best"


def build_video_format_selector(prefer_hls):
    if prefer_hls:
        return (
            "bv*[fps>=50][ext=mp4][protocol^=m3u8]+ba[ext=m4a][protocol^=m3u8]/"
            "b[fps>=50][ext=mp4][protocol^=m3u8]/"
            "bv*[fps>=50][protocol^=m3u8]+ba[protocol^=m3u8]/"
            "b[fps>=50][protocol^=m3u8]/"
            "bv*[ext=mp4][protocol^=m3u8]+ba[ext=m4a][protocol^=m3u8]/"
            "b[ext=mp4][protocol^=m3u8]/"
            "bv*[protocol^=m3u8]+ba[protocol^=m3u8]/"
            "b[protocol^=m3u8]/best"
        )

    return (
        "bv*[fps>=50][ext=mp4]+ba[ext=m4a]/"
        "b[fps>=50][ext=mp4]/"
        "bv*[fps>=50]+ba/"
        "b[fps>=50]/"
        "bv*[ext=mp4]+ba[ext=m4a]/"
        "b[ext=mp4]/best[ext=mp4]/best"
    )


def get_available_js_runtimes():
    runtimes = {}

    for runtime in ("deno", "node", "quickjs", "bun"):
        if shutil.which(runtime):
            runtimes[runtime] = {}

    return runtimes


def should_retry_with_cookie_file(error):
    error_message = str(error).lower()
    return any(term in error_message for term in COOKIE_RETRY_ERROR_TERMS)
