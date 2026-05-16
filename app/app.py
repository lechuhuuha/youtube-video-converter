from pathlib import Path
from tkinter import Tk, messagebox

from .downloaders import create_default_registry
from .errors import describe_error, write_error_log
from .local_conversion import convert_to_mp3
from .paths import ERROR_LOG_PATH
from .ui import (
    ask_download_urls,
    choose_output_dir,
    choose_output_format,
    choose_videos,
    run_with_progress,
    show_error,
)


def handle_online_downloads(root, urls):
    downloader_registry = create_default_registry()
    output_format = choose_output_format(root)
    if output_format is None:
        return

    output_dir = choose_output_dir(root)
    if not output_dir:
        messagebox.showinfo("Online Downloader", "No folder selected.", parent=root)
        return

    def worker(report):
        downloaded = []
        failed = []

        for index, url in enumerate(urls, start=1):
            report(f"Downloading {index} of {len(urls)}:\n{url}")
            print(f"Downloading {index} of {len(urls)}: {url}")
            try:
                provider = downloader_registry.resolve(url)
                title = provider.download(url, output_dir, output_format)
            except Exception as error:
                failed.append((url, describe_error(error)))
                write_error_log(error, context=f"URL: {url}", append=len(failed) > 1)
            else:
                downloaded.append(title)

        return downloaded, failed

    try:
        downloaded, failed = run_with_progress(
            root,
            "Online Downloader",
            f"Preparing to download {len(urls)} link(s)...",
            worker,
        )
    except Exception as error:
        show_error(root, "Online Downloader", error)
        return

    if failed:
        failed_message = "\n".join(f"{url}: {error}" for url, error in failed[:5])
        if len(failed) > 5:
            failed_message += f"\n...and {len(failed) - 5} more."

        messagebox.showwarning(
            "Online Downloader",
            f"Downloaded {len(downloaded)} of {len(urls)} links as "
            f"{output_format.upper()}.\n\n"
            f"Failed links:\n{failed_message}\n\n"
            f"Full details were saved to:\n{ERROR_LOG_PATH}",
            parent=root,
        )
    else:
        messagebox.showinfo(
            "Online Downloader",
            f"Downloaded {len(downloaded)} links as {output_format.upper()}.\n\n"
            f"Saved in:\n{output_dir}",
            parent=root,
        )


def handle_local_conversions(root):
    video_paths = choose_videos(root)
    if not video_paths:
        messagebox.showinfo("MP4 to MP3", "No files selected.", parent=root)
        return

    def worker(report):
        converted = []
        failed = []

        for index, video_path in enumerate(video_paths, start=1):
            report(
                f"Converting {index} of {len(video_paths)}:\n"
                f"{Path(video_path).name}"
            )
            try:
                converted.append(convert_to_mp3(video_path))
            except Exception as error:
                failed.append((Path(video_path).name, describe_error(error)))

        return converted, failed

    try:
        converted, failed = run_with_progress(
            root,
            "MP4 to MP3",
            f"Preparing to convert {len(video_paths)} file(s)...",
            worker,
        )
    except Exception as error:
        show_error(root, "MP4 to MP3", error)
        return

    if failed:
        failed_message = "\n".join(f"{name}: {error}" for name, error in failed)
        messagebox.showwarning(
            "MP4 to MP3",
            f"Converted {len(converted)} of {len(video_paths)} files.\n\n"
            f"Failed files:\n{failed_message}",
            parent=root,
        )
    else:
        messagebox.showinfo(
            "MP4 to MP3",
            f"Converted {len(converted)} files successfully.",
            parent=root,
        )


def main():
    root = Tk()

    try:
        download_urls = ask_download_urls(root)

        if download_urls is None:
            return

        if download_urls:
            handle_online_downloads(root, download_urls)
        else:
            handle_local_conversions(root)
    finally:
        root.destroy()
