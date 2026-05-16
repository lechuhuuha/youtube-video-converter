import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.filedialog import askdirectory, askopenfilenames

from .errors import describe_error, write_error_log
from .paths import ERROR_LOG_PATH
from .urls import parse_download_urls


def show_error(parent, title, error):
    write_error_log(error)
    messagebox.showerror(
        title,
        f"{describe_error(error)}\n\nFull details were saved to:\n{ERROR_LOG_PATH}",
        parent=parent,
    )


def run_with_progress(root, title, initial_message, worker):
    updates = queue.Queue()
    result = {"status": None, "value": None}

    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.geometry("520x150")
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.lift()
    dialog.focus_force()
    dialog.attributes("-topmost", True)
    dialog.after(250, lambda: dialog.attributes("-topmost", False))

    message_var = tk.StringVar(value=initial_message)

    frame = ttk.Frame(dialog, padding=16)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, textvariable=message_var, wraplength=480).pack(
        fill=tk.X, anchor="w"
    )

    progress = ttk.Progressbar(frame, mode="indeterminate")
    progress.pack(fill=tk.X, pady=(18, 0))
    progress.start(16)

    def report(message):
        updates.put(("progress", message))

    def run_worker():
        try:
            updates.put(("done", worker(report)))
        except Exception as error:
            updates.put(("error", error))

    def poll_updates():
        while True:
            try:
                event, payload = updates.get_nowait()
            except queue.Empty:
                break

            if event == "progress":
                message_var.set(payload)
            elif event == "done":
                result["status"] = "done"
                result["value"] = payload
                progress.stop()
                dialog.destroy()
                return
            elif event == "error":
                result["status"] = "error"
                result["value"] = payload
                progress.stop()
                dialog.destroy()
                return

        dialog.after(50, poll_updates)

    dialog.protocol("WM_DELETE_WINDOW", lambda: None)
    threading.Thread(target=run_worker, daemon=True).start()
    dialog.after(50, poll_updates)
    root.wait_window(dialog)

    if result["status"] == "error":
        raise result["value"]

    return result["value"]


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

    text_box = tk.Text(text_frame, height=10, wrap="word", yscrollcommand=scrollbar.set)
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
    tk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.RIGHT, padx=(0, 8))

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

    return "mp3" if download_mp3 else "mp4"


def choose_output_dir(root):
    return askdirectory(parent=root, title="Choose download folder")
