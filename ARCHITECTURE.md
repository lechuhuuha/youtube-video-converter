# Architecture Notes

## Current Shape

`main.py` is a thin entrypoint so `python main.py` remains simple. Application code lives in `mp4mp3_app/`:

- `app.py`: Tkinter orchestration and batch flow
- `ui.py`: dialogs, file pickers, and threaded progress window
- `local_conversion.py`: local MP4-to-MP3 conversion
- `downloaders/`: download provider registry plus yt-dlp provider/facade
- `urls.py`: URL parsing and YouTube URL normalization
- `errors.py`: user-facing error messages and logging
- `paths.py`: project-local paths such as `cookies.txt` and `error.log`

This is still deliberately small. The app does not yet need a large class hierarchy.

## Recommended Patterns

Online downloads use Strategy. Each downloader exposes the same small interface:

```python
class DownloadProvider:
    def supports(self, url: str) -> bool: ...
    def download(self, url: str, output_dir: Path, output_format: str) -> str: ...
```

Current and future examples:

- `YtDlpProvider` handles YouTube and other yt-dlp-supported sites today
- `DirectHttpProvider` could handle direct `.mp4`/`.mp3` URLs later
- `LocalFileProvider` could move local conversion into the same job pipeline later

The Registry/Factory selects the provider:

```python
provider = provider_registry.resolve(url)
provider.download(url, output_dir, output_format)
```

`YtDlpFacade` owns yt-dlp details. The GUI does not know about cookies, JS runtimes, HLS fallback, or format selectors.

Use Command for batch work if the app grows. A batch can become a list of jobs such as `DownloadJob` and `ConvertJob`, each with a common `run(report)` method.

## Current Module Split

```text
main.py                   # entrypoint only
mp4mp3_app/
  app.py                  # Tkinter orchestration and batch flow
  ui.py                   # dialogs, pickers, progress window
  urls.py                 # URL parsing and normalization
  local_conversion.py     # local MP4 -> MP3 conversion
  downloaders/
    base.py               # provider protocol
    registry.py           # provider registry/factory
    ytdlp_provider.py     # yt-dlp provider strategy
    ytdlp_facade.py       # yt-dlp options/retry/cookie details
  errors.py               # user-facing error messages and logging
  paths.py                # project-local paths
```

If more download providers are added later, register them in `create_default_registry()` without changing the GUI flow.
