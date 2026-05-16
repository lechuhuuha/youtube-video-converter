# Architecture Notes

## Structure

Hexagonal architecture (ports & adapters) under `src/app/`:

```text
main.py                          # backward-compat entrypoint (adds src/ to sys.path)
pyproject.toml                   # project metadata and dependencies

src/app/
  __init__.py                    # PROJECT_ROOT constant
  __main__.py                    # python -m app entrypoint
  app.py                         # detects CLI vs GUI and launches the right UI

  domain/
    models.py                    # OutputFormat, BatchResult, DownloadResult, ConversionResult
    errors.py                    # user-facing error messages and builders

  ports/
    downloader.py                # Downloader protocol, DownloaderRegistry
    converter.py                 # Converter protocol

  adapters/
    __init__.py                  # create_default_registry() factory
    ytdlp_downloader.py          # yt-dlp Downloader implementation
    local_converter.py           # moviepy Converter implementation
    cookie_store.py              # cookies.txt file handling

  application/
    jobs.py                      # batch download/conversion with progress reporting
    use_cases.py                 # single-item download/convert operations

  ui/
    tk_app.py                    # Tkinter GUI (Windows / Linux with display)
    progress.py                  # Tkinter threaded progress dialog
    cli.py                       # Terminal CLI with argparse (Linux)

  utils/
    urls.py                      # URL parsing and YouTube URL normalization
    logging.py                   # error.log writing
```

## Running

```bash
# CLI mode (Linux)
python main.py https://youtube.com/watch?v=xxx --format mp3 -o ~/music
python main.py -f urls.txt --format mp4
python main.py --local video.mp4

# GUI mode (Windows, or Linux with tkinter)
python main.py
```

## How It Works

`app.py` checks `sys.argv`: if CLI args are present, it runs `cli_main()`.
Otherwise it tries to import tkinter for the GUI; if tkinter is unavailable
(common on headless Linux), it falls back to the CLI help screen.

Downloads use the Strategy pattern via `DownloaderRegistry`. Each downloader
implements the `Downloader` protocol from `ports/downloader.py`. Currently
only `YtDlpDownloader` is registered.

Local conversion uses the `Converter` protocol from `ports/converter.py`,
implemented by `MoviePyConverter`.

Both GUI and CLI flows call the same `run_download_batch()` and
`run_conversion_batch()` functions from `application/jobs.py`, passing
different `report` callbacks for progress output.
