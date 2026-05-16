import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory, askopenfilenames

from ..application.jobs import run_conversion_batch, run_download_batch
from ..domain.errors import describe_error
from ..domain.models import OutputFormat
from ..utils.logging import ERROR_LOG_PATH, write_error_log
from ..utils.urls import parse_download_urls
from .progress import run_with_progress


def show_error(parent, title, error):
    write_error_log(error)
    messagebox.showerror(
        title,
        f"{describe_error(error)}\n\nFull details were saved to:\n{ERROR_LOG_PATH}",
        parent=parent,
    )


def ask_download_urls(root):
    result = {"cancelled": True, "text": ""}
    done = tk.BooleanVar(root, value=False)

    root.title("MP4 / MP3 Converter")
    root.geometry("720x360")
    root.minsize(560, 280)
    root.deiconify()
    root.lift()
    root.focus_force()

    container = tk.Frame(root)
    container.pack(fill=tk.BOTH, expand=True)

    label = tk.Label(
        container,
        text=(
            "Paste one or more video links below, one per line.\n"
            "Leave the box empty and click Continue to select local MP4 files."
        ),
        justify="left",
        anchor="w",
        padx=12,
        pady=10,
    )
    label.pack(fill=tk.X)

    text_frame = tk.Frame(container, padx=12)
    text_frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_box = tk.Text(
        text_frame, height=10, wrap="word", yscrollcommand=scrollbar.set
    )
    text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_box.yview)

    button_frame = tk.Frame(container, padx=12, pady=10)
    button_frame.pack(fill=tk.X)

    def submit():
        result["cancelled"] = False
        result["text"] = text_box.get("1.0", tk.END)
        done.set(True)

    def cancel():
        done.set(True)

    tk.Button(button_frame, text="Continue", command=submit).pack(side=tk.RIGHT)
    tk.Button(button_frame, text="Cancel", command=cancel).pack(
        side=tk.RIGHT, padx=(0, 8)
    )

    root.protocol("WM_DELETE_WINDOW", cancel)
    text_box.focus_set()
    root.wait_variable(done)
    container.destroy()
    root.withdraw()

    if result["cancelled"]:
        return None

    return parse_download_urls(result["text"])


def choose_videos(root):
    return askopenfilenames(
        parent=root,
        title="Select MP4 files to convert",
        filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*")),
    )


def choose_output_format(root):
    download_mp3 = messagebox.askyesnocancel(
        "Download Format",
        "Download as MP3?\n\nYes = MP3 audio\nNo = MP4 video\nCancel = stop",
        parent=root,
    )

    if download_mp3 is None:
        return None

    return OutputFormat.MP3 if download_mp3 else OutputFormat.MP4


def choose_output_dir(root):
    return askdirectory(parent=root, title="Choose download folder")


def handle_online_downloads(root, urls):
    output_format = choose_output_format(root)
    if output_format is None:
        return

    output_dir = choose_output_dir(root)
    if not output_dir:
        messagebox.showinfo("Online Downloader", "No folder selected.", parent=root)
        return

    def worker(report):
        return run_download_batch(urls, output_dir, output_format, report)

    try:
        batch = run_with_progress(
            root,
            "Online Downloader",
            f"Preparing to download {len(urls)} link(s)...",
            worker,
        )
    except Exception as error:
        show_error(root, "Online Downloader", error)
        return

    if batch.failed:
        failed_message = "\n".join(
            f"{url}: {error}" for url, error in batch.failed[:5]
        )
        if len(batch.failed) > 5:
            failed_message += f"\n...and {len(batch.failed) - 5} more."

        messagebox.showwarning(
            "Online Downloader",
            f"Downloaded {len(batch.succeeded)} of {batch.total} links as "
            f"{output_format.value.upper()}.\n\n"
            f"Failed links:\n{failed_message}\n\n"
            f"Full details were saved to:\n{ERROR_LOG_PATH}",
            parent=root,
        )
    else:
        messagebox.showinfo(
            "Online Downloader",
            f"Downloaded {len(batch.succeeded)} links as {output_format.value.upper()}.\n\n"
            f"Saved in:\n{output_dir}",
            parent=root,
        )


def handle_local_conversions(root):
    video_paths = choose_videos(root)
    if not video_paths:
        messagebox.showinfo("MP4 to MP3", "No files selected.", parent=root)
        return

    def worker(report):
        return run_conversion_batch(video_paths, report)

    try:
        batch = run_with_progress(
            root,
            "MP4 to MP3",
            f"Preparing to convert {len(video_paths)} file(s)...",
            worker,
        )
    except Exception as error:
        show_error(root, "MP4 to MP3", error)
        return

    if batch.failed:
        failed_message = "\n".join(
            f"{name}: {error}" for name, error in batch.failed
        )
        messagebox.showwarning(
            "MP4 to MP3",
            f"Converted {len(batch.succeeded)} of {batch.total} files.\n\n"
            f"Failed files:\n{failed_message}",
            parent=root,
        )
    else:
        messagebox.showinfo(
            "MP4 to MP3",
            f"Converted {len(batch.succeeded)} files successfully.",
            parent=root,
        )


def gui_main():
    root = tk.Tk()

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
