import argparse
import glob
import sys
from pathlib import Path

from ..application.jobs import run_conversion_batch, run_download_batch
from ..domain.models import OutputFormat
from ..utils.logging import ERROR_LOG_PATH
from ..utils.urls import parse_download_urls


def build_parser():
    parser = argparse.ArgumentParser(
        prog="mp4mp3",
        description="Download YouTube videos as MP3/MP4, or convert local MP4 files to MP3.",
    )
    parser.add_argument(
        "urls", nargs="*", default=[], help="URLs to download"
    )
    parser.add_argument(
        "-f", "--file", type=Path, help="text file containing URLs (one per line)"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("./downloads"),
        help="output directory (default: ./downloads)",
    )
    parser.add_argument(
        "--format",
        choices=["mp3", "mp4"],
        dest="output_format",
        help="output format (prompted if not specified)",
    )
    parser.add_argument(
        "--local",
        nargs="+",
        metavar="FILE",
        help="local MP4 files to convert to MP3 (supports globs)",
    )
    return parser


def ask_format():
    while True:
        try:
            choice = input("Output format - MP3 or MP4? [mp3]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)

        if choice in ("", "mp3"):
            return OutputFormat.MP3
        if choice == "mp4":
            return OutputFormat.MP4
        print("Please enter 'mp3' or 'mp4'.")


def resolve_local_files(patterns):
    paths = []
    for pattern in patterns:
        expanded = glob.glob(pattern)
        if expanded:
            paths.extend(expanded)
        else:
            path = Path(pattern)
            if path.exists():
                paths.append(str(path))
            else:
                print(f"Warning: {pattern} not found, skipping.")
    return paths


def ask_urls():
    print("Paste video URLs below (one per line).")
    print("Or enter a path to a text file containing URLs.")
    print("Leave blank and press Enter to convert local MP4 files.\n")

    lines = []
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)

        if not line:
            break
        lines.append(line)

    if not lines:
        return []

    if len(lines) == 1 and Path(lines[0]).is_file():
        text = Path(lines[0]).read_text(encoding="utf-8")
        return parse_download_urls(text)

    return parse_download_urls("\n".join(lines))


def ask_output_dir():
    try:
        folder = input("Output folder [./downloads]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)

    if not folder:
        return Path("./downloads")

    return Path(folder).expanduser()


def ask_local_files():
    print("Enter MP4 file paths (one per line, supports globs).")
    print("Press Enter on a blank line when done.\n")

    patterns = []
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)

        if not line:
            break
        patterns.append(line)

    return resolve_local_files(patterns) if patterns else []


def cli_report(message):
    lines = message.strip().split("\n")
    print(f"  [{lines[0]}]" if len(lines) == 1 else f"  [{lines[0]}] {lines[1]}")


def interactive_main():
    print("=== MP4 / MP3 Converter ===\n")

    urls = ask_urls()

    if urls:
        output_format = ask_format()
        output_dir = ask_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)

        print(
            f"\nDownloading {len(urls)} link(s) as {output_format.value.upper()} "
            f"to {output_dir}\n"
        )

        result = run_download_batch(urls, output_dir, output_format, cli_report)

        print()
        if result.failed:
            print(
                f"Done: {len(result.succeeded)} succeeded, "
                f"{len(result.failed)} failed."
            )
            for url, error in result.failed:
                print(f"  FAILED: {url}")
                print(f"          {error}")
            print(f"\nFull error details saved to: {ERROR_LOG_PATH}")
        else:
            print(f"Done: all {len(result.succeeded)} downloads succeeded.")
    else:
        file_paths = ask_local_files()
        if not file_paths:
            print("No files provided.")
            return

        print(f"\nConverting {len(file_paths)} file(s) to MP3\n")

        result = run_conversion_batch(file_paths, cli_report)

        print()
        if result.failed:
            print(
                f"Done: {len(result.succeeded)} converted, "
                f"{len(result.failed)} failed."
            )
            for name, error in result.failed:
                print(f"  FAILED: {name} - {error}")
        else:
            print(f"Done: all {len(result.succeeded)} files converted.")


def cli_main():
    parser = build_parser()
    args = parser.parse_args()

    if args.local:
        run_local_mode(args.local)
        return

    raw_urls = list(args.urls)
    if args.file:
        if not args.file.exists():
            print(f"Error: file not found: {args.file}")
            sys.exit(1)
        raw_urls.append(args.file.read_text(encoding="utf-8"))

    urls = parse_download_urls("\n".join(raw_urls))

    if not urls:
        parser.print_help()
        return

    output_format = (
        OutputFormat(args.output_format) if args.output_format else ask_format()
    )

    args.output.mkdir(parents=True, exist_ok=True)

    print(
        f"\nDownloading {len(urls)} link(s) as {output_format.value.upper()} "
        f"to {args.output}\n"
    )

    result = run_download_batch(urls, args.output, output_format, cli_report)

    print()
    if result.failed:
        print(
            f"Done: {len(result.succeeded)} succeeded, {len(result.failed)} failed."
        )
        for url, error in result.failed:
            print(f"  FAILED: {url}")
            print(f"          {error}")
        print(f"\nFull error details saved to: {ERROR_LOG_PATH}")
    else:
        print(f"Done: all {len(result.succeeded)} downloads succeeded.")


def run_local_mode(file_patterns):
    file_paths = resolve_local_files(file_patterns)
    if not file_paths:
        print("No MP4 files found.")
        return

    print(f"\nConverting {len(file_paths)} file(s) to MP3\n")

    result = run_conversion_batch(file_paths, cli_report)

    print()
    if result.failed:
        print(
            f"Done: {len(result.succeeded)} converted, {len(result.failed)} failed."
        )
        for name, error in result.failed:
            print(f"  FAILED: {name} - {error}")
    else:
        print(f"Done: all {len(result.succeeded)} files converted.")
