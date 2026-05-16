# MP4 / MP3 Converter

Download YouTube videos as MP3 or MP4, or convert local MP4 files to MP3.

## Requirements

- Python 3.10 or newer
- Node.js or Deno (so yt-dlp can solve YouTube JavaScript challenges)

## Installation

```bash
# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate    # Linux / macOS
# .venv\Scripts\activate     # Windows

# Install the package
pip install -e .
```

## Usage

### Interactive mode (easiest)

```bash
python main.py
```

Follow the prompts: paste URLs, pick a format, choose a folder.

### Command-line mode

```bash
# Download a single video as MP3
python main.py https://youtube.com/watch?v=xxx --format mp3

# Download from a file of URLs
python main.py -f urls.txt --format mp4 -o ~/videos

# Convert local MP4 files to MP3
python main.py --local video.mp4 *.mp4
```

Run `python main.py --help` for all options.

### GUI mode (Windows / Linux with display)

When no arguments are provided and a display is available, a Tkinter GUI launches automatically.

## Notes

- Put each URL on its own line for bulk downloads
- Duplicate YouTube links with tracking parameters are skipped automatically
- MP4 downloads prefer high-FPS formats when YouTube provides them
- Restricted YouTube videos may need browser cookies:
  export cookies to `cookies.txt` and place it beside `main.py`
- Keep `cookies.txt` private because it contains browser session data
- If YouTube returns HTTP 403, install a yt-dlp PO-token provider:
  https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide

## License

MIT License - see [LICENSE](LICENSE) for details.
