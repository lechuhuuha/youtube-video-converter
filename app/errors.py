import re
import sys
import traceback

from .paths import ERROR_LOG_PATH


DOWNLOAD_BLOCKED_HELP = (
    "The video site blocked this download with HTTP 403.\n\n"
    "Try these fixes:\n"
    "1. Use Python 3.10 or newer.\n"
    '2. Run: python -m pip install -U "yt-dlp[default,curl-cffi]" '
    "imageio-ffmpeg moviepy\n"
    "3. If it still fails, this video may need a yt-dlp PO-token provider:\n"
    "https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide"
)


COOKIE_FILE_HELP = (
    "The video may require your browser session. Export browser cookies to "
    "cookies.txt and place that file beside main.py, then run again.\n\n"
    "Do not disable Chrome security settings for this. cookies.txt is sensitive, "
    "so keep it private and delete it when you no longer need it."
)


COOKIE_RETRY_ERROR_TERMS = (
    "this video is not available",
    "video unavailable",
    "private video",
    "this video is private",
    "removed by the uploader",
    "has been removed",
    "not available in your country",
    "members-only",
    "sign in to confirm your age",
    "age-restricted",
)


def get_python_version_text():
    return ".".join(str(part) for part in sys.version_info[:3])


def build_python_too_old_help():
    return (
        "Online downloads need Python 3.10 or newer because yt-dlp no longer "
        "supports Python 3.9.\n\n"
        f"Current Python: {get_python_version_text()}\n"
        f"Current executable: {sys.executable}\n\n"
        "Create or activate your Python 3.14 venv and reinstall dependencies:\n\n"
        "deactivate\n"
        "py -3.14 -m venv .venv314\n"
        ".venv314\\Scripts\\activate\n"
        "python --version\n"
        "python -m pip install -U -r requirements.txt\n"
        "python main.py"
    )


def describe_error(error):
    error_type = type(error).__name__
    error_message = str(error).strip()

    if error_message:
        return f"{error_type}: {error_message}"

    return f"{error_type}: No error message was provided by the library."


def write_error_log(error, context=None, append=False):
    details = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    if context:
        details = f"{context}\n{details}"

    if append:
        with ERROR_LOG_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write(f"\n\n{details}")
    else:
        ERROR_LOG_PATH.write_text(details, encoding="utf-8")

    print(details, file=sys.stderr)


def build_download_error(error, tried_cookie_file=False):
    if error is None:
        return RuntimeError("Download failed before yt-dlp returned an error.")

    error_message = str(error)
    error_message_lower = error_message.lower()

    cookie_error_terms = (
        "failed to load cookies",
        "failed to decrypt with dpapi",
        "could not copy chrome cookie database",
    )

    if any(term in error_message_lower for term in cookie_error_terms):
        return RuntimeError(
            "Could not load cookies.txt. Export a fresh cookies.txt file and place "
            "it beside main.py, then run again.\n\n"
            f"Original error:\n{strip_ansi(error_message)}"
        )

    if any(term in error_message_lower for term in COOKIE_RETRY_ERROR_TERMS):
        if tried_cookie_file:
            return RuntimeError(
                "The program tried cookies.txt, but YouTube still did not make "
                "the video available. The video may be private, restricted, or "
                "unavailable to that browser session.\n\n"
                f"Original error:\n{strip_ansi(error_message)}"
            )

        return RuntimeError(
            f"YouTube says this video is unavailable.\n\n{COOKIE_FILE_HELP}\n\n"
            f"Original error:\n{strip_ansi(error_message)}"
        )

    blocked_terms = ("403", "forbidden", "po token", "sabr")

    if any(term in error_message_lower for term in blocked_terms):
        return RuntimeError(
            f"{DOWNLOAD_BLOCKED_HELP}\n\nOriginal error:\n{strip_ansi(error_message)}"
        )

    if "requested format is not available" in error_message_lower:
        return RuntimeError(
            "YouTube did not provide a downloadable audio/video format for the "
            "selected output type. Try exporting a fresh cookies.txt from a new "
            "private/incognito YouTube session. If it still fails, install Node.js "
            "or Deno, update yt-dlp, or try the other output type.\n\n"
            f"Original error:\n{strip_ansi(error_message)}"
        )

    return error


def strip_ansi(text):
    return re.sub(r"\x1b\[[0-9;]*m", "", text)
