import queue
import threading
import tkinter as tk
from tkinter import ttk


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
