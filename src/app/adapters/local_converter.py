from pathlib import Path


class MoviePyConverter:
    def convert(self, source_path):
        VideoFileClip = _load_video_file_clip()

        source_path = Path(source_path)
        if source_path.suffix.lower() != ".mp4":
            raise ValueError("Only .mp4 files are supported")

        mp3_path = source_path.with_suffix(".mp3")
        if mp3_path.exists():
            raise FileExistsError(f"{mp3_path.name} already exists")

        with VideoFileClip(str(source_path)) as video:
            if video.audio is None:
                raise ValueError("No audio track found")
            video.audio.write_audiofile(str(mp3_path))

        return mp3_path


def _load_video_file_clip():
    try:
        from moviepy.editor import VideoFileClip
    except ModuleNotFoundError:
        try:
            from moviepy import VideoFileClip
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "moviepy is not installed. Install it with: pip install moviepy"
            ) from error
    return VideoFileClip
